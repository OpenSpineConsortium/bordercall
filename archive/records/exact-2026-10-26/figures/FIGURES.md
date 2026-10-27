# The exact-identification figures

Built with `python run.py exact-figures --json ../records/exact-2026-10-26/exact.json --outdir ../records/exact-2026-10-26/figures`.

- Run: `../records/exact-2026-10-26/exact.json`, sha256 b3438f9082cb732b15f0dfa97a722f48877fade5909d691cd8f7266891f754c7; scoring seed 97; 2000 columns; synth {"noise_mm": 1.0, "rho": 0.5, "scale_sd": 0.07}; 161 Gauss-Hermite nodes.
- Reference table: `bordercall/reference/panjabi_full_spine.csv`, sha256 6b51079dbe60b6ec336a85f73c2c11a174fdc2abce4d5d398d405b814edc853c.
- Code: `bordercall/exact_figures.py`, sha256 44e2676650cd246c94ab370c9813eb4173ec6ae0100cea40f31dc6b953e223ac.
- Code: `bordercall/exact.py`, sha256 022b73c36011dcd01368b06aaffabde983cf79754947ab92eb888e255948b260.
- Code: `bordercall/identify_figures.py`, sha256 31ea50ee70ff4b38ea6e6faf9744a14637989eb644ef730da436e99039e69a8e.
- Code: `bordercall/neighbour.py`, sha256 e527384fbfc0b367bda12433fe3f0f2f5cd7bcb9027ea8517d2177d7b0c537d1.
- Code: `bordercall/junction_figures.py`, sha256 aca7801c59e24b8a2db3600d7cfdc77291ff39ec9f3ef403988a65ece82ebf3f.
- Code: `bordercall/panjabi.py`, sha256 b1c68d1143cdf10d2180db2d9907020573c845d89b393a2401f4fab4e96b5f17.
- Code: `bordercall/covariance.py`, sha256 4a8105951e797787762aa97e724dfc3e054088b68814ad02a52e5a466322ccd9.
- Python 3.13.17, numpy 2.5.3, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| exact_ceiling | `exact_ceiling.caption.txt`, `exact_ceiling.csv`, `exact_ceiling.pdf`, `exact_ceiling.png` | Naming a run of consecutive bodies. A, share named exactly by the generator's Bayes rule, by plane; crosses, the earlier linear classifier, both planes, first 1,000 columns. B, share named at posterior 0.99 and 0.999, both planes. C, points by which approximations and rules fitted on 5,000 columns fall short of it, bars two standard errors. 2000 synthetic columns. |
| exact_calibration | `exact_calibration.caption.txt`, `exact_calibration.csv`, `exact_calibration.pdf`, `exact_calibration.png` | The posterior is the probability of being right. A, error predicted by the posterior against error counted, by posterior bin, on fresh draws; diagonal, exact agreement; a bin with no error drawn at 1e-4. B, share named at posterior 0.99 by true centre level, both planes: a rate given the truth, measured, not guaranteed. 2000 synthetic columns. |
| exact_claims | `exact_claims.caption.txt`, `exact_claims.csv`, `exact_claims.pdf`, `exact_claims.png` | What a field says for certain about its middle body: at each border, the share of fields whose middle body lies within two levels of it for which the rule says above or below at probability 0.99, both planes, by the bodies in view. Wrong claims and the precision near each border are in the CSV. 2000 synthetic columns. |
| exact_measures | `exact_measures.caption.txt`, `exact_measures.csv`, `exact_measures.pdf`, `exact_measures.png` | Which measure makes claims at which border, one body (A) and three (B): of the fields whose middle body lies within two levels of the border, the share given a claim at probability 0.99 by that measure alone, the best pair and all seven, as a square of proportional area. Wrong claims are counted in the CSV. |
| exact_subsets | `exact_subsets.caption.txt`, `exact_subsets.csv`, `exact_subsets.pdf`, `exact_subsets.png` | How many measures naming needs: the share named exactly by the best subset of each size of the seven SPINEPS measures, every one of the 127 subsets scored on the same fields, by the number of bodies in view; the best single measure is named in the CSV. 2000 synthetic columns. |
| exact_interval | `exact_interval.caption.txt`, `exact_interval.csv`, `exact_interval.pdf`, `exact_interval.png` | The narrowest claim of its kind: the median number of consecutive levels in the shortest run that holds 99 per cent of the middle body's posterior, by its true level and the number of bodies in view, both planes. A width of one is the name itself. 2000 synthetic columns. |
| exact_robust | `exact_robust.caption.txt`, `exact_robust.csv`, `exact_robust.pdf`, `exact_robust.png` | When the generator is not the truth, three bodies, both planes, three rules, thirteen worlds: precision of the name at 0.99 (A), of border claims within two levels of the border (B), share named (C). Bars, two standard errors. Dotted, 99 per cent: promised for A under the generator; for B, a group picked by the truth, a reference. |
| exact_robust_widths | `exact_robust_widths.caption.txt`, `exact_robust_widths.csv`, `exact_robust_widths.pdf`, `exact_robust_widths.png` | The rule built on a table re-estimated from twelve spines, forty such tables pooled, by the bodies in view: precision of the name given at 0.99 (A), of border claims within two levels of the border (B), and share named (C), for three rules. Bars, two standard errors clustered by table. |
