# The fixed-k NUTS review's figures

Built with `python -m schwingcheck.fixed_k figures`.

- Record: `records/fixed-k-2026-10-29/fixed_k.json`, sha256 98437008c135960529064cf7a37c9053705c8d1a90e8b152bc91ded3fc332192.
- Record: `records/fixed-k-2026-10-29/known-seven.nc`, sha256 7669bd3a51e86bb2aa545753b9fddcc5d072710c8c8e250a9a8817389b8b8685.
- Code: `schwingcheck/figures.py`, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576.
- Code: `schwingcheck/fixed_k.py`, sha256 e26eea3419d8b2e2eeb1f3112f75b3da691f51cb5fcbf01de70040bf207aa852.
- Python 3.12.3, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| fixed_k_trace | `fixed_k_trace.caption.txt`, `fixed_k_trace.csv`, `fixed_k_trace.pdf`, `fixed_k_trace.png` | Log size of one synthetic field of three bodies, the seven SPINEPS measures, every level known: 4 chains of NUTS, A by draw and B as histograms beside the posterior in closed form, the panels az.plot_trace draws. |
| fixed_k_forest | `fixed_k_forest.caption.txt`, `fixed_k_forest.csv`, `fixed_k_forest.pdf`, `fixed_k_forest.png` | Log size of 8 synthetic three-body fields, every level known: NUTS's mean and 89 per cent interval, as az.plot_forest draws them, beside the closed form's; A the seven SPINEPS measures, B all 32. |
| fixed_k_mixing | `fixed_k_mixing.caption.txt`, `fixed_k_mixing.csv`, `fixed_k_mixing.pdf`, `fixed_k_mixing.png` | Each chain's share of draws at the exact top place on synthetic fields with two likely places, the place free: Metropolis-within-NUTS with PyMC's uniform and the proportional proposal, and the place summed out by pymc-extras and recovered; the bar is the exact posterior. |
| fixed_k_tail | `fixed_k_tail.caption.txt`, `fixed_k_tail.csv`, `fixed_k_tail.pdf`, `fixed_k_tail.png` | The naming model's estimate of each place over its exact posterior, on synthetic three-body fields with the seven measures: the median over runs and the interquartile range, on NUTS's draws, on independent draws from the exact posterior of the size, and on NUTS ten times as long. |
