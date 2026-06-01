# Call Queue Automator

> A desktop Python tool for loading phone numbers from Excel, driving a browser-based dial pad with saved screen coordinates, and tracking call progress in a local CSV log.

Call Queue Automator is built for small internal workflows where a user already has a web calling page open and wants a repeatable queue runner. It reads an Excel phone list, normalizes valid 10-digit US numbers, skips completed numbers from previous sessions, clicks configured screen positions, and gives the operator simple hotkeys for moving through the list.

This project does not depend on a specific calling provider. It works by using screen coordinates, so it can be adapted to any browser page or desktop dialer that has a number input, a call button, and an end-call button.

## Project Trophies

:trophy: Excel import with flexible phone-column detection  
:trophy: Coordinate picker for browser or desktop dial pads  
:trophy: Resume support through local call logs  
:trophy: Operator hotkeys for next call and stop  
:trophy: CSV history export for follow-up reporting  
:trophy: One-file Windows executable build path  
:trophy: No web-loaded README assets, so GitHub renders cleanly

## Features

- Load `.xlsx` or `.xls` phone lists with columns such as `Phone`, `Phone Number`, `Mobile`, or `Number`.
- Strip non-digit characters from phone values before dialing.
- Keep only valid 10-digit US numbers.
- Skip numbers already marked `ENDED` in `call_logs.csv`.
- Save and reuse screen coordinates for:
  - number input field
  - call button
  - end-call button
- Start with a configurable delay so the operator can switch to the calling window.
- Use `X` to end the current call and move to the next number.
- Use `Esc` to stop the dialer.
- Track total, completed, and remaining calls.
- View call history inside the app.
- Export logs to CSV.
- Build a Windows `.exe` with PyInstaller.

## Repository Name

Recommended GitHub repository name:

```text
excel-call-queue-automator
```

Recommended GitHub repository description:

```text
Desktop Python call-queue tool that imports Excel phone lists, controls a dial pad by screen coordinates, supports hotkeys, resumes completed calls, and exports CSV call logs.
```

## Tech Stack

- Python 3.8+
- Tkinter
- ttkbootstrap
- pandas
- openpyxl
- pyautogui
- pynput
- PyInstaller for Windows builds

## File Overview

| File | Purpose |
| --- | --- |
| `autodialer_gui.py` | Main desktop GUI and dialing workflow |
| `build_exe.py` | Installs build dependencies and creates a Windows executable |
| `dialer_config.json` | Default coordinate and startup-delay configuration |
| `requirements.txt` | Runtime Python dependencies |
| `.gitignore` | Keeps local logs, build output, virtual environments, and private spreadsheets out of Git |

## Requirements

- Python 3.8 or newer
- Windows is recommended for the packaged `.exe` workflow
- A browser-based or desktop calling interface open on your machine
- Permission to contact every number in your uploaded call list

## Install

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python autodialer_gui.py
```

## Excel Input Format

The spreadsheet must include one supported phone column:

- `Phone`
- `phone`
- `PHONE`
- `Phone Number`
- `Mobile`
- `Number`

Example:

| Phone |
| --- |
| 3055551234 |
| 786-555-9876 |
| (954) 555-0101 |

The app removes formatting characters and keeps valid 10-digit US numbers.

## Coordinate Setup

1. Open your calling page or dialer.
2. Open the app and go to the `Coordinates` tab.
3. For each target, click `Pick`.
4. When the app minimizes, click the matching element on your screen.
5. Save coordinates.

The required targets are:

- Number input field
- Call button
- End-call button

You can use the test buttons to move the mouse to each saved position without clicking.

## Calling Workflow

1. Open the `Dialer` tab.
2. Browse for your Excel file.
3. Click `Load Numbers`.
4. Confirm the total, completed, and remaining counts.
5. Click `Start Dialer`.
6. Switch to the calling page before the countdown finishes.

Controls while dialing:

| Control | Action |
| --- | --- |
| `X` | Hang up the current call, log it as ended, and dial the next number |
| `Esc` | Stop the dialer |
| `Next Call (X)` | Same as pressing `X` |
| `Stop` | Stop the dialer |

## Logs and Resume Behavior

Calls are written to `call_logs.csv`.

Statuses:

- `STARTED` when a call begins
- `ENDED` when the operator moves to the next call

When the app loads a spreadsheet, it checks `call_logs.csv` and skips numbers already marked `ENDED`. This lets the user resume a partially completed list without starting over.

## Build a Windows Executable

Install PyInstaller and build:

```powershell
pip install pyinstaller
python build_exe.py
```

The executable will be created in:

```text
dist/CallQueueAutomator.exe
```

Generated `build/` and `dist/` folders are ignored by Git.

## Safety Notes

- Keep `pyautogui.FAILSAFE` enabled. Moving the mouse to a screen corner can interrupt runaway automation.
- Test coordinates before starting a real call queue.
- Keep the calling window visible and positioned the same way it was during coordinate capture.
- Do not upload private spreadsheets, exported logs, or customer phone data to GitHub.
- Use this tool only for lawful, permission-based calling workflows.

## GitHub Upload Commands

Run these from the project folder:

```powershell
git init
git add .
git commit -m "Prepare call queue automator for GitHub"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/excel-call-queue-automator.git
git push -u origin main
```

If the GitHub repository already exists and the remote is already added, use:

```powershell
git remote -v
git push -u origin main
```

## Recommended GitHub Topics

```text
python
tkinter
desktop-app
excel
automation
call-queue
pyautogui
pandas
csv
pyinstaller
```

## License

No license file is included yet. Add a license before accepting outside contributions or allowing reuse.
