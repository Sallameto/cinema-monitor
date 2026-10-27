import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://tanta.galaxy-cinema.com/"
PAGES = [
    BASE,
    urljoin(BASE, "next_releasing"),
]
TARGET = "avengers: doomsday"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def notify(message):
    r = session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=20,
    )
    r.raise_for_status()

def find_movie(page_url):
    response = session.get(page_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        title = heading.get_text(" ", strip=True).lower()

        if TARGET not in title:
            continue

        parent = heading

        for _ in range(5):
            if parent.parent is None:
                break

            parent = parent.parent

            for link in parent.find_all("a", href=True):
                label = link.get_text(" ", strip=True).lower()

                if label in ("book now", "book tickets"):
                    return {
                        "title": heading.get_text(" ", strip=True),
                        "booking_url": urljoin(
                            page_url, link["href"]
                        ),
                    }

        # Film is listed, but no nearby booking link was found.
        return {
            "title": heading.get_text(" ", strip=True),
            "booking_url": None,
        }

    return None

for page in PAGES:
    try:
        result = find_movie(page)

        if result and result["booking_url"]:
            notify(
                "Avengers: Doomsday ظهر مع رابط حجز محتمل "
                "في Galaxy Cinema Tanta.\n"
                + result["booking_url"]
            )
            print("Potential booking link found.")
            break

        elif result:
            print("Movie listed, but no booking link found:", page)

        else:
            print("Movie not found:", page)

    except Exception as error:
        print(f"Could not check {page}: {error}")
        
