-- srt_importer.lua
-- Reads a .srt subtitle file and creates Text+ clips on the timeline.
-- Run from: Workspace > Scripts > Comp > srt_importer (DaVinci Resolve Studio 18+)

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
    fu:AskUser("SRT Importer — Error", {
        {"Message", "Text", Lines = 4, ReadOnly = true, Default = msg}
    })
end

-- Get project and timeline (works from any page)
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
local settings = fu:AskUser("SRT Subtitle Importer", {
    {"SRTFile",  "FileBrowse", Default = os.getenv("HOME") or "/"},
    {"FontSize", "Slider",     Min = 20, Max = 120, Default = 60, Integer = true},
})
if not settings then return end

local srtPath  = settings["SRTFile"]
local fontSize = settings["FontSize"]

if not srtPath or srtPath == "" then
    showError("No SRT file selected.")
    return
end

-- ── SRT parser ──────────────────────────────────────────────────────────────
-- Returns array of {startSec, endSec, text}

local function parseSRTTimecode(tc)
    -- Format: HH:MM:SS,mmm
    local h, m, s, ms = tc:match("(%d+):(%d+):(%d+),(%d+)")
    if not h then return nil end
    return tonumber(h) * 3600 + tonumber(m) * 60 + tonumber(s) + tonumber(ms) / 1000
end

local function parseSRT(path)
    local f, err = io.open(path, "r")
    if not f then
        return nil, "Cannot open file: " .. (err or path)
    end
    local content = f:read("*a")
    f:close()

    -- Normalise line endings
    content = content:gsub("\r\n", "\n"):gsub("\r", "\n")

    local entries = {}
    -- Split into blocks separated by one or more blank lines
    for block in content:gmatch("([^\n]+\n[^\n]+\n.-)\n*\n") do
        -- Line 1: index (ignored)
        -- Line 2: timecode range
        -- Lines 3+: text
        local lines = {}
        for line in (block .. "\n"):gmatch("([^\n]*)\n") do
            table.insert(lines, line)
        end
        if #lines >= 2 then
            local tcLine = lines[2]
            local tcStart, tcEnd = tcLine:match("([%d:,]+)%s*%-%-%>%s*([%d:,]+)")
            if tcStart and tcEnd then
                local startSec = parseSRTTimecode(tcStart)
                local endSec   = parseSRTTimecode(tcEnd)
                -- Collect text lines (3 onwards), strip HTML tags
                local textParts = {}
                for i = 3, #lines do
                    local t = lines[i]:gsub("<[^>]+>", "")
                    if t ~= "" then
                        table.insert(textParts, t)
                    end
                end
                local text = table.concat(textParts, "\n")
                if startSec and endSec and text ~= "" then
                    table.insert(entries, {
                        startSec = startSec,
                        endSec   = endSec,
                        text     = text,
                    })
                end
            end
        end
    end
    return entries, nil
end

-- ── Timeline helpers ─────────────────────────────────────────────────────────

local fps = tonumber(timeline:GetSetting("timelineFrameRate")) or 24

local function secToFrames(sec)
    return math.floor(sec * fps + 0.5)
end

-- Timeline start offset in frames (for timecode alignment)
local timelineStartTC = timeline:GetStartTimecode() or "00:00:00:00"
local function tcStringToFrames(tc)
    local h, m, s, ff = tc:match("(%d+):(%d+):(%d+):(%d+)")
    if not h then return 0 end
    return (tonumber(h)*3600 + tonumber(m)*60 + tonumber(s)) * math.floor(fps + 0.5) + tonumber(ff)
end
local timelineStartFrame = tcStringToFrames(timelineStartTC)

-- ── Parse SRT ────────────────────────────────────────────────────────────────

local entries, parseErr = parseSRT(srtPath)
if not entries then
    showError(parseErr or "Failed to parse SRT file.")
    return
end
if #entries == 0 then
    showError("No subtitle entries found in the SRT file.")
    return
end

-- ── Add a new video track for subtitles ─────────────────────────────────────

local subtitleTrackIndex = timeline:GetTrackCount("video") + 1
local ok = timeline:AddTrack("video")
if not ok then
    showError("Could not add a new video track for subtitles.")
    return
end

-- ── Insert Text+ clips ───────────────────────────────────────────────────────

local mediaPool = project:GetMediaPool()
local inserted  = 0
local skipped   = 0

for _, entry in ipairs(entries) do
    local startFrame = timelineStartFrame + secToFrames(entry.startSec)
    local endFrame   = timelineStartFrame + secToFrames(entry.endSec)
    local durFrames  = endFrame - startFrame
    if durFrames < 1 then durFrames = 1 end

    -- Move playhead to the start of this subtitle so the generator lands there
    timeline:SetCurrentTimecode(
        string.format("%02d:%02d:%02d:%02d",
            math.floor(startFrame / (fps * 3600)),
            math.floor(startFrame / (fps * 60)) % 60,
            math.floor(startFrame / fps) % 60,
            startFrame % math.floor(fps + 0.5)
        )
    )

    -- Insert a Fusion Title (Text+) at the playhead on the subtitle track
    local clipInfo = {
        startFrame   = startFrame,
        endFrame     = endFrame,
        mediaType    = "Fusion Title",
        trackIndex   = subtitleTrackIndex,
    }

    local newItem = timeline:InsertFusionTitleIntoTimeline("Text+")

    if newItem then
        -- Open the Fusion comp of this clip and set the text and font size
        local itemComp = newItem:GetFusionCompByIndex(1)
        if itemComp then
            itemComp:Lock()
            local textNode = itemComp:FindToolByID("Template")
                          or itemComp:FindToolByID("Text1")
            if textNode then
                textNode.StyledText = entry.text
                textNode.Size       = fontSize / 1000  -- Fusion normalises size to ~0–1
            end
            itemComp:Unlock()
        end
        inserted = inserted + 1
    else
        -- Fallback: log to console for manual creation
        print(string.format("SKIPPED [%s --> %s]: %s",
              string.format("%.3f", entry.startSec),
              string.format("%.3f", entry.endSec),
              entry.text))
        skipped = skipped + 1
    end
end

-- ── Done ─────────────────────────────────────────────────────────────────────

local msg
if skipped == 0 then
    msg = string.format("Successfully inserted %d subtitle clip(s) on Video Track %d.",
                        inserted, subtitleTrackIndex)
else
    msg = string.format("Inserted %d clip(s); %d skipped (see Fusion Console for details).\nVideo Track %d.",
                        inserted, skipped, subtitleTrackIndex)
end

fu:AskUser("SRT Importer — Done", {
    {"Message", "Text", Lines = 4, ReadOnly = true, Default = msg}
})
