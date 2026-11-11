"""
WhatsApp notification helper for the Global QoL Explorer ingestion pipeline.
Follows the unified multi-repo alert format (`🌍 *[GLOBAL-QOL]* ...`) and shared
env var convention (`WHATSAPP_PHONE` + `WHATSAPP_APIKEY`) for TextMeBot & CallMeBot.
Supports both WhatsApp Group IDs (`120363...@g.us`) and direct phone numbers (`+41...`).
"""

from datetime import datetime, timezone
import json
import os
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


def build_whatsapp_message(
    success: bool,
    indicators_ok: int,
    indicators_total: int,
    countries_count: int,
    total_rows: int,
    delta_rows: int,
    duration_sec: float,
    error_detail: str = "",
) -> str:
    """Format a unified, searchable WhatsApp message (`[GLOBAL-QOL]`) summarizing the run."""
    corte = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if success:
        sign = "+" if delta_rows >= 0 else ""
        return (
            "🌍 *[GLOBAL-QOL]* ✅ OK_INGESTION\n"
            f"📅 Corte: {corte} | Indicadores: {indicators_ok}/{indicators_total} | Países: {countries_count}\n"
            f"• Filas totales: {total_rows:,} ({sign}{delta_rows:,} vs baseline)\n"
            f"• Duración: {duration_sec:.1f}s"
        )
    return (
        "🌍 *[GLOBAL-QOL]* ❌ ERROR_INGESTION\n"
        f"📅 Corte: {corte} | Indicadores: {indicators_ok}/{indicators_total} | Duración: {duration_sec:.1f}s\n"
        f"• Detalle: {error_detail or 'Fallo inesperado durante la ejecución'}"
    )


def send_whatsapp_notification(message: str) -> bool:
    """
    Send `message` via TextMeBot or CallMeBot using the standardized credentials:
      - WHATSAPP_PHONE: WhatsApp Group JID (`120363...@g.us`) OR phone number (`+4177...`)
      - WHATSAPP_APIKEY: TextMeBot alphanumeric key or CallMeBot numeric key
    Returns True if sent, False if skipped or failed.
    """
    recipient = os.getenv("WHATSAPP_PHONE", "").strip()
    if not recipient:
        logger.info("WHATSAPP_PHONE not configured; skipping WhatsApp dispatch.")
        return False

    api_key = (
        os.getenv("WHATSAPP_APIKEY", "").strip()
        or os.getenv("WHATSAPP_CALLMEBOT_APIKEY", "").strip()
    )
    if not api_key:
        logger.warning("WHATSAPP_PHONE is set, but WHATSAPP_APIKEY was not found.")
        return False

    encoded_msg = urllib.parse.quote(message)

    # TextMeBot uses alphanumeric keys (supports both @g.us group IDs and +phone)
    if not api_key.isdigit():
        if "@g.us" in recipient:
            formatted_recipient = recipient
        else:
            clean_phone = recipient.lstrip("+").replace(" ", "").replace("-", "")
            formatted_recipient = urllib.parse.quote(f"+{clean_phone}")
        url = (
            f"https://api.textmebot.com/send.php?"
            f"recipient={formatted_recipient}&apikey={urllib.parse.quote(api_key)}"
            f"&text={encoded_msg}&json=yes"
        )
        provider_name = "TextMeBot"
    else:
        clean_phone = recipient.lstrip("+").replace(" ", "").replace("-", "")
        url = (
            f"https://api.callmebot.com/whatsapp.php?"
            f"phone={clean_phone}&text={encoded_msg}&apikey={api_key}"
        )
        provider_name = "CallMeBot"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="ignore").strip()
            if provider_name == "TextMeBot":
                try:
                    ok = json.loads(body).get("status") == "success"
                except Exception:
                    ok = "Success" in body or "success" in body
            else:
                ok = 200 <= resp.status < 300
            logger.info("WhatsApp notification via %s: HTTP %s (ok=%s)", provider_name, resp.status, ok)
            return ok
    except Exception as exc:
        logger.error("Failed to send WhatsApp via %s: %s", provider_name, exc)
        return False
