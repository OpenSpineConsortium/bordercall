"""Build the run monitor page from the study's PROGRESS.txt lines as the gate's status shows them.

    python3 build.py --state state.json [--progress progress.txt] [--phase P --label L --note N]
                     [--jobs prepare=ID,array=ID,merge=ID] --out index.html

state.json keeps what earlier reads gave (the trace of units done), so each read adds a point.
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = re.compile(r"drr-gap at (?P<at>\S+ \S+) UTC: stage (?P<stage>\S+)(?:; units (?P<done>\d+) of (?P<total>\d+) done,"
                  r" (?P<running>\d+) running, (?P<failed>\d+) failed)?")
STAGE = re.compile(r"stage (?P<name>[a-z]+): (?:(?P<state>[a-z]+) in (?P<seconds>\d+) s|running since (?P<since>\S+) UTC \((?P<min>\d+) min\))(?:, (?P<detail>.*))?")
READING = re.compile(r"reading (?P<key>\S+): (?:not read, (?P<invalid>.*)|(?P<done>\d+) of (?P<total>\d+) \((?P<kinds>.*)\))")
KIND = re.compile(r"(?P<kind>\S+) (?P<done>\d+) of (?P<total>\d+)")
TASK = re.compile(r"task (?P<task>\d+) \((?P<job>[^,]+), (?P<host>[^,]+), (?P<gpu>[^)]+)\): (?P<state>[a-z]+), (?P<done>\d+) done,"
                  r" (?P<running>\d+) running, (?P<failed>\d+) failed, beat (?P<beat>\S+) UTC")
RATE = re.compile(r"rate: (?P<per>\S+) units a minute over the last 10 minutes(?:, about (?P<left>\d+) min left)?")
TIMELINE = re.compile(r"timeline of units done: (?P<steps>.*)")
LOG = re.compile(r"log: (?P<at>\d\d:\d\d:\d\d) (?P<text>.*)")
PREPARE_STAGES = ("render", "plan", "images", "features", "heads")


def parse(lines):
    found = {"stages": {}, "readings": [], "tasks": [], "log": []}
    for raw in lines:
        line = raw.strip()
        for name, pattern in (("head", HEAD), ("stage", STAGE), ("reading", READING), ("task", TASK), ("rate", RATE), ("timeline", TIMELINE), ("log", LOG)):
            m = pattern.fullmatch(line)
            if not m:
                continue
            g = m.groupdict()
            if name == "stage":
                found["stages"][g["name"]] = g
            elif name == "reading":
                g["kinds"] = [k.groupdict() for k in KIND.finditer(g["kinds"] or "")]
                found["readings"].append(g)
            elif name == "task":
                found["tasks"].append(g)
            elif name == "log":
                found["log"].append(g)
            else:
                found[name] = g
            break
    return found


def stage_state(stages, name):
    entry = stages.get(name)
    if not entry:
        return "waiting", ""
    if entry.get("since"):
        return "running", f"since {entry['since']} UTC, {entry['min']} min" + (f"; {entry['detail']}" if entry.get("detail") else "")
    return entry["state"], f"{entry['seconds']} s" + (f"; {entry['detail']}" if entry.get("detail") else "")


def group_state(states):
    if any(s == "failed" for s in states):
        return "failed"
    if states and all(s in ("done", "finished") for s in states):
        return "done"
    if any(s in ("running", "watching", "done", "finished") for s in states):
        return "running"
    return "waiting"


def pipeline(found, jobs, phase):
    stages = found["stages"]
    prepare = []
    for name in PREPARE_STAGES:
        state, detail = stage_state(stages, name)
        prepare.append({"name": name, "state": state, "detail": detail})
    head, tasks = found.get("head") or {}, found["tasks"]
    shard = [{"name": f"task {t['task']} on {t['host']}", "state": t["state"],
              "detail": f"{t['done']} done, {t['running']} running, {t['failed']} failed; beat {t['beat']} UTC"} for t in tasks]
    if head.get("total"):
        done, total = int(head["done"]), int(head["total"])
        shard_state = "failed" if int(head.get("failed") or 0) else "done" if done == total else "running" if tasks else "waiting"
        shard_name = f"Shard tasks: {done} of {total} units"
    else:
        shard_state, shard_name = ("queued" if phase == "queued" else "waiting"), "Shard tasks: 16, each on the first GPU that frees"
    merge = []
    for name in ("figures", "summary"):
        state, detail = stage_state(stages, name)
        merge.append({"name": name, "state": state, "detail": detail})
    prepare_state = group_state([p["state"] for p in prepare])
    if phase == "queued" and prepare_state == "waiting":
        prepare_state = "queued"
    return [
        {"job": f"prepare {jobs.get('prepare', '')}".strip(), "name": "Prepare: render to heads", "state": prepare_state, "items": prepare},
        {"job": f"array {jobs.get('array', '')}".strip(), "name": shard_name, "state": shard_state, "items": shard},
        {"job": f"merge {jobs.get('merge', '')}".strip(), "name": "Merge: results, figures, summary", "state": group_state([m["state"] for m in merge]), "items": merge},
    ]


def minutes_left(found):
    rate = found.get("rate") or {}
    return rate.get("left")


def build(args):
    state = json.loads(Path(args.state).read_text()) if Path(args.state).is_file() else {"history": []}
    lines = Path(args.progress).read_text().splitlines() if args.progress else state.get("lines", [])
    lines = [line.strip() for line in lines if line.strip()]
    found = parse(lines)
    jobs = dict(state.get("jobs", {}))
    for part in filter(None, (args.jobs or "").split(",")):
        key, value = part.split("=", 1)
        jobs[key] = value
    phase = args.phase or state.get("phase", "waiting")
    head = found.get("head") or {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    history = state.get("history", [])
    if head.get("total") and args.progress:
        at = datetime.strptime(head["at"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        first = state.get("first_at") or at.isoformat()
        state["first_at"] = first
        minute = (at - datetime.fromisoformat(first)).total_seconds() / 60
        if not history or history[-1]["minute"] != minute:
            history.append({"minute": round(minute, 1), "done": int(head["done"])})
    done, total = (int(head["done"]), int(head["total"])) if head.get("total") else (0, 0)
    alive = sum(1 for t in found["tasks"] if t["state"] in ("running", "watching"))
    figures = [
        {"value": f"{done} / {total}" if total else "not listed yet", "label": "units done of the list prepare wrote"},
        {"value": str(alive) if found["tasks"] else "none yet", "label": "array tasks beating now"},
        {"value": f"about {minutes_left(found)} min" if minutes_left(found) else "not known yet", "label": "time left at the last rate"},
        {"value": head.get("failed") or "0", "label": "units failed (three in a row stop a task)"},
    ]
    out = {
        "subtitle": "FleXray and FluXray DRRs against real fluoroscopy and film: prepare, an array of 16 shard tasks and a merge, each on any GPU of the grid",
        "progress_at": (head["at"] + " UTC") if head.get("at") else state.get("progress_at"), "phase": phase, "phase_label": args.label or state.get("phase_label", phase), "updated": now,
        "note": args.note or state.get("note", ""), "jobs": jobs, "figures": figures,
        "pipeline": pipeline(found, jobs, phase), "total_units": total or None,
        "readings": [{"key": r["key"], "invalid": r.get("invalid"), "done": int(r["done"] or 0), "total": int(r["total"] or 0),
                      "kinds": [{"kind": k["kind"], "done": int(k["done"]), "total": int(k["total"])} for k in r["kinds"]]}
                     for r in found["readings"]],
        "log": found["log"],
        "tasks": [{**t, "done": int(t["done"]), "running": int(t["running"]), "failed": int(t["failed"])} for t in found["tasks"]],
        "history": history, "first_at": state.get("first_at"), "lines": lines,
        "footer": ("Read from the gate's status word, which prints the study's PROGRESS.txt through the grid's filter: counts and"
                   " stage names only, no result of the study and no file name. The page shows the run as it stood at the last read;"
                   " Claude reads it again during the run and republishes."),
    }
    Path(args.state).write_text(json.dumps(out, indent=1))
    html = (HERE / "template.html").read_text().replace("__STATE__", json.dumps(out).replace("</", "<\\/"))
    Path(args.out).write_text(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--progress")
    parser.add_argument("--phase")
    parser.add_argument("--label")
    parser.add_argument("--note")
    parser.add_argument("--jobs")
    parser.add_argument("--out", required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    main()
