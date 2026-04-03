# Smooth Zoom — DaVinci Resolve Script

A Lua script that applies a smooth animated zoom in or zoom out effect to any clip in the Edit page timeline. The animation uses Fusion's cubic spline interpolation for a natural ease-in/ease-out feel over the full clip duration.

---

## Requirements

- DaVinci Resolve **Studio** 17 or later (tested on version 20)
- macOS or Windows

---

## Installation

### Option A — DRFX (recommended, one-click)

1. Download `smooth_zoom.drfx`.
2. Double-click the file. DaVinci Resolve opens and asks if you want to install the bundle.
3. Click **Install**. The script is placed in the correct folder automatically.
4. Restart DaVinci Resolve.

### Option B — Manual

Copy `smooth_zoom.lua` into the DaVinci Resolve Comp scripts folder:

**macOS**
```
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/
```

**Windows**
```
%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\
```

If the `Comp` folder does not exist, create it. Restart DaVinci Resolve after copying the file.

---

## Usage

1. Open DaVinci Resolve Studio and switch to the **Edit** page.
2. Place a video clip on the timeline.
3. Move the **playhead** over the clip you want to zoom.
4. Go to **Workspace > Scripts > Comp > smooth_zoom**.
5. In the dialog, choose your settings and click **OK**.
6. The zoom animation is applied. The Edit page regains focus automatically.

To verify the effect, right-click the clip and choose **Open in Fusion Page** — you will see a Transform node wired between MediaIn and MediaOut with two Size keyframes.

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Direction | Zoom In | Zoom In / Zoom Out | Whether the scale grows (zoom in) or shrinks (zoom out) over the clip |
| Amount | 1.3 | 1.05 – 2.0 | Peak scale factor. `1.3` = 130% size at peak; `2.0` = 200% (double size) |

---

## Removing the Effect

Right-click the clip in the timeline and select **Delete Fusion Composition**.

Alternatively, open the clip in the Fusion page, delete the Transform node, and reconnect MediaIn directly to MediaOut.

---

## Limitations

- Operates on the **clip at the playhead** position only. Move the playhead over each clip you want to affect and run the script again.
- If the clip already has a Fusion composition, the script reuses it and replaces any existing Transform node. Other Fusion nodes in the comp are left untouched.
- The Fusion page may briefly become visible while the comp is being built. The script returns focus to the Edit page when done.
- Re-running the script on the same clip replaces the prior zoom effect with the new parameters.
- Audio-only clips and gap clips are not supported.
