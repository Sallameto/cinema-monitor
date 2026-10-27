import os
import requests
from bs4 import BeautifulSoup

SITE = "https://tanta.galaxy-cinema.com/"
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TARGET = "avengers: doomsday"

def notify(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=20,
    )
    response.raise_for_status()

response = requests.get(
    SITE,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
found_booking = False

for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
    title = heading.get_text(" ", strip=True).lower()

    if TARGET not in title:
        continue

    parent = heading

    for _ in range(5):
        if parent.parent is None:
            break

        parent = parent.parent
        links = parent.find_all("a", href=True)
        booking_links = [
            link for link in links
            if "book now" in link.get_text(" ", strip=True).lower()
            or "book tickets" in link.get_text(" ", strip=True).lower()
        ]

        if booking_links:
            link = booking_links[0]["href"]
            if link.startswith("/"):
                from urllib.parse import urljoin
                link = urljoin(SITE, link)

            notify(
                "تم العثور على Avengers: Doomsday مع رابط حجز محتمل "
                "في Galaxy Cinema Tanta.\n"
                "تحقق من توفر التذاكر هنا:\n" + link
            )
            found_booking = True
            break

    if found_booking:
        break

if found_booking:
    print("Potential booking link found.")
else:
    print("No matching movie booking link found.")
