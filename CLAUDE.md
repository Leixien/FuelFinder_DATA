# CLAUDE.md — fuel-data

Pipeline che produce `stations.json` dai CSV MIMIT. Leggi `CONTRACT.md` e `TODO.md` prima di lavorare e aggiorna `TODO.md` a fine sessione.

## Regole

1. **Questo repo possiede il contratto.** Ogni modifica a `stations.json` passa da `CONTRACT.md` e va riportata in `specificheTecniche.md` §3 di entrambi i client. Modifiche incompatibili incrementano `schema_version`.
2. **Solo libreria standard Python.** Niente pandas/requests: il volume (~90k righe) non li giustifica.
3. **Mai pubblicare dati peggiori di quelli già online:** in caso di dubbio lo script fallisce e GitHub Pages resta sull'ultima versione buona.
4. **Niente segreti**, niente dati committati (CSV e output sono in `.gitignore`).
5. **Attribuzione MIMIT (IODL 2.0)** sempre nel campo `source` e nel README.
6. Ogni regola di normalizzazione nuova nasce con un caso in `test_build_stations.py`.
7. Commit piccoli in inglese, `type(scope): subject`, senza trailer `Co-Authored-By` né riferimenti a Claude.
