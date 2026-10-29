# The census's inputs

The clinical reread's two tables, copied byte for byte from bordercall pull request 26 (branch
claude/project-thread-adplcz, commit e3bcb2c, 29 October 2026, where they were last changed by
commit 401aaee at 12:42 UTC), so that the census record beside them names files this repository
holds whatever that pull request does later. Once the reread's branch is on main, the same files
are research_notes/paper-tables/data/series.csv and research_notes/paper-tables/tools/vocabulary.csv,
and a later run may name those instead; the record's `inputs` carry each file's sha256.

- `series.csv`: one row per printed value of the 39 other papers' tables (4,357 rows): paper, cohort,
  technique, whether the paper measured the value itself or quoted it, the measure's key, the level,
  sex, group, side, mean, sd, n, where the sd and n came from, units, how it stands to Panjabi's
  definition, the definition as the paper gives it, and the table and page.
- `vocabulary.csv`: the 106 keys of the reread (key, kind, units, whether Panjabi printed it, its
  mnemonic, its definition).
