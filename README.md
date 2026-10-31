# Harzer Stempelkarte

Karte aller 222 Stempelstellen der Harzer Wandernadel. Stempel abhaken, Fortschritt bis zu allen Leistungsabzeichen verfolgen (inkl. 23 Pflichtstellen „Harzer Steiger“).

**Online:** https://git-von-markus.github.io/wandernadel/

## Touren planen (ab v1.2.0)
- Stempel öffnen → „Zur Tour“, eigene Wegpunkte über „Wegpunkte setzen“
- Reihenfolge nach echter Fußweg-Entfernung (OSRM), per Griff umsortierbar
- Route über BRouter (Wanderprofil) mit km, Höhenmetern und Gehzeit, Export „GPX für Navigation“

## Aufs Handy
- iPhone: in Safari öffnen → Teilen → „Zum Home-Bildschirm“
- Android: in Chrome öffnen → ⋮ → „App installieren“

Danach nur noch über das Icon öffnen – der Fortschritt wird auf dem Gerät gespeichert. Schon angesehene Kartenbereiche funktionieren auch ohne Netz.

## Daten
- Stempelstellen: offizielle Übersichtstabelle harzer-wandernadel.de
- Positionen: OpenStreetMap (`ref=HWN …`) als `stempel-positionen.json` im Repo. Die GitHub Action „Stempel-Positionen aktualisieren“ holt sie montags neu (`tools/osm-positionen.py`) und committet nur bei Änderungen. Manuell starten: Actions → Stempel-Positionen aktualisieren → Run workflow.
- Alternativ offizielle GPX-ZIP auf dem eigenen Gerät einlesen (nur privat nutzbar, deshalb nicht im Repo)
- Route-Links: komoot-Highlights der öffentlichen Sammlung „Die 222 Stempelstellen der Harzer Wandernadel“
- Karte: © OpenStreetMap-Mitwirkende, OpenTopoMap
