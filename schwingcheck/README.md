# schwingcheck: the exact rule as a package, on data shaped for PyMC

Step c of item P ([TODO.md](../TODO.md)), 27 October 2026. The archive's exact Bayes rule ([archive/bordercall/exact.py](../archive/bordercall/exact.py)), its column generator ([panjabi.py](../archive/bordercall/panjabi.py), [neighbour.py](../archive/bordercall/neighbour.py)) and its scores, lifted into one package whose data is shaped for the PyMC rewrite of step d: the checked table as one long CSV loaded into an xarray Dataset with named dimensions; columns and fields as arrays with NaN for a missing value and integer offsets for gaps; every result as ArviZ InferenceData in NetCDF with the command, the seeds and the digests in its attributes; the code vectorised, with no loop per body or per field. It is the same rule: the tests hold the posterior to the archive's on every contiguous complete field, the generator to the archive's bit for bit, and the rescoring of seed 97's 2,000 columns to [exact.json](../archive/records/exact-2026-10-26/exact.json) at 1, 3 and 9 bodies, rate for rate. Items 1 and 2 of TODO.md are done by it. Nothing here runs PyMC yet; it is pinned now so that step d runs in the same environment.

## Install

The archive and its 222 tests still need numpy alone (and matplotlib for the figures). The package needs the pinned environment of [requirements-schwingcheck.txt](../requirements-schwingcheck.txt), a full freeze made on Python 3.13.17: pymc 6.3.2, pytensor 3.3.4, arviz 1.3.0, xarray 2026.9.0, h5netcdf 1.8.2 with h5py 3.16.0 (the NetCDF engine; h5netcdf was allowed as one more pinned dependency by the owner's word of 27 October 2026, 10:04 UTC), numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, and what they bring.

```
python3 -m venv ~/venv-sc
~/venv-sc/bin/pip install -r requirements-schwingcheck.txt
~/venv-sc/bin/python -m unittest discover -s tests          # the package's tests, from the repository's root
cd archive && python3 -m unittest discover -s tests         # the archive's 222, as before
```

## Commands

Run every command from the repository's root.

```
python -m schwingcheck table check                 # the committed long CSV is what write would write
python -m schwingcheck table write                 # rewrite it from the provenance record
python -m schwingcheck name FIELD.csv [--measures endplate h_post ...] [--offsets 0 1 2]
python -m schwingcheck rescore --n 1 3 9 --outdir records/exact-rescore [--table archive]
```

`name` names one field. The CSV has a column `body` (0, 1, 2, ... down the column), one column per measure in millimetres, blank where the value was not read, and optionally a column `offset`, each body's offset from the first (0, 2, 4 for every other body; without it the bodies are consecutive). [examples/t11-t12-l1.csv](examples/t11-t12-l1.csv) is Panjabi's means at T11, T12 and L1 for the seven measures, the README's example:

```
$ python -m schwingcheck name schwingcheck/examples/t11-t12-l1.csv
field of 3 bodies at offsets [0, 1, 2], measures endplate, endplate_depth, endplate_lower, endplate_lower_depth, h_post, canal_w, canal_ap
place (level of the first body)  posterior
  T11   0.607628  <- named
  T10   0.285740
  T12   0.075913
  L1    0.015071
  ...
99% set: {T9, T10, T11, T12, L1} (5 places)
the top place reaches 0.99: no
```

The archive's example in [README.md](../README.md) prints the same three leading posteriors. With no body the command says there is nothing to name and exits 1; with no measure read on any body it says the posterior is the prior and exits 1; a measure that is an area or an angle is refused by name until step e.

`rescore` draws the archive's scoring columns (seed 97, 2,000 columns, the typical phenotype) and scores every field of the widths given under the three regimes, both planes, AP and lateral, writing one InferenceData file per width and regime and `rates.json` beside them. `--table archive` scores on the archive's own table, which reproduces exact.json to the bit; the default is the checked table, which differs from it in one value (below).

## Layout

- [`__init__.py`](__init__.py): the levels (C2 to L5, and the rule's C3 to L5), the sides, the kinds and the planes.
- [`mnemonics.py`](mnemonics.py): every mnemonic the four papers print (EPWu, SCD, PDWr, FCAs, ...) with its measure name, its side, its kind (length, area, angle), the planes that show it (a SPINEPS mask, an AP view, a lateral view, only a CT) and its definition in words.
- [`table.py`](table.py): the long CSV, written from the provenance record and loaded as an xarray Dataset.
- [`data/panjabi_long.csv`](data/panjabi_long.csv): the checked table, generated; do not edit it by hand.
- [`measures.py`](measures.py): one `Measure` object per measurement and side, the registry, and the selection the rule reads.
- [`rule.py`](rule.py): the exact rule, vectorised over fields, with gaps and missing values.
- [`columns.py`](columns.py): the generator, every phenotype, and the cutting of fields from columns.
- [`score.py`](score.py): the archive's rates, computed the same way.
- [`records.py`](records.py): a result as InferenceData, written and read as NetCDF.
- [`__main__.py`](__main__.py): the commands above.
- [`examples/`](examples/): the field above.
- Tests in [tests/](../tests/): `test_schwingcheck_table.py`, `test_schwingcheck_rule.py`, `test_schwingcheck_columns.py`, `test_schwingcheck_record.py`, `test_schwingcheck_cli.py`.

## The table

[data/panjabi_long.csv](data/panjabi_long.csv) is written by `table write` from the provenance record of step b, [archive/bordercall/reference/provenance/provenance.csv](../archive/bordercall/reference/provenance/provenance.csv) (two readings by eye of every cell, both agreeing) and [absent.csv](../archive/bordercall/reference/provenance/absent.csv) (the thoracic body table, printed on page 892, which the scan lacks), and nothing else; `table check` fails when the committed file differs from what `write` would write, and a test runs it. It holds every present-study mean and standard error of the papers' dimension tables (cervical Tables 2 to 6, thoracic 4 to 7 and the absent 3, lumbar 2 to 5, facets 2 to 8), one row per value:

| column | what it holds |
|---|---|
| `measure`, `side` | the measure's name and `whole`, `right` or `left` |
| `level` | C2 to L5 |
| `mnemonic` | the paper's own, as the provenance record names the cell |
| `statistic`, `value`, `units` | `mean` or `sem`; mm, mm2 or deg |
| `kind`, `planes` | length, area or angle; which of mask, ap, lateral, ct show it |
| `n` | the specimens, 12 in every table |
| `paper`, `table`, `cell` | the paper, its table and the provenance cell id, or no cell for the absent table |
| `basis` | `cell`, or where the thoracic body table's value comes from |

2,582 rows: 1,395 means and 1,187 standard errors, 1,144 lengths, 624 areas and 814 angles, from the cervical (358), thoracic (676), lumbar (260) and facets (1,288) papers, 48 measure names under 74 mnemonics. The thoracic body table's 36 means that Table 8 restates come from Table 8's cells (basis `table 8 restates the absent Table 3`); its other 84 values come from the transcription (basis `transcription of the absent Table 3 (provenance/absent.csv)`) and stay unverifiable until a scan of page 892 arrives.

`table.load()` gives an xarray Dataset with dimensions (level, measure, side) and the variables `mean`, `sem`, `sd` (sem x sqrt(12), the population SD the rule and the generator use), `n`, `cell` and `basis`, with `kind`, `units`, `planes`, `definition` and `mnemonic` as coordinates and the file's sha256 in its attributes; NaN where a paper prints nothing.

**One value differs from the archive's table.** The archive's [panjabi_full_spine.csv](../archive/bordercall/reference/panjabi_full_spine.csv) gives the lower end-plate depth (EPDl) at T3 as 23.3, transcribed from the absent Table 3; Table 8 prints 23.2, and step b held that as the one contradiction. The long table takes Table 8's 23.2. A test compares the two tables over all 592 values they share and finds that difference and no other. The rescoring reproduces the archive's record on the archive's table (`--table archive`); on the checked table the rates are: CHECKED_RATES.

## The measures

`measures.registry()` has one `Measure` per measurement and side, 100 in all, keyed `measure` for a whole-body measure and `measure:right`, `measure:left` or `measure:mean` for a paired one: its mnemonic, kind, planes, definition, the levels the table gives it, its error in millimetres, its table rows (the mean and the SD at every level, from the Dataset), its measurers and its correlations. `measures.select(keys)` is what the rule reads: it refuses a key that is not registered (KeyError), an area or an angle (ValueError naming step e, where each kind gets its own term), a measure with no error, and one with no table row at a level asked for. `pedicle` and `pedicle_h`, the archive's names, resolve to the pair's mean, as the archive's build took them, so a left and right pair is never two independent measures. A test selects every registered measure and asserts that each is scored or refused for one of those reasons.

What the table lets the rule score today: 32 lengths, every one printed at all of C3 to L5 (the archive's seven; the pedicle widths and heights, right, left and mean; the spinous process length; the transverse process width; the facet widths and heights, superior and inferior, right, left and mean; the interfacet widths; the interfacet heights). What waits for step e: 30 areas and 24 angles, and 14 entries printed as a mean with no spread (the rib articulation totals of the thoracic paper's Table 6, `costovertebral_area` and `rib_articulation_area`, and the facets paper's card angles, `facet_card_x_sup`, `facet_card_x_inf`, `facet_card_y_sup` and `facet_card_y_inf`, right, left and mean), which no rule can take until a spread is found for them. The error is 1 mm for every length, the archive's `noise_mm`; the measurers are the archive's [spineps_map.py](../archive/bordercall/spineps_map.py) for the seven and nothing yet for the rest; the correlations are empty until a CT table estimates them.

## The rule

`rule.name(X, offsets, mu, sd, synth)` takes every field at once: `X` is (fields, measures, bodies) in millimetres with NaN for a value not read, `offsets` the bodies' offsets from the first (0, 1, 2 for three consecutive bodies, 0, 2, 4 for every other body), `mu` and `sd` the table as (measures, levels). A place is the level of the first body, and there are as many places as starts at which the last offset still fits (`places_of`). The likelihood of one measure given the patient's size is the archive's, Delta + u u' inverted by Sherman-Morrison, and the size is integrated by the same 161-node Gauss-Hermite rule over log s; the product over measures and the uniform prior give the posterior, and `name` returns it for every subset of measures asked (the archive's regimes are subsets).

Two things the archive did not do:

- **Gaps.** The offsets place the bodies; a gap is an offset skipped, and the places shrink accordingly.
- **Missing values.** Given s, the covariance of one measure's values on any subset of bodies is the same form on that subset, so a NaN is dropped from the sums and the likelihood is the exact marginal. A measure missing on every body contributes a constant; a field with no value at all gets the prior back.

The whole likelihood is one matrix product per block of fields: the sums the Sherman-Morrison form needs (sum of x^2 / v, sum of x / v, sum of 1 / v over the bodies, with the missing ones weighted out) are rows of one matrix and the table's terms at every place and node are its columns, so one product gives every field's log likelihood at every place, measure and node, and NaN never enters it. Fields go through in blocks of 32 so the product's operands fit the cache; TIMING. The tests hold the result to the archive's `field_loglik` and posterior at 1e-10 on contiguous complete fields of every width, to a dense multivariate normal computed independently (scipy) on gapped fields and on fields with values missing, and the guarantee holds: on fresh columns, a name given at 0.99 is right at least 99 per cent of the time.

## The generator and the fields

`columns.draw_columns(ref, phenotypes, seed, n, measures, ...)` is the archive's `neighbour.draw_columns` with the random stream consumed in the same order (the size, the offsets, 24 level draws per measure, 24 noise draws per measure), so the same seed gives the same columns bit for bit, for every phenotype (typical, four_lumbar, six_lumbar, t13, lumbar_rib, no_rib_t12), with the exchangeable correlation between measures' offsets and with the archive's settings or others. It returns a `Columns` object whose `values` are (column, body, measure) with NaN past the end of a column shorter than the longest, with each column's levels, phenotype, transitional position and scale. `columns.fields(values, offsets)` cuts every field of the offsets given from every column, in the archive's order for consecutive offsets, with the truth (the place) and the column of each field, and leaves out a column too short for the pattern.

## The scores and the records

`score.summary` and `score.claims` are the archive's `exact.summary` and `exact.claims_summary` with the same keys, so a rate here means what it meant in the record: the share named exactly with its standard error clustered by column, within one, the Bayes error predicted and counted, the log loss, the share answered and the precision at 0.9, 0.99 and 0.999, the 99 per cent set's size and coverage, the mapping quality, the calibration, the rates by true start and by true centre, the landmark windows, the confusion of offsets, and the claims about the middle body (the cuts, the regions, the shortest interval).

`records.build` puts one scoring into an InferenceData tree, written and read as NetCDF (`records.write`, `records.read`): the group `posterior` (every field's posterior over the places), `observed_data` (the fields), `truth`, `constant_data` (the offsets, the table) and `rates` (the summary and the claims), and in the root's attributes the command, the seeds, the generator's settings, the digests (the long CSV's sha256, the archive table's where it was used, and the sha256 of the package's own code) and the measures, levels, offsets and versions. `rescore` writes one per width and regime.

**The record of 2026-10-26 reproduced.** `rescore --n 1 3 9 --table archive` reproduces every rate of exact.json's `widths` at 1, 3 and 9 bodies, in all three regimes, with no difference past 1e-9 over every key (`n_fields`, `places`, `exact`, `se_cluster`, `within_one`, `errors`, `bayes_error_predicted`, `bayes_error_counted`, `log_loss`, `selective`, `selective_099_by_called_region`, `credible`, `mapq`, `calibration`, `by_start`, `by_centre`, `landmarks`, `confusion_offsets`, `measures`, `claims`); `tests/test_schwingcheck_record.py` holds it there, in a few minutes. RESCORE_TIMING.

## Tests

TEST_SUMMARY

## What step d and step e take from here

Step d rewrites the rule and the generator in PyMC on these shapes: the Dataset is the table, `X` with its offsets is the observed data, `Columns.values` is what the generator must match in distribution, `records.build` is the InferenceData every result goes into, and `score.compare` with `tests/test_schwingcheck_record.py` is how the rewrite proves it reproduces the record. Step e adds the areas and the angles as kinds of their own in that model, takes the 14 spread-less means up only if a spread is found, and scores every family as TODO.md's step 5 says.
