"""
WhatsApp notification helper for the Global QoL Explorer ingestion pipeline.
Supports CallMeBot, Meta WhatsApp Cloud API, or Twilio WhatsApp API.
Always sends a human-readable plain-text summary (no raw JSON).
"""

import os
import logging
import urllib.parse
import urllib.request
import json

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
    """Format a clean, readable WhatsApp message summarizing the ingestion run."""
    if success:
        sign = "+" if delta_rows >= 0 else ""
        return (
            "✅ *Global QoL Explorer — Ingesta Exitosa*\n"
            f"• Indicadores: {indicators_ok}/{indicators_total}\n"
            f"• Países: {countries_count}\n"
            f"• Filas totales: {total_rows:,} ({sign}{delta_rows:,} vs baseline)\n"
            f"• Duración: {duration_sec:.1f}s"
        )
    return (
        "❌ *Global QoL Explorer — Error en Ingesta*\n"
        f"• Indicadores procesados: {indicators_ok}/{indicators_total}\n"
        f"• Duración: {duration_sec:.1f}s\n"
        f"• Detalle: {error_detail or 'Fallo inesperado durante la ejecución'}"
    )


def send_whatsapp_notification(message: str) -> bool:
    """
    Send `message` via the configured WhatsApp provider:
      1. CallMeBot: WHATSAPP_PHONE + WHATSAPP_CALLMEBOT_APIKEY
      2. Meta Cloud API: WHATSAPP_PHONE + WHATSAPP_META_TOKEN + WHATSAPP_META_PHONE_ID
      3. Twilio: WHATSAPP_PHONE + TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN + TWILIO_WHATSAPP_FROM
    Returns True if sent, False if skipped or failed.
    """
    phone = os.getenv("WHATSAPP_PHONE", "").strip()
    if not phone:
        logger.info("WHATSAPP_PHONE not configured; skipping WhatsApp dispatch.")
        return False

    # 1. CallMeBot
    callmebot_key = os.getenv("WHATSAPP_CALLMEBOT_APIKEY", "").strip()
    if callmebot_key:
        try:
            clean_phone = phone.lstrip("+").replace(" ", "")
            encoded_msg = urllib.parse.quote(message)
            url = (
                f"https://api.callmebot.com/whatsapp.php?"
                f"phone={clean_phone}&text={encoded_msg}&apikey={callmebot_key}"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "GlobalQoLExplorer/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info("WhatsApp notification sent via CallMeBot (HTTP %s).", resp.status)
                return 200 <= resp.status < 300
        except Exception as exc:
            logger.error("Failed to send WhatsApp via CallMeBot: %s", exc)
            return False

    # 2. Meta WhatsApp Cloud API
    meta_token = os.getenv("WHATSAPP_META_TOKEN", "").strip()
    meta_phone_id = os.getenv("WHATSAPP_META_PHONE_ID", "").strip()
    if meta_token and meta_phone_id:
        try:
            url = f"https://graph.facebook.com/v20.0/{meta_phone_id}/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "to": phone.lstrip("+").replace(" ", ""),
                "type": "text",
                "text": {"preview_url": False, "body": message},
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {meta_token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info("WhatsApp notification sent via Meta Cloud API (HTTP %s).", resp.status)
                return 200 <= resp.status < 300
        except Exception as exc:
            logger.error("Failed to send WhatsApp via Meta Cloud API: %s", exc)
            return False

    # 3. Twilio WhatsApp API
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    twilio_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886").strip()
    if twilio_sid and twilio_token:
        try:
            import base64
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            to_formatted = phone if phone.startswith("whatsapp:") else f"whatsapp:{phone}"
            from_formatted = twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}"
            data = urllib.parse.urlencode({
                "From": from_formatted,
                "To": to_formatted,
                "Body": message,
            }).encode("utf-8")
            creds = base64.b64encode(f"{twilio_sid}:{twilio_token}".encode("utf-8")).decode("ascii")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                logger.info("WhatsApp notification sent via Twilio (HTTP %s).", resp.status)
                return 200 <= resp.status < 300
        except Exception as exc:
            logger.error("Failed to send WhatsApp via Twilio: %s", exc)
            return False

    logger.warning("WHATSAPP_PHONE is set, but no provider credentials were found.")
    return False
