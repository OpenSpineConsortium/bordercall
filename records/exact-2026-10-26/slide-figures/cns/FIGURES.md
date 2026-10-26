# The exact-identification slide figures, CNS (results only)

Built with `python run.py exact-slide-figures --json ../records/exact-2026-10-26/exact.json --outdir ../records/exact-2026-10-26/slide-figures`, which writes this set into its `cns/` folder.

- Run: `../records/exact-2026-10-26/exact.json`, sha256 b3438f9082cb732b15f0dfa97a722f48877fade5909d691cd8f7266891f754c7; scoring seed 97; 2000 columns; synth {"noise_mm": 1.0, "rho": 0.5, "scale_sd": 0.07}; 161 Gauss-Hermite nodes.
- The posterior panel scores the record's scoring columns again for the fields centred on T12; its share named exactly at each width equals the record's `by_centre` rate, checked before it draws; the column drawn is scoring column 1476, the one with the least summed distance of its rank from the median rank of the posterior at T12 over one, three and nine bodies.
- Reference table: `bordercall/reference/panjabi_full_spine.csv`, sha256 6b51079dbe60b6ec336a85f73c2c11a174fdc2abce4d5d398d405b814edc853c.
- Code: `bordercall/exact_slide_figures.py`, sha256 42537955b2b97b5a055fdb930185332b46f0d9c83161b8222435d3adca7dcab8.
- Code: `bordercall/exact_figures.py`, sha256 44e2676650cd246c94ab370c9813eb4173ec6ae0100cea40f31dc6b953e223ac.
- Code: `bordercall/exact.py`, sha256 022b73c36011dcd01368b06aaffabde983cf79754947ab92eb888e255948b260.
- Code: `bordercall/neighbour.py`, sha256 e527384fbfc0b367bda12433fe3f0f2f5cd7bcb9027ea8517d2177d7b0c537d1.
- Code: `bordercall/junction_figures.py`, sha256 aca7801c59e24b8a2db3600d7cfdc77291ff39ec9f3ef403988a65ece82ebf3f.
- Code: `bordercall/panjabi.py`, sha256 b1c68d1143cdf10d2180db2d9907020573c845d89b393a2401f4fab4e96b5f17.
- Code: `bordercall/covariance.py`, sha256 4a8105951e797787762aa97e724dfc3e054088b68814ad02a52e5a466322ccd9.
- Python 3.13.17, numpy 2.5.3, matplotlib 3.11.2; serif type Caladea where installed, embedded in the PDF.
- Each panel is drawn at the size the CNS slide gives it, in inches: exact_slide_view 2.1 x 4.85; exact_slide_measures 3.48 x 4.67; exact_slide_posterior 5.77 x 4.8; exact_slide_ceiling 6.9 x 4.7; exact_slide_claims 4.99 x 4.85; exact_slide_robust 6.77 x 3.66.

| Figure | Files | Caption |
|---|---|---|
| exact_slide_view | `exact_slide_view.caption.txt`, `exact_slide_view.csv`, `exact_slide_view.pdf`, `exact_slide_view.png` | A field of view: three consecutive vertebral bodies seen, the rest of the column unseen, and no C2 or sacrum to count from. Bodies drawn to Panjabi's mean upper end-plate width, C3 to L5, the tables' range. |
| exact_slide_measures | `exact_slide_measures.caption.txt`, `exact_slide_measures.csv`, `exact_slide_measures.pdf`, `exact_slide_measures.png` | The seven measures each body gives, schematic and not to scale: the AP plane shows the upper and lower end-plate widths and the canal width, the lateral plane the two end-plate depths, the canal depth and the posterior body height, which both planes show. |
| exact_slide_posterior | `exact_slide_posterior.caption.txt`, `exact_slide_posterior.csv`, `exact_slide_posterior.pdf`, `exact_slide_posterior.png` | Probability of each level for the middle body, every level equally likely before looking, then from one, three and nine bodies centred on T12, for the synthetic column nearest the median of 2,000 at all three widths. |
| exact_slide_ceiling | `exact_slide_ceiling.caption.txt`, `exact_slide_ceiling.csv`, `exact_slide_ceiling.pdf`, `exact_slide_ceiling.png` | Share of fields named exactly (solid) and named at 99% confidence (dashed), both planes, by consecutive bodies in view; crosses, a linear classifier fitted on other synthetic columns, scored on the first 1,000. 2,000 synthetic columns. |
| exact_slide_claims | `exact_slide_claims.caption.txt`, `exact_slide_claims.csv`, `exact_slide_claims.pdf`, `exact_slide_claims.png` | What a field says for certain about its middle body: at each border, the share of fields whose middle body lies within two levels of it that say which side at 99% confidence, by bodies in view, both planes. 2,000 synthetic columns. |
| exact_slide_robust | `exact_slide_robust.caption.txt`, `exact_slide_robust.csv`, `exact_slide_robust.pdf`, `exact_slide_robust.png` | When the anatomy table or the measurement error is wrong, three bodies, both planes: how often a name given at 99% confidence is right (A) and the share named (B), printed table and a corrected rule, on separate synthetic columns. Bars, two standard errors; dotted, 99 per cent. |
