# Figures

Drawn by `python3 -I figures.py --records records --out figures` from the records of
`python3 -I run.py --out records` (bordercall 560bd00). Each figure's numbers are its CSV; its caption is its .caption.txt.
The three renders are drawn by render.py from the generator itself, seed 2029, 4000 people.

Drawn at bordercall f313dd8, from and by:

- records/RECORD.json, sha256 8229f63cad6bc1ddf0ecc53c9faa6602bb4d79b590165b4c4cd80f5d614c9df1
- figures.py, sha256 df7e5d8794c0a291faf0b536769e7035a78817b03b24e7d397cda8e82db6281d
- figures_all.py, sha256 b6890f20cde88191a56df5be8ea6bce7fb548f272862e33c2364475301524476
- render.py, sha256 d4bc0d70416d843a6d019ffefe741cb0fe01013357027395c24448c01cc3a9d9
- synthval/house.py, sha256 396822b88fcb46e9533162f8a46b8e2443c1d58ac15d1f40e2d0eb4f5653323a
- schwingcheck/figures.py, sha256 3908d42cc8e93c839d8ddca5bf06591af281e1490d775483e20535a0908b0576

Abbreviations on the axes: EPW upper end-plate width; EPD upper end-plate depth; EPWl lower end-plate width; EPDl lower end-plate depth; EPA upper end-plate area; EPAl lower end-plate area; VBHp posterior body height; SCW canal width; SCD canal depth; SCA canal area; PDW pedicle width; PDH pedicle height; PDA pedicle area; PDIs pedicle angle, sagittal; PDIt pedicle angle, transverse; SPL spinous process length; TPW transverse process span; FW upper facet width.

## fig1_means

Lumbar means of eight measures. The generator draws around Panjabi's means; each grey circle is one published series of the 39 papers (bone and CT, adults, Panjabi's definitions or close ones), pooled by REML where three or more exist. The grey band is the synthetic population's measured spread.

- fig1_means.caption.txt, sha256 4f28f42d7a588bb8d7f9cdab4296ba45414d3c79d4c580dd766a33704b3d6d57
- fig1_means.csv, sha256 cd2f55e32b653a64a19bc929ab3143735e37d76901506c969740866ebfcfa9f0
- fig1_means.pdf, sha256 1561ab3a7fc73ec7f6298acfa887b6450e149e9bbafa5a67d44d2eb8bed0959a
- fig1_means.png, sha256 b563724dc567dbbf6a82a837ed245a7df047711f3892f92aee25dafaaf89d018

## fig2_spread

The spread of the synthetic population against the published series: each cell's measured SD over the pooled published SD (bone and CT, Tan's SDs left out). One means the papers' spread; Panjabi's own SDs are shown beside the three settings of the generator. B keeps the levels that four measures or more reach.

- fig2_spread.caption.txt, sha256 91f97836d13427f5f3db8ed9b3772cc704878f11372965965ae29a154bd05db5
- fig2_spread.csv, sha256 e182025d19f19e0990299b33ab0bc6701a30eb11fcf9044e4bb4dd31150e7c25
- fig2_spread.pdf, sha256 0cf6ec1792a4407e1084dc3a01ac1feab8b2b886de05442100d71e115faf2185
- fig2_spread.png, sha256 794fd3dbabd3b61a36d6f03834c38b31b1eee49522be5e976d71d1fc1258022c

## fig3_structure

What the means and SDs do not test. A, the canal's correlations with the body, synthetic against Griffith's 1,080 CTs, his sexes apart and together; B, the share of the body's sex difference each measure carries (the generator scales all alike); C and D, two ratios by level against the papers that print them.

- fig3_structure.caption.txt, sha256 8fb896351d4ec86fd29a2f75015cd96bedbecaf7c5c2a7bc78c2f1003e0a072c
- fig3_structure.csv, sha256 d32d994ea3eef3d9aecba58d2b68c79af874639ac285cd8e22ec6007ca3b2291
- fig3_structure.pdf, sha256 a737da503e0b1fa2ed40c7f951415977815f3fdd898488cd8a726cbf0272b2e5
- fig3_structure.png, sha256 978b56555278f9c8334f813a8923facac52c3ab8acc317bd34c35f87812f48e9

## fig4_state_space

The generator's state space, one axis at a time from its own point (circled), and the grid searched for the point nearest the papers: the squared log SD ratio plus the mean squared distance from Griffith's four correlations; in F, grey, past the grid's lowest sd_scale.

- fig4_state_space.caption.txt, sha256 d6f51515c29724d176d8a6aa971c1a6272e6ab711343bb59a15736e68a8cc018
- fig4_state_space.csv, sha256 349adfb50dcc88b444217187573df88c6e68b611e6b25ce916ad4ccd43f94a76
- fig4_state_space.pdf, sha256 0e2cc40c6594f86dfd1356b66dcc765ba2f3ab570ccc3e7f41b3c971b4796d6a
- fig4_state_space.png, sha256 ce5a79bbd29dba8669e8fb9d6617129a3852c70a301f1bb6bd746cecc6c919cb

## fig5_naming

Naming by the exact rule on the seven SPINEPS measures, with the CT's errors, at points of the state space: the rule built for the generator against one that knows the setting, left out where no rule holds the setting whole (the generator, phi, r_between, the nearest point, whose rule ignores r_between). Bars are 95% intervals over the columns.

- fig5_naming.caption.txt, sha256 e855faa97a8793d973fc94f894bda158a9696e9e4ac9bf43a215990878e00daa
- fig5_naming.csv, sha256 3313c2e0f6962b94e25e154840c98fce153e8a0a322c3a20c507446dd5641860
- fig5_naming.pdf, sha256 d9526f04cd63e7d13867fffcb25c4b7d0dbe63bca688faf5e2cf41c67ed9dedd
- fig5_naming.png, sha256 0a352cf1ab3d291b776e29b0e3295310ab61f8f55efec490293528efd9bba330

## fig6_power

The power calculations rerun. A, the REML spread between published series over Panjabi's SD, cell by cell; B and C, the exact rule built on tables moved as the papers disagree; D to F, what whole spines can test against the table taken as exact, and against Panjabi's twelve as a sample (two-sided, 5%, 80% power; 159 marked).

- fig6_power.caption.txt, sha256 c1f5664a660796a1db50dd3d52edc0f96890776e66a75cbcc340f3dcac7c03b8
- fig6_power.csv, sha256 0b7143583831150301c897da4f381ed8fc526cadae400e97152ced4cb9c507f8
- fig6_power.pdf, sha256 76abe2995f08a7e7a4c1cd580b37573177bcd10536a7871a33100328d670b480
- fig6_power.png, sha256 7cadd3db2b5325037e1889e3d9b62f65ad8a063ac9971c5c027531bb9e7fc465

## fig7_quality

Quality indicators of synthetic vertebrae: a length or area at or below zero (sign), a measured value at the floor, an area larger than its own width times depth (box), an end-plate under half of it (convex), a canal wider than its transverse processes (inside). Sign and inside no anatomy can fail; box and convex hold under allowances.

- fig7_quality.caption.txt, sha256 68acf8351bf495e4a6abb533b6211b6e5f0c1426972ad676bbe32dad0d858165
- fig7_quality.csv, sha256 9513f854d80f5d1a116dccb31f417dfd727094134365efc4390ee119de4ea2e5
- fig7_quality.pdf, sha256 f0bb6cd7283e7e1c9d50a891db28d143ec85b5edafbdc89b6a8405939dfb6fe1
- fig7_quality.png, sha256 5c1833449198a6d48f2a982e6296e396092961522e74c0d20fcf0e4b4fb7d91a

## fig8_assumptions

Two things the generator assumes, set beside the papers. A, the error of one reading as the reread's checked error part gives it, two figures from pig bone; B, how often a column carries each anomaly, from Eisenstein's 443 skeletons and Duman's 517 CTs (the reread's checked priors).

- fig8_assumptions.caption.txt, sha256 abeb264dd22898eea79014c89b28bab912908fcb5bfcb2917a38e75c6da9a0de
- fig8_assumptions.csv, sha256 cb381b8bbc51abf1fa05c1efc6f057185700c9bedeb4d7760bbfdef193da9cf1
- fig8_assumptions.pdf, sha256 d6d477abcb5f5b5758a938088b88872f7efc0ae2ba55e83288c9c9b8091abbd0
- fig8_assumptions.png, sha256 55384bdbb9a7a48cb74fd3e5db05dbf08f763acfc61cecb0b7550a53b7483162

## fig9_tables

Every measure of the reread. A, what became of each of the vocabulary's keys; B, the measures each table holds at each level of C3 to L5; C, the papers' placed cells by level and by where their SD comes from, Tan 2004's SDs being uncertain.

- fig9_tables.caption.txt, sha256 34dd26e753da9cb3fec88a92cb3fe757ea21835358004eb6aebb344d24d7009b
- fig9_tables.csv, sha256 c489732979a95f70f5ad586c3d193dd9bf2016f56e04dd223246ccc4b2d77bed
- fig9_tables.pdf, sha256 09da33cad6c6b14da0e5a256dad54e777289ad6a4bb6eb6d5d6fcb4d7fe956aa
- fig9_tables.png, sha256 5ec5bb474034f8498cf4d8f61bd09c65c5a086b2151572b3964acfc1f23dfc67

## fig10_relations

Quality indicators on every measure. A, each relation between the papers' measures and Panjabi's, the share of synthetic vertebrae of table C that fail it at the generator and at C's nearest point; B, the unions on each table at both points, necessary being the relations no anatomy can fail.

- fig10_relations.caption.txt, sha256 2283e59ca0a196ffae12da6ec04f095ae89ebdc5453019c046237146745ef19b
- fig10_relations.csv, sha256 0148152e15c6ef7019c940bd57f3355ad0eb71a72c1709dd56db0fbc53520dcb
- fig10_relations.pdf, sha256 643b4afc77279a4438339bb43878cc6f65763ca9226015926b9f24e242a50e88
- fig10_relations.png, sha256 7947b1c1b6ba3d3b721e107ec2447dddeea52973c8fa1846eff9716ac46ced61

## fig11_state_space_all

The state space read on the three tables, one axis moved alone from the generator's point, with each table's nearest grid point in grey. A, the spread over the table's own SDs; B, the relations no anatomy can fail; C, the correlation between neighbouring levels; D, every indicator but the floor.

- fig11_state_space_all.caption.txt, sha256 d72fc1173a96ff79e062d0205d4650d2b13bb2e45db4b8e2d970a5b65befad38
- fig11_state_space_all.csv, sha256 df4de0e13a830dfca5779a0aafcb614c2761fa0383d74a2443600c4074734c58
- fig11_state_space_all.pdf, sha256 ecdec2e78ed1d56fd740953ed264d51bb5c91790b0f7c0ff2d6158091aaa1097
- fig11_state_space_all.png, sha256 0bba34052a0519ea4a76790ea36b2572ef2d0fd67a12674a12d8ed437cc8c179

## fig12_naming_measures

Exact naming by the rule built on more and more measures of table C, on columns drawn from it at the generator's point (solid) and at C's nearest point (dotted): over the whole column, the seven, the 32 and every complete measure; over the lumbar run, those of A, B and C too.

- fig12_naming_measures.caption.txt, sha256 268d0d583e953e81fef6e7f6abc3c2d4edbb6e54aaa2829c396059ed3e8ff1d5
- fig12_naming_measures.csv, sha256 cd02c6e3776df3719dcc1146d4224bbbca5090e381063c4738cd7a3014f14b8d
- fig12_naming_measures.pdf, sha256 d3e20aff87663d2200d606aafe2510a14283dd206495c53fe590376f80c26810
- fig12_naming_measures.png, sha256 0bd0f3de58365662db664dbf5d1519c3bce2ab7bd3e5a6b059dd20b89794754f

## fig13_spread_all

The spread between published series on every measure the papers pool from three series or more: the REML tau over the cell's SD, one grey point a cell, the marker the measure's median. One means the series differ among themselves by a person's SD.

- fig13_spread_all.caption.txt, sha256 501df4aa1ead7d1b2d7d03c1544a3cf57c0aa8df2e1a7f77bb0f9ac138e24ac6
- fig13_spread_all.csv, sha256 d993e3f54c91f14825eebebbcfe232e2b235a18f1181a70dd34683b2fad1c507
- fig13_spread_all.pdf, sha256 aa14bda6638988b57a97348dcfc911fadc66180415aaaf37abee6b2145fe8c1e
- fig13_spread_all.png, sha256 608775526e079d7ff71d11d5ef290575abc4f6a5fae7006d724d2e0765da7450

## fig14_strata

Every paper its own population. A, the rule built on the other papers, pooled, scored on each paper's population at three bodies, the small triangles the SD difference alone, the diamond's line the interval for one more population; B, the pooled loss by field width and reading; C, whether answers at 0.99 stay right; D, populations drawn from the model.

- fig14_strata.caption.txt, sha256 000f03e0be751aa7599728377596989799a35236501d23ebb2c5f57d569d0a22
- fig14_strata.csv, sha256 6b3c562c88c66df8da85139816323193913eacd0992eff5c6f013137968c3f69
- fig14_strata.pdf, sha256 e217a1f280e4ccda8d5381da7feca24c6d552e954ea26c92a4cc4bf958779cf8
- fig14_strata.png, sha256 83b6790cbbaa802fcd79872d1c1da13e7dae3d673670cb804bca0c60d3537327

## fig15_select

Choosing the rule by held-out prediction, every paper held out in turn. A and B, each candidate's log loss and accuracy on the held-out populations; C, calibration; D and E, the SD factor and the temperature swept, the inner choices as ticks; F, the winner against the plain rule, population by population.

- fig15_select.caption.txt, sha256 0130dea38ece554e3dc572f75dbd90300191919b53cf98d39cf462162d811f11
- fig15_select.csv, sha256 cb5b3a33d11a26fd3cf4c7ca901582234c832567bfda1ccd53598bbac9e2f0ba
- fig15_select.pdf, sha256 dc368c06dda9da5d088a777bd63bec8b19f6849ee225ee604611993ac6f19bae
- fig15_select.png, sha256 ae8c161edbbd4ee26674ba91f14735b2d279579868e72a94507848fc895db048

## render1_axial

The third lumbar vertebra from above, anterior up, drawn to its measures: Panjabi's means, then three synthetic people the generator draws (seed 2029). Each section is the superellipse of its width, depth and area, dashed where none holds the area. The spinous process reaches its length from the end-plate's centre. Laminae and process thickness are fixed.

- render1_axial.caption.txt, sha256 dba96c14790ef7249894a1a67f7ac4c2ab1475020bc0b740597a58a58b4277e1
- render1_axial.csv, sha256 e1e5c128a1918fec1d96c91dfdf2ae4f5378ba17830b2c5d7ad61ba7a7d60c13
- render1_axial.pdf, sha256 c5b635799caecbcde1fccd5129c0b56ee5360f9d8216d89365b8ef4935c4a084
- render1_axial.png, sha256 1406a861c58c691751b3190319da4bd580ac86d94793035222b092280901dbe7

## render2_column

The lumbar column from in front, each body its end-plate width by its posterior height with the canal hatched over it and the transverse span as a line: Panjabi's means and two synthetic people. A heavy outline marks a body some quality indicator flags; the flags are named.

- render2_column.caption.txt, sha256 beb8d3df56eb01837aa2061608f3f22149c2a6b66cb1b472db44b01db53cf7fe
- render2_column.csv, sha256 0420dd5e3617d828542b936f6956c5f955b353006d0f89efc7e0635367687f53
- render2_column.pdf, sha256 6a733668fc21771eea771463b781fb85693b6561abec6cae4ceec23ed81f663e
- render2_column.png, sha256 7cfa7d0f8cc150b6a75a12ea22ca909c39aa2ed1338a9f6ea529cb5df22fb410

## render3_solid

Lumbar columns as solids, seen from the left and behind, shaded grey from one light: Panjabi's means and two synthetic people of the first drawing. Bodies are lofted between the two end-plates' superellipses, an area past its box drawn as the box (C's L3 lower plate); pedicles, laminae and processes are boxes, their thicknesses fixed.

- render3_solid.caption.txt, sha256 a38f5f4c3fd2c59eafb6a8b514adac2236022d505d701a54c273f819c8b6f073
- render3_solid.csv, sha256 5c4ec049aed6c586552a13971e6dc62b9a1e0d38bec5b467a1b51de2257abaab
- render3_solid.pdf, sha256 9021e4eb305e7033a86a78202ce747708f4301bc91a84da6ae4975d633de8b38
- render3_solid.png, sha256 4faebeb6f3df7742f14f023edd335c2064cda91514f7e671d0a28d795217e996
