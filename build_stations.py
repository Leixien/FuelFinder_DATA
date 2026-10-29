"""Build stations.json (contract v1) from the MIMIT daily CSVs.

Usage: python build_stations.py OUTPUT [ANAGRAFICA_CSV PREZZI_CSV]
Without CSV paths the files are downloaded from MIMIT.
"""

import csv
import json
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA_VERSION = 1
MIMIT_URL = "https://www.mimit.gov.it/images/exportCSV/"
SOURCE = {
    "name": "MIMIT - Osservaprezzi Carburanti",
    "license": "IODL 2.0",
    "url": "https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti",
}
FUEL_TYPES = ["benzina", "gasolio", "gpl", "metano", "gnl", "hvo", "benzina_special", "gasolio_special"]
STATION_TYPES = {"stradale": "stradale", "autostradale": "autostradale"}
ROME = ZoneInfo("Europe/Rome")
# Generous bounding box (Lampedusa to Vetta d'Italia): catches 0,0 and swapped lat/lon, not subtler outliers.
LAT_RANGE, LON_RANGE = (35.0, 47.5), (6.0, 19.0)
# A broken upstream file must not replace good published data.
MIN_STATIONS = 15_000

DIESEL_WORDS = ("gasolio", "diesel")
PETROL_WORDS = ("benzina", "super", "ottani", "verde", "perform", "v-power")


def map_fuel(desc):
    """MIMIT descCarburante -> (fuel, label). fuel is None when the description cannot be classified."""
    name = " ".join(desc.split())
    low = name.lower()
    if low in FUEL_TYPES[:6]:
        return low, None
    if low == "l-gnc":  # liquefied methane dispensed as compressed methane
        return "metano", name
    if "hvo" in low:
        return "hvo", name
    if any(word in low for word in DIESEL_WORDS):
        return "gasolio_special", name
    if any(word in low for word in PETROL_WORDS):
        return "benzina_special", name
    return None, name


def parse_csv(text):
    """Returns (extraction date, rows as dicts). Line 1 is 'Estrazione del YYYY-MM-DD', line 2 the header."""
    lines = text.splitlines()
    extraction = datetime.strptime(lines[0].split()[-1], "%Y-%m-%d").date()
    # MIMIT changed the separator in February 2026: pick whichever splits the header the most.
    delimiter = max("|;,\t", key=lines[1].count)
    return extraction, list(csv.DictReader(lines[1:], delimiter=delimiter))


def clean(value):
    return " ".join((value or "").split())


def to_utc(dt_comu):
    local = datetime.strptime(dt_comu.strip(), "%d/%m/%Y %H:%M:%S").replace(tzinfo=ROME)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build(anagrafica_text, prezzi_text, now):
    extraction, stations_rows = parse_csv(anagrafica_text)
    _, price_rows = parse_csv(prezzi_text)
    stats = Counter()
    unknown_fuels = Counter()

    prices = {}
    for row in price_rows:
        try:
            station_id = int(row["idImpianto"])
            price = round(float(row["prezzo"].replace(",", ".")), 3)
            updated_at = to_utc(row["dtComu"])
        except (ValueError, KeyError, AttributeError):
            stats["bad_price_rows"] += 1
            continue
        fuel, label = map_fuel(row["descCarburante"] or "")
        if fuel is None:
            unknown_fuels[label] += 1
            continue
        if not 0 < price < 10:
            stats["implausible_prices"] += 1
            continue
        entry = {"fuel": fuel, "price": price, "self": row["isSelf"].strip() == "1", "updated_at": updated_at}
        if label:
            entry["label"] = label
        # Same product reported twice: keep the latest communication.
        key = (fuel, label, entry["self"])
        current = prices.setdefault(station_id, {}).get(key)
        if current is None or current["updated_at"] < updated_at:
            prices[station_id][key] = entry

    stations = []
    for row in stations_rows:
        try:
            station_id = int(row["idImpianto"])
            lat = float(row["Latitudine"].replace(",", "."))
            lon = float(row["Longitudine"].replace(",", "."))
        except (ValueError, KeyError, AttributeError):
            stats["bad_station_rows"] += 1
            continue
        if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
            stats["invalid_coordinates"] += 1
            continue
        if station_id not in prices:
            stats["without_prices"] += 1
            continue
        stations.append({
            "id": station_id,
            "name": clean(row["Nome Impianto"]),
            "brand": clean(row["Bandiera"]),
            "operator": clean(row["Gestore"]),
            "type": STATION_TYPES.get(clean(row["Tipo Impianto"]).lower(), "altro"),
            "address": clean(row["Indirizzo"]),
            "city": clean(row["Comune"]),
            "province": clean(row["Provincia"]),
            # 6 decimals is ~10 cm: more is noise from the operators' input and only adds bytes.
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "prices": sorted(
                prices[station_id].values(),
                key=lambda p: (FUEL_TYPES.index(p["fuel"]), p.get("label") or "", not p["self"]),
            ),
        })
    stations.sort(key=lambda s: s["id"])

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prices_reference_date": extraction.isoformat(),
        "source": SOURCE,
        "fuel_types": FUEL_TYPES,
        "stations": stations,
    }
    return payload, stats, unknown_fuels


def download(name, attempts=3):
    request = urllib.request.Request(MIMIT_URL + name, headers={"User-Agent": "fuel-data (+https://github.com/Leixien)"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read().decode("utf-8")
        except OSError:
            if attempt == attempts:
                raise
            time.sleep(10 * attempt)


def main(argv):
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    out = Path(argv[1])
    if len(argv) == 4:
        anagrafica, prezzi = Path(argv[2]).read_text("utf-8"), Path(argv[3]).read_text("utf-8")
    else:
        anagrafica, prezzi = download("anagrafica_impianti_attivi.csv"), download("prezzo_alle_8.csv")

    payload, stats, unknown_fuels = build(anagrafica, prezzi, datetime.now(timezone.utc))
    count = len(payload["stations"])
    print(f"stations={count} prices={sum(len(s['prices']) for s in payload['stations'])} "
          f"reference_date={payload['prices_reference_date']} {dict(stats)}", file=sys.stderr)
    if unknown_fuels:
        print(f"::warning::unclassified fuels skipped: {dict(unknown_fuels)}", file=sys.stderr)
    if count < MIN_STATIONS:
        sys.exit(f"only {count} stations (< {MIN_STATIONS}): refusing to publish")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), "utf-8")


if __name__ == "__main__":
    main(sys.argv)
