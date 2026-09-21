# Validation scope

The exported validation.json is generated from CAD boolean intersections and STL topology.

Checks required before this independent prototype can be reviewed:
- Each of four printable parts: positive volume, single connected component, watertight, consistent winding.
- Every pair of six assembled printed instances plus nominal M5 envelope: intersection volume below 1e-5 mm³.
- Source parameters are explicitly UNMEASURED and restricted to prototype range.
- Preview is rendered from the exact CAD solids exported to STEP/STL.

Not covered by those numerical checks:
- Original pinboard rim interface, pin sweep, sliding tolerances, static-frame deformation.
- Actual M5 USB plug shell and keys, RF attenuation, thermal conditions.
- Printed fit, screw pullout, grip, fatigue, dropping, material shrinkage.

No physical print performed. No source pinboard fit claimed.

## Executed results (2026-09-22)
Four STL parts passed topology checks; each has one closed consistently wound component. 21 assembled-pair intersections were zero. Two clamps each passed 11 closure samples over 0.4 mm. STEP roundtrip: four valid positive-volume individual solids and six valid assembly solids. Assembly/exploded renders visually inspected after fixing per-object depth sorting. See exports/validation.json and step_roundtrip.json. These results do not close the explicitly blocked original-pinboard fit or physical-print gates.
