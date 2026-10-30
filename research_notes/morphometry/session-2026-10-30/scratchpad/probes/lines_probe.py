from morphoview.tests import test_projection as T
tmp, mask, lines, frames, rows = T.exported()
seen = {}
for r in rows:
    seen.setdefault((r["key"], r["part"]), []).append(r["level"])
for k, v in seen.items():
    print(k, v)
print(list(rows[0].keys()))
