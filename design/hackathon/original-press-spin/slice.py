"""Actual PrusaSlicer CLI screen. G-code ignored, never a machine-ready delivery.
python slice.py --slicer PATH_TO_PRUSA_SLICER_CONSOLE
"""
import argparse,subprocess,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
a=argparse.ArgumentParser(); a.add_argument('--slicer',required=True); a.add_argument('--only',nargs='*'); args=a.parse_args()
out=ROOT/'_checks'; out.mkdir(exist_ok=True)
petg=(ROOT/'slice_screen_pla.ini').read_text().replace('filament_type = PLA','filament_type = PETG').replace('temperature = 210','temperature = 240').replace('bed_temperature = 60','bed_temperature = 80')
(out/'petg.ini').write_text(petg)
report=json.loads((ROOT/'slicing_report.json').read_text()) if args.only and (ROOT/'slicing_report.json').exists() else {'profile_status':'generic 220x220, not machine-qualified; G-code excluded from delivery','parts':{}}
for file in sorted((ROOT/'stl').glob('*.stl')):
    name=file.stem; flex=name.startswith('press_') or name in ['rotor_clip','cal_clip_open','cal_snap_pin','drawer_key']
    if args.only and name not in args.only: continue
    profile=out/'petg.ini' if flex else ROOT/'slice_screen_pla.ini'
    gcode=out/(name+'.gcode')
    cmd=[args.slicer,'--datadir',str(out/'prusa-profile'),'--load',str(profile),'--export-gcode','--output',str(gcode),'--center','110,110']
    if name=='body': cmd+=['--support-material','--brim-width','6']
    if name=='metal_rotor_sleeve': cmd+=['--brim-width','3']
    cmd.append(str(file)); start=time.time()
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    (out/(name+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
    text=gcode.read_text(encoding='utf-8',errors='replace') if gcode.exists() else ''
    warnings=[line for line in (r.stdout+'\n'+r.stderr).splitlines() if any(w in line.lower() for w in ['warn','error','empty','repair'])]
    metadata={key:re.findall(r'; '+re.escape(key)+r'\s*=\s*(.+)',text) for key in ['filament used [mm]','filament used [g]','estimated printing time (normal mode)']}
    report['parts'][name]={'exit_code':r.returncode,'material_profile':'PETG' if flex else 'PLA','support':name=='body','layer_changes':text.count(';LAYER_CHANGE'),
         'extrusion_commands':len(re.findall(r'^G1 .*E[\d.-]+',text,re.M)),'gcode_bytes':len(text),'warnings':warnings,'metadata':metadata,'seconds':round(time.time()-start,2)}
    print(name,r.returncode,report['parts'][name]['layer_changes'],warnings,flush=True)
    (ROOT/'slicing_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert r.returncode==0 and report['parts'][name]['layer_changes']>0 and report['parts'][name]['extrusion_commands']>0,name
