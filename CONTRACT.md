# Contratto `stations.json` — schema v1

Questo repo è il proprietario del contratto. I client (`FuelFinder_IOS`, `FuelFinder_ANDROID`) lo consumano e ne tengono una copia in `specificheTecniche.md` §3: ogni modifica parte da qui.

```json
{
  "schema_version": 1,
  "generated_at": "2026-10-29T08:00:00Z",
  "prices_reference_date": "2026-10-28",
  "source": {
    "name": "MIMIT - Osservaprezzi Carburanti",
    "license": "IODL 2.0",
    "url": "https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti"
  },
  "fuel_types": ["benzina", "gasolio", "gpl", "metano", "gnl", "hvo", "benzina_special", "gasolio_special"],
  "stations": [
    {
      "id": 3513,
      "name": "S.PIETRO",
      "brand": "Q8",
      "operator": "SARNI S.R.L.",
      "type": "autostradale",
      "address": "Autostrada A1 MILANO-NAPOLI Ramo Capodichino, Km. 1+600",
      "city": "NAPOLI",
      "province": "NA",
      "lat": 40.884159,
      "lon": 14.298187,
      "prices": [
        { "fuel": "benzina", "price": 1.994, "self": true, "updated_at": "2026-10-26T05:30:31Z" },
        { "fuel": "hvo", "price": 2.099, "self": true, "updated_at": "2026-10-26T05:30:31Z", "label": "HVOlution" }
      ]
    }
  ]
}
```

## Campi

| Campo | Regola |
|---|---|
| `generated_at` | Istante UTC in cui la pipeline ha prodotto il file. |
| `prices_reference_date` | Data della estrazione MIMIT (`Estrazione del …`): prezzi in vigore alle 8 di quel giorno. È questa, non `generated_at`, a dire quanto sono vecchi i dati. |
| `id` | `idImpianto` MIMIT, stabile (usato anche da OpenStreetMap come `ref:mise`). |
| `name`, `brand`, `operator`, `address`, `city`, `province` | Sempre presenti, mai `null`; spazi normalizzati. Possono essere stringa vuota (oggi succede solo per `name`, ~10 impianti). |
| `type` | `stradale`, `autostradale`, `altro` (qualunque altro valore MIMIT, es. "Pompe Bianche"). |
| `lat`, `lon` | Gradi decimali, 6 decimali. Impianti con coordinate non numeriche o fuori dall'Italia esclusi. |
| `prices` | Mai vuoto: impianti senza prezzi esclusi. Ordinati per `fuel` (ordine di `fuel_types`), `label`, self prima del servito. |
| `price` | Euro con 3 decimali, al litro; **al kg** per `metano` e `gnl`. Prezzi ≤ 0 o ≥ 10 scartati. |
| `self` | `true` self service, `false` servito. |
| `updated_at` | `dtComu` MIMIT (ora italiana) convertito in UTC. Se lo stesso prodotto compare più volte, vince la comunicazione più recente. |
| `label` | Presente solo se la descrizione MIMIT differisce dal nome della categoria: contiene la descrizione originale. |

## Mappatura `descCarburante` → `fuel`

1. `Benzina`, `Gasolio`, `GPL`, `Metano`, `GNL`, `HVO` → categoria omonima, senza `label`.
2. `L-GNC` → `metano` con `label` (metano liquefatto erogato compresso: per l'utente è un rifornimento di metano).
3. Descrizione che contiene "HVO" → `hvo` (HVOlution, HVO100, REHVO, Gasolio Bio HVO, …).
4. Contiene "gasolio" o "diesel" → `gasolio_special` (Blue Diesel, Gasolio artico, V-Power Diesel, …).
5. Contiene "benzina", "super", "ottani", "verde", "perform" o "v-power" → `benzina_special` (Blue Super, V-Power, HiQ Perform+, …).
6. Altro → scartato e segnalato come warning nel log della Action (oggi solo "F101"/"F-101", ~50 prezzi).

## Compatibilità

- Aggiungere campi o valori di `fuel` è **compatibile**: i client ignorano campi sconosciuti e scartano i prezzi con `fuel` sconosciuto.
- Rinominare/rimuovere campi o cambiarne il tipo è **incompatibile**: incrementa `schema_version`; i client rifiutano versioni maggiori di quella supportata.

## Dimensioni (2026-10-28)

21.495 impianti, 92.070 prezzi; 13 MB non compresso, 2 MB con gzip (GitHub Pages lo serve compresso, con `ETag`).
