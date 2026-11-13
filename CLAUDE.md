# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Tooling to slim down a home TCL Android TV (Android TV 9/10/11, not Google TV) so only **YouTube** (`com.google.android.youtube.tv`) and **one Israeli TV-provider app** (Cellcom TV / yes+ / HOT / Partner TV) remain enabled. `README.md` is the end-user guide, written in Hebrew; keep user-facing text Hebrew.

## Commands

No build, lint or test suite. Python 3.8+ stdlib only; requires `adb` (Android platform-tools) on PATH.

```
python3 -m py_compile tcl_slim.py                  # syntax check (only check runnable in the cloud)
python tcl_slim.py --ip <TV_IP>                    # dry run: prints what would be disabled
python tcl_slim.py --ip <TV_IP> --apply            # disable apps, write state file, reboot TV
python tcl_slim.py --ip <TV_IP> --restore          # re-enable everything in the state file
```

The TV is on the user's home LAN (private IP). Cloud sessions cannot reach it: the user must run the script on a home computer and paste output back, or connect a machine via Remote Control.

## How `tcl_slim.py` works

- Connects with `adb connect <ip>:5555`, then builds the disable list as: (all third-party packages ∪ installed entries of `KNOWN_BLOAT`) − keep-set − anything matching `PROTECTED_PREFIXES`.
- The provider app is **detected on the TV** by keyword match (`PROVIDER_KEYWORDS`) and confirmed interactively. Exact Israeli provider package names are unverified — don't hardcode them without evidence from a real device.
- Uses `pm disable-user --user 0` (reversible), never uninstall. Successfully disabled packages are merged into `disabled_packages.txt` (gitignored) next to the script; `--restore` reads that file. Also sets the three global animation scales to 0.5 (restore resets to 1.0).

## Safety invariants (keep when editing)

- Dry run must stay the default; `--apply` is opt-in.
- `PROTECTED_PREFIXES` must keep covering: launchers, Settings/`com.android.*`, GMS/GSF, Play Store (needed to update the two kept apps), WebView, keyboard, voice search (`katniss`), Chromecast built-in (`mediashell`), and all vendor/SoC packages (`com.tcl.*`, `com.mediatek.*`, etc. — HDMI inputs, picture, tuner). TCL-specific packages are never auto-disabled.
- `KNOWN_BLOAT` includes TalkBack; the README tells users to remove it if someone needs a screen reader.
