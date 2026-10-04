#!/usr/bin/env python3
"""Tekee näennäisen jonodatan sivun esikatselua varten: data/demo.csv (4 viikkoa, päättyy nykyhetkeen).

Sivu lukee tiedoston osoitteella index.html?demo. Oikeaan data/queue.csv:hen ei koske.
"""
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(__file__).parent / "data" / "demo.csv"
FIELDS = ["fetched_at", "closed", "available", "time", "label", "color", "hint", "updated_at"]
BUCKETS = [
    ("5–15 min", "green", "🟢 Vihreä", "pöytiä vapaana"),
    ("15–25 min", "green", "🟢 Vihreä", "pöytiä vapaana"),
    ("25–45 min", "yellow", "🟡 Keltainen", "muutama pöytä vapaana"),
    ("45–60 min", "red", "🔴 Punainen", "pöydät täynnä"),
    ("60–90 min", "red", "🔴 Punainen", "pöydät täynnä"),
]


def load(local: datetime) -> float:
    """Kuvitteellinen kuormitus: viikonloppu ja lounas/illallinen ovat kiireisiä."""
    wd, h = local.weekday(), local.hour + local.minute / 60
    base = 8 + (14 if wd >= 4 else 0) + (10 if wd == 6 else 0)
    peak = math.exp(-((h - 12.7) / 1.1) ** 2) * 22 + math.exp(-((h - 17.5) / 1.3) ** 2) * 26
    return base + peak + random.gauss(0, 4)


def main() -> None:
    random.seed(4)
    hel = ZoneInfo("Europe/Helsinki")
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    t = (now - timedelta(days=28)).replace(minute=0)
    rows, prev, lag = [], None, None
    while t <= now:
        local = t.astimezone(hel)
        iso = t.isoformat(timespec="seconds")
        if not 11 <= local.hour < 20:
            key, row = ("closed",), [iso, True, True, "Suljettu", "Suljettu", "", "", ""]
        else:
            if lag is None or random.random() < 0.18:
                lag = load(local)
            b = BUCKETS[min(4, max(0, int((lag - 5) / 14)))]
            key, row = b, [iso, False, True, b[0], b[2], b[1], b[3], iso]
        if key != prev:
            rows.append(row)
            prev = key
        t += timedelta(minutes=5)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows)
    print(f"{len(rows)} riviä -> {OUT}")


if __name__ == "__main__":
    main()
