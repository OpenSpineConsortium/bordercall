# The one-body evaluation's figures

Built with `python -m schwingcheck.one_body figures --outdir records/one-body-2026-10-29/figures`.

- Record: `records/one-body-2026-10-29/one_body.json`, sha256 b36796daf74177e35f631ba5fefd447928e456dee1ae0d41c65c1524dd827603.
- Code: `schwingcheck/figures.py`, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576.
- Code: `schwingcheck/one_body.py`, sha256 e7a86f5278a283a324d4a498ab274b9aa60b27a37a784bd9780180c1b4534a29.
- Python 3.12.3, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| one_body_levels | `one_body_levels.caption.txt`, `one_body_levels.csv`, `one_body_levels.pdf`, `one_body_levels.png` | A lone body named from its own measures, synthetic typical columns, 500 fields a level, the chain's prior, size unknown: A, per cent named exactly; B, the mean size of the 99 per cent set; C, per cent named at 0.99. Lines, the measure sets. |
| one_body_buildup | `one_body_buildup.caption.txt`, `one_body_buildup.csv`, `one_body_buildup.pdf`, `one_body_buildup.png` | A lone body as the build-up study's measures are added in its order, synthetic columns, every body of 500 a type a field, the chain's prior, size unknown: A, per cent named exactly; B, per cent named at 0.99; C, per cent within one level. Lines, the three column types. |
| one_body_coarse | `one_body_coarse.caption.txt`, `one_body_coarse.csv`, `one_body_coarse.pdf`, `one_body_coarse.png` | Coarse claims a lone body decides at 0.99 either way, synthetic typical columns, the chain's prior, size unknown, 11,000 fields a point, as the build-up study's measures are added: A, per cent decided; B, per cent of those right, dotted at 99. Markers, the six claims. |
| one_body_size | `one_body_size.caption.txt`, `one_body_size.csv`, `one_body_size.pdf`, `one_body_size.png` | What knowing the patient's size gives a lone body, synthetic typical columns, the chain's prior, 11,000 fields a point: A, per cent named exactly; B, per cent named at 0.99; from size unknown through a known height to the size itself. Lines, the measure sets. |
