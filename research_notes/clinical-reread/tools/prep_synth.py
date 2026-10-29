"""Split the checked records into the topic extracts the synthesis reads."""

import json
import re
import sys
from pathlib import Path

notes = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
JUNCTION = re.compile(r"\b(C1|C2|C3|C7|T1|T11|T12|T13|L1|L5|L6|S1|S2)\b|junction|transition|sacral|lumbari|rib", re.I)

records = []
for path in sorted(notes.glob("*.json")):
    record = json.loads(path.read_text())
    record["id"] = path.stem
    records.append(record)

def head(r):
    return {k: r.get(k) for k in ("id", "citation", "population", "modality", "levels_covered")}

topics = {
    "papers": [dict(head(r), gaps=r.get("gaps")) for r in records],
    "anomalies": [dict(head(r), anomalies=r.get("anomalies"),
                       junction_details=[d for d in r.get("level_details", []) if JUNCTION.search(d.get("level", "") + " " + d.get("detail", ""))])
                  for r in records],
    "measures": [dict(head(r), measures=r.get("measures")) for r in records],
    "errors": [dict(head(r), errors=r.get("errors"),
                    measure_error=[{k: m.get(k) for k in ("name", "projection", "error", "covariates", "page")} for m in r.get("measures", [])])
               for r in records],
    "atlas": [dict(head(r), level_details=r.get("level_details"), pearls_pitfalls=r.get("pearls_pitfalls"),
                   instructions=r.get("instructions"), bordercall=r.get("bordercall")) for r in records],
}
for name, rows in topics.items():
    (out / (name + ".json")).write_text(json.dumps(rows, indent=1, ensure_ascii=True) + "\n")
    print(name, len(rows), (out / (name + ".json")).stat().st_size)
