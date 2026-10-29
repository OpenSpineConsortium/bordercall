# Reviews of the paper-tables tools and data

Source: thread "Finish the clinical reread", project symphony_4, 2026-10-29. Confidential, like the rest of this
repository.

Two rounds of independent readers reviewed tools/series.py, tools/cross_naming.py, tools/results.py, the series and
the record they write, the results page and the notes that quote it. Each finder reported only defects it had
reproduced, and each finding was then given to refuters told to show it wrong.

- Round 1 (tools/code_review.js, then code_fix.js and code_fix_2.js): 37 findings held, 27 faults and 10 wording
  findings, each fixed and checked again by a reader of its own; 5 were refuted. They are fixed in the commits of
  2026-10-29 up to 401aaee, which remade data/series.csv (4,357 series).
- Round 2 (the record at 3aff843, five lenses: statistics, data rules, the page, the numbers other notes quote, and
  rules that silently do nothing): [round-2-findings.json](round-2-findings.json), each finding with its lens,
  scenario, impact, severity, the refuters' verdicts and a status. Two refuters judged each finding, one by
  reproducing it and one on its merits, with a third on a split; "unverified" means the refuters had not finished
  when the file was written. Quotes of a paper are cut to twelve words and no run of a paper's text is kept.

Of round 2, these were fixed in pull request 26 by hand, each checked against the page or the file it names: page 2
(Chen 2011's contrast is on p. 1819), page 3 (the two end-plate rows print the same numbers, the cervical most
probably the original, rather than "reprints"), prose-numbers 2, 3 and 4 (measures.md 3.5, HANDOFF.md and the
end-plate note's status line no longer say the angles are left out). The rest change data/series.csv or the
record and come in the next pull request, with the comparison rerun.
