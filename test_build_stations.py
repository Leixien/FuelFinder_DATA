import unittest
from datetime import datetime, timezone

from build_stations import build, map_fuel, parse_csv

ANAGRAFICA = """Estrazione del 2026-10-28
idImpianto|Gestore|Bandiera|Tipo Impianto|Nome Impianto|Indirizzo|Comune|Provincia|Latitudine|Longitudine
1|ROSSI  SRL|Q8|Autostradale|A1 EST|VIA  ROMA   1 |NAPOLI|NA|40.88415920489065|14.27
2|BIANCHI|Pompe Bianche|Pompe Bianche|NO NAME|VIA X|SALERNO|SA|40.68|14.77
3|VERDI|Agip Eni|Stradale|ZERO|VIA Y|CASERTA|CE|0|0
4|NERI|IP|Stradale|NO PRICES|VIA Z|AVELLINO|AV|40.91|14.79
5|GIALLI|Shell|Stradale|BAD|VIA W|BENEVENTO|BN|abc|14.78
"""

PREZZI = """Estrazione del 2026-10-28
idImpianto|descCarburante|prezzo|isSelf|dtComu
1|Benzina|1.789|1|23/10/2026 20:00:07
1|Benzina|1.939|0|26/10/2026 08:00:00
1|Blue Diesel|1.899|1|26/10/2026 08:00:00
1|HVOlution|1.999|1|26/10/2026 08:00:00
1|L-GNC|1.459|1|26/10/2026 08:00:00
1|Benzina|1.799|1|24/10/2026 09:00:00
1|Mistero 2000|1.5|1|26/10/2026 08:00:00
2|GNL|1.6|1|26/10/2026 08:00:00
2|Gasolio|0|1|26/10/2026 08:00:00
3|Benzina|1.7|1|26/10/2026 08:00:00
5|Benzina|1.7|1|26/10/2026 08:00:00
"""

NOW = datetime(2026, 10, 29, 8, 0, tzinfo=timezone.utc)


class MapFuelTest(unittest.TestCase):
    def test_mapping(self):
        cases = {
            "Benzina": ("benzina", None),
            "Gasolio": ("gasolio", None),
            "GPL": ("gpl", None),
            "Metano": ("metano", None),
            "GNL": ("gnl", None),
            "HVO": ("hvo", None),
            "L-GNC": ("metano", "L-GNC"),
            "HVOlution": ("hvo", "HVOlution"),
            "Gasolio Bio HVO": ("hvo", "Gasolio Bio HVO"),
            "Blue Diesel": ("gasolio_special", "Blue Diesel"),
            "V-Power Diesel": ("gasolio_special", "V-Power Diesel"),
            "Gasolio artico": ("gasolio_special", "Gasolio artico"),
            "Blue Super": ("benzina_special", "Blue Super"),
            "V-Power": ("benzina_special", "V-Power"),
            "HiQ Perform+": ("benzina_special", "HiQ Perform+"),
            "Benzina  Energy 98 ottani": ("benzina_special", "Benzina Energy 98 ottani"),
            "F101": (None, "F101"),
        }
        for desc, expected in cases.items():
            with self.subTest(desc=desc):
                self.assertEqual(map_fuel(desc), expected)


class ParseCsvTest(unittest.TestCase):
    def test_detects_delimiter(self):
        for sep in "|;":
            text = f"Estrazione del 2026-10-28\nidImpianto{sep}prezzo\n7{sep}1.5\n"
            with self.subTest(sep=sep):
                date, rows = parse_csv(text)
                self.assertEqual(date.isoformat(), "2026-10-28")
                self.assertEqual(rows, [{"idImpianto": "7", "prezzo": "1.5"}])


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.payload, self.stats, self.unknown = build(ANAGRAFICA, PREZZI, NOW)
        self.stations = {s["id"]: s for s in self.payload["stations"]}

    def test_header(self):
        self.assertEqual(self.payload["schema_version"], 1)
        self.assertEqual(self.payload["generated_at"], "2026-10-29T08:00:00Z")
        self.assertEqual(self.payload["prices_reference_date"], "2026-10-28")
        self.assertIn("gnl", self.payload["fuel_types"])

    def test_excludes_invalid_coordinates_and_stations_without_prices(self):
        self.assertEqual(sorted(self.stations), [1, 2])
        self.assertEqual(self.stats["invalid_coordinates"], 1)
        self.assertEqual(self.stats["without_prices"], 1)
        self.assertEqual(self.stats["bad_station_rows"], 1)

    def test_station_fields(self):
        station = self.stations[1]
        self.assertEqual(station["type"], "autostradale")
        self.assertEqual(station["operator"], "ROSSI SRL")
        self.assertEqual(station["address"], "VIA ROMA 1")
        self.assertEqual(station["lat"], 40.884159)
        self.assertEqual(self.stations[2]["type"], "altro")

    def test_prices(self):
        prices = self.stations[1]["prices"]
        self.assertEqual(
            [(p["fuel"], p.get("label"), p["self"]) for p in prices],
            [
                ("benzina", None, True),
                ("benzina", None, False),
                ("metano", "L-GNC", True),
                ("hvo", "HVOlution", True),
                ("gasolio_special", "Blue Diesel", True),
            ],
        )
        # Duplicate self benzina: the latest communication wins.
        self.assertEqual(prices[0]["price"], 1.799)
        self.assertEqual(prices[0]["updated_at"], "2026-10-24T07:00:00Z")  # CEST, UTC+2
        self.assertEqual(prices[1]["updated_at"], "2026-10-26T07:00:00Z")  # CET, UTC+1

    def test_skips_unknown_fuels_and_implausible_prices(self):
        self.assertEqual(dict(self.unknown), {"Mistero 2000": 1})
        self.assertEqual(self.stats["implausible_prices"], 1)
        self.assertEqual([p["fuel"] for p in self.stations[2]["prices"]], ["gnl"])


if __name__ == "__main__":
    unittest.main()
