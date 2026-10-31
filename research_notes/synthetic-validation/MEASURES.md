# Every measure of the reread: what became of each key

Written by `python3 -I tables.py --records records --write MEASURES.md` from records/all/inventory.csv,
which run_all.py writes; `--check MEASURES.md` fails when the table differs from the record. The
vocabulary is the reread's (data/vocabulary.csv, cut from research_notes/paper-tables/tools/vocabulary.csv
at bordercall main 6409164), 106 keys. "Panjabi" says he prints the measure; "generator" that it is one
of the 32 schwingcheck draws; "rows" counts the snapshot's rows under the key, "usable series" those
with a mean, an SD and a count of two or more that pass literature.py's rules, "cells pooled" the
(measure, level as printed) cells with a usable series, and "with 3 series or more" those pooled with
a prediction interval. A key split into variants (papers_table.VARIANTS) lists them; the last column
says in which table the measure is drawn, with its cells in A, B and C, or why it is drawn in none.

<!-- table all_measures -->
| key | kind | Panjabi | generator | rows | usable series | papers | cells pooled | with 3 series or more | variants | what became of it |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| endplate | length | yes | yes | 115 | 36 | 4 | 22 | 5 |  | drawn: A 22, B 21, C 22 cells |
| endplate_depth | length | yes | yes | 106 | 42 | 4 | 23 | 0 |  | drawn: A 22, B 22, C 22 cells |
| endplate_lower | length | yes | yes | 103 | 36 | 4 | 22 | 5 |  | drawn: A 22, B 22, C 22 cells |
| endplate_lower_depth | length | yes | yes | 109 | 42 | 4 | 23 | 0 |  | drawn: A 22, B 22, C 22 cells |
| h_post | length | yes | yes | 112 | 76 | 7 | 22 | 7 |  | drawn: A 22, B 22, C 22 cells |
| endplate_area | area | yes | yes | 40 | 25 | 2 | 23 | 0 |  | drawn: A 22, B 22, C 22 cells |
| endplate_lower_area | area | yes | yes | 45 | 24 | 2 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| endplate_incl | angle | yes | yes | 27 | 22 | 1 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| endplate_lower_incl | angle | yes | yes | 27 | 22 | 1 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| endplate_wedge | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| canal_w | length | yes | yes | 180 | 47 | 6 | 22 | 5 |  | drawn: A 22, B 22, C 22 cells |
| canal_ap | length | yes | yes | 273 | 70 | 10 | 23 | 5 |  | drawn: A 22, B 22, C 22 cells |
| canal_area | area | yes | yes | 67 | 32 | 3 | 22 | 5 |  | drawn: A 22, B 22, C 22 cells |
| pedicle_w | length | yes | yes | 444 | 109 | 12 | 22 | 9 |  | drawn: A 22, B 22, C 22 cells |
| pedicle_h | length | yes | yes | 360 | 109 | 12 | 22 | 9 |  | drawn: A 22, B 22, C 22 cells |
| pedicle_area | area | yes | yes | 37 | 27 | 2 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| pedicle_incl_sag | angle | yes | yes | 161 | 79 | 7 | 22 | 7 |  | drawn: A 22, B 22, C 22 cells |
| pedicle_incl_trans | angle | yes | yes | 137 | 56 | 3 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| spinous_length | length | yes | yes | 27 | 22 | 1 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| transverse_width | length | yes | yes | 27 | 22 | 1 | 22 | 0 |  | drawn: A 22, B 22, C 22 cells |
| pars_area | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 15, B 0, C 15 cells |
| uncovertebral_area_upper | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| uncovertebral_area_lower | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| uncovertebral_incl_frontal_upper | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| uncovertebral_incl_sag_upper | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| uncovertebral_incl_frontal_lower | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| uncovertebral_incl_sag_lower | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 5, B 0, C 5 cells |
| costovertebral_area_upper | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 12, B 0, C 12 cells |
| costovertebral_area_lower | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 10, B 0, C 10 cells |
| costovertebral_area | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| costotransverse_area | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | drawn: A 11, B 0, C 11 cells |
| rib_articulation_area | area | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| facet_w_sup | length | yes | yes | 10 | 5 | 1 | 5 | 0 |  | drawn: A 22, B 5, C 22 cells |
| facet_w_inf | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_h_sup | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_h_inf | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_area_sup | area | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_area_inf | area | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| interfacet_w_sup | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| interfacet_w_inf | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| interfacet_h | length | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_trans_sup | angle | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_trans_inf | angle | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_sag_sup | angle | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_sag_inf | angle | yes | yes | 0 | 0 | 0 | 0 | 0 |  | drawn: A 22, B 0, C 22 cells |
| facet_card_x_sup | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| facet_card_x_inf | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| facet_card_y_sup | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| facet_card_y_inf | angle | yes |  | 0 | 0 | 0 | 0 | 0 |  | Panjabi: printed as a mean with no spread, so no rule can take it |
| h_ant | length |  |  | 122 | 82 | 7 | 23 | 7 |  | drawn: A 0, B 22, C 22 cells |
| h_mid | length |  |  | 57 | 31 | 3 | 22 | 2 |  | drawn: A 0, B 22, C 22 cells |
| h_lat | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| body_w_mid | length |  |  | 50 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| body_d_mid | length |  |  | 62 | 11 | 2 | 6 | 0 |  | drawn: A 0, B 5, C 5 cells |
| body_w | length |  |  | 7 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| body_d | length |  |  | 12 | 11 | 2 | 11 | 0 | body_d [end-plates' mean],  body_d [through the pedicles] | drawn: A 0, B 11, C 11 cells |
| body_area | area |  |  | 45 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| wedge | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| body_index | ratio |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| endplate_concavity | length |  |  | 7 | 0 | 0 | 0 | 0 |  | no series with a mean, an SD and a count of two or more passes the rules |
| disc_h_ant | length |  |  | 139 | 23 | 3 | 18 | 0 |  | drawn: A 0, B 18, C 18 cells |
| disc_h_mid | length |  |  | 173 | 45 | 4 | 40 | 0 |  | drawn: A 0, B 18, C 18 cells |
| disc_h_post | length |  |  | 139 | 23 | 3 | 18 | 0 |  | drawn: A 0, B 18, C 18 cells |
| disc_h_mean | length |  |  | 310 | 29 | 3 | 24 | 0 | disc_h_mean [area over depth],  disc_h_mean [not defined],  disc_h_mean [three points],  disc_h_mean [two rims] | drawn: A 0, B 17, C 17 cells |
| disc_index | ratio |  |  | 20 | 0 | 0 | 0 | 0 |  | no series with a mean, an SD and a count of two or more passes the rules |
| disc_w | length |  |  | 5 | 3 | 1 | 3 | 0 |  | drawn: A 0, B 3, C 3 cells |
| disc_d | length |  |  | 55 | 3 | 1 | 3 | 0 |  | drawn: A 0, B 3, C 3 cells |
| interpedicular | length |  |  | 296 | 54 | 3 | 22 | 5 |  | drawn: A 0, B 22, C 22 cells |
| canal_index | ratio |  |  | 35 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| lateral_recess | length |  |  | 17 | 7 | 1 | 7 | 0 |  | drawn: A 0, B 6, C 6 cells |
| foramen_h | length |  |  | 105 | 16 | 3 | 6 | 5 |  | drawn: A 0, B 6, C 6 cells |
| foramen_w | length |  |  | 22 | 17 | 3 | 17 | 0 | foramen_w [body to facet],  foramen_w [not defined],  foramen_w [the notch] | drawn: A 0, B 10, C 10 cells |
| foramen_area | area |  |  | 5 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| pedicle_w_outer | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| pedicle_w_inner | length |  |  | 10 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| pedicle_h_outer | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| pedicle_h_inner | length |  |  | 10 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| pedicle_chord | length |  |  | 159 | 63 | 7 | 26 | 5 | pedicle_chord [along the axis],  pedicle_chord [parallel to the midline] | drawn: A 0, B 26, C 26 cells |
| pedicle_length | length |  |  | 29 | 10 | 2 | 10 | 0 | pedicle_length [proper],  pedicle_length [to the ligament] | drawn: A 0, B 10, C 10 cells |
| pedicle_cortex | length |  |  | 16 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| pedicle_angle_transverse | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| pedicle_angle_sagittal | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| lamina_thickness | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| lamina_h | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| lamina_w | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| lamina_angle | angle |  |  | 20 | 10 | 1 | 10 | 0 | lamina_angle [between the laminae],  lamina_angle [to the body] | drawn: A 0, B 10, C 10 cells |
| pars_w | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| spinous_h | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| spinous_angle | angle |  |  | 13 | 0 | 0 | 0 | 0 |  | no series with a mean, an SD and a count of two or more passes the rules |
| transverse_length | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| transverse_h | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| facet_angle_axial | angle |  |  | 10 | 5 | 1 | 5 | 0 |  | drawn: A 0, B 5, C 5 cells |
| facet_angle_sagittal | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| facet_tropism | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| facet_gap | length |  |  | 0 | 0 | 0 | 0 | 0 |  | no paper of the 39 prints a series |
| rib | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
| sacrum | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
| alignment | angle |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (angle) |
| subject_age | years |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (years) |
| subject_height | length |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (length) |
| subject_weight | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
| subject_bmi | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
| subject_count | count |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (count) |
| prevalence | percent |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (percent) |
| reliability | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
| other | other |  |  | 0 | 0 | 0 | 0 | 0 |  | not a measure of one vertebra (other) |
<!-- end all_measures -->
