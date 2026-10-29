# The chain study's figures

Built with `python -m schwingcheck.chain_figures --outdir records/chain-2026-10-28/figures`.

- Record: `records/chain-2026-10-28/chain.json`, sha256 c7072f4d98bf011cdf8e586db228fb1555508a54d9f265a6b3933d71fa25c7d1.
- Record: `records/chain-2026-10-28/axis.json`, sha256 c7939956a85f09f98c2f70677d53e53840fbb362b38df8326e1680a036db6de0.
- Record: `records/chain-2026-10-28/speed.json`, sha256 bf01c14c6e86a830c13c2d4a89ab6520db8bd0b151f9381f4f59e57a4bc63ed4.
- Code: `schwingcheck/figures.py`, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576.
- Code: `schwingcheck/chain_figures.py`, sha256 7aeb7eecc282331d6fea7aefaac2ea58ab5b15e509cf7e90f6b74a2a8a24fc61.
- Code: `schwingcheck/chain_study.py`, sha256 5a837dfdb3a8ca32a05eb5942e58e1628aa89acb86fe9b95294a8d971505eb94.
- Python 3.12.3, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| chain_accuracy | `chain_accuracy.caption.txt`, `chain_accuracy.csv`, `chain_accuracy.pdf`, `chain_accuracy.png` | Naming the middle body of a field on synthetic columns of three types, 200 fields a point: per cent named exactly against the bodies in view, A to C with all 32 measures, D to F with the seven SPINEPS measures. Lines, the four rules on the same fields; each step misses a body with probability 0.167. |
| chain_answers | `chain_answers.caption.txt`, `chain_answers.csv`, `chain_answers.pdf`, `chain_answers.png` | The answers at posterior 0.99, all 32 measures, synthetic columns of three types, 200 fields a point: A to C, per cent of fields named at 0.99; D to F, per cent of those right, drawn where 50 or more were named, dotted at 99 per cent. Lines, the four rules on the same fields. |
| chain_data | `chain_data.caption.txt`, `chain_data.csv`, `chain_data.pdf`, `chain_data.png` | The chain's table re-estimated from P people, 5 bodies, synthetic columns: A to C, per cent named exactly; D to F, per cent right of those named at 0.99, where 50 or more were named; the seven and all 32, nominal or widened for a new person (predictive); thin lines, the table as printed on the same fields. |
| chain_speed | `chain_speed.caption.txt`, `chain_speed.csv`, `chain_speed.pdf`, `chain_speed.png` | Time to name the middle body of one synthetic typical field, single-threaded, each rule built beforehand: A, all 32 measures; B, the seven as a mask on that rule. Alone (lines, median of 30 calls) and per field in a batch of 128 (points, median of 5 calls); crosses, chain.path_logev, which builds its blocks in every call. |
