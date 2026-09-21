"""Additional independent probes against archived artifacts, not author JSON."""
import json, pathlib, cadquery as cq, trimesh as tm
r=pathlib.Path('.local/audit')
def cylinder(x,radius):
    return cq.Workplane('XY').center(x,0).circle(radius).extrude(3)
baseline=['9617a85ecac72aca835b35ad6ff31bf38a961ecf','5671da9560c9cf4d59e8d8b7a0ae00e196fc6e8b','9591aa5f5f97bfa24b1af5b126e911e062610498']
out={'pin_head_probe':{'sha':baseline[0],'pitch_mm':5,'head_diameter_mm':6,'head_height_mm':3,'overlap_mm3':cylinder(-7,3).intersect(cylinder(-2,3)).val().Volume()}}
for folder in r.iterdir():
    if folder.name not in baseline: continue
    for sub in (folder/'design/hackathon').iterdir():
        files=list(sub.rglob('*.stl'))
        volume=sum(tm.load_mesh(f).volume*(2 if f.stem in ['lower_clamp','upper_clamp'] else 1) for f in files)
        out[folder.name]={'scheme':sub.name,'printed_solid_volume_cm3':round(volume/1000,3),'solid_PETG_mass_g_at_assumed_1p27':round(volume/1000*1.27,2),'mass_is_not_sliced_or_measured':True}
pathlib.Path('docs/hackathon/testing/probes.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out,indent=2))
