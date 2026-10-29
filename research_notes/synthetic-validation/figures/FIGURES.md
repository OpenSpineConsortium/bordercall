# Figures

Drawn by `python3 -I figures.py --records records --out figures` from the records of
`python3 -I run.py --out records` (bordercall 391571a). Each figure's numbers are its CSV; its caption is its .caption.txt.
The three renders are drawn by render.py from the generator itself, seed 2029, 4000 people.

## fig1_means

Lumbar means of eight measures. The generator draws around Panjabi's means; each grey circle is one published series of the 39 papers (bone and CT, adults, Panjabi's definitions), pooled by REML where three or more exist. The grey band is the synthetic population's measured spread.

- fig1_means.caption.txt, sha256 c6e99b5415af3d7f61625339bfcd9d3a619c30b5d40aa93bbc62352460cc24d5
- fig1_means.csv, sha256 05a49da25a66ff47bba04a19efd796a966dc746d2d251eb3dc1855048c9d3e28
- fig1_means.pdf, sha256 cd89f2acdd1535ab71b110696b3efa0c183add6ca508f33f9e4c41759925ebe0
- fig1_means.png, sha256 b00e2e67fd54daa2ce542db4c0ebeeba116f5bfd67c02f4415e6e636f8f6e1c9

## fig2_spread

The spread of the synthetic population against the published series: each cell's measured SD over the pooled published SD (bone and CT, Tan's SDs left out). One means the papers' spread; Panjabi's own SDs are shown beside the three settings of the generator. B keeps the levels that four measures or more reach.

- fig2_spread.caption.txt, sha256 91f97836d13427f5f3db8ed9b3772cc704878f11372965965ae29a154bd05db5
- fig2_spread.csv, sha256 3011cc94907f3e6c896e6fd428c1465656e3340e133c723bc27ef6bd6862f8c2
- fig2_spread.pdf, sha256 f9f8a7d77770efafac0d0eba64699101405485ea484d0e2c96ce5c89d2685734
- fig2_spread.png, sha256 b75e8afd13658a7f755e5fa92209650cbd3a09c07edd34dac9c764ad56b44539

## fig3_structure

What the means and SDs do not test. A, the canal's correlations with the body, synthetic against Griffith's 1,080 CTs; B, the share of the body's sex difference each measure carries (the generator scales all alike); C and D, two ratios by level against the papers that print them.

- fig3_structure.caption.txt, sha256 a4e352a3676070287cbaacdf8043b2fc228f7cdea01fe3a87fe9ada5646bc65f
- fig3_structure.csv, sha256 3edc06ac2966c52df71d2ea71f5494b7bb918b08a3e2633a2565c53ff0f8c8da
- fig3_structure.pdf, sha256 778045e6bbd98bf671c013b4054422bd6d10c5ad675f70a115aeea1f8d09e547
- fig3_structure.png, sha256 6bd82bd8b80ac0fece7c3de5f9f829373a07feb2ede280079d69fd84350e713d

## fig4_state_space

The generator's state space, one axis at a time from its own point (circled), and the grid searched for the point nearest the papers: the squared log SD ratio plus the mean squared distance from Griffith's four correlations.

- fig4_state_space.caption.txt, sha256 f315a75656434c590594598b255f80f71c3f1e2537b27cae67a520ab545245d4
- fig4_state_space.csv, sha256 be7a1cc4d6b1de1b17f822591a8cea4af4c2b5eb102f6f526a9d96cf69a9dfbc
- fig4_state_space.pdf, sha256 723087abcaba930433a1139e5dc7d0b8034208c42e0775b6462379470bd4f71c
- fig4_state_space.png, sha256 e3c4c215d64c7caf4e674e7ad5c09495e9114a2b23f6b3121555b3b43a83d527

## fig5_naming

Naming by the exact rule on the seven SPINEPS measures, with the CT's errors, at points of the state space: the rule built for the generator against one that knows the setting (no rule here holds phi or r_between). Bars are 95% intervals over the columns.

- fig5_naming.caption.txt, sha256 66b083cf92dbe6aa63e416c5d9e91cfaacf3f192da63e1ee6892d9c6f850666f
- fig5_naming.csv, sha256 a1d0634d19b2b8477634736c1c238fdd9d28c1d614455b321f03a93b4fcad339
- fig5_naming.pdf, sha256 4854ae19f0393292909dc7777f5d70288397a47aae5c04cfe93e0a19ede0de89
- fig5_naming.png, sha256 1f56d4a7f6240b2023f579940b1a148d553773aab884fbce4d02566281b51b17

## fig6_power

The power calculations rerun. A, the REML spread between published series over Panjabi's SD, cell by cell; B and C, the exact rule built on tables moved as the papers disagree; D to F, what a count of whole spines can test (two-sided, 5%, 80% power, exact tests; 159 marked).

- fig6_power.caption.txt, sha256 25017d97ea24c2eeebab2e88fb695b42b85e5a0a6e87bfc36cc50c21ba80e3bd
- fig6_power.csv, sha256 c976bfc6d8b3b5fb8091daac88eacb0e9caf092ee11488baf0661042e07f4224
- fig6_power.pdf, sha256 252691bbec85d4e81cbe6f6c7fbc9d71a1e5b479d54a4de2c4a2157767222f33
- fig6_power.png, sha256 5b6770fde2d86a71bade73888e7b1285f57f1aaa6a4a9a7a8a62d46d318c0a9d

## fig7_quality

Quality indicators of synthetic vertebrae: a length or area at or below zero (sign), a measured value at the floor, an area larger than its own width times depth (box), an end-plate under half of it (convex), a canal wider than its transverse processes (inside).

- fig7_quality.caption.txt, sha256 4fea894ebc27a136bf9c7fc470842fcbf8b5f14b4f58f4fa1e3881122b0af22a
- fig7_quality.csv, sha256 293542df36d77fa303a1e8ff03c6942441b60c3c1c076bacb756e2f388c12073
- fig7_quality.pdf, sha256 e890105027e96bdd84dffd47bca41cb12abc2375a87b96daba97c99b68a9f343
- fig7_quality.png, sha256 c2667286b96c9a3e296cdd42d0e7f6849b938d8b2c84a2755540215560fe1c29

## fig8_assumptions

Two things the generator assumes, set beside the papers. A, the error of one reading as the reread's error draft gives it from repeated readings; B, how often a column carries each anomaly, from Eisenstein's 443 skeletons and Duman's 517 chest CTs (the reread's checked priors).

- fig8_assumptions.caption.txt, sha256 76cd5264716e12a71779a37b618c32cc6060a4827bbb2a44061c81ac63950d0c
- fig8_assumptions.csv, sha256 8b070c05a976af6c912923cdf89ccf2b90dc812f4fe101b40729404b90a08bc6
- fig8_assumptions.pdf, sha256 6daed255c4b5320bbf7baa5d84692fc5eb3642f9a641fc0def51c40097abffef
- fig8_assumptions.png, sha256 4e639ad35edcc480694b506db921a0364fbfb5543d75ed1f9b1eed7dedf36634

## render1_axial

The third lumbar vertebra from above, anterior up, drawn to its measures: Panjabi's means, then three synthetic people the generator draws (seed 2029). Each section is the superellipse with the measured width, depth and area; dashed where no superellipse of those extents holds the area. Laminae and process thickness are drawn at fixed sizes.

- render1_axial.caption.txt, sha256 8ff28db63eeea3773cfc30113ae8b608b414ffef0ff2d1c07b8f886a3d614b4c
- render1_axial.csv, sha256 e1e5c128a1918fec1d96c91dfdf2ae4f5378ba17830b2c5d7ad61ba7a7d60c13
- render1_axial.pdf, sha256 0f26c5ea12871f214933f0d4e4f47133b561f811dfc3806e6f00b2d2a0340a45
- render1_axial.png, sha256 546a2f01479e1b0378570c71d472b59441f3d9e861ba4a73b48f42cbbbe42d8e

## render2_column

The lumbar column from in front, each body its end-plate width by its posterior height with the canal hatched over it and the transverse span as a line: Panjabi's means and two synthetic people. A heavy outline marks a body some quality indicator flags; the flags are named.

- render2_column.caption.txt, sha256 beb8d3df56eb01837aa2061608f3f22149c2a6b66cb1b472db44b01db53cf7fe
- render2_column.csv, sha256 0420dd5e3617d828542b936f6956c5f955b353006d0f89efc7e0635367687f53
- render2_column.pdf, sha256 6a733668fc21771eea771463b781fb85693b6561abec6cae4ceec23ed81f663e
- render2_column.png, sha256 7cfa7d0f8cc150b6a75a12ea22ca909c39aa2ed1338a9f6ea529cb5df22fb410

## render3_solid

Lumbar columns as solids, seen from the left and behind, shaded grey from one light: Panjabi's means and two synthetic people of the first drawing. Bodies are lofted between the two end-plates' superellipses; pedicles, laminae and processes are boxes, their thicknesses fixed.

- render3_solid.caption.txt, sha256 6d0f0e54c76c6b732e62a7719859a5c3a646e3bb5bf7399e309da89569bf4f78
- render3_solid.csv, sha256 9c735ec7bb926cfabc825a1a01d4a95be3d863d9745dfe88b9d5d52076458c20
- render3_solid.pdf, sha256 290537891137fd64589ffc38d980f08f942e206e9e5af2fd7185a7b85f87c86e
- render3_solid.png, sha256 fc2b7d5a1d4a9aa0fe23ceb0090401cf3bd5c0202cdccd72c499485892783d99
