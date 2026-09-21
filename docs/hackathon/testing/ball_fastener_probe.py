"""Test a conditional bottom washer envelope; not a chosen production fastener."""
import pathlib,json,trimesh as tm
f=next(pathlib.Path('.local/audit').glob('9591*/design/hackathon/*/palm_cradle.stl'))
base=tm.load_mesh(f); out={'sha':'9591aa5f5f97bfa24b1af5b126e911e062610498','washer_od_mm':7,'washer_height_mm':.5,'washer_z_mm':[2.5,3],'overlap_mm3':{}}
for x in [35,65]:
    for y in [-27,27]:
        outer=tm.creation.cylinder(radius=3.5,height=.5,sections=64);outer.apply_translation([x,y,2.75])
        inner=tm.creation.cylinder(radius=1.7,height=2,sections=64);inner.apply_translation([x,y,2.75])
        washer=tm.boolean.difference([outer,inner],engine='manifold')
        hit=tm.boolean.intersection([washer,base],engine='manifold')
        out['overlap_mm3'][f'{x},{y}']=float(hit.volume) if len(hit.faces) else 0
pathlib.Path('docs/hackathon/testing/ball_fastener_probe.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(out)
