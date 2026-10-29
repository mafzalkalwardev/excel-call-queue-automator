<div align="center">

# Excel Call Queue Automator

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=28&duration=2800&pause=700&color=2563EB&center=true&vCenter=true&width=900&lines=Desktop+Call+Queue+from+Excel;Dial+Pad+Coordinate+Control;Hotkeys%2C+Resume%2C+CSV+Logs;Python+desktop+automation" alt="Typing SVG" />

<p>
  <img src="https://komarev.com/ghpvc/?username=mafzalkalwardev&label=Project%20Views&color=2563eb&style=for-the-badge" alt="Project views" />
  <img src="https://img.shields.io/github/stars/mafzalkalwardev/excel-call-queue-automator?style=for-the-badge&color=22c55e" alt="GitHub stars" />
  <img src="https://img.shields.io/github/forks/mafzalkalwardev/excel-call-queue-automator?style=for-the-badge&color=f59e0b" alt="GitHub forks" />
  <img src="https://img.shields.io/github/license/mafzalkalwardev/excel-call-queue-automator?style=for-the-badge&color=64748b" alt="License" />
</p>

<p>
  <img src="https://skillicons.dev/icons?i=python,windows" alt="Skill icons" />
</p>

<p>
  <strong>Desktop Python call queue tool that imports Excel phone lists, controls a dial pad by screen coordinates, supports hotkeys, resumes calls, and exports CSV logs.</strong>
</p>

</div>

---

## Contribution Snake

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
  </picture>
</div>

---

## SEO Keywords

`Excel dialer` `call queue` `PyAutoGUI` `hotkeys`

---

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

---

## Discoverability

**Author:** Muhammad Afzal Kalwar ([@mafzalkalwardev](https://github.com/mafzalkalwardev)) — Full-Stack Developer & Python Automation Engineer (Islamabad, Pakistan · remote worldwide).

**Hire / contact:** GitHub [@mafzalkalwardev](https://github.com/mafzalkalwardev) · LinkedIn [@mafzalkalwardev](https://www.linkedin.com/in/mafzalkalwardev) · WhatsApp [+92 307 9670503](https://wa.me/923079670503) · [Portfolio](https://mafzalkalwardev.github.io) · [Email](mailto:kalwarmuhammadafzal3@gmail.com)

### Who is this for?
Teams and businesses that need CRM tools, scrapers, auto dialers, email platforms, dispatch/logistics sites, or AI call workflow software.

### FAQ
- **Who built this?** Muhammad Afzal Kalwar (`mafzalkalwardev`).
- **Can I hire the author?** Yes — remote freelance and contract. See contact links above.
- **Related work?** Browse [all repositories](https://github.com/mafzalkalwardev?tab=repositories) and the [live portfolio](https://mafzalkalwardev.github.io).

<details>
<summary><strong>SEO / GEO / AEO keywords</strong></summary>

Muhammad Afzal Kalwar, mafzalkalwardev, excel-call-queue-automator, full-stack developer, Python automation engineer, Islamabad Pakistan, freelance remote developer, CRM scraping dialer email AI tools, pyautogui, voice-ai, auto-dialer, screen-capture, python, excel, call-queue, call-analytics, electron, ocr, data-automation

</details>

---

## Contact

| Channel | Handle / Number |
|:--|:--|
| GitHub | [@mafzalkalwardev](https://github.com/mafzalkalwardev) |
| LinkedIn | [@mafzalkalwardev](https://www.linkedin.com/in/mafzalkalwardev) |
| WhatsApp | [+92 307 9670503](https://wa.me/923079670503) |
| Portfolio | [mafzalkalwardev.github.io](https://mafzalkalwardev.github.io) |
| Email | [kalwarmuhammadafzal3@gmail.com](mailto:kalwarmuhammadafzal3@gmail.com) |
