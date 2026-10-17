# How to run VedaMind (Windows)

## Every day: double-click

Open the project folder in File Explorer:

| To | Double-click |
|---|---|
| **Start** | `START-VedaMind.bat` |
| **Stop** | `STOP-VedaMind.bat` |

**START** opens three small server windows (backend, RAG, frontend) and the website in your browser.
Leave those three windows open while you use the app. Close them, or double-click **STOP**, when you're done.

| What | Address | Login |
|---|---|---|
| Website | <http://localhost:5173> | `demo@vedamind.local` / `VedaMind@Demo123` (or register a new account) |
| Admin panel | <http://localhost:5173/admin> | `admin@vedamind.local` / `VedaMind@Admin123` |

The logins come from `.env` (`DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD` and `DEMO_EMAIL` / `DEMO_PASSWORD`); change them there.

## First time on a new laptop

1. **Install** (free, one time):
   - Python 3.12, 3.13 or 3.14 from <https://www.python.org/downloads/>. Tick **"Add python.exe to PATH"** in the installer.
   - Node.js 20 or newer (LTS) from <https://nodejs.org/>.
2. **Get a free Gemini API key**: <https://aistudio.google.com/apikey>. A free Groq key is optional but recommended
   (it is used when Gemini is busy): <https://console.groq.com/keys>.
3. **Double-click `START-VedaMind.bat`.** The first run installs everything (Python packages, npm packages, a local
   PostgreSQL database and Redis), which takes a few minutes. It then opens `.env` in Notepad: paste your key after
   `GEMINI_API_KEY=` (and `GROQ_API_KEY=` if you have one), save, and close Notepad. The app then starts.
4. **Build the knowledge base, once** (about 5 minutes). In PowerShell, in the project folder:
   ```
   powershell -ExecutionPolicy Bypass -File scripts\windows\ingest.ps1
   ```

From then on, just double-click **START**.

## If something goes wrong

| Problem | Fix |
|---|---|
| Chat says the knowledge base "has not yet been populated" | Run the `ingest.ps1` command from step 4 |
| `Port 8000 is already in use` | Another project is using it. Close it, or start with other ports: `powershell -ExecutionPolicy Bypass -File scripts\windows\start.ps1 -BackendPort 8010 -RagPort 8011` |
| `Python 3.12, 3.13 or 3.14 is required` | Install Python (tick "Add to PATH"), then open a new window and try again |
| Location is blocked on the Dinacharya page | Type your city in the box shown there, or use **Change city** |
| Anything else | See the full guide in [README.md](README.md) (Troubleshooting section) |

Do not share or upload `.env`: it contains your API keys.
