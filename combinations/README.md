# combinations: what a combination variable adds to naming

Confidential with the rest of this repository: nothing here goes to a public place before the provisional is filed.

The owner's queue of 27 October 2026, 09:44 UTC, item 6, second line: "evaluate for the power of combination variables native to pymc". A combination variable is a quantity made from the measures: a ratio such as end-plate width over depth, canal over body, or height over width; a product such as a body's size; or a ratio between neighbours. In PyMC it is written with `pm.Deterministic`, a named function of the model's variables that adds no term to the joint density, or it is given a likelihood of its own and observed.

Every number here comes from synthetic columns drawn from Panjabi's tables (400 typical columns at the archive's score seed, every window of each width). Nothing here is a patient.

## The answer

A combination variable cannot make the exact rule name a body better. On these columns no combination did. Combinations earn their place when the scale is unknown or wrong, and there the rule's own scale-free form already uses all of them at once.

1. **By construction.** A combination is a function of the measures, so a rule that sees it and the measures sees no more than the measures alone (the data processing inequality). The exact rule is the Bayes rule on the measures ([archive/bordercall/exact.py](../archive/bordercall/exact.py)), so no combination can raise its accuracy under the generator. A `pm.Deterministic` changes no density at all: the compiled log density of the rule written in PyMC is the same to the last bit with and without three combinations (the aspect, the canal to body ratio and a body-size product). [pymc_check.py](pymc_check.py) shows this, and [tests/test_study.py](tests/test_study.py) holds it.
2. **Alone, every family loses.** A rule that sees only some combinations, and not the measures, loses what they leave out. The exact rate on the nominal world (the generator is the truth), with 22 places, so chance is 0.05 for one body:

   | Rule | n = 1 | n = 3 | n = 5 | n = 9 |
   | --- | --- | --- | --- | --- |
   | exact rule, raw measures | 0.478 | 0.735 | 0.861 | 0.962 |
   | raw measures, log-normal approximation (the archive's formula rule) | 0.472 | 0.720 | 0.845 | 0.956 |
   | exact rule, scale-free (every ratio at once) | 0.396 | 0.698 | 0.841 | 0.959 |
   | every ratio, log-normal approximation | 0.384 | 0.683 | 0.827 | 0.956 |
   | every ratio within a body | 0.384 | 0.636 | 0.768 | 0.910 |
   | each measure over the body above | | 0.413 | 0.714 | 0.930 |
   | body size, EPWu x EPDu x VBHp | 0.213 | 0.324 | 0.417 | 0.509 |
   | canal to body, SCW / EPWu and SCD / EPDu | 0.202 | 0.374 | 0.493 | 0.662 |
   | height to width, VBHp / EPWu | 0.093 | 0.121 | 0.154 | 0.239 |
   | aspect, EPWu / EPDu | 0.092 | 0.171 | 0.249 | 0.459 |

   The cluster standard error of the exact rule's rate is 0.006 at n = 1 and 0.005 at n = 9. At one body, its size alone names 0.21 of the fields, its ratios alone 0.38, and the measures together 0.48. The cost of giving up the scale falls from 0.08 at one body to 0.003 at nine, because several bodies fix their own scale.
3. **Where the scale is wrong, the ratios hold.** A size is the same added constant on every log measure, so a ratio does not see it. Every film here is magnified by 1.35 while the rules assume 1.15 with a spread of 0.08, two spreads off, as a C-arm's unrecorded geometry can be. The raw exact rule then falls to 0.392 at one body and 0.695 at three, while the scale-free rule stays at 0.396 and 0.698, so it matches or beats the raw rule. The body-size product falls from 0.213 to 0.089. Where the magnification is uncertain but rightly described (log m about log 1.15 with SD 0.08), the raw rule loses only 0.035 at one body and nothing measurable by nine. Where there is no unit at all (pixels), only scale-free rules can run, and the exact scale-free rule is the best of them at every width.
4. **Observing a combination as well as the measures counts the same data twice.** With the aspect given a likelihood of its own beside the measures, the exact rate falls (0.478 to 0.462 at one body, 0.861 to 0.840 at five). The rule also says it is sure more often while being right less often when it says so: at n = 5 it answers 41 per cent of fields at posterior 0.99 with precision 0.994, against 37 per cent at 0.999 for the rule that counts the aspect once. In PyMC, that is the difference between `pm.Deterministic`, which is safe and adds nothing, and an observed combination, which is a second likelihood for data the model already has.
5. **The PyMC model is the rule.** The exact rule written in PyMC, with the size the only continuous variable and the place summed in the likelihood by a logsumexp, gives through NUTS (4 chains of 1,000 draws) the exact enumeration's posterior over places within three Monte Carlo standard errors (ArviZ's, from the effective sample size). On the two fields checked the largest difference is 0.007, the largest standard error 0.014, with no divergences and R-hat at most 1.007; no discrete variable is ever sampled, and the run repeats to the bit.

What follows for the PyMC rewrite: name combinations with `pm.Deterministic` for reading and plotting, never observe them beside the measures, and keep the scale integrated, flat where the unit is unknown, rather than replacing measures by ratios.

## Commands

It runs in the environment of [requirements-schwingcheck.txt](../requirements-schwingcheck.txt) (`python3 -m venv ~/venv-sc; ~/venv-sc/bin/pip install -r requirements-schwingcheck.txt`), which pins PyMC and ArviZ; `study` itself needs only numpy and the archive.

```sh
~/venv-sc/bin/python -m combinations study      --outdir combinations/records/combinations-2026-10-27
~/venv-sc/bin/python -m combinations pymc-check --outdir combinations/records/combinations-2026-10-27
~/venv-sc/bin/python -m unittest discover -s combinations/tests -t .
```

[records/combinations-2026-10-27/](records/combinations-2026-10-27/) holds its record (`combinations.json`, with every rule's rate, standard error, rate within one place, log loss and selective answers at 0.99), the table of all four worlds (`TABLE.md`) and the PyMC check (`pymc_check.json`). The six tests take a few seconds.

## How each rule is computed

[study.py](study.py) says it in full. Every combination here is a linear combination of the log measures, so under the archive's log-normal approximation (`exact.log_moments`) a set of them, the rows of a matrix A, has mean A m_k and covariance A S_k A' at each place k. The Bayes rule on them alone is one quadratic discriminant per place, in closed form, with nothing fitted. With A the identity this is the archive's formula rule, to 1e-10 (tested). The exact scale-free rule is the exact rule with the size under a flat prior on log s, which is the Bayes rule on every ratio at once (scanimport/bridge.py's unknown scale).
