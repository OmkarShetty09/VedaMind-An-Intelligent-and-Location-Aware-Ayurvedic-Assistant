# VedaMind — Setup Guide (Windows)

Everything you need to do to get VedaMind running on a Windows 10/11 laptop, from a fresh machine to a working app.
No Docker and no administrator rights are needed.

**Time:** about 20–30 minutes the first time (mostly downloads). After that, starting the app takes about 20 seconds.

---

## Contents

1. [Install the required software](#1-install-the-required-software)
2. [Get the project](#2-get-the-project)
3. [Get your free API keys](#3-get-your-free-api-keys)
4. [First start](#4-first-start)
5. [Build the knowledge base (one time)](#5-build-the-knowledge-base-one-time)
6. [Use the app](#6-use-the-app)
7. [Starting and stopping every day](#7-starting-and-stopping-every-day)
8. [Updating to a newer version](#8-updating-to-a-newer-version)
9. [Troubleshooting](#9-troubleshooting)
10. [Good to know](#10-good-to-know)

---

## 1. Install the required software

Install these three programs (all free). If you already have them, check the versions.

| Software | Version | Download | Important |
|---|---|---|---|
| **Python** | 3.12, 3.13 or 3.14 | <https://www.python.org/downloads/> | On the first installer screen, **tick "Add python.exe to PATH"** before clicking *Install Now*. |
| **Node.js** | 20 or newer (choose **LTS**) | <https://nodejs.org/> | Keep the default options. |
| **Git** | any | <https://git-scm.com/download/win> | Keep the default options. (Not needed if you download the project as a ZIP.) |

**Check the installs:** open a **new** PowerShell window (Start menu → type `PowerShell` → Enter) and run:

```powershell
python --version
node --version
git --version
```

You should see something like `Python 3.12.x`, `v20.x` (or higher) and `git version 2.x`. If a command is
"not recognized", re-run that installer (for Python, make sure *Add python.exe to PATH* is ticked), then open a
**new** PowerShell window.

---

## 2. Get the project

**Option A — with Git (recommended, makes updating easy):** in PowerShell:

```powershell
cd $HOME\Documents
git clone https://github.com/OmkarShetty09/VedaMind-An-Intelligent-and-Location-Aware-Ayurvedic-Assistant.git VedaMind
```

The project is now in `Documents\VedaMind`.

**Option B — ZIP:** on the GitHub page click **Code → Download ZIP**, then right-click the ZIP → **Extract All…** and
extract it to `Documents\VedaMind`.

> Put the folder somewhere simple like `Documents\VedaMind`. Avoid folders synced by OneDrive and paths with
> unusual characters.

---

## 3. Get your free API keys

VedaMind uses Google Gemini to answer questions and to build its knowledge base.

**Gemini key (required):**
1. Go to <https://aistudio.google.com/apikey> and sign in with a Google account.
2. Click **Create API key** and copy the key.

**Groq key (optional, recommended):** used automatically when Gemini is busy, so chat keeps working.
1. Go to <https://console.groq.com/keys> and sign in.
2. Click **Create API Key** and copy the key.

Keep the keys private; you will paste them into a settings file in the next step.

---

## 4. First start

1. Open the `VedaMind` folder in File Explorer.
2. Double-click **`START-VedaMind.bat`**.
   - If Windows shows *"Windows protected your PC"*, click **More info → Run anyway** (this appears for files
     downloaded from the internet).
3. The first run **installs everything automatically**: Python packages, website packages, a local PostgreSQL
   database (with pgvector) and Redis. This takes several minutes; let it finish.
4. **Notepad opens a file called `.env`.** Find these lines and paste your keys after the `=` sign
   (no spaces, no quotes):

   ```
   GEMINI_API_KEY=paste-your-gemini-key-here
   GROQ_API_KEY=paste-your-groq-key-here
   ```

   Leave everything else as it is. **Save** (Ctrl+S) and **close Notepad**.
5. The app now starts. Three small windows open (**VedaMind backend**, **VedaMind rag**, **VedaMind frontend**) and
   your browser opens <http://localhost:5173>.
   - If Windows Firewall asks about Python, Node or PostgreSQL, click **Allow** (everything only runs on your own
     computer).
   - **Keep the three VedaMind windows open** while you use the app.

The black START window says *"Knowledge base is empty"* the first time — that is the next step.

---

## 5. Build the knowledge base (one time)

The chat answers from classical Ayurvedic texts that must be loaded into the database once.
Do this **while the app is running** (after step 4).

1. In File Explorer, open the `VedaMind` folder, click the address bar, type `powershell` and press **Enter**.
   A PowerShell window opens in the project folder.
2. Run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1
   ```

3. Wait about **5 minutes**. Messages like *"Gemini rate limited, waiting 10s"* are normal (free tier); it retries
   automatically. It finishes with a report ending in **Total chunks: 375**.

You never need to do this again on this laptop (the data is kept in the `.localdev` folder).

---

## 6. Use the app

Open <http://localhost:5173>.

| Account | Email | Password |
|---|---|---|
| Ready-made demo user | `demo@vedamind.local` | `VedaMind@Demo123` |
| Admin panel (<http://localhost:5173/admin>) | `admin@vedamind.local` | `VedaMind@Admin123` |

Or click **Create a free account** to register your own user. (These logins are set in `.env` — the
`DEMO_USER_EMAIL`, `DEMO_USER_PASSWORD`, `DEMO_EMAIL` and `DEMO_PASSWORD` lines — and you can change them there.)

**A quick tour of every feature:**
1. **Register / sign in** → accept the disclaimer → take the **11-question dosha quiz** → see your result → **Start chatting**.
2. Ask *"How should a vata person structure their morning in this season?"* — a streamed answer personalised to your
   dosha and the current season, with clickable `[S1]` source tags and a *Sources* list.
3. Ask *"Can I take turmeric with warfarin?"* — a red **safety warning** with the interaction and advice.
4. Click **New chat** and ask *"Suggest a herb for better sleep"* — it first asks about medication; click
   **No medication — please answer**.
5. Open **Profile & Health**, add `warfarin 5 mg` under medications, **Save**. In a new chat ask
   *"Is turmeric good for joint pain?"* — blocked, because your saved medication is checked.
6. Open **Dinacharya** → **Generate routine** — a daily routine from your local sunrise/sunset, season and weather.
   Allow location when the browser asks, or use **Change city** to type your city.
7. **History** (top of the chat) reopens earlier conversations.

**Admin panel** (<http://localhost:5173/admin>): edit the quiz questions, routine activities, chat suggestions,
herb/drug names and safety rules without touching code.

---

## 7. Starting and stopping every day

| To | Do this |
|---|---|
| **Start** | Double-click **`START-VedaMind.bat`** (opens the app in your browser) |
| **Stop** | Double-click **`STOP-VedaMind.bat`** (closes the three windows, the database and Redis) |

Closing the three VedaMind windows also stops the website, but the database keeps running in the background until
you use **STOP** (or restart the laptop).

---

## 8. Updating to a newer version

If the project was cloned with Git (step 2, option A):

1. Double-click **`STOP-VedaMind.bat`**.
2. In PowerShell in the project folder:

   ```powershell
   git pull
   powershell -ExecutionPolicy Bypass -File scripts\windows\setup.ps1
   ```

   (`setup.ps1` installs any new packages; your `.env`, accounts and knowledge base are kept.)
3. Double-click **`START-VedaMind.bat`**.

---

## 9. Troubleshooting

| Problem | What to do |
|---|---|
| `Python 3.12, 3.13 or 3.14 is required` | Install Python (step 1) with **Add python.exe to PATH** ticked, then open a **new** window and try again. |
| `Node.js 20 or newer is required` | Install the Node.js **LTS** version (step 1), then try again. |
| `... cannot be loaded because running scripts is disabled` | Use the exact commands shown here (they include `-ExecutionPolicy Bypass`), or use the `.bat` files. |
| `Port 8000 is already in use` (or 8001 / 5173) | Another program uses that port. Close other projects, or start on other ports: `powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1 -BackendPort 8010 -RagPort 8011` (then stop with the same options on `stop.ps1`). |
| `Port 5432 is used by another program` | You have PostgreSQL installed and running. Stop its Windows service (Services app → *postgresql* → Stop), or use it instead: see *"Manual setup (macOS / Linux / your own PostgreSQL)"* in [README.md](README.md) and start with `start.ps1 -SkipInfra`. |
| `Port 6379 is used by another program` | Another Redis/Memurai is running. Stop it, or keep using it with `start.ps1 -SkipInfra` (see README). |
| Chat says the knowledge base *"has not yet been populated"* | Do step 5. |
| `ingest.ps1` says `GEMINI_API_KEY not configured` or `http 400` | The key in `.env` is missing or wrong. Open `.env` in Notepad, fix the `GEMINI_API_KEY=` line (no spaces or quotes), save, and run step 5 again. |
| Chat answers fail / *"Could not reach the answer engine"* | The **VedaMind rag** window was closed or shows an error. Double-click STOP, then START. |
| Answers are slow or show *"high demand"* errors | Gemini's free tier is busy. Add a Groq key (step 3) — VedaMind then switches automatically. |
| Dinacharya says *"Location is blocked"* | Type your city in the box shown there, or allow location for `localhost` in the browser (icon left of the address bar → Location → Allow) and click **Retry**. |
| The website is blank or shows an old version | Press **Ctrl+F5** in the browser. |
| Something else | Read the error in the three VedaMind windows, then see the Troubleshooting section of [README.md](README.md). |

**Start completely fresh** (deletes accounts, chats and the knowledge base on this laptop): double-click
`STOP-VedaMind.bat`, delete the `.localdev` folder, double-click `START-VedaMind.bat`, then do step 5 again.

---

## 10. Good to know

- **Internet is required** while using the app (Gemini/Groq answers, weather, city search).
- **`.env` contains your API keys — never share or upload it.** It is excluded from Git automatically. If you send
  the project to someone, send it via GitHub or a ZIP **without** `.env`, `.localdev`, `backend\.venv`, `rag\.venv`
  and `frontend\node_modules` (they are machine-specific and are re-created by `START-VedaMind.bat`).
- Everything runs only on your computer: website <http://localhost:5173>, backend on port 8000, AI service on
  port 8001, database on 5432, Redis on 6379.
- The free Gemini tier is enough for development and demos.
- VedaMind gives general wellness education. It is not medical advice and does not replace a doctor.
- More details (configuration, architecture, tests, Docker, macOS/Linux): [README.md](README.md).
