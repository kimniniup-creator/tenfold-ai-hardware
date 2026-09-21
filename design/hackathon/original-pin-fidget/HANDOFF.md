# HANDOFF — 原创十粒掌盘

Branch: codex/original-pin-fidget. Own background worktree D:\tenfold-worktrees\471703.
Formal output: design/hackathon/original-pin-fidget/.
Kim changed scope to complete original printable EDC. No original toy source files required. All toy geometry is original elementary CAD; M5 references remain local-only.

Default envelope: 70×42×29.2 body, 32.4 including extended pins. Ten pins Ø6 with Ø8.8 captive flange, stroke3.2, guideØ6.6, chamberØ9.5. Roof is separate structural deck2.4 thick, M5 isolated above sled1.2+EVA0.5. Front rails retain full M5. Screws: 4 M3×25 countersunk front; 4 M3×16 countersunk rear; 8 M3 AF5.5 nuts; 2mm hex driver. No springs/magnets/bearings.

Build: Python3.13 + requirements.txt; python build.py. STL print transforms already applied: pins flange down, rails top face down, all others flat. Formal STEP maintains assembly coordinates. Calibration guide has radial .2/.3/.4 holes from left to right, chamber5.2 and roof2.4 plus production pin form a hand-held trial.

Manufacturing candidates only. No physical print, gravity-return, friction, durability, electronics actuation or thermal performance tested. Do not call them proven. Source interfaces from old project do not block this original design. Independent testing should use default M5 params first; alternate board params need their own checks.

Initial checks caught sled/frame corner overlap and unrelieved long front screw shafts in spacer; fixed with0.3mm corner relief and four shaft holes. Continue on published commits only; do not edit another task worktree.

Default geometry frozen at fff72958bb91eae20329228ae780f97f60e82f3b. Independent tester confirms corrected sled/pin100% rectilinear slicing exit0/no empty layers, sled sampled min1.2mm and no sample<.8,9 STL rebuilds consistent,11 STEP valid,official3-shell/32-solid intersections0. O-PIN-01 digitally closed. Added three print plates,PRINT_FIRST and Chinese assembly card without part changes. Physical actuation/gravity-return/feel remain untested.

2026-09-22 independent test confirms5526578 three arranged plates actually sliced by Prusa: calibration/details100% rectilinear,structure25%; all exit0,no empty extrusion layers. Default geometry remainsfff7295. No physical print or feel/return/button pass claimed.
