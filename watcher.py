#!/usr/bin/env python3
"""
Name‑watcher for WWE SummerSlam 2025 store page.

Adds a polling loop: the page is re‑checked every POLL_INTERVAL_MINUTES
(default 10).  All other behaviour (name search + Gmail alert) is unchanged.

Environment variables
---------------------
NAMES_TO_FIND          Comma‑separated names to look for (optional)
GMAIL_USER             Gmail address (sender & default recipient)   [required]
GMAIL_PASS             Gmail App Password or OAuth2 token           [required]
GMAIL_TO               Override recipient (optional)
POLL_INTERVAL_MINUTES  Polling cadence in minutes (float, default 10)

Example (Docker):
    docker run --rm \
      -e NAMES_TO_FIND="Chelsea Green,Becky Lynch" \
      -e GMAIL_USER="you@gmail.com" \
      -e GMAIL_PASS="abcd efgh ijkl mnop" \
      -e POLL_INTERVAL_MINUTES=5 \
      summerslam-watcher
"""
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

URL = "https://store.epic.leapevent.tech/wwe-summerslam/2025"
DEFAULT_NAMES = ["alexa", "alexa bliss", "bayley", "cm punk", "punk", "randy orton", "randy", "cody rhodes","cody"]


def get_names() -> list[str]:
    env = os.getenv("NAMES_TO_FIND")
    return [n.strip() for n in env.split(",")] if env else DEFAULT_NAMES


def fetch_html(url: str) -> str:
    resp = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; NameWatcher/1.1)"
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def search_names(html: str, targets: list[str]) -> list[str]:
    page_text = BeautifulSoup(html, "html.parser").get_text(" ").lower()
    return [name for name in targets if name.lower() in page_text]


def send_email(found: list[str]) -> None:
    user = os.getenv("GMAIL_USER")
    pwd = os.getenv("GMAIL_PASS")
    to_ = os.getenv("GMAIL_TO", user)

    if not (user and pwd):
        print("[WARN] Email skipped: GMAIL_USER or GMAIL_PASS not set.", file=sys.stderr)
        return

    msg = EmailMessage()
    msg["Subject"] = f"[SummerSlam Alert] Found {', '.join(found)}"
    msg["From"] = user
    msg["To"] = to_
    msg.set_content(
        f"Found {', '.join(found)} on {URL} at "
        f"{datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC.\n\n— Your bot"
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, pwd)
        smtp.send_message(msg)

    print(f"[INFO] Email sent → {to_}")


def once() -> None:
    targets = get_names()
    print(f"[INFO] Checking {URL} for {targets}")
    try:
        found = search_names(fetch_html(URL), targets)
        if found:
            print(f"[FOUND] {found}")
            send_email(found)
        else:
            print("[INFO] No matches.")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}", file=sys.stderr)


def main() -> None:
    interval = float(os.getenv("POLL_INTERVAL_MINUTES", "10"))
    print(f"[INFO] Poll interval: {interval} min")

    while True:
        start = time.time()
        once()
        elapsed = time.time() - start
        sleep_for = max(interval * 60 - elapsed, 0)
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()

