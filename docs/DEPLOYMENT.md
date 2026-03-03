# Deployment Guide — CognizantWeatherApp

This guide covers everything you need to deploy CognizantWeatherApp to **Azure App Service** using the included GitHub Actions workflow, as well as notes for other deployment scenarios.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Production Configuration](#production-configuration)
- [Azure App Service — Step-by-Step](#azure-app-service--step-by-step)
  - [1. Create the Azure resources](#1-create-the-azure-resources)
  - [2. Configure GitHub Secrets](#2-configure-github-secrets)
  - [3. Trigger the deployment](#3-trigger-the-deployment)
  - [4. Verify the deployment](#4-verify-the-deployment)
- [GitHub Actions Workflow Explained](#github-actions-workflow-explained)
- [Environment Variables in Production](#environment-variables-in-production)
- [Gunicorn Configuration](#gunicorn-configuration)
- [Manual Deployment (zip deploy)](#manual-deployment-zip-deploy)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Notes |
|---|---|
| Azure account | [Sign up free](https://azure.microsoft.com/free/) |
| GitHub repository | Fork / clone of `ibnehussain/cognizantweatherapp` |
| OpenWeatherMap API key | [Free tier](https://home.openweathermap.org/api_keys) — 60 calls/min |
| Azure CLI (optional) | Needed for the CLI approach; not required if using Azure Portal |

---

## Local Development

See the [Quick Start](../README.md#quick-start-local) section in the main README.

```bash
cd backend
python app.py          # serves on http://localhost:5000
```

The Flask development server serves both the API and the static frontend. Do **not** use this in production.

---

## Production Configuration

Before deploying, ensure the following environment variables are set (as GitHub Secrets or App Service Application Settings):

| Variable | Production value |
|---|---|
| `OWM_API_KEY` | Your OpenWeatherMap API key |
| `SECRET_KEY` | A long random string (32+ characters recommended) |
| `FLASK_DEBUG` | `false` |
| `CACHE_TTL_SECONDS` | `600` (adjust as needed) |
| `CORS_ORIGINS` | Your production domain(s), e.g. `https://myapp.azurewebsites.net` |

Generate a strong secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Azure App Service — Step-by-Step

### 1. Create the Azure resources

**Option A — Azure Portal**

1. Go to [portal.azure.com](https://portal.azure.com).
2. Click **Create a resource** → search for **Web App**.
3. Fill in:
   - **Subscription:** your subscription
   - **Resource Group:** create new or use existing
   - **Name:** a globally unique name (this becomes `<name>.azurewebsites.net`)
   - **Publish:** Code
   - **Runtime stack:** Python 3.11
   - **Operating System:** Linux
   - **Region:** choose one close to your users
4. Click **Review + create** → **Create**.

**Option B — Azure CLI**

```bash
# Log in
az login

# Create a resource group
az group create --name weatherapp-rg --location eastus

# Create an App Service plan (free tier)
az appservice plan create \
  --name weatherapp-plan \
  --resource-group weatherapp-rg \
  --sku F1 \
  --is-linux

# Create the web app
az webapp create \
  --name <your-unique-app-name> \
  --resource-group weatherapp-rg \
  --plan weatherapp-plan \
  --runtime "PYTHON:3.11"
```

### 2. Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions → New repository secret** and add the following:

| Secret name | Value |
|---|---|
| `AZURE_WEBAPP_NAME` | The App Service name you chose (e.g. `cognizantweatherapp`) |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Contents of the publish profile XML file (see below) |
| `OWM_API_KEY` | Your OpenWeatherMap API key |
| `SECRET_KEY` | A long random string |

**Getting the publish profile:**

1. In Azure Portal, open your App Service.
2. In the top toolbar, click **Get publish profile**.
3. Open the downloaded `.PublishSettings` file in a text editor.
4. Copy the entire XML content and paste it as the value of `AZURE_WEBAPP_PUBLISH_PROFILE`.

### 3. Trigger the deployment

The workflow runs automatically on every push to `main`:

```bash
git push origin main
```

Or trigger it manually from **GitHub → Actions → Deploy to Azure Web App → Run workflow**.

### 4. Verify the deployment

Once the workflow succeeds (green ✓ in GitHub Actions):

```
https://<your-app-name>.azurewebsites.net/api/health
```

Expected response:
```json
{ "status": "ok" }
```

Then open the root URL to see the full weather dashboard:
```
https://<your-app-name>.azurewebsites.net/
```

---

## GitHub Actions Workflow Explained

The workflow file is at `.github/workflows/azure-deploy.yml`.

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:         # manual trigger
```

| Step | What it does |
|---|---|
| **Checkout** | Checks out the repository at the current commit |
| **Set up Python 3.11** | Installs Python and caches pip dependencies |
| **Install dependencies** | Runs `pip install -r backend/requirements.txt` and installs `gunicorn` |
| **Create backend .env** | Writes `OWM_API_KEY`, `SECRET_KEY`, `FLASK_DEBUG=false` from GitHub Secrets into `backend/.env` |
| **Zip artifact** | Creates `release.zip` excluding `.git`, `__pycache__`, `*.pyc`, `venv/`, `.env.example` |
| **Deploy to Azure** | Uses `azure/webapps-deploy@v3` with the publish profile to upload and start the app |

The startup command passed to gunicorn is:

```
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=60 --chdir backend "app:create_app()"
```

Azure routes port 80/443 to the gunicorn port automatically.

---

## Environment Variables in Production

Azure App Service has two ways to pass environment variables:

**Option A (recommended for secrets) — GitHub Secrets + .env file**

The workflow already handles this by writing a `backend/.env` from GitHub Secrets. This is the default approach.

**Option B — Azure App Service Application Settings**

1. In Azure Portal, open your App Service.
2. Go to **Configuration → Application settings**.
3. Add each variable (e.g. `OWM_API_KEY`, `SECRET_KEY`) as a key-value pair.
4. Click **Save** and restart the app.

App Service injects these as environment variables that `python-dotenv` / `os.getenv()` will pick up.

> If using Option B, you can remove the "Create backend .env" step from the workflow.

---

## Gunicorn Configuration

The production startup command uses:

| Flag | Value | Reason |
|---|---|---|
| `--bind` | `0.0.0.0:8000` | Listen on all interfaces on port 8000 |
| `--workers` | `2` | Two worker processes (adjust for your App Service plan) |
| `--timeout` | `60` | Kill workers that take more than 60 s per request |
| `--chdir` | `backend` | Set the working directory so relative imports resolve |
| App module | `app:create_app()` | Flask application factory pattern |

**Scaling workers:** A rule of thumb is `(2 × CPU cores) + 1`. For an F1 / B1 plan (1 vCPU): 3 workers. Update the startup command in the workflow YAML if needed.

---

## Manual Deployment (zip deploy)

If you prefer to deploy without GitHub Actions:

```bash
# 1. Install dependencies into the project (no venv)
pip install -r backend/requirements.txt --target backend/lib

# 2. Zip the project
zip -r release.zip . \
  --exclude "*.git*" \
  --exclude "*__pycache__*" \
  --exclude "*.pyc" \
  --exclude "venv/*"

# 3. Deploy via Azure CLI
az webapp deploy \
  --resource-group weatherapp-rg \
  --name <your-app-name> \
  --src-path release.zip \
  --type zip
```

---

## Troubleshooting

### App returns 500 on startup

Check the App Service logs:

```bash
az webapp log tail --name <your-app-name> --resource-group weatherapp-rg
```

Common causes:
- `OWM_API_KEY` is not set → `RuntimeError: OWM_API_KEY is not set`.
- Wrong startup command — verify the gunicorn command in the workflow or App Service configuration.

### Health check returns 404

The app is not running or the startup command failed. Check logs as above.

### CORS errors in the browser

Set `CORS_ORIGINS` to include your production domain:

```env
CORS_ORIGINS=https://your-app.azurewebsites.net
```

Then redeploy.

### Slow first response after deployment

Azure App Service on the free (F1) tier has cold-start latency. Upgrade to B1 or higher, or enable **Always On** in Configuration → General settings.

### Deployment fails at "Deploy to Azure Web App" step

- Verify that `AZURE_WEBAPP_NAME` exactly matches the App Service name (case-sensitive).
- Re-download and re-paste the publish profile — profiles expire when you reset deployment credentials.
