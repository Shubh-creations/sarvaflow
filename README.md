# FinanceOS MVP

Local-first cash forecasting workspace for finance teams. Import a CSV of bank transactions, review a rolling 13-week cash forecast, drill into source transactions, export the forecast, and generate an executive summary.

## Run locally

1. Start the API:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. Start the web app in a second terminal:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Open the address printed by Vite. The app ships with demo data and accepts CSV columns `date`, `description`, `amount`, and optional `category`.

## Local Webhook Tunnel Setup (Plaid / Bank Telemetry)

To receive real-time bank webhooks locally on `http://127.0.0.1:8000`:

1. Run the HTTPS public tunnel command:
   ```powershell
   npx --yes cloudflared tunnel --url http://127.0.0.1:8000
   ```
2. Copy the generated `https://<random-subdomain>.trycloudflare.com` URL.
3. Register `https://<random-subdomain>.trycloudflare.com/api/v1/plaid/webhook` in the Plaid Developer Dashboard.

> [!WARNING]
> **Local Tunnel Limitation**: Free temporary tunnel URLs change every time local development restarts. You must update the Plaid webhook endpoint URL in the Plaid dashboard when restarting a local tunnel session.
> Production deployments (e.g. Render / Cloud Run) use a static domain (e.g. `https://api.sarvaflow.com/api/v1/plaid/webhook`) and do NOT suffer from this limitation.

## Optional AI summary

Set `OPENAI_API_KEY` in `backend/.env` to enable a live OpenAI executive summary. Without it, the API returns a deterministic finance-focused summary so the MVP stays usable offline.
