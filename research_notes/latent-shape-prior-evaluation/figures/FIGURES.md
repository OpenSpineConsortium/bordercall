# Figures

Drawn by `python3 -I figures.py --out figures` from fig1_design.csv and fig2_stages.csv beside this file;
each figure's caption is its .caption.txt. Nothing here is a result: the figures draw the plan itself.

## fig1_design

The design matrix of the plan: six arms down the side (A the rules as they stand, B the pure latent PDM, C the hybrid, C0 the latent head with no prior, D the heatmap head with the PDM penalty, E the named values predicted directly), what each is scored on across the top. A filled square is a primary endpoint or one of the two calibration gates (coverage at one and two spreads on the test persons, and sharpness); an open square is reported beside them as the price or the diagnosis; a blank means the quantity does not exist for that arm (E draws no line and has no modes). Arm A's modes are read through the projection of its landmarks onto the PDM. Nothing here is a result.

- fig1_design.caption.txt, sha256 f94bf601be323b5fcbfdbc10f2843b164413d35e18d6c7400354aa3eb2cd0520
- fig1_design.csv, sha256 535a20cec39c4e4380ce20d5c3282afa4ab11a942bd25ff4a8278b4d0f703398
- fig1_design.pdf, sha256 40e6337c60421bf027a5d604d1ff20354f276ad93760ca28a3ac22140d0805c9
- fig1_design.png, sha256 cddc02651fbcfd123f52802115f1137a5feecf20c48c51787e005064684c46a9

## fig2_stages

The stages in order, each bar the grid jobs it would ask for (black) or none (white, a container or the flow's own end step), with the decision it informs. Stage 1 asks for no job of its own only where the line-end export and morphoview reach SchwingNet's pinned copy of bordercall before the two morphometry jobs the owner counted on 2026-10-29 are sent; stage 3 asks for none where the head block joins the phantom_smoke plan another thread is writing before its PREREG is frozen. Stage 4 is the screen greg asked for on 2026-10-30: every arm in parallel on a short run of 50 epochs, each trial an array task on a card of its own and a merge run after it, read on validation; stage 5 the full run of what it keeps, the same two jobs, every trial read once on test, in a fixed design and not the search flow's halving. Every count waits for the owner's word; none has been sent.

- fig2_stages.caption.txt, sha256 15aeb91758cef85fb7d8ec54555eb341df5d9eb148940c3452632b1fb0a4b6e0
- fig2_stages.csv, sha256 c464fc200d34a47514818b01463117aaea9fd34ff46b4cc22fd8560ab1dd32e6
- fig2_stages.pdf, sha256 ff4389b755ffedeae2ec0a08a2ce5a27dbacfcca08f990ffc97610df73915a48
- fig2_stages.png, sha256 e4416f053104568d0fe7a7cdead7cabf44bc06acd57db9e8daeb5d4d145bf7c0
