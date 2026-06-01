"""
Build script — creates the Call Queue Automator EXE.
Run:  python build_exe.py
"""
import subprocess
import sys
import os


def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


# Ensure dependencies
DEPS = [
    "ttkbootstrap",
    "pyautogui",
    "pynput",
    "pandas",
    "openpyxl",
    "pyinstaller",
]

print("📦 Installing dependencies...")
for dep in DEPS:
    install(dep)

print("\n🔨 Building EXE with PyInstaller...")

cmd = [
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--name", "CallQueueAutomator",
    "--add-data", "dialer_config.json;." if os.name == "nt" else "dialer_config.json:.",
    "autodialer_gui.py",
]

# Create default config if missing
if not os.path.exists("dialer_config.json"):
    import json
    cfg = {
        "number_field": [1514, 315],
        "call_button": [1848, 309],
        "end_call_button": [1693, 934],
        "excel_path": "",
        "initial_delay": 5
    }
    with open("dialer_config.json", "w") as f:
        json.dump(cfg, f, indent=2)
    print("✅ Created default dialer_config.json")

result = subprocess.run(cmd, capture_output=False)

if result.returncode == 0:
    print("\n✅ BUILD SUCCESSFUL!")
    print("📁 EXE is in:  dist/CallQueueAutomator.exe")
else:
    print("\n❌ Build failed — check output above.")
