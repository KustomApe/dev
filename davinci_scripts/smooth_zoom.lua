-- smooth_zoom.lua
-- Adds a smooth zoom in/out effect to the clip at the current playhead position.
-- Run from: Workspace > Scripts > Comp > smooth_zoom (DaVinci Resolve Studio 17+)

local resolve = bmd.scriptapp("Resolve")
if not resolve then
    print("ERROR: Could not connect to DaVinci Resolve.")
    return
end

local fu = resolve:Fusion()
if not fu then
    print("ERROR: Could not access Fusion scripting API.")
    return
end

local function showError(msg)
    fu:AskUser("Smooth Zoom — Error", {
        {"Message", "Text", Lines = 3, ReadOnly = true, Default = msg}
    })
end

-- Must be on the Edit page
if resolve:GetCurrentPage() ~= "edit" then
    showError("Please switch to the Edit page before running this script.")
    return
end

-- Get current project and timeline
local project = resolve:GetProjectManager():GetCurrentProject()
if not project then
    showError("No project is currently open.")
    return
end

local timeline = project:GetCurrentTimeline()
if not timeline then
    showError("No active timeline found.")
    return
end

-- Get clip at the current playhead position
local item = timeline:GetCurrentVideoItem()
if not item then
    showError("No clip found at the current playhead position.\nMove the playhead over a clip and try again.")
    return
end

-- Show settings dialog
local settings = fu:AskUser("Smooth Zoom", {
    {"Direction", "Dropdown", Options = {"Zoom In", "Zoom Out"}, Default = 1},
    {"Amount",    "Slider",   Min = 1.05, Max = 2.0, Default = 1.3, Integer = false},
})
if not settings then return end  -- user cancelled

-- Dropdown returns 1-based index when Default = 1 means first item
-- Resolve/Fusion versions vary; treat 1 (or 0 in some builds) as "Zoom In"
local dirValue = settings["Direction"]
local zoomIn = (dirValue == 1 or dirValue == 0)
local amount = settings["Amount"]

-- Clip duration in comp-relative frames (0-indexed)
local duration  = item:GetDuration()
local compStart = 0
local compEnd   = duration - 1

-- Open or create the Fusion composition on this clip
local comp
if item:GetFusionCompCount() > 0 then
    comp = item:GetFusionCompByIndex(1)
else
    comp = item:AddFusionComp()
end

if not comp then
    showError("Failed to open or create a Fusion composition on this clip.")
    return
end

comp:Lock()

-- Locate the required MediaIn and MediaOut nodes
local mediaIn  = comp:FindToolByID("MediaIn1")
local mediaOut = comp:FindToolByID("MediaOut1")
if not mediaIn or not mediaOut then
    comp:Unlock()
    showError("Could not find MediaIn/MediaOut nodes in the Fusion composition.")
    return
end

-- Remove any existing Transform node from a prior run
local existing = comp:FindToolByID("Transform1")
if existing then
    existing:Delete()
end

-- Add the Transform node and wire it between MediaIn and MediaOut
local transform = comp:AddTool("Transform", 1, 0)
transform.Center = { 0.5, 0.5 }  -- scale from centre, no translation
transform:ConnectInput("Input", mediaIn,   "Output")
mediaOut:ConnectInput("Input",  transform, "Output")

-- Set the comp render range to match the clip length
comp:SetAttrs({
    COMPN_RenderStart = compStart,
    COMPN_RenderEnd   = compEnd,
})

-- Animate Size with two keyframes — Fusion uses smooth cubic spline by default
if zoomIn then
    transform.Size[compStart] = 1.0
    transform.Size[compEnd]   = amount
else
    transform.Size[compStart] = amount
    transform.Size[compEnd]   = 1.0
end

comp:Unlock()

-- Return focus to the Edit page
resolve:OpenPage("edit")

print("Smooth zoom applied: " .. (zoomIn and "Zoom In" or "Zoom Out") ..
      ", Amount=" .. string.format("%.2f", amount) ..
      ", Duration=" .. duration .. " frames.")
