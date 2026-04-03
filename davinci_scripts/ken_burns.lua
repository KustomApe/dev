-- ken_burns.lua
-- Applies an animated slow pan + zoom (Ken Burns effect) to the clip at the playhead.
-- Ideal for still images. Run from: Workspace > Scripts > Comp > ken_burns
-- DaVinci Resolve Studio 17+

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
    fu:AskUser("Ken Burns — Error", {
        {"Message", "Text", Lines = 3, ReadOnly = true, Default = msg}
    })
end

-- Must be on the Edit page
if resolve:GetCurrentPage() ~= "edit" then
    showError("Please switch to the Edit page before running this script.")
    return
end

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

local item = timeline:GetCurrentVideoItem()
if not item then
    showError("No clip found at the current playhead position.\nMove the playhead over a clip and try again.")
    return
end

-- Show settings dialog
local settings = fu:AskUser("Ken Burns Effect", {
    {"Direction",   "Dropdown", Options = {"Left", "Right", "Up", "Down", "No Pan (zoom only)"}, Default = 1},
    {"ZoomAmount",  "Slider",   Min = 1.05, Max = 1.5, Default = 1.2, Integer = false},
})
if not settings then return end

local dirValue  = settings["Direction"]   -- 1=Left 2=Right 3=Up 4=Down 5=No Pan
local amount    = settings["ZoomAmount"]

-- Pan presets: {startCenter, endCenter}
-- Center is expressed as {X, Y} in 0–1 space; 0.5,0.5 = frame centre
local panPresets = {
    [1] = { {0.55, 0.5},  {0.45, 0.5}  },  -- Left
    [2] = { {0.45, 0.5},  {0.55, 0.5}  },  -- Right
    [3] = { {0.5,  0.55}, {0.5,  0.45} },  -- Up
    [4] = { {0.5,  0.45}, {0.5,  0.55} },  -- Down
    [5] = { {0.5,  0.5},  {0.5,  0.5}  },  -- No Pan
}

-- Handle 0-based dropdown in some Resolve builds
if dirValue == 0 then dirValue = 1 end
local preset = panPresets[dirValue] or panPresets[1]
local startCenter = preset[1]
local endCenter   = preset[2]

-- Clip frame range (comp-relative, 0-indexed)
local duration  = item:GetDuration()
local compStart = 0
local compEnd   = duration - 1

-- Open or create Fusion comp
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

local mediaIn  = comp:FindToolByID("MediaIn1")
local mediaOut = comp:FindToolByID("MediaOut1")
if not mediaIn or not mediaOut then
    comp:Unlock()
    showError("Could not find MediaIn/MediaOut nodes in the Fusion composition.")
    return
end

-- Remove stale Transform from a prior run
local old = comp:FindToolByID("Transform1")
if old then old:Delete() end

-- Add Transform node and wire it
local transform = comp:AddTool("Transform", 1, 0)
transform:ConnectInput("Input", mediaIn,   "Output")
mediaOut:ConnectInput("Input",  transform, "Output")

-- Set comp render range
comp:SetAttrs({
    COMPN_RenderStart = compStart,
    COMPN_RenderEnd   = compEnd,
})

-- Animate Size (zoom always starts at 1.0 and grows)
transform.Size[compStart] = 1.0
transform.Size[compEnd]   = amount

-- Animate Center (pan) — smooth cubic spline by default
transform.Center[compStart] = startCenter
transform.Center[compEnd]   = endCenter

comp:Unlock()

resolve:OpenPage("edit")

local dirNames = {"Left", "Right", "Up", "Down", "No Pan"}
print(string.format("Ken Burns applied: pan=%s, zoom=%.2f, duration=%d frames.",
      dirNames[dirValue] or "?", amount, duration))
