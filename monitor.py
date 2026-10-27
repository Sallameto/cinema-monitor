import os
import requests
from bs4 import BeautifulSoup

SITE = "https://tanta.galaxy-cinema.com/"
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

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
text = soup.get_text(" ", strip=True).lower()

if "avengers: doomsday" in text and any(
    word in text
    for word in ["book now", "book tickets", "showtime"]
):
    notify(
        "ظهر مؤشر محتمل لحجز Avengers: Doomsday في Galaxy Cinema Tanta. "
        "افحص الرابط للتأكد من توفر التذاكر:\n" + SITE
    )
    print("Potential booking detected.")
else:
    print("No booking indication detected.")
  
