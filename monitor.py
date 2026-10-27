import requests
from bs4 import BeautifulSoup

SITE = "https://tanta.galaxy-cinema.com/"

response = requests.get(
    SITE,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("PAGE TITLE:", soup.title.get_text(" ", strip=True) if soup.title else "None")
print("PAGE URL:", response.url)

print("\n--- HEADINGS ---")
for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
    title = tag.get_text(" ", strip=True)
    if title:
        print(title[:200])

print("\n--- MOVIE AND BOOKING LINKS ---")
for link in soup.find_all("a", href=True):
    name = link.get_text(" ", strip=True)
    href = link["href"]

    if name or "book" in href.lower():
        print(f"TEXT: {name[:100]} | URL: {href[:250]}")
        
