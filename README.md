# fuel-data

Pipeline open data per l'app **Fuel** ([iOS](https://github.com/Leixien/FuelFinder_IOS), [Android](https://github.com/Leixien/FuelFinder_ANDROID)): ogni mattina scarica i CSV dell'Osservaprezzi Carburanti del MIMIT, li normalizza e pubblica un unico `stations.json` su GitHub Pages.

Da metà ottobre 2026 il sito del MIMIT non risponde ai runner di GitHub Actions, quindi il download gira su un homelab (rete domestica, vedi sotto) e GitHub si limita a pubblicare.

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

## Pubblicazione dall'homelab

`deploy/publish.sh` (in un container Docker) scarica i CSV, genera `stations.json`, archivia i CSV grezzi in `deploy/archive/AAAA-MM-GG/` e, se la data dei prezzi è più recente di quella online, fa push del file sul branch `data`. Il branch contiene un solo commit sovrascritto ogni giorno: è l'unica eccezione alla regola "niente dati committati" ed esiste solo come canale verso Pages. Il workflow `Publish stations.json` su `main` (09:15 e 12:30 UTC) ripubblica quel branch su Pages e fallisce, mandando un'email, se i prezzi online sono più vecchi di 48 ore dalla fine del giorno di riferimento.

Installazione su un server con Docker (comandi da adattare al percorso scelto):

```sh
sudo git clone https://github.com/Leixien/FuelFinder_DATA.git /opt/FuelFinder_DATA
cd /opt/FuelFinder_DATA/deploy
sudo ssh-keygen -t ed25519 -N "" -C "fuel-data homelab" -f deploy_key
# Aggiungi deploy_key.pub su GitHub: Settings → Deploy keys → Add deploy key, con "Allow write access".
sudo docker compose build
sudo DRY_RUN=1 docker compose run --rm publish   # prova: scarica e verifica, senza push
sudo docker compose run --rm publish             # prima pubblicazione: crea il branch data
sudo cp fuel-data.service fuel-data.timer /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now fuel-data.timer
systemctl list-timers fuel-data.timer            # prossima esecuzione
journalctl -u fuel-data.service                  # log
```

Dopo un `git pull` serve `docker compose build` per aggiornare l'immagine.

Codici d'uscita di `publish.sh`: `0` pubblicato, `75` niente di nuovo (il MIMIT non ha ancora aggiornato o la data è già online; per systemd è un successo grazie a `SuccessExitStatus=75`), qualsiasi altro codice è un errore. Homelab Notify li usa per distinguere "pubblicato", "niente di nuovo" e "fallito". Dopo l'aggiornamento serve `sudo cp fuel-data.service /etc/systemd/system/ && sudo systemctl daemon-reload`.

## Fonte dati

Fonte dati: **MIMIT – Osservaprezzi Carburanti** ([dataset](https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti)), licenza [IODL 2.0](https://www.dati.gov.it/iodl/2.0/). Il file pubblicato riporta l'attribuzione nel campo `source`.

## Licenza

Codice: [Apache 2.0](LICENSE).
