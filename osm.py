#!/usr/bin/env python3
"""
Orbit Simple Monitor (OSM)
A host-level monitoring tool running inside a Docker container.

Author: @OrbitTurner
Description:
  - Gathers CPU, RAM, and DISK usage from the host.
  - Stores data in a SQLite database.
  - Sends alerts via Slack and/or Email if thresholds are exceeded.
  - Cleans up data older than 30 days.
  - Made From Senegal 🇸🇳 🚀
"""
"""
Orbit Simple Monitor (OSM) - Open Source License / GNU AFFERO GENERAL PUBLIC LICENSE (OSM-License v1.0)
This software is free for personal and non-commercial use.
Selling or licensing this software for profit is strictly prohibited.
Full license available at: https://github.com/orbitturner/osm/LICENSE
"""

from pyfiglet import figlet_format
from loguru import logger
from email.header import Header
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import sys
import signal
import psutil
import requests
import smtplib
import schedule
import sqlite3
import time
import os

# ─────────────────────────────────────────────────────────────────────────────
# 1) ENVIRONMENT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DB_FILE = os.getenv("DB_FILE", "osm.db")  # SQLite DB file

# Thresholds (%)
CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", "90"))
RAM_THRESHOLD = int(os.getenv("RAM_THRESHOLD", "90"))
DISK_THRESHOLD = int(os.getenv("DISK_THRESHOLD", "90"))

# Interval scheduling
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1"))
CHECK_INTERVAL_UNIT = os.getenv("CHECK_INTERVAL_UNIT", "m").lower()
# Accept "s", "m", "h" for seconds, minutes, hours

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "alerts@example.com").replace(" ", "").split(',')
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "user@example.com")
SMTP_PASS = os.getenv("SMTP_PASS", "secret")
ALERT_CHANNELS = os.getenv(
    "ALERT_CHANNELS", "SLACK,EMAIL")  # e.g. "SLACK,EMAIL"
HOSTNAME = os.getenv("YOUR_SERVER_NAME", "SamaServerBouNeikhBi")

# Docker host /proc mount path
HOST_PROC_PATH = "/host_proc"

# Override psutil's default /proc path for host-level monitoring only if we are not in a windows host
# psutil.PROCFS_PATH = HOST_PROC_PATH


# ─────────────────────────────────────────────────────────────────────────────
# 2) LOGGING CONFIGURATION (LOGURU)
# ─────────────────────────────────────────────────────────────────────────────

LOG_FORMAT = "<b><magenta>⪢OSM⪡</magenta></b> • <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>\n"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Remove default handler
logger.remove()

# 2.1) Console Logging
logger.add(
    sys.stdout,  # prints to stdout
    level=LOG_LEVEL,
    colorize=True,
    format=LOG_FORMAT
)

# 2.2) Rotating File Logging (e.g. 10 MB rotation, keep 14 days)
logger.add(
    "osm.log",
    rotation="10 MB",     # Rotate when the file is >= 10MB
    retention="14 days",  # Remove logs older than 14 days
    colorize=True,
    level=LOG_LEVEL,
    format=LOG_FORMAT
)


# ─────────────────────────────────────────────────────────────────────────────
# 3) PRINT ASCII ART ON STARTUP
# ─────────────────────────────────────────────────────────────────────────────
def print_ascii_banner():
    banner = figlet_format("OrbitSimpleMonitor", font="slant")
    logger.info("\n" + banner + "🚀 Welcome to Orbit Simple Monitor (OSM)!\n")


# ─────────────────────────────────────────────────────────────────────────────
# 4) INIT SQLITE DB
# ─────────────────────────────────────────────────────────────────────────────
def init_db(conn=None):
    """Initializes the SQLite database and creates required tables."""
    # Check if DB already exists
    if os.path.exists(DB_FILE):
        logger.info(f"🗄 Existing DB file '{DB_FILE}' detected. Reusing it.")
    else:
        logger.info(f"💾 No DB file '{DB_FILE}' found. Creating a new one...")

    if conn is None:
        conn = sqlite3.connect(DB_FILE)

    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                cpu_usage REAL NOT NULL,
                ram_usage REAL NOT NULL,
                disk_usage REAL NOT NULL
            )
        """)
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# 5) COLLECT METRICS
# ─────────────────────────────────────────────────────────────────────────────
def collect_metrics(conn=None):
    """Collect CPU, RAM, and DISK usage from the host, store in DB, and send alerts if needed."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    now = datetime.now()
    logger.info(
        f"🩺 CPU: {cpu_usage:.2f}% | RAM: {ram_usage:.2f}% | DISK: {disk_usage:.2f}%")

    if conn is None:
        conn = sqlite3.connect(DB_FILE)

    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usage_history (timestamp, cpu_usage, ram_usage, disk_usage)
            VALUES (?, ?, ?, ?)
        """, (now, cpu_usage, ram_usage, disk_usage))
        conn.commit()

    # Debug logs for threshold checks
    logger.debug(
        f"✅ Threshold Check - CPU({cpu_usage}%) >= {CPU_THRESHOLD}? {cpu_usage >= CPU_THRESHOLD}")
    logger.debug(
        f"✅ Threshold Check - RAM({ram_usage}%) >= {RAM_THRESHOLD}? {ram_usage >= RAM_THRESHOLD}")
    logger.debug(
        f"✅ Threshold Check - DISK({disk_usage}%) >= {DISK_THRESHOLD}? {disk_usage >= DISK_THRESHOLD}")

    # If threshold exceeded, trigger alert
    if (cpu_usage >= CPU_THRESHOLD) or (ram_usage >= RAM_THRESHOLD) or (disk_usage >= DISK_THRESHOLD):
        alert_msg = (
            f"⚠️ **Orbit Simple Monitor Alert** ⚠️\n\n"
            f"🏠 Host: {HOSTNAME}\n"
            f"🕒 Timestamp: {now}\n"
            f"🔴 CPU Usage: {cpu_usage:.2f}% (Threshold = {CPU_THRESHOLD}%)\n"
            f"🔴 RAM Usage: {ram_usage:.2f}% (Threshold = {RAM_THRESHOLD}%)\n"
            f"🔴 DISK Usage: {disk_usage:.2f}% (Threshold = {DISK_THRESHOLD}%)\n"
        )
        logger.debug("🚀 send_alert() should be triggered now!")
        send_alert(alert_msg)
    else:
        logger.debug("⚠️ No alert triggered - conditions not met!")


# ─────────────────────────────────────────────────────────────────────────────
# 6) SEND ALERTS (SLACK & EMAIL)
# ─────────────────────────────────────────────────────────────────────────────
def send_alert(message: str):
    channels = [ch.strip().upper() for ch in ALERT_CHANNELS.split(",")]
    if "SLACK" in channels and SLACK_WEBHOOK_URL:
        send_slack(message)
    if "EMAIL" in channels and ALERT_EMAIL:
        send_email(message)


def send_slack(message: str):
    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        logger.success("✅ Slack alert sent successfully.")
    except Exception as e:
        logger.error(f"❌ Slack alert failed: {e}")


def send_email(message: str):
    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = Header("Orbit Simple Monitor Alert", "utf-8")
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL

        logger.info(
            f"📧 Attempting to send email alert to {ALERT_EMAIL} via {SMTP_SERVER}:{SMTP_PORT}")

        if SMTP_PORT == 465:
            # Use direct SSL connection for port 465
            logger.info("🔒 Using SMTP_SSL for port 465")
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            server.ehlo()  # Say hello to the server
        else:
            # Use STARTTLS for ports like 587
            logger.info("🔐 Using STARTTLS for port 587 or other ports")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()

        # Login to the SMTP server
        server.login(SMTP_USER, SMTP_PASS)
        logger.success("✅ SMTP login successful!")

        # Send the email
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        logger.success("✅ Email alert sent successfully.")

        # Close the connection
        server.quit()

    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {e}")
    except Exception as e:
        logger.error(f"❌ Email alert failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 7) CLEANUP OLD DATA (>30 days)
# ─────────────────────────────────────────────────────────────────────────────


def cleanup_history():
    cutoff_date = datetime.now() - timedelta(days=30)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM usage_history WHERE timestamp < ?", (cutoff_date,))
        conn.commit()
    logger.info("🧹 Cleaned up records older than 30 days.")


# ─────────────────────────────────────────────────────────────────────────────
# 8) MAIN & GRACEFUL SHUTDOWN
# ─────────────────────────────────────────────────────────────────────────────
def schedule_collections():
    """Schedules metric collection based on interval and interval unit."""
    if CHECK_INTERVAL_UNIT.startswith("s"):
        logger.info(
            f"⏱  Scheduling metric collection every {CHECK_INTERVAL} second(s).")
        schedule.every(CHECK_INTERVAL).seconds.do(collect_metrics)
    elif CHECK_INTERVAL_UNIT.startswith("h"):
        logger.info(
            f"⏱  Scheduling metric collection every {CHECK_INTERVAL} hour(s).")
        schedule.every(CHECK_INTERVAL).hours.do(collect_metrics)
    else:
        logger.info(
            f"⏱  Scheduling metric collection every {CHECK_INTERVAL} minute(s).")
        schedule.every(CHECK_INTERVAL).minutes.do(collect_metrics)


def handle_signal(signum, frame):
    """Handle SIGINT/SIGTERM to shut down gracefully."""
    logger.warning(f"👋 Caught signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    print_ascii_banner()
    logger.info("🎉 Initializing Orbit Simple Monitor database...")
    init_db()

    schedule_collections()
    logger.info("⏱  Scheduling daily cleanup at 00:00.")
    schedule.every().day.at("00:00").do(cleanup_history)

    logger.info("🚀 Orbit Simple Monitor started. Monitoring your host now...")

    # Catch SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
