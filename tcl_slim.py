#!/usr/bin/env python3
"""
tcl_slim.py - slim down a TCL Android TV (9/10/11) to YouTube + one Israeli TV-provider app.

Safety model:
  * Default is DRY RUN: it only prints what it would do. Use --apply to act.
  * Apps are DISABLED (pm disable-user), never uninstalled from the system image.
    Everything is reversible with:  python tcl_slim.py --restore
  * System-critical packages (launcher, settings, Google services, WebView,
    Play Store, TCL TV/input/system packages, Chromecast) are never touched.
  * Every package that gets disabled is written to disabled_packages.txt so
    --restore knows exactly what to re-enable.

Requirements: Python 3.8+, adb (Android platform-tools) in PATH, ADB debugging on the TV.
Usage:
  python tcl_slim.py --ip 192.168.1.50            # dry run
  python tcl_slim.py --ip 192.168.1.50 --apply    # actually disable
  python tcl_slim.py --ip 192.168.1.50 --restore  # undo everything
"""
import argparse
import os
import subprocess
import sys

YOUTUBE = "com.google.android.youtube.tv"
# User's provider is Cellcom TV+. Its Android TV package name is NOT verified,
# so it is detected on the TV by this keyword and confirmed at runtime.
PREFERRED_PROVIDER_KEYWORD = "cellcom"

# Keywords used to auto-detect the TV provider app. The exact package names of
# Cellcom TV / yes+ / HOT / Partner TV were not verified, so the script detects
# them on the TV itself and asks you to confirm.
PROVIDER_KEYWORDS = ("cellcom", "yes", "hot", "partner", "sting")

# Never disable anything that matches these prefixes / names.
PROTECTED_PREFIXES = (
    "android",
    "com.android.",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.tvlauncher",       # stock home screen
    "com.google.android.leanbacklauncher",
    "com.google.android.apps.tv.launcherx",
    "com.google.android.tv.remote",        # remote services: phone remote app, BT remote pairing
    "com.google.android.tv.remote.service",
    "com.google.android.tv.axel",          # remote/accessory pairing on some builds
    "com.google.android.bluetooth",
    "com.google.android.apps.tv.remote",
    "com.google.android.tvsetup",
    "com.google.android.tungsten.setupwraith",
    "com.google.android.webview",
    "com.google.android.apps.mediashell",  # Chromecast built-in (cast from phone to YouTube)
    "com.google.android.katniss",          # voice search / remote mic
    "com.google.android.inputmethod",      # on-screen keyboard
    "com.google.android.leanback.ime",
    "com.android.vending",                 # Play Store - needed to update the 2 apps
    "com.google.android.tv.bugreportsender",
    "com.tcl.",                            # TCL system: inputs, picture, tuner, settings
    "com.mediatek.",
    "com.realtek.",
    "com.amlogic.",
    "com.droidlogic.",
    "com.mstar.",
)

# Pre-installed apps that are known to be safe to disable on Android TV.
# Only the ones actually installed on your TV are touched.
KNOWN_BLOAT = (
    "com.netflix.ninja",
    "com.amazon.amazonvideo.livingroom",
    "com.disney.disneyplus",
    "com.spotify.tv.android",
    "com.google.android.youtube.tvmusic",
    "com.google.android.youtube.tvkids",
    "com.google.android.youtube.tvunplugged",
    "com.google.android.videos",            # Play Movies / Google TV app
    "com.google.android.music",
    "com.google.android.play.games",
    "com.google.android.tvrecommendations",
    "com.google.android.feedback",
    "com.google.android.marvin.talkback",   # screen reader - keep if someone needs it!
    "com.facebook.katana",
    "com.plexapp.android",
    "tv.twitch.android.app",
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "disabled_packages.txt")


def adb(serial, *args, check=True):
    cmd = ["adb", "-s", serial, *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"adb failed: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def connect(ip):
    serial = ip if ":" in ip else f"{ip}:5555"
    out = subprocess.run(["adb", "connect", serial], capture_output=True, text=True).stdout
    print(out.strip())
    state = subprocess.run(["adb", "-s", serial, "get-state"], capture_output=True, text=True)
    if state.stdout.strip() != "device":
        sys.exit("Not connected. Approve the 'Allow USB debugging' prompt on the TV and run again.")
    return serial


def packages(serial, flag=""):
    out = adb(serial, "shell", "pm", "list", "packages", *([flag] if flag else []))
    return sorted(l.split(":", 1)[1] for l in out.splitlines() if l.startswith("package:"))


def is_protected(pkg):
    return any(pkg == p or pkg.startswith(p) for p in PROTECTED_PREFIXES)


def pick_provider(serial):
    for pkg in packages(serial):
        if PREFERRED_PROVIDER_KEYWORD in pkg.lower():
            ans = input(f"Found Cellcom TV app ({pkg}). Keep it? [Y/n]: ").strip().lower()
            if ans in ("", "y", "yes"):
                return pkg
    candidates = [p for p in packages(serial, "-3")
                  if any(k in p.lower() for k in PROVIDER_KEYWORDS)]
    if not candidates:
        print("No provider app detected automatically. Third-party apps on the TV:")
        for p in packages(serial, "-3"):
            print("   ", p)
        name = input("Type the exact package name of your provider app (or Enter to skip): ").strip()
        return name or None
    print("Possible TV-provider apps found:")
    for i, p in enumerate(candidates, 1):
        print(f"  {i}. {p}")
    choice = input("Number of the provider app to KEEP (Enter = 1): ").strip() or "1"
    return candidates[int(choice) - 1]


def tweak_animations(serial, apply):
    for key in ("window_animation_scale", "transition_animation_scale", "animator_duration_scale"):
        print(f"  settings put global {key} 0.5")
        if apply:
            adb(serial, "shell", "settings", "put", "global", key, "0.5")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ip", required=True, help="TV IP address (Settings > Network > status)")
    ap.add_argument("--apply", action="store_true", help="actually disable apps (default: dry run)")
    ap.add_argument("--restore", action="store_true", help="re-enable everything this script disabled")
    args = ap.parse_args()

    serial = connect(args.ip)
    model = adb(serial, "shell", "getprop", "ro.product.model")
    sdk = adb(serial, "shell", "getprop", "ro.build.version.release")
    print(f"TV: {model}  Android {sdk}")

    if args.restore:
        if not os.path.exists(STATE_FILE):
            sys.exit("No disabled_packages.txt found - nothing to restore.")
        for pkg in open(STATE_FILE).read().split():
            print("enable", pkg, "->", adb(serial, "shell", "pm", "enable", pkg, check=False))
        for key in ("window_animation_scale", "transition_animation_scale", "animator_duration_scale"):
            adb(serial, "shell", "settings", "put", "global", key, "1.0")
        print("Restored. Reboot the TV.")
        return

    keep = {YOUTUBE}
    provider = pick_provider(serial)
    if provider:
        keep.add(provider)
    print("KEEP:", ", ".join(sorted(keep)))

    installed = set(packages(serial))
    third_party = set(packages(serial, "-3"))
    targets = sorted(
        p for p in (third_party | (set(KNOWN_BLOAT) & installed))
        if p not in keep and not is_protected(p)
    )

    if YOUTUBE not in installed:
        print("WARNING: YouTube for TV is not installed - install it from Play Store.")

    print("\nApps to DISABLE:" if targets else "\nNothing to disable.")
    for p in targets:
        print("   ", p)
    print("\nAnimation speed-up:")
    tweak_animations(serial, args.apply)

    if not args.apply:
        print("\nDRY RUN - nothing changed. Review the list, then run again with --apply.")
        return

    done = []
    for p in targets:
        res = adb(serial, "shell", "pm", "disable-user", "--user", "0", p, check=False)
        print(p, "->", res)
        if "disabled" in res.lower():
            done.append(p)
    prev = open(STATE_FILE).read().split() if os.path.exists(STATE_FILE) else []
    with open(STATE_FILE, "w") as f:
        f.write("\n".join(sorted(set(prev) | set(done))) + "\n")
    print(f"\nDisabled {len(done)} apps (saved to {STATE_FILE}). Rebooting TV...")
    adb(serial, "reboot", check=False)


if __name__ == "__main__":
    main()
