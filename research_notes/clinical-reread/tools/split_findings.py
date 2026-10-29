"""Split the synthesis critics' findings by part, and add the priors verifier's to anomalies."""
import ast, collections, json, sys
journal, priors_out, out_dir = sys.argv[1:4]
by_part = collections.defaultdict(list)
labels = {}
for line in open(journal):
    e = json.loads(line)
    if e.get("type") == "started":
        labels[e["key"]] = e["label"]
    if e.get("type") != "result":
        continue
    r = e["result"]
    if isinstance(r, str):
        try:
            r = json.loads(r)
        except ValueError:
            r = ast.literal_eval(r)
    for f in r["findings"]:
        by_part[f["part"]].append(dict(f, critic=labels.get(e["key"], "")))
pv = json.load(open(priors_out))["result"]["priors"]
by_part["anomalies"] += [dict(part="anomalies", kind=f["verdict"], where="section " + f["section"], what=f["claim"],
                              fix=f["fix"], source=f["evidence"], critic="priors verifier")
                         for f in pv["findings"] if f["verdict"] != "holds"]
for part, fs in by_part.items():
    json.dump(fs, open("%s/%s.json" % (out_dir, part), "w"), indent=1)
    print(part, len(fs), dict(collections.Counter(f["kind"] for f in fs)))
