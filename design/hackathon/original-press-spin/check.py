"""Independent checks against constructed solids and exported print meshes.
Nominal CAD, not physical certification. No source toy assumptions.
"""
import json, itertools, math
import numpy as np
import cad

def collisions(parts):
    result=[]
    for a,b in itertools.combinations(parts,2):
        v=cad.volume(parts[a],parts[b])
        if v>1e-5: result.append({'a':a,'b':b,'mm3':v})
    return result

def main():
    p=cad.parts(); m5=cad.box(48,24,15,z=4.8)
    report={'physical_printed':False,'vendor':'M5StickS3 K150 only','m5_bounds_mm':[[-24,-12,4.8],[24,12,19.8]],
        'neutral_collisions':collisions({**p,'m5':m5})}
    print('neutral',report['neutral_collisions'],flush=True)
    report['rotation']=[]
    stationary={k:v for k,v in p.items() if k!='wheel'}
    for angle in range(0,361,15):
        rotor=p['wheel'].rotate((cad.RX,0,0),(cad.RX,0,1),angle)
        hits={k:cad.volume(rotor,v) for k,v in {**stationary,'m5':m5}.items()}
        report['rotation'].append({'angle_deg':angle,'max_mm3':max(hits.values()),'failures':{k:v for k,v in hits.items() if v>1e-5}})
    report['rotation_continuous_envelope']={k:cad.volume(cad.ring(15,6.25,5,cad.RX,0,27.4),v) for k,v in {**stationary,'m5':m5}.items()}
    report['press']=[]
    for delta in np.linspace(0,cad.TRAVEL,15):
        spring=cad.spring(delta=float(delta))
        hits={k:cad.volume(spring,v) for k,v in {**{k:v for k,v in p.items() if k!='press_leaf'},'m5':m5}.items()}
        report['press'].append({'deflection_mm':float(delta),'failures':{k:v for k,v in hits.items() if v>1e-5}})
    # Drawer insertion from negative X, lock key removed. Board travels with tray.
    report['drawer_path']=[]
    for x in np.linspace(-65,0,27):
        hits={}
        for name,part in {'tray':p['m5_tray'],'m5':m5}.items():
            for k,v in p.items():
                if k in ['m5_tray','drawer_key']: continue
                amount=cad.volume(part.translate((float(x),0,0)),v)
                if amount>1e-5: hits[name+'/'+k]=amount
        report['drawer_path'].append({'x_offset_mm':float(x),'failures':hits})
    # Plug bodies + insertion travel reserve, based on official end arrangement.
    # USB and Grove at +X end; pin-header at -X not guaranteed accessible.
    usb=cad.box(22,14,6,35,0,7.5)
    grove=cad.box(22,14,7,35,0,12.5)
    report['connector_corridors']={label:{k:cad.volume(shape,v) for k,v in p.items()} for label,shape in [('USB_14x6_body',usb),('Grove_14x7_body',grove)]}
    # PLA + normal metal fasteners: omit PETG flex parts; rotor remains usable.
    metal={k:v for k,v in p.items() if k not in ['rotor_pin','rotor_clip','press_leaf','press_pin_a','press_pin_b','drawer_key']}
    metal.update({k:v for k,v in cad.alternatives().items() if k.startswith('metal')})
    metal.update(cad.metal_reference())
    report['PLA_metal_rotation_collisions']=collisions({**metal,'m5':m5})
    report['minimums_mm']={'wheel_radial_clearance':.25,'wheel_axial_up_clearance':.6,
      'pin_to_m5_clearance':1.2,'clip_to_m5_clearance':2.4,'drawer_rail_side':.4,
      'tray_to_device_X':.4,'leaf_thickness':1.2,'soft_leaf_thickness':1.,
      'printed_thrust_ring_thickness':.4,'snap_leg_thickness':.9}
    report['elastic_assumptions']={'leaf_formula':'3*t*d/(2*L^2), L20mm, no fatigue/FEA validation',
      'leaf_nominal_peak_strain':3*1.2*1.4/(2*20**2),
      'press_snap_radial_deflection_mm':.3,'drawer_key_tip_deflection_mm':.15,
      'rotor_C_clip_mouth_expansion_total_mm':.4,'material':'PETG for full flex build; PLA rotation mode uses metal retention',
      'warning':'Elastic assembly stages are NOT collision-free rigid insertion; calibration must pass before full build.'}
    errors=[]
    for label in ['neutral_collisions','PLA_metal_rotation_collisions']:
        if report[label]: errors.append(label)
    for label in ['rotation','press','drawer_path']:
        if any(row['failures'] for row in report[label]): errors.append(label)
    if any(v>1e-5 for v in report['rotation_continuous_envelope'].values()): errors.append('rotation_continuous_envelope')
    if any(v>1e-5 for group in report['connector_corridors'].values() for v in group.values()): errors.append('connector_corridors')
    report['errors']=errors
    (cad.OUT/'mechanical_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('ERRORS',errors,flush=True)
    assert not errors
if __name__=='__main__': main()
