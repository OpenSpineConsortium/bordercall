# morphometry enhance: job 40872077 on vm, commit 2ff760a, 2026-10-30 17:19:47 UTC
- interpreter: /tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/venv/bin/python (3.13.17) for the measuring
- bordercall copy: bordercall 16f7b40540fafd86fef98737c8666a271944705f OpenSpineConsortium/bordercall
- code stamp: 81e732f142d3aa16
- screening interpreter: /tmp/tmpia83ao2s/go2432/morphometry/enhance/env/bin/python, a throwaway venv on the measuring interpreter with icontract==2.7.3 beartype==0.23.1
- ENHANCE.PET: 2 masks linked; 2 studies chosen, 2 to measure, code 81e732f142d3aa16; 0 studies flagged error; 6 s wall; its lines in /tmp/tmpia83ao2s/go2432/morphometry/enhance/run.log
- ENHANCE.PET rows: /tmp/tmpia83ao2s/go2432/morphometry/enhance/rows.csv (19306 bytes, sha256 7f856444937bcdef8b62f2aab3882b026157e5fcb8d24c8176168f8fa25972f3)
- ENHANCE.PET per level (rows with h_post_inset, medians over values that parse as finite):
    | level | n (h_post_inset) | median h_ant | median h_post_inset | median body_index_ant_post |
    |---|---|---|---|---|
    | L2 | 1 | 27.13 | 27.13 | 1.000 |
    | L3 | 2 | 27.16 | 27.09 | 1.002 |
    | L4 | 2 | 27.14 | 27.12 | 1.001 |
    | L5 | 1 | 27.08 | 27.16 | 0.997 |
- FAILED at facts:   File "/tmp/tmpia83ao2s/old/grid/bordercall/screening/contracts.py", line 18, in <module>     from beartype import beartype ModuleNotFoundError: No module named 'beartype' 
- FAILED at whole:   File "/tmp/tmpia83ao2s/old/grid/bordercall/screening/contracts.py", line 18, in <module>     from beartype import beartype ModuleNotFoundError: No module named 'beartype' 
- ENHANCE.PET facts: /tmp/tmpia83ao2s/go2432/morphometry/enhance/facts.jsonl (not written)
- ENHANCE.PET verdicts: /tmp/tmpia83ao2s/go2432/morphometry/enhance/verdicts.csv (not written)
- every step's full output is under /tmp/tmpia83ao2s/go2432/morphometry/enhance/<step>.log (and /tmp/tmpia83ao2s/go2432/morphometry/enhance/totalseg/<step>.log); only the aggregates above leave the grid
- exit 0 at 2026-10-30 17:19:54 UTC
