# Review round 1 of the prior-art notes and the validation folder

Source: thread "Finish the clinical reread", project symphony_5, 2026-10-29 23:36 UTC to 2026-10-30, on the branch
of pull request 39 at 1e57300. Confidential, like the rest of this repository. Pushed at the owner's word of
2026-10-30 01:16 UTC ("PLEASE JUST PUSH ALL RESULTS NOW!") as the raw record, before any fix was applied to a note.

Two runs, both of independent readers who report only what they read at the source:

- [round-1-findings.json](round-1-findings.json): one reader a family note checked every claim it makes against the
  source it names (1,954 claims over the nine notes), and one reader reproduced the validation README's counts
  from its files and tools (84 statements). Each finding carries the note's claim, the source's own words cut to
  twelve words, a verdict (wrong, unsupported, imprecise), a severity and the replacement text, and then a
  refuter's verdict. At the time of this push only the vertebral-body note's refuter had finished (10 held, 1
  refuted); the other refuters, and the reader of the mapping audit against the papers' pages, stopped at the
  account's usage limit and were resumed. A finding marked "refuter not yet run" is a reader's claim only.
- [gaps-round-1.json](gaps-round-1.json): one searcher a family took up the searches the README's Gaps section says
  its reader's budget did not reach (Comp2Comp, automated body width and depth, Blomenkamp, Fujimori, MRSpineSeg,
  Spinal-AI2024, BUU-LSPINE's paper, EOS and Keops, and the papers read only in part), each returning new table
  rows and facts that complete existing rows, and a verifier read every row at its source. At this push the
  vertebral-body and pedicle searches are verified; the other five verifiers were resumed.

Nothing in the notes has changed yet. The next commits apply each held finding and each verified row to its note,
with the README table brought to the new counts, and record which findings were refuted.
