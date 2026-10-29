# TODO — fuel-data

Legenda: `[ ]` da fare · `[~]` in corso · `[x]` fatto · `[!]` bloccato

## MVP
- [x] `build_stations.py`: download, separatore auto-rilevato, normalizzazione, mappatura carburanti, controlli di sanità
- [x] Test unitari (`test_build_stations.py`)
- [x] Workflow giornaliero con deploy su GitHub Pages
- [x] `CONTRACT.md` con le risposte alle richieste dei client (nullabilità, "Pompe Bianche", mappatura carburanti)
- [x] Output reale verificato con il decoder Swift dell'app iOS (21.495 impianti decodificati in 0,6 s su Mac)
- [ ] Creare il repo GitHub e abilitare Pages (source: GitHub Actions)
- [!] Il download dal MIMIT con lo User-Agent dello script riceve `Connection reset by peer` (dal Mac del maintainer, 2026-10-29); da verificare dai runner GitHub. Non aggirare il filtro: chiarire con il MIMIT o cercare un canale ufficiale di distribuzione.
- [ ] Aggiornare `DATA_URL` nei client con l'URL definitivo di Pages

## Dopo
- [ ] Classificare "F101" / "F-101" (~50 prezzi oggi scartati): capire di che prodotto si tratta
- [ ] Pubblicare una fixture ridotta ufficiale (≈ 30 impianti campani) accanto a `stations.json` per i test dei client
- [ ] GitHub disattiva i workflow schedulati dei repo pubblici dopo 60 giorni senza attività: prevedere un keepalive o un controllo periodico
- [ ] Archivio storico (backlog dei client: storico prezzi)
