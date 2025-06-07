# app.py

import os, json
from fastapi import FastAPI, Request

from drive_service import summarize_changes
from gmail_service import send_email

# Load team email addresses from environment (comma-separated)
NOTIFY_EMAILS = os.getenv("NOTIFY_EMAILS", "").split(",")

app = FastAPI()


@app.post("/webhook")
async def drive_change_webhook(req: Request):
    payload = await req.json()

    # Only handle Google Drive change events
    if payload.get("type") != "googledrive_google_drive_changes":
        return {"status": "ignored"}

    # Summarize the list of changed files
    summary = summarize_changes(payload["data"])
    print(f"Change summary: {summary}")
    if summary:
        # Compose subject and body for the notification email
        subject = "📂 Google Drive Folder Updated"
        body = f"The following file changes were detected:\n\n{summary}"

        # Send email to all team members
        await send_email(NOTIFY_EMAILS, subject, body)
        return {"status": "emailed"}

    return {"status": "no_changes"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
