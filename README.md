# fuel-data

Pipeline open data per l'app **Fuel** ([iOS](https://github.com/Leixien/FuelFinder_IOS), [Android](https://github.com/Leixien/FuelFinder_ANDROID)): ogni mattina una GitHub Action scarica i CSV dell'Osservaprezzi Carburanti del MIMIT, li normalizza e pubblica un unico `stations.json` su GitHub Pages. Nessun server, nessuna chiave.

- Contratto del file: [CONTRACT.md](CONTRACT.md)
- Stato e problemi aperti: [TODO.md](TODO.md)

## Uso locale

Solo libreria standard, Python 3.12+.

```sh
python -m unittest -v
python build_stations.py public/stations.json                      # scarica dal MIMIT
python build_stations.py public/stations.json anagrafica.csv prezzi.csv  # da file locali
```

Lo script si rifiuta di produrre il file se trova meno di 15.000 impianti: un CSV rotto non deve sovrascrivere dati buoni.

## Fonte dati

Fonte dati: **MIMIT – Osservaprezzi Carburanti** ([dataset](https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti)), licenza [IODL 2.0](https://www.dati.gov.it/iodl/2.0/). Il file pubblicato riporta l'attribuzione nel campo `source`.

## Licenza

Codice: [Apache 2.0](LICENSE).
