#!/usr/bin/env python3
"""Holt die Positionen der Stempelstellen der Harzer Wandernadel aus OpenStreetMap
(Overpass, Objekte mit ref=HWN …) und schreibt stempel-positionen.json.

Läuft wöchentlich per GitHub Action. Die Datei wird nur neu geschrieben, wenn sich
Positionen geändert haben, und nie mit einem offensichtlich unvollständigen Ergebnis.
Daten: © OpenStreetMap-Mitwirkende, ODbL.
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
# Harz mit Vorland (Süd, West, Nord, Ost)
QUERY = '[out:json][timeout:180];nwr["ref"~"HWN",i](51.25,9.85,52.15,11.85);out center tags;'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stempel-positionen.json")
REF = re.compile(r"^\s*HWN\s*[-_.]?\s*0*(\d{1,3})\s*$", re.I)
MIN_STELLEN = 150


def fetch():
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    last = None
    for runde in range(3):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, data=body, headers={
                    "User-Agent": "harzer-stempelkarte (github.com/git-von-markus/wandernadel)"})
                with urllib.request.urlopen(req, timeout=240) as r:
                    return json.load(r)["elements"]
            except Exception as e:  # nächsten Server versuchen
                last = e
                print(f"{ep}: {e}", file=sys.stderr)
        time.sleep(30 * (runde + 1))
    raise SystemExit(f"Overpass nicht erreichbar: {last}")


def parse(elements):
    """{nr: [lat, lon]} – bevorzugt Knoten mit checkpoint-Tag, ignoriert stillgelegte."""
    best = {}
    for el in elements:
        center = el.get("center") or {}
        lat, lon = el.get("lat", center.get("lat")), el.get("lon", center.get("lon"))
        if lat is None or lon is None:
            continue
        tags = el.get("tags") or {}
        for part in str(tags.get("ref", "")).split(";"):
            m = REF.match(part)
            if not m:
                continue
            nr = int(m.group(1))
            if not 1 <= nr <= 222:
                continue
            score = (4 if tags.get("checkpoint") else 0) + (2 if el.get("type") == "node" else 0) \
                - (6 if tags.get("disused") or tags.get("disused:checkpoint") else 0)
            if nr not in best or score > best[nr][0]:
                best[nr] = (score, [round(lat, 6), round(lon, 6)])
    return {str(nr): best[nr][1] for nr in sorted(best)}


def render(pts):
    stand = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    zeilen = ",\n".join(f'"{k}":{json.dumps(v)}' for k, v in pts.items())
    return (
        "{" + f'"stand":"{stand}","anzahl":{len(pts)},'
        '"quelle":"© OpenStreetMap-Mitwirkende (ODbL), Objekte mit ref=HWN …",'
        '"pts":{\n' + zeilen + "\n}}\n"
    )


def main():
    pts = parse(fetch())
    if len(pts) < MIN_STELLEN:
        raise SystemExit(f"Nur {len(pts)} Stellen gefunden – Datei bleibt unverändert.")
    try:
        with open(OUT, encoding="utf-8") as f:
            if json.load(f).get("pts") == pts:
                print(f"Keine Änderung ({len(pts)} Stellen).")
                return
    except (OSError, ValueError):
        pass
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(pts))
    fehlend = [n for n in range(1, 223) if str(n) not in pts]
    print(f"{len(pts)} Stellen geschrieben. Ohne Position: {fehlend}")


if __name__ == "__main__":
    main()
