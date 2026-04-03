# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository contains scripts and effects for DaVinci Resolve Studio. The primary languages used are:

- **Lua** — DaVinci Resolve's native scripting language for macros, effects, and automation via the Fusion scripting API
- **Python** — for DaVinci Resolve's external scripting API (project management, timeline automation, color grading, etc.)
- **DCTL (DaVinci Color Transform Language)** — a C-like language for custom LUT/color transforms usable in Resolve's Color page

## DaVinci Resolve Scripting Environments

### Fusion (Lua/Python inside Resolve)
Scripts live in one of:
- `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/` — general scripts
- `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/` — comp scripts (run via Fusion > Scripts menu)
- `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Tool/` — tool scripts (run on selected nodes)
- `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Macros/` — reusable Fusion macros (`.setting` files)

### External Python Scripting API
Scripts connect to a running DaVinci Resolve instance via the `DaVinciResolveScript` module. Requires Resolve to be open.

```python
import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
```

The module path on macOS:
`/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/`

### DCTL Files
- Extension: `.dctl`
- Installed to: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
- Applied as LUTs or via the DCTL transform in the Color page

## Running Scripts

**Lua scripts (inside Resolve):** Load via Fusion > Scripts menu, or place in the Macros folder and access via the Effects Library.

**Python scripts (external):** Ensure DaVinci Resolve is running, then:
```bash
python3 <script_name>.py
```
Add the scripting modules to your path if needed:
```bash
export PYTHONPATH="$PYTHONPATH:/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
```

**DCTL:** Copy `.dctl` files to the LUT directory; they appear in Resolve's LUT browser after a rescan.

## Key API References

- Resolve scripting API docs: installed at `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt`
- Fusion scripting guide: accessible from Resolve's Help menu
- DCTL language reference: included with Resolve at `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/DCTL/`
