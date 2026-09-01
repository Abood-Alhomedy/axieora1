import base64
from email.message import EmailMessage
import httpx
from .clean_registry import ToolConfig, CleanToolRegistry

# ─── Gmail Send ───────────────────────────────────────────────────────────────

gmail_send_config = ToolConfig(
    id="gmail_send",
    name="Gmail Send",
    description="Send emails using Gmail",
    parameters={
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body content"}
        },
        "required": ["to", "body"]
    }
)

async def execute_gmail_send(params: dict, context: dict) -> dict:
    access_token = context.get("access_token")
    if not access_token:
        return {"success": False, "error": "No access token. User must connect Gmail."}

    message = EmailMessage()
    message.set_content(params["body"])
    message["To"] = params["to"]
    message["Subject"] = params.get("subject", "")

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"raw": encoded_message}
        )
        if resp.status_code == 200:
            return {"success": True, "output": {"content": "Email sent successfully"}}
        return {"success": False, "error": resp.text}

CleanToolRegistry.register(gmail_send_config, execute_gmail_send)


# ─── Gmail Read ───────────────────────────────────────────────────────────────

gmail_read_config = ToolConfig(
    id="gmail_read",
    name="Gmail Read",
    description="Fetch recent emails from Gmail inbox. Can filter by read/unread status and limit the number of results.",
    parameters={
        "type": "object",
        "properties": {
            "max_results": {
                "type": "integer",
                "description": "Maximum number of emails to return (default: 10, max: 50)"
            },
            "only_unread": {
                "type": "boolean",
                "description": "If true, fetch only unread emails. Default is false (all emails)."
            },
            "query": {
                "type": "string",
                "description": "Optional Gmail search query (e.g. 'from:boss@example.com', 'subject:invoice')"
            }
        },
        "required": []
    }
)

async def execute_gmail_read(params: dict, context: dict) -> dict:
    access_token = context.get("access_token")
    if not access_token:
        return {"success": False, "error": "No access token. User must connect Gmail via OAuth."}

    max_results = min(int(params.get("max_results", 10)), 50)
    only_unread = params.get("only_unread", False)
    extra_query = params.get("query", "")

    # بناء استعلام البحث
    query_parts = []
    if only_unread:
        query_parts.append("is:unread")
    if extra_query:
        query_parts.append(extra_query)
    q = " ".join(query_parts) if query_parts else ""

    async with httpx.AsyncClient() as client:
        # الخطوة 1: جلب قائمة الرسائل
        list_params: dict = {"maxResults": max_results}
        if q:
            list_params["q"] = q

        list_resp = await client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params=list_params
        )

        if list_resp.status_code != 200:
            return {"success": False, "error": list_resp.text}

        messages_meta = list_resp.json().get("messages", [])
        if not messages_meta:
            return {"success": True, "emails": [], "count": 0, "message": "No emails found."}

        # الخطوة 2: جلب تفاصيل كل رسالة
        emails = []
        for msg_ref in messages_meta[:max_results]:
            msg_id = msg_ref["id"]
            detail_resp = await client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "format": "metadata",
                    "metadataHeaders": ["From", "To", "Subject", "Date"]
                }
            )
            if detail_resp.status_code != 200:
                continue

            msg_data = detail_resp.json()
            headers = {
                h["name"]: h["value"]
                for h in msg_data.get("payload", {}).get("headers", [])
            }
            labels = msg_data.get("labelIds", [])

            emails.append({
                "id": msg_id,
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", ""),
                "unread": "UNREAD" in labels,
                "snippet": msg_data.get("snippet", "")
            })

        return {
            "success": True,
            "count": len(emails),
            "emails": emails
        }

CleanToolRegistry.register(gmail_read_config, execute_gmail_read)