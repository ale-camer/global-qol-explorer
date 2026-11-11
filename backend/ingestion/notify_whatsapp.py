"""
WhatsApp notification helper for the Global QoL Explorer ingestion pipeline.
Follows the unified multi-repo alert format (`🌍 *[GLOBAL-QOL]* ...`) and shared
env var convention (`WHATSAPP_PHONE` + `WHATSAPP_APIKEY`) for TextMeBot & CallMeBot.
"""

from datetime import datetime, timezone
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
      - WHATSAPP_PHONE (e.g. +54911...)
      - WHATSAPP_APIKEY (TextMeBot alphanumeric key or CallMeBot numeric key)
    Returns True if sent, False if skipped or failed.
    """
    phone = os.getenv("WHATSAPP_PHONE", "").strip()
    if not phone:
        logger.info("WHATSAPP_PHONE not configured; skipping WhatsApp dispatch.")
        return False

    api_key = (
        os.getenv("WHATSAPP_APIKEY", "").strip()
        or os.getenv("WHATSAPP_CALLMEBOT_APIKEY", "").strip()
    )
    if not api_key:
        logger.warning("WHATSAPP_PHONE is set, but WHATSAPP_APIKEY was not found.")
        return False

    clean_phone = phone.lstrip("+").replace(" ", "").replace("-", "")
    encoded_msg = urllib.parse.quote(message)

    # TextMeBot uses alphanumeric keys (e.g. "aBc123XyZ"); CallMeBot uses purely numeric keys
    if not api_key.isdigit():
        url = (
            f"https://api.textmebot.com/send.php?"
            f"recipient=+{clean_phone}&apikey={urllib.parse.quote(api_key)}&text={encoded_msg}"
        )
        provider_name = "TextMeBot"
    else:
        url = (
            f"https://api.callmebot.com/whatsapp.php?"
            f"phone={clean_phone}&text={encoded_msg}&apikey={api_key}"
        )
        provider_name = "CallMeBot"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GlobalQoLExplorer/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            logger.info("WhatsApp notification sent via %s (HTTP %s).", provider_name, resp.status)
            return 200 <= resp.status < 300
    except Exception as exc:
        logger.error("Failed to send WhatsApp via %s: %s", provider_name, exc)
        return False
