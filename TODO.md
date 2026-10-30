# TODO — fuel-data

Legenda: `[ ]` da fare · `[~]` in corso · `[x]` fatto · `[!]` bloccato

## MVP
- [x] `build_stations.py`: download, separatore auto-rilevato, normalizzazione, mappatura carburanti, controlli di sanità
- [x] Test unitari (`test_build_stations.py`)
- [x] Workflow giornaliero con deploy su GitHub Pages
- [x] `CONTRACT.md` con le risposte alle richieste dei client (nullabilità, "Pompe Bianche", mappatura carburanti)
- [x] Output reale verificato con il decoder Swift dell'app iOS (21.495 impianti decodificati in 0,6 s su Mac)
- [x] Creare il repo GitHub e abilitare Pages (source: GitHub Actions)
- [x] Download dal MIMIT sbloccato (via homelab): dal Mac del maintainer funziona (2026-10-30: 21.495 impianti, 92.070 prezzi, 17 s; il `Connection reset` del 29 era temporaneo); dai runner GitHub Actions va in timeout (riprovato il 2026-10-30, stesso esito). Il blocco è iniziato verso il 2026-10-16 (anche il mirror LucaDDDD/benzina-data, su Actions, fallisce da allora). Non aggirarlo: bozza di email al MIMIT pronta. Soluzione adottata: download dall'homelab del maintainer (`deploy/`), GitHub pubblica solo.
- [x] Installare `deploy/` sull'homelab e fare la prima pubblicazione (2026-10-30: branch `data` creato, Pages online con 21.495 impianti, timer systemd attivo)
- [ ] Inviare l'email al MIMIT e, in base alla risposta, valutare il ritorno al download da GitHub Actions
- [x] Rifiutare la pubblicazione se `prices_reference_date` non è più recente dell'ultima pubblicata (il MIMIT può ritardare)
- [x] Archiviare i CSV grezzi per giorno (base per lo storico prezzi), sull'homelab in `deploy/archive/`
- [x] Aggiornare `DATA_URL` nei client con l'URL definitivo di Pages (iOS già allineato; Android da fare quando parte)

## Dopo
- [ ] Classificare "F101" / "F-101" (~50 prezzi oggi scartati): capire di che prodotto si tratta
- [ ] Pubblicare una fixture ridotta ufficiale (≈ 30 impianti campani) accanto a `stations.json` per i test dei client
- [ ] GitHub disattiva i workflow schedulati dei repo pubblici dopo 60 giorni senza attività: prevedere un keepalive o un controllo periodico
- [ ] Archivio storico (backlog dei client: storico prezzi)
