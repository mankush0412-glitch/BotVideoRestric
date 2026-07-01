"""
Flask web server — Render free tier ko alive rakhta hai (ping endpoint).
"""
from flask import Flask
import threading
import asyncio

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "BotExtractor is running! 🔓"

@flask_app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(__import__("os").environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_flask()
