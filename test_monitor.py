import re
import unicodedata
import json
import tempfile
from pathlib import Path

def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()

def should_alert(state, event):
    key = f"{event}_sent"
    if state.get(key, False):
        return False
    state[key] = True
    return True

# Test 1: movie name matching
names = [
    "Avengers: Doomsday",
    "Avengers:  Doomsday",
    "  AVENGERS: DOOMSDAY  ",
]
assert len({normalize(name) for name in names}) == 1
assert normalize("Avengers: Doomsday") == "avengers doomsday"
print("PASS: movie name matching")

# Test 2: separate Coming Soon and booking alerts
state = {
    "coming_soon_sent": False,
    "booking_sent": False,
}

assert should_alert(state, "coming_soon") is True
assert should_alert(state, "coming_soon") is False
assert should_alert(state, "booking") is True
assert should_alert(state, "booking") is False
print("PASS: each alert is sent once")

# Test 3: saved state survives reload
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "state.json"
    path.write_text(json.dumps(state), encoding="utf-8")
    restored = json.loads(path.read_text(encoding="utf-8"))

    assert should_alert(restored, "coming_soon") is False
    assert should_alert(restored, "booking") is False

print("PASS: saved state prevents duplicate alerts")
print("ALL TESTS PASSED")
