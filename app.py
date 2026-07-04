"""
Flask web server — Render free tier ko alive rakhta hai (ping endpoint).

IMPORTANT (Render free tier gotcha):
Render's free Web Service spins down the ENTIRE container after ~15 min of
no INBOUND HTTP traffic. The Telegram bot's connection is OUTBOUND (MTProto),
so it does NOT count as "activity" — Render kills the whole process anyway,
taking the bot's live connection down with it. That's why the bot works
right after a deploy/restart but goes silent a few minutes later.
Fix: self-ping our own public URL every ~10 min so Render always sees
inbound traffic and never spins the container down.
"""
import os
import time
import logging
import threading
import urllib.request
from flask import Flask

logger = logging.getLogger("BotExtractor.flask")

flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "BotExtractor is running! 🔓"


@flask_app.route("/health")
def health():
    return "OK", 200


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)


def _self_ping_loop():
    """Pings our own public URL every 10 minutes so Render never spins down."""
    url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("SELF_URL")
    if not url:
        logger.warning(
            "⚠️ RENDER_EXTERNAL_URL/SELF_URL env var not set — self-ping disabled. "
            "Bot may go silent after ~15 min on Render free tier. "
            "Set SELF_URL to your https://xxxx.onrender.com address to fix this, "
            "or use an external uptime pinger (UptimeRobot/cron-job.org) hitting that URL every 5-10 min."
        )
        return

    ping_url = url.rstrip("/") + "/health"
    # First ping after a short delay so the server has time to bind the port
    time.sleep(15)
    while True:
        try:
            with urllib.request.urlopen(ping_url, timeout=20) as resp:
                logger.info(f"🔁 Self-ping OK: {ping_url} -> {resp.status}")
        except Exception as e:
            logger.warning(f"⚠️ Self-ping failed: {e}")
        time.sleep(600)  # every 10 minutes (< Render's 15 min spin-down window)


def start_self_ping():
    threading.Thread(target=_self_ping_loop, daemon=True).start()


if __name__ == "__main__":
    run_flask()
