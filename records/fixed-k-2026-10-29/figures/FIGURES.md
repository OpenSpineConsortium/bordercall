# The fixed-k NUTS review's figures

Built with `python -m schwingcheck.fixed_k figures`.

- Record: `records/fixed-k-2026-10-29/fixed_k.json`, sha256 8d88b790d6abda0ece0d6a73783867f0fc78ede6dc53526b1ceb42e078719e79.
- Record: `records/fixed-k-2026-10-29/known-seven.nc`, sha256 02c5b82c31cb0d7a0735cd2ff9ce3e73ac3166cdd619bcd6f16b461290413cff.
- Code: `schwingcheck/figures.py`, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576.
- Code: `schwingcheck/fixed_k.py`, sha256 8bc2d8f376115151d0ebc5bf6f4d154baf028cc63f94c5f923430473558c7102.
- Python 3.12.3, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| fixed_k_trace | `fixed_k_trace.caption.txt`, `fixed_k_trace.csv`, `fixed_k_trace.pdf`, `fixed_k_trace.png` | Log size of one synthetic field of three bodies, the seven SPINEPS measures, every level known: 4 chains of NUTS, A by draw and B as histograms beside the posterior in closed form, what az.plot_trace shows, drawn in the house format. |
| fixed_k_forest | `fixed_k_forest.caption.txt`, `fixed_k_forest.csv`, `fixed_k_forest.pdf`, `fixed_k_forest.png` | Log size of 8 synthetic three-body fields, every level known: NUTS's mean and 89 per cent interval, what az.plot_forest shows, drawn in the house format beside the closed form's; A the seven SPINEPS measures, B all 32. |
| fixed_k_mixing | `fixed_k_mixing.caption.txt`, `fixed_k_mixing.csv`, `fixed_k_mixing.pdf`, `fixed_k_mixing.png` | Each chain's share of draws at the exact top place on synthetic fields with two likely places, the place free: Metropolis-within-NUTS with PyMC's uniform and the proportional proposal, and the place summed out by pymc-extras and recovered; the bar is the exact posterior. |
| fixed_k_tail | `fixed_k_tail.caption.txt`, `fixed_k_tail.csv`, `fixed_k_tail.pdf`, `fixed_k_tail.png` | The naming model's estimate of each place over its exact posterior, on synthetic three-body fields with the seven measures: the median over runs and the interquartile range, on NUTS's draws, on independent draws from the exact posterior of the size, and on NUTS ten times as long. |
