# The morphometry session's own files, 2026-10-30

Source: the thread "Run morphometry on gold tier 3 masks" in the claude.ai project symphony_5,
cloud session https://claude.ai/code/session_01Pn5qEJbGG6tvpFq8R3s7FA, on the owner's word of
20:24 UTC: "please write the first prompt for the new account then make sure all files local to
this account and session are pushed". The container is reclaimed when the session ends, so this
folder keeps what it held that no repository did. It is a record. Nothing here is part of the
engine or its tests, and the scripts are scratch work that may no longer match the code. The
owner's first rule (never run archived code) applies to them. The handoff that says what to do
next is research_notes/morphometry/handoff.md, entry of 20:30 UTC, and SchwingNet's
docs/checkpoints/2026-10-30-morphometry-lines/HANDOFF.md.

## What is here

A file counts as the session's own when its bytes are in no object database of the four
repositories the session held: bordercall, SchwingNet, spine-program and symphony-template. The
session hashed every file of its scratchpad as git hashes a blob to find them. Copies of
repository files are not listed, since their bytes are in the repositories.

- scratchpad/: the session's own text files of up to 2 MB, under their scratchpad paths. There
  are 1,725 of them.
  - review-*/ and skeptic-*/ are the review agents' working copies. Only the files an agent wrote
    or changed are here.
  - wall/ is the posterior wall's slope study: its runs, its candidates and the judges.
  - fix*/ are the fix rounds, and mut/, mutx/ and fix-mutants/ the mutant runs. mutx/run_mutants.py
    is the harness; it needs SRC set and new mutants for the code of PR 49.
  - proto*/ are the prototype sagittal readers.
  - dry2/ to dry4/ are dry runs of the morphometry job.
  - probes/ holds the probes behind the research note's numbers.
  - edits/ and edit_*.py are the scripts that edited files.
  - refute*/ are the skeptics' attempts to refute findings.
  - proj-*/ and lines-try/ are the projection work's drafts and probes.
  - merge/ and merge2/ are SchwingNet's trial merges and merge2_gate_check.sh and sn-check.log
    its check runs; bc-main/ and sn-check/ were git worktrees of the two repositories, whose
    link files alone were the session's own and are left out.
  - The *-before-*.py files are copies of files before a change.
  - The *.log files are suite and probe runs.
- tasks/: the logs of the session's 160 background commands.
- workflows/: the six review and design workflows' scripts and run records.
- project-files/morphometry/verse-per-level-2026-10-30.png: the plot of the verse run's
  per-level median anterior and posterior body heights and their ratio, from C3 to L5, with
  VerSe's 374 masks and TotalSegmentator's 159 subjects shown apart. It was made from the report
  of job 40877151, which ran the old engine, 16f7b40. It was kept in the Claude project's files,
  which another account cannot open.
- environments/: the packages of the session's four Python environments.
  - venv: Python 3.13, the plain one the 94 tests ran in.
  - fxr-venv: Python 3.13, with FleXray 1.0.2, nanoDRR 0.1.5 and torch 2.15.0+cpu. This is the
    environment Live and tests/flexray_record.py need.
  - The two review-runtime ones: Python 3.11, with scipy 1.13.1 and 1.15.3.
- MANIFEST.tsv: every one of the session's 12,244 own files, with its bytes, its sha256 and
  whether it was pushed, or why not.
- scratch-commits/: the five commits of the session's scratch clones of SchwingNet that no remote
  held, kept as text since the clones' object databases are binary and were not pushed. Each
  clone forked from e95e5fa, the pin at bordercall ee495d5, now on SchwingNet's branch
  claude/project-thread-gv744i.
  - sn2-2b6e307.patch: the gate fixes as the review of 18:03 UTC read them, which SchwingNet's
    1c5e76a replaced.
  - merge2-f19c420.patch and merge-d5b3fb6.patch: the working tree's fixes as two trial merges
    took them, at 19:02 and 18:56 UTC.
  - merge2-2617786.remerge.diff and merge-a1264cc.remerge.diff: those trial merges with
    SchwingNet's main at 69371c2, as `git show --remerge-diff` prints them, which is each
    merge's conflict resolution alone; the rest of each merge is main's own history.
  `git am` applies a .patch onto e95e5fa. Their contents are superseded: the work is in
  SchwingNet's 1c5e76a and df667a1.

## What was not pushed, and why

- 10,010 files (481 MB) of virtual environments and third-party source trees. These are the
  review environments and bash 4.2's source and build, which a skeptic compiled to run the grid
  scripts under the grid's bash. The package lists in environments/ rebuild the environments.
- 257 binary data files (513 MB). Most are the pickled phantom caches the wall study read
  (rebuilt by morphometry/tests/probe_wall.py). The rest are numpy arrays, phantom NIfTI volumes,
  DICOM test files and archives.
- 17 binaries (5 MB): CentOS 7's bash, gawk, grep and sed and their libraries, for the same test.
- 233 files (2 MB) under dl/: the sources of flexray 1.0.2, nanodrr 0.1.5 and 0.1.7 and roma
  1.8.0, read for their camera code. `pip download` brings them back.
- The session's transcript, the subagents' transcripts and the tool results the session saved.
  The repositories keep transcripts and tool output out (SchwingNet's .claude/rules/research.md),
  and a transcript can carry what no file should.

## Before PR 49 merges

This folder rides on PR 49's branch in commits that change nothing outside it (b1103d0,
2a80945, 6dc87bb and the one that wrote this line). Delete the folder in one more commit
before the merge if main should not carry it; the owner decides.
