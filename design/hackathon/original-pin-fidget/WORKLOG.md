# 原创十粒掌盘 / WORKLOG
2026-09-22 Scope changed by Kim: complete original printable mechanical EDC, no source-toy dependency.
Branch codex/original-pin-fidget from origin/main 833ee4b. All writes owned by this worktree.
Original architecture: ten captive 6mm rounded sliding pins, 3.2mm travel, five columns/two rows; separate guide plate, spacer, structural deck, removable M5 sled, mirrored retaining rails. M5 nominal 48x24x15 kept whole. Open both short ends for USB/Grove and HAT; no copied MakerWorld geometry.
Official M5 PDF visually inspected; official STL local-only previously verified assembled envelope approx24.001x48.002x15. Ports: USB/Grove high-Y end, HAT low-Y, front button low-Y. Use whole-end access and conservative cable envelope instead of guessed narrow aperture.
Next: generated solids, assembly/fastener/cable/motion checks, calibration coupon, print orientations, independent testing.

First geometry iteration: corrected four sled skirt/post overlaps (1.19mm³ each), then added four spacer screw-pass holes for long front bolts. Pin-only full-travel checks passed before hardware correction. Added printable calibration roof so trial chamber is complete.

O-PIN-01 fixed: locating ears now reach Y=3 and39, around unchanged Y6/36, R1.75 holes. Outer lip1.25mm, full build passes again. Official source containment/guard test added, independent b4ba300 direct three-shell/32-solid check cited without claiming physical actuation. Business mappings now defer to USER_JOURNEY and firmware task.
