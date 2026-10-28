# The build-up study's figures

Built with `python -m schwingcheck curve figures --record records/curve-2026-10-28/curve.nc --outdir records/curve-2026-10-28/figures`.

- Record: `records/curve-2026-10-28/curve.nc`, sha256 c4d0cc979da8454609c19a2c7337c7eed1723d0a654c02cbe8536fd0f5167672.
- Code: `schwingcheck/curve_report.py`, sha256 74e6145566f414027c9876f19bd692655578cabc10ae3034c9f7be70ab1686e6.
- Code: `schwingcheck/curve.py`, sha256 d2a36049dc5e5f4d3a1563e07e208d2b3d6e93fd302ea3f7868286c85d97b4e4.
- Python 3.13.17, numpy 2.5.4, matplotlib 3.11.2; serif type Liberation Serif, embedded in the PDF.
- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs beside them hold every number drawn.

| Figure | Files | Caption |
|---|---|---|
| curve_accuracy | `curve_accuracy.caption.txt`, `curve_accuracy.csv`, `curve_accuracy.pdf`, `curve_accuracy.png` | Naming a field as measures are added in the greedy order, typical synthetic columns: A, share named exactly; B, share named at posterior 0.99; C, share of those right, where 1,000 or more were named, dotted at 99 per cent. Crosses, the seven SPINEPS measures. By the bodies in view; 2,000 columns. |
| curve_speed | `curve_speed.caption.txt`, `curve_speed.csv`, `curve_speed.pdf`, `curve_speed.png` | Time to name one field, one thread, as measures are added: A, rule.py on the trapezoid's nodes, one field alone (median of 30 calls), by bodies in view; B, three bodies, each engine with its table built once, alone (lines) and per field in a batch of 128 (points, median of 5 calls). |
| curve_data | `curve_data.caption.txt`, `curve_data.csv`, `curve_data.pdf`, `curve_data.png` | The rule's table re-estimated from P people, three bodies, on the same typical columns: A, share named exactly; B, share right of those named at 0.99, dotted at 99 per cent; the seven and all 32, the estimate as it is (nominal) or widened for a new person (predictive); thin lines, the table as printed on those columns. |
