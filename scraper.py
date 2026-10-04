#!/usr/bin/env python3
"""Hakee Grill Room Hankasalmen keittiön jonotustilanteen ja lisää sen CSV-tiedostoon.

grillroom.fi upottaa jonotilanteen iframena (Cloudflare Worker), joka lukee tiedon
JSON-endpointista. Haetaan se suoraan. Rivi lisätään vain, jos tilanne on muuttunut
edellisestä rivistä.
"""
import csv
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://grillroom.sami-c0d.workers.dev/api/status"
CSV_PATH = Path(__file__).parent / "data" / "queue.csv"
FIELDS = ["fetched_at", "closed", "available", "time", "label", "color", "hint", "updated_at"]
COMPARE = FIELDS[1:7]  # muutos näillä kentillä => uusi rivi


def fetch() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "grillroom-queue-tracker (github actions)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def to_row(data: dict) -> dict:
    status = data.get("status") or {}
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "closed": data.get("closed"),
        "available": data.get("available"),
        "time": status.get("time", ""),
        "label": status.get("label", ""),
        "color": status.get("color", ""),
        "hint": status.get("hint", ""),
        "updated_at": data.get("updatedAt", ""),
    }


def last_row() -> dict | None:
    if not CSV_PATH.exists():
        return None
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-1] if rows else None


def main() -> int:
    row = to_row(fetch())
    prev = last_row()
    if prev and all(str(row[k]) == prev[k] for k in COMPARE):
        print("Ei muutosta:", row["time"], row["label"])
        return 0

    CSV_PATH.parent.mkdir(exist_ok=True)
    is_new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)
    print("Tallennettu:", row["time"], row["label"], row["hint"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
