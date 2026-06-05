# UHMS Super Admin Dashboard

Python + Flask + Plotly demo dashboard for a Unified Hospital Management System managing Hospital A, Hospital B, and Hospital C.

## MVP Backend Added

This repository now also includes an MVP-ready FastAPI/PostgreSQL scaffold for the real Healthcare Management Platform:

- [backend README](backend/README.md)
- [MVP architecture](docs/MVP_ARCHITECTURE.md)
- [roadmap, team, CI/CD, and cost](docs/ROADMAP_TEAM_COST.md)
- [Docker Compose deployment](docker-compose.yml)

The existing Flask dashboard remains available for client demos. The new `backend/` folder is the implementation foundation for the FastAPI MVP.

## Features

- Executive dashboard with KPI cards, revenue charts, department split, revenue vs expenses trend, doctor-to-patient gauge, alerts, staff, inventory, ambulance and admissions widgets.
- Architecture view for the client pitch, covering roles, high-level system flow, core platform layers, mobile app and recommended technology stack.
- Clickable sidebar modules for Patients, Doctors, Radiology, Pathology, Pharmacy, Billing, Insurance, Inventory, Staff Management, Analytics, Reports and Settings.
- Dummy static data only. No database required.
- Responsive enterprise healthcare SaaS UI.

## Local Setup

```bash
"C:\Users\arindam.d\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt
launch_uhms_dashboard.bat
```

Open:

```text
http://127.0.0.1:8001
```

The launch scripts prefer Python 3.12 when installed, then fall back to the
installed Python 3.14 runtime. If PyCharm shows `No module named encodings`, it
is usually running a broken virtual environment whose base Python was removed.
Do not run this app with
`C:\Users\arindam.d\PycharmProjects\app.py\.venv1\Scripts\python.exe`; that
venv points to a missing Python 3.13 install. Use `launch_uhms_dashboard.bat` or
set the PyCharm interpreter to
`C:\Users\arindam.d\AppData\Local\Programs\Python\Python314\python.exe`.

For longer local demos, use:

```bat
keep_uhms_running.bat
```

Keep that command window open. It will restart the local Flask server if it
stops. For a URL that works even after your laptop sleeps or the terminal is
closed, deploy using the Render hosting steps below.

## Share A Public Demo URL

### Option 1: Netlify Static Hosting

Use this when you want a public URL that your BA/client can open from any
system without running Python.

Fastest drag-and-drop method:

1. Open Netlify.
2. Go to **Sites**.
3. Drag the `netlify` folder from this project into Netlify.
4. Netlify will publish the static demo and give you a public URL.

GitHub method:

1. Push this project to GitHub.
2. Create a new Netlify site from the repository.
3. Use these settings:
   - Base directory: leave empty
   - Build command: leave empty
   - Publish directory: `netlify`
4. Deploy and share the generated Netlify URL.

The Netlify demo uses:

- `netlify/index.html`
- `netlify/_redirects`
- `netlify.toml`

### Option 2: Render Hosting For Flask

1. Push this folder to a GitHub repository.
2. Go to Render and create a new Web Service from that repository.
3. Render will detect `render.yaml`, or use these settings manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. After deploy, Render gives a public URL you can share with your BA/client.

### Option 3: Temporary Local Tunnel

Use a tunnel when you want to share your local running app quickly:

```bash
launch_uhms_dashboard.bat
ngrok http 8001
```

Then share the HTTPS forwarding URL shown by ngrok.
