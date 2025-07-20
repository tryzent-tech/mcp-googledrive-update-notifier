# mcp-googledrive-update-notifier

GoogleDrive-UpdateNotifier turns Google Drive into an automated “change bulletin” service: every time **any** file on your Drive is added, removed, or edited, a FastAPI webhook receives the event from Composio, summarises the change, and dispatches a plain-text e-mail through Gmail. The stack uses Composio MCP triggers + LangChain function-calling + FastAPI; it needs no polling and deploys in under 15 minutes. ([developers.google.com][1])

---

## Table of contents

1. Project architecture
2. Google Cloud (2025 UI) – OAuth client & consent screen
3. Composio – Drive & Gmail integrations
4. Local setup & environment variables
5. Bootstrapping the Drive trigger
6. Running the FastAPI server
7. Troubleshooting
8. License

---

## 1  Architecture overview

```
Google Drive   ──►  Composio Trigger (GOOGLEDRIVE_GOOGLE_DRIVE_CHANGES)
                              │  HTTPS JSON payload
                              ▼
                    FastAPI /webhook   ──►  summarize_changes()
                                                │
                                                ▼
                              LangChain GSMail agent (GMAIL_SEND_EMAIL)
                                                      │
                         Gmail API  ──►  team inboxes
```

* **Global change trigger** = one push channel covers every file your account can see ﻿– no folder IDs. ([developers.google.com][2])
* **`drive.metadata.readonly` scope** is sufficient; it’s *Sensitive* (not *Restricted*) so no security assessment is required. ([developers.google.com][3])
* The Gmail agent uses a single Composio action (`GMAIL_SEND_EMAIL`) invoked through LangChain’s OpenAI-functions wrapper. ([support.google.com][4])

---

## 2  Google Cloud setup (2025 interface)

Google moved OAuth settings to **Google Auth Platform** in 2025. Follow the left-nav as written; menu names are verbatim from the June-2025 release. ([developers.google.com][5])

### 2.1 Create/choose a project

`console.cloud.google.com` → project picker → **NEW PROJECT**.

### 2.2 Enable Drive API

`Google Auth Platform → Enable API → APIs` → search **Google Drive API** → **Enable**. ([developers.google.com][1])

### 2.3 OAuth consent screen

| Tab (left nav)                     | Action                                                                                                                            |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Overview → Configure**           | User type = External, App name & logo (optional).                                                                                 |
| **Data Access → Scopes**           | **Add scope** → tick `https://www.googleapis.com/auth/drive.metadata.readonly` → **Add** → **Save**. ([developers.google.com][6]) |
| **Data Access → Sensitive scopes** | Scope now appears under *Sensitive* → click **Confirm**.                                                                          |
| **Data Access → Test users**       | **Add** the Gmail address you will connect in Composio; click **Save**.                                                           |

Status at top now reads **TESTING** (100-user cap, no Google verification needed). ([developers.google.com][6])

### 2.4 Create OAuth client (Web application)

1. **Google Auth Platform → Clients** → **Create client**.
2. *Application type* = **Web application** → **Next**.
3. **Authorized redirect URI** → paste

```
https://backend.composio.dev/api/v1/auth-apps/add
```

(the value Composio shows in its integration wizard) ([developers.google.com][7])
4\. **Create** → copy *Client ID* & *Client secret* (you only see the secret once). ([support.google.com][4])

---

## 3  Composio configuration

### 3.1 Google Drive integration

1. **Integrations → New → Google Drive**.
2. Add scopes: keep `drive.file`, add `https://www.googleapis.com/auth/drive.metadata.readonly`.
3. Toggle **Use your own developer app** → paste the Client ID & Secret from §2.4.
4. **Create integration** → OAuth window appears (shows your app name + scope) → **Continue**.

### 3.2 Gmail integration

1. **Integrations → New → Gmail**.
2. Scope requested = `https://www.googleapis.com/auth/gmail.send` only.
3. Finish consent; row turns **ACTIVE**.

### 3.3 Webhook URL

Project → **Webhooks** → **Add** →

```
https://<your-ngrok-id>.ngrok-free.app/webhook
```

Save.

---

## 4  Local setup

```bash
git clone https://github.com/your-org/drivewatcher-mailalert.git
cd drivewatcher-mailalert
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
COMPOSIO_API_KEY=sk_live_**********************************
NOTIFY_EMAILS=you@example.com,team@example.com
```

---

## 5  Bootstrap Drive trigger

```bash
python mcp_client.py          # prints “Trigger status: success”
```

The trigger ID now shows **ACTIVE** in Composio and begins logging events. ([developers.google.com][8])

---

## 6  Run the webhook & tunnel

```bash
uvicorn app:app --reload
ngrok http 8000
```

Upload a test file to Drive → Uvicorn logs:

```
Change summary: - demo.txt (file)
GMAIL_SEND_EMAIL result: {'status': 'success'}
```

Email lands in the inboxes listed in `NOTIFY_EMAILS`.

---

## 7  Troubleshooting

| Issue                         | Symptom                                       | Fix                                                       |
| ----------------------------- | --------------------------------------------- | --------------------------------------------------------- |
| Wrong payload filter          | Uvicorn shows “status: ignored”               | Ensure `type=="googledrive_google_drive_changes"`         |
| No Gmail send                 | LangChain returns error “account\_not\_found” | Connect Gmail integration or reconfirm `COMPOSIO_API_KEY` |
| Composio log “No subscribers” | ngrok closed / webhook URL blank              | Restart ngrok, update URL in Project → Webhooks           |
| 401 in log                    | Drive token lost scope                        | Reconnect Drive & re-enable trigger                       |

---
