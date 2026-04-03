-- clip_list_exporter.lua
-- Exports all clips in the current timeline to a CSV file.
-- Run from: Workspace > Scripts > Comp > clip_list_exporter (DaVinci Resolve Studio 17+)

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
    fu:AskUser("Clip List Exporter — Error", {
        {"Message", "Text", Lines = 3, ReadOnly = true, Default = msg}
    })
end

-- Get project and timeline
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

-- Show settings dialog
local settings = fu:AskUser("Clip List Exporter", {
    {"OutputFolder", "PathBrowse", Default = os.getenv("HOME") or "/tmp"},
    {"Tracks",       "Dropdown",  Options = {"All Video Tracks", "Track 1 Only"}, Default = 1},
})
if not settings then return end

local outputFolder = settings["OutputFolder"]
if not outputFolder or outputFolder == "" then
    showError("No output folder selected.")
    return
end

-- Timecode conversion: frames → HH:MM:SS:FF
local fps = tonumber(timeline:GetSetting("timelineFrameRate")) or 24

local function framesToTC(totalFrames, rate)
    rate = math.floor(rate + 0.5)
    local ff = totalFrames % rate
    local totalSec = math.floor(totalFrames / rate)
    local ss = totalSec % 60
    local totalMin = math.floor(totalSec / 60)
    local mm = totalMin % 60
    local hh = math.floor(totalMin / 60)
    return string.format("%02d:%02d:%02d:%02d", hh, mm, ss, ff)
end

-- CSV escaping: wrap in quotes if value contains comma, quote, or newline
local function csvEscape(val)
    val = tostring(val or "")
    if val:find('[,"\n]') then
        val = '"' .. val:gsub('"', '""') .. '"'
    end
    return val
end

-- Collect clips
local trackMode = settings["Tracks"]  -- 1 = All, 2 = Track 1 Only
local trackCount = timeline:GetTrackCount("video")
local startTrack = 1
local endTrack   = (trackMode == 2) and 1 or trackCount

local rows = {}
table.insert(rows, "Track,Clip Name,Source File,Start Frame,End Frame,Duration Frames,Start TC,End TC,Duration TC")

local clipCount = 0

for t = startTrack, endTrack do
    local clips = timeline:GetItemListInTrack("video", t)
    if clips then
        for _, clip in ipairs(clips) do
            local name      = clip:GetName() or ""
            local startF    = clip:GetStart() or 0
            local endF      = clip:GetEnd()   or 0
            local durF      = clip:GetDuration() or 0
            local startTC   = framesToTC(startF, fps)
            local endTC     = framesToTC(endF,   fps)
            local durTC     = framesToTC(durF,   fps)

            local srcPath = ""
            local mediaItem = clip:GetMediaPoolItem()
            if mediaItem then
                srcPath = mediaItem:GetClipProperty("File Path") or ""
            end

            table.insert(rows, table.concat({
                csvEscape(t),
                csvEscape(name),
                csvEscape(srcPath),
                csvEscape(startF),
                csvEscape(endF),
                csvEscape(durF),
                csvEscape(startTC),
                csvEscape(endTC),
                csvEscape(durTC),
            }, ","))
            clipCount = clipCount + 1
        end
    end
end

-- Write CSV file
local outPath = outputFolder .. "/clip_list_" .. os.date("%Y%m%d_%H%M%S") .. ".csv"
local f, err = io.open(outPath, "w")
if not f then
    showError("Could not write file:\n" .. (err or outPath))
    return
end
f:write(table.concat(rows, "\n"))
f:close()

-- Success dialog
fu:AskUser("Clip List Exporter — Done", {
    {"Message", "Text", Lines = 4, ReadOnly = true,
     Default = string.format("Exported %d clip(s) from %d track(s).\n\nSaved to:\n%s",
                             clipCount, (endTrack - startTrack + 1), outPath)}
})
