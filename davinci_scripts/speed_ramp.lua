-- speed_ramp.lua
-- Applies a smooth speed ramp to the clip at the playhead via a Fusion TimeSpeed node.
-- Run from: Workspace > Scripts > Comp > speed_ramp (DaVinci Resolve Studio 17+)

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
    fu:AskUser("Speed Ramp — Error", {
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
local settings = fu:AskUser("Speed Ramp", {
    {"Shape",   "Dropdown", Options = {"Ramp Down (normal → slow)", "Ramp Up (slow → normal)", "Valley (normal → slow → normal)"}, Default = 1},
    {"SlowPct", "Slider",   Min = 5, Max = 75, Default = 25, Integer = true},
})
if not settings then return end

local shape    = settings["Shape"]    -- 1=RampDown 2=RampUp 3=Valley
local slowPct  = settings["SlowPct"]
local slowFrac = slowPct / 100.0

-- Handle 0-based dropdown in some Resolve builds
if shape == 0 then shape = 1 end

-- Clip frame range (comp-relative, 0-indexed)
local duration  = item:GetDuration()
local compStart = 0
local compEnd   = duration - 1

if duration < 3 then
    showError("Clip is too short for a speed ramp (minimum 3 frames).")
    return
end

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

-- Remove stale TimeSpeed from a prior run
local old = comp:FindToolByID("TimeSpeed1")
if old then old:Delete() end

-- Add TimeSpeed node and wire it
local ts = comp:AddTool("TimeSpeed", 1, 0)
ts:ConnectInput("Input", mediaIn, "Output")
mediaOut:ConnectInput("Input", ts, "Output")

-- Set comp render range
comp:SetAttrs({
    COMPN_RenderStart = compStart,
    COMPN_RenderEnd   = compEnd,
})

-- Set keyframes based on shape
-- Speed=1.0 is normal; Speed=slowFrac is slow motion
if shape == 1 then
    -- Ramp Down: normal at start, slow at end
    ts.Speed[compStart] = 1.0
    ts.Speed[compEnd]   = slowFrac

elseif shape == 2 then
    -- Ramp Up: slow at start, normal at end
    ts.Speed[compStart] = slowFrac
    ts.Speed[compEnd]   = 1.0

else
    -- Valley: normal → slow → normal
    local third = math.floor(compEnd / 3)
    ts.Speed[compStart]         = 1.0
    ts.Speed[third]             = slowFrac
    ts.Speed[compEnd - third]   = slowFrac
    ts.Speed[compEnd]           = 1.0
end

comp:Unlock()

resolve:OpenPage("edit")

local shapeNames = {"Ramp Down", "Ramp Up", "Valley"}
print(string.format("Speed ramp applied: shape=%s, slow=%d%%, duration=%d frames.",
      shapeNames[shape] or "?", slowPct, duration))
