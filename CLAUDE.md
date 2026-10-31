# bordercall

Confidential and private: naming vertebral levels from the shape of the bone with no count from C2 (the exact Bayes rule over Panjabi's tables, SchwingCheck), the morphometry engine, the correlation prior and the auto-anatomist. Nothing here goes public; the landmark and phantom direction (#51) is not in the provisional and stays private.

## Read first

- README.md (the rule and the repository as it stands) and TODO.md (the owner's order of work).
- The X-ray plan: issue #67 (umbrella) and its stages #68 to #75, with six owner decisions and their defaults; the phantom plan #51 to #58.
- research_notes/ for each study's record; records/ for fitted results (records/prior-2026-10-31 is the current correlation prior).
- SchwingNet runs this code on the grid from a pinned copy under SchwingNet's grid/bordercall/ (its VENDORED record); a change here reaches the grid only when that copy is moved.

## Continuing locally

Since 2026-10-31 the owner runs this project from a local Claude Code session instead of claude.ai project threads. Start every local session the same way:

1. Clone the four private repositories side by side and keep them current: `git clone git@github.com:OpenSpineConsortium/<name>.git` for SchwingNet, bordercall, symphony-template and spine-program, then `git fetch origin` before any work.
2. Read SchwingNet's docs/checkpoints/2026-10-31-final/README.md (the latest handoff: every thread's state, open pull requests, grid jobs and next steps) and the project memory beside it in memory/MEMORY.md.
3. Work one piece at a time on its own branch, open a pull request, and merge it yourself once CI is green: no merge waits for the owner (his word of 2026-10-31 03:45 UTC). Test what you change before pushing.
4. Grid work: ssh to the grid and run `cd ~/SchwingNet && git pull && bash grid/gate.sh <word>`, or dispatch symphony-template's grid-accounts.yml (action=job, job=schwingnet-<word>); the size rule holds; the login node only submits jobs.
5. Never public, sign nothing about the provisional, no usage credits, never run archived code, and be frugal with tokens.

## Conventions

- One branch and one pull request per change; run the tests a change touches (`python -m pytest tests/<module>`; the auto-anatomist needs requirements-autoanatomist.txt, SchwingCheck requirements-schwingcheck.txt) before pushing.
- Every number names the file it came from; a frozen PREREG is never edited, a departure goes in DEVIATIONS.md.
- Never run code under archive/; it is kept as the record.
- The sacrum is one full union mask on all gold tier data; no separate S1 class. CTSpinoPelvic1K's labels are not a trusted reference.
