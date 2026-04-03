# DaVinci Resolve Studio Scripts

A collection of Lua plugins for DaVinci Resolve Studio. Each plugin is available as a one-click `.drfx` installer or a manual `.lua` file.

---

## Installation

### Option A — DRFX (recommended, one-click)

1. Download the `.drfx` file for the plugin you want.
2. Double-click it. DaVinci Resolve opens and asks if you want to install the bundle.
3. Click **Install**. Restart DaVinci Resolve.

### Option B — Manual

Copy the `.lua` file into the DaVinci Resolve Comp scripts folder:

**macOS**
```
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/
```

**Windows**
```
%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\
```

Create the `Comp` folder if it does not exist, then restart DaVinci Resolve.

---

## Running a Script

All scripts are available inside Resolve at **Workspace > Scripts > Comp > `<script name>`**.

---

## Plugins

---

### Smooth Zoom (`smooth_zoom`)

Applies a smooth animated zoom in or zoom out to the clip at the current playhead position. Uses Fusion's cubic spline interpolation for a natural ease-in/ease-out feel.

**Files:** `smooth_zoom.lua` · `smooth_zoom.drfx`

**Usage**
1. Switch to the **Edit** page.
2. Move the playhead over a clip.
3. Run **Workspace > Scripts > Comp > smooth_zoom**.
4. Set parameters and click **OK**.

**Parameters**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Direction | Zoom In | Zoom In / Zoom Out | Whether scale grows or shrinks over the clip |
| Amount | 1.3 | 1.05 – 2.0 | Peak scale factor (1.0 = original size) |

**Removing the effect:** Right-click the clip → **Delete Fusion Composition**.

---

### Ken Burns Effect (`ken_burns`)

Applies an animated slow pan and zoom to the clip at the playhead. Ideal for still images. Direction and zoom amount are fully configurable.

**Files:** `ken_burns.lua` · `ken_burns.drfx`

**Usage**
1. Switch to the **Edit** page.
2. Move the playhead over a clip or still image.
3. Run **Workspace > Scripts > Comp > ken_burns**.
4. Set parameters and click **OK**.

**Parameters**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Direction | Left | Left / Right / Up / Down / No Pan (zoom only) | Pan direction over clip duration |
| Zoom Amount | 1.2 | 1.05 – 1.5 | How much to zoom in (scale factor at clip end) |

**Removing the effect:** Right-click the clip → **Delete Fusion Composition**.

---

### Speed Ramp (`speed_ramp`)

Applies a smooth speed ramp to the clip at the playhead using a Fusion TimeSpeed node. Choose from three ramp shapes: slow down, speed up, or a valley (normal → slow → normal).

**Files:** `speed_ramp.lua` · `speed_ramp.drfx`

**Usage**
1. Switch to the **Edit** page.
2. Move the playhead over a clip.
3. Run **Workspace > Scripts > Comp > speed_ramp**.
4. Set parameters and click **OK**.

**Parameters**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Shape | Ramp Down | Ramp Down / Ramp Up / Valley | Speed curve shape over the clip |
| Slow % | 25 | 5 – 75 | Playback speed at the slowest point (% of original) |

**Removing the effect:** Right-click the clip → **Delete Fusion Composition**.

---

### SRT Subtitle Importer (`srt_importer`)

Reads a `.srt` subtitle file and creates Text+ title clips on a new video track in the current timeline, timed to each subtitle entry.

**Files:** `srt_importer.lua` · `srt_importer.drfx`

**Requirements:** DaVinci Resolve Studio **18 or later** (uses `InsertFusionTitleIntoTimeline`).

**Usage**
1. Open the project and timeline where you want subtitles.
2. Run **Workspace > Scripts > Comp > srt_importer** from any page.
3. Browse to your `.srt` file, set a font size, and click **OK**.
4. A new video track is created with one Text+ clip per subtitle entry.

**Parameters**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| SRT File | — | — | Path to the `.srt` subtitle file |
| Font Size | 60 | 20 – 120 | Text size for all subtitle clips |

**Notes**
- If a subtitle clip cannot be inserted automatically, the entry is logged to the Fusion Console (timecode and text) for manual creation.
- HTML tags (`<i>`, `<b>`, etc.) in the SRT file are stripped from the displayed text.
- The script places clips on a new top video track and does not modify existing clips.

---

### Clip List Exporter (`clip_list_exporter`)

Exports all clips in the current timeline to a timestamped CSV file. Each row contains the track number, clip name, source file path, start/end timecodes, and duration.

**Files:** `clip_list_exporter.lua` · `clip_list_exporter.drfx`

**Usage**
1. Open the timeline you want to export.
2. Run **Workspace > Scripts > Comp > clip_list_exporter** from any page.
3. Choose an output folder and click **OK**.
4. A CSV file named `clip_list_YYYYMMDD_HHMMSS.csv` is saved to the chosen folder.

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| Output Folder | Home folder | Directory where the CSV is saved |
| Tracks | All Video Tracks | Export all tracks or Track 1 only |

**CSV columns:** Track, Clip Name, Source File, Start Frame, End Frame, Duration Frames, Start TC, End TC, Duration TC

---

## Requirements

- DaVinci Resolve **Studio** 17 or later for all plugins except SRT Importer
- DaVinci Resolve **Studio** 18 or later for SRT Subtitle Importer
- macOS or Windows
