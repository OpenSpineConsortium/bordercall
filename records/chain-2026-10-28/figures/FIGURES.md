# The chain study's figures

Built with `python -m schwingcheck.chain_figures --outdir records/chain-2026-10-28/figures`.

- Record: `records/chain-2026-10-28/chain.json`, sha256 19d51cef924e9b7b1bb9b9cfade171023764623adaf91945e25af3191224c374.
- Record: `records/chain-2026-10-28/axis.json`, sha256 63e4eb17baa70f8bac9cbcb9d979fc991f431e1ea50ca8b597e3d6c91e18943f.
- Record: `records/chain-2026-10-28/speed.json`, sha256 d5651a8eaa3714da4439be526efa61ea5b40fa9687f64c19d251d4b31dc20f2e.
- Code: `schwingcheck/figures.py`, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576.
- Code: `schwingcheck/chain_figures.py`, sha256 97a8f7f6334b8f4325da486cecc98c9c71c4e14a687133221d44899d82a73568.
- Code: `schwingcheck/chain_study.py`, sha256 257ea2c4569f13c1834118c2a3b67c20402b7474f636039f6997a80d7fd80a05.
- Python 3.12.3, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| chain_accuracy | `chain_accuracy.caption.txt`, `chain_accuracy.csv`, `chain_accuracy.pdf`, `chain_accuracy.png` | Naming the middle body of a field on synthetic columns of three types, 200 fields a point: per cent named exactly against the bodies in view, A to C with all 32 measures, D to F with the seven SPINEPS measures. Lines, the four rules on the same fields; each step misses a body with probability 0.167. |
| chain_answers | `chain_answers.caption.txt`, `chain_answers.csv`, `chain_answers.pdf`, `chain_answers.png` | The answers at posterior 0.99, all 32 measures, synthetic columns of three types, 200 fields a point: A to C, per cent of fields named at 0.99; D to F, per cent of those right, drawn where 50 or more were named, dotted at 99 per cent. Lines, the four rules on the same fields. |
| chain_data | `chain_data.caption.txt`, `chain_data.csv`, `chain_data.pdf`, `chain_data.png` | The chain's table re-estimated from P people, 5 bodies, synthetic columns: A to C, per cent named exactly; D to F, per cent right of those named at 0.99, where 50 or more were named; the seven and all 32, nominal or widened for a new person (predictive); thin lines, the table as printed on the same fields. |
| chain_speed | `chain_speed.caption.txt`, `chain_speed.csv`, `chain_speed.pdf`, `chain_speed.png` | Time to name the middle body of one synthetic typical field, single-threaded, each rule built beforehand: A, all 32 measures; B, the seven, a rule cut to them. Alone (lines, median of 30 calls) and per field in a batch of 128 (points, median of 5 calls); crosses, chain.path_logev, which builds its blocks in every call. |
