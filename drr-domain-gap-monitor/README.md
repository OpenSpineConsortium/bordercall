# DRR comparison monitor tooling

Copied 2026-10-28 17:15 UTC from the scratchpad of the thread "Compare synthetic FluXray against real fluoroscopy" before an account change, so the next account can keep the monitor page going exactly as before.

- The private page: https://claude.ai/artifact/G7bBTwqwTYUtCP6di4W7Du (publish build.py's output to that url with the Artifact tool).
- refresh.sh TAG sends the status word once (grid-accounts.yml, job schwingnet-status), waits for its answer with wait_answer.sh, cuts the study's progress and sacct lines out of it and rebuilds index.html with build.py from template.html.
- The scripts name the old account's scratchpad path in their S= line: change it to a folder of the new session (copy these files there) before running.
- Confidential: SchwingNet research. Never copy to a public place.
