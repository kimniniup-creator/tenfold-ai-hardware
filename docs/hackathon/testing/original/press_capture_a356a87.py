import sys,json,pathlib
folder=pathlib.Path('.local/original-audit/a356a870456fc85082aeabbc974698314f6ee273/design/hackathon/original-press-spin');sys.path.insert(0,str(folder));import cad
p=cad.parts();m5=cad.box(48,24,15,z=4.8)
tests={'wheel_up_0p7_vs_pin':cad.volume(p['wheel'].translate((0,0,.7)),p['rotor_pin']),'rotor_pin_up_0p5_vs_clip':cad.volume(p['rotor_pin'].translate((0,0,.5)),p['rotor_clip']),'drawer_out_1_vs_key':cad.volume(p['m5_tray'].translate((-1,0,0)),p['drawer_key']),'press_pin_up_0p5_vs_body':cad.volume(p['press_pin_a'].translate((0,0,.5)),p['body']),'m5_up_0p7_vs_body':cad.volume(m5.translate((0,0,.7)),p['body']),'m5_down_0p7_vs_tray':cad.volume(m5.translate((0,0,-.7)),p['m5_tray'])}
r={'sha':'a356a870456fc85082aeabbc974698314f6ee273','scope':'Rigid sampled positive-stop checks only. Does not validate clip elasticity, loads, fatigue or all escape paths.','physical_tested':False,'intersection_mm3':tests}
pathlib.Path('docs/hackathon/testing/original/press-a356a87-capture.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
