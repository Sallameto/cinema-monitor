import json
import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://tanta.galaxy-cinema.com/"
COMING_SOON = urljoin(BASE, "next_releasing")
STATE_FILE = Path("state.json")
TARGET = "avengers doomsday"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()

def get_page(url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def movie_heading(soup):
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        if TARGET in normalize(heading.get_text(" ", strip=True)):
            return heading
    return None

def booking_link(heading):
    parent = heading
    for _ in range(5):
        if parent.parent is None:
            break
        parent = parent.parent

        for link in parent.find_all("a", href=True):
            label = normalize(link.get_text(" ", strip=True))
            if label in ("book now", "book tickets"):
                return urljoin(BASE, link["href"])
    return None

def notify(message):
    response = session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=20,
    )
    response.raise_for_status()

state = {"coming_soon_sent": False, "booking_sent": False}

if STATE_FILE.exists():
    try:
        state.update(json.loads(STATE_FILE.read_text()))
    except (json.JSONDecodeError, OSError):
        print("Could not read saved state; using defaults.")

home = get_page(BASE)
coming = get_page(COMING_SOON)

home_heading = movie_heading(home)
coming_heading = movie_heading(coming)

# Stage 1: movie appears in Coming Soon.
if coming_heading and not state["coming_soon_sent"]:
    notify(
        "Avengers: Doomsday ظهر في Coming Soon على Galaxy Cinema Tanta:\n"
        + COMING_SOON
    )
    state["coming_soon_sent"] = True
    print("Coming Soon alert sent.")
else:
    print("No new Coming Soon alert.")

# Stage 2: a booking link is associated with the movie.
link = booking_link(home_heading) if home_heading else None

if link and not state["booking_sent"]:
    notify(
        "ظهر رابط حجز محتمل لفيلم Avengers: Doomsday في Galaxy Cinema Tanta:\n"
        + link
    )
    state["booking_sent"] = True
    print("Booking alert sent.")
else:
    print("No new booking alert.")

STATE_FILE.write_text(
    json.dumps(state, indent=2),
    encoding="utf-8",
    )
