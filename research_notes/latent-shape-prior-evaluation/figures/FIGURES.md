# Figures

Drawn by `python3 -I figures.py --out figures` from fig1_design.csv and fig2_stages.csv beside this file;
each figure's caption is its .caption.txt. Nothing here is a result: the figures draw the plan itself.

## fig1_design

The design matrix of the plan: six arms down the side (A the rules as they stand, B the pure latent PDM, C the hybrid, C0 the latent head with no prior, D the heatmap head with the PDM penalty, E the named values predicted directly), what each is scored on across the top. A filled square is a primary endpoint or one of the two calibration gates (coverage at one and two spreads on the test persons, and sharpness); an open square is reported beside them as the price or the diagnosis; a blank means the quantity does not exist for that arm (E draws no line and has no modes). Arm A's modes are read through the projection of its landmarks onto the PDM. Nothing here is a result.

- fig1_design.caption.txt, sha256 f94bf601be323b5fcbfdbc10f2843b164413d35e18d6c7400354aa3eb2cd0520
- fig1_design.csv, sha256 535a20cec39c4e4380ce20d5c3282afa4ab11a942bd25ff4a8278b4d0f703398
- fig1_design.pdf, sha256 0ea36633d5c0a733138da7009f8226e1f3c9c738c0df6f933360f4277c4dc5f7
- fig1_design.png, sha256 cddc02651fbcfd123f52802115f1137a5feecf20c48c51787e005064684c46a9

## fig2_stages

The stages in order, each bar the grid jobs it would ask for (black) or none (white, a container or the flow's own end step), with the decision it informs. Stage 1 asks for no job of its own only where the line-end export and morphoview reach SchwingNet's pinned copy of bordercall before the two morphometry jobs the owner counted on 2026-10-29 are sent; stage 3 asks for none where the heads join the phantom_smoke plan another thread is writing. Stage 4 is a fixed design, every trial read on the test persons, not the search flow's halving. Every count waits for the owner's word; none has been sent.

- fig2_stages.caption.txt, sha256 687f77b49723ba52abf6071ee35f7d7485ce0130fc64f91b35d724302d0b6139
- fig2_stages.csv, sha256 812c1d8509e520496bfdd9afb0b9932841bdff5f2faf1badf96aec6ecab14aa8
- fig2_stages.pdf, sha256 a2283000b059c8016cf11cadef796148de0f8ded08a31e1108bfbba16f29bf96
- fig2_stages.png, sha256 d86de595918746d460d57249169bf31c7c6ddcd6347f99e21310d62cff368d36
