"""Original parametric accessory, mm. NO MakerWorld geometry included.
python build.py exports STEP/STL, assembly/exploded PNG and validation.json.
Source model fit is deliberately NOT asserted. See README.md.
"""
from pathlib import Path
import json, math
import cadquery as cq
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT=Path(__file__).resolve().parent
P=dict(device_l=48.,device_w=24.,device_h=15.,clearance=.6,
       device_x=0.,mount_x=0.,static_grip_width=22.,pad=1.,
       hypothetical_rotor_radius=28.,hypothetical_rotor_bottom=41.)
def box(l,w,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(l,w,h,centered=(True,True,False)).translate((x,y,z))
def hole(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))
def slot(x,y,l,w,z,h):
    return cq.Workplane('XY').center(x,y).slot2D(l,w,90).extrude(h).translate((0,0,z))

def build():
    # Compact two-sided stack. Screen faces down; mechanism sits on upper deck.
    base=box(54,48,3,0,0,24).edges('|Z').fillet(3)
    for s in [-1,1]:
        for t in [-1,1]:
            base=base.union(box(6,6,22,s*23.7,t*16.5,2))
            base=base.cut(hole(s*23.7,t*16.5,1,1.7,28))
            base=base.union(box(2.4,4,22,s*25.8,t*8,2))
            # Rear corner stops limit lift; 0.6 mm above official device box.
            base=base.union(box(4,4,2,s*23.6,t*8,18.2))
    # Two long jaw adjustment slots. Two bolts per jaw prevent twisting.
    for x in [P['mount_x']-9,P['mount_x']+9]:
        for s in [-1,1]:
            base=base.cut(slot(x,s*14,15,3.4,23,6))
    # Raised seat: static source foot rests on an adhesive rubber pad here.
    base=base.union(box(26,10,4,P['mount_x'],0,27))
    parts={'spine':base}
    # Two jaw blocks: inward face +1 mm pad, 10..30 mm clear grip range.
    for s,name in [(1,'jaw_front'),(-1,'jaw_back')]:
        inner=P['static_grip_width']/2+P['pad']
        jaw=box(26,7,9,P['mount_x'],s*(inner+3.5),27)
        for x in [P['mount_x']-9,P['mount_x']+9]:
            jaw=jaw.cut(hole(x,s*(inner+3.5),26,1.7,12))
            jaw=jaw.cut(hole(x,s*(inner+3.5),33,3.2,4))
        parts[name]=jaw
    # Removable screen-side bars, 44.4 mm central opening along X.
    for s,name in [(-1,'retainer_left'),(1,'retainer_right')]:
        bar=box(3,40,2,s*23.7,0,0)
        for t in [-1,1]:
            # Local bosses allow M3 holes without leaving thin split webs.
            bar=bar.union(box(6,6,2,s*23.7,t*16.5,0))
            bar=bar.cut(hole(s*23.7,t*16.5,-1,1.7,4))
        parts[name]=bar
    return parts

def mesh(shape):
    verts,faces=shape.val().tessellate(.12,.15)
    return trimesh.Trimesh(vertices=[v.toTuple() for v in verts],faces=faces,process=True)

def hardware():
    result={}
    for x in [-9,9]:
        for s in [-1,1]:
            y=s*(P['static_grip_width']/2+4.5)
            result[f'jaw_bolt_{x}_{s}']=hole(x,y,19,1.5,14).union(hole(x,y,33,3,3))
            result[f'jaw_nut_{x}_{s}']=hole(x,y,20.5,3.2,3).cut(hole(x,y,20,1.5,5))
            result[f'jaw_washer_{x}_{s}']=hole(x,y,23.5,4.5,.5).cut(hole(x,y,23,1.7,2))
    for x in [-23.7,23.7]:
        for y in [-16.5,16.5]:
            result[f'corner_bolt_{x}_{y}']=hole(x,y,0,1.5,32).union(hole(x,y,-3,3,3))
            result[f'corner_washer_{x}_{y}']=hole(x,y,27,3,.5).cut(hole(x,y,26,1.7,3))
            result[f'corner_nut_{x}_{y}']=hole(x,y,27.5,3.2,3).cut(hole(x,y,27,1.5,5))
    return result

def overlap_volume(a,b):
    # Broad-phase only skips disjoint/tangent bounding boxes, never penetration.
    aa=a.val().BoundingBox(); bb=b.val().BoundingBox()
    if any(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-
           max(getattr(aa,k+'min'),getattr(bb,k+'min'))<=1e-8 for k in 'xyz'):
        return 0.
    hit=a.intersect(b)
    return float(hit.val().Volume()) if hit.vals() else 0.

def validate_hardware(parts,env):
    hw=hardware(); groups={
        'hardware_printed':[(a,b,x,y) for a,x in hw.items() for b,y in parts.items()],
        'hardware_pairs':[(a,b,hw[a],hw[b]) for i,a in enumerate(hw) for b in list(hw)[i+1:]],
        'hardware_m5':[(a,'m5',x,env) for a,x in hw.items()]}
    out={}
    for group,pairs in groups.items():
        failures=[]; maximum=0.
        for a,b,x,y in pairs:
            volume=overlap_volume(x,y); maximum=max(maximum,volume)
            if volume>1e-6: failures.append({'a':a,'b':b,'volume_mm3':volume})
        out[group]={'tested_pairs':len(pairs),'max_intersection_mm3':maximum,'failures':failures}
        assert not failures,(P['static_grip_width'],group,failures)
    return out

def tool_paths(parts,env):
    """Straight insertion envelopes, source absent; nut sockets are <=8 mm OD.
    Jaw socket stage excludes M5 and retainers (install them afterwards).
    Target fastener contact is intentional; all other hardware is checked.
    """
    hw=hardware(); results=[]
    for key,target in list(hw.items()):
        if '_washer_' in key: continue
        b=target.val().BoundingBox(); x=(b.xmin+b.xmax)/2; y=(b.ymin+b.ymax)/2
        family,kind,_=key.split('_',2)
        suffix=key.split('_',2)[2]
        if kind=='bolt':
            tool=hole(x,y,36 if family=='jaw' else -23,1.3,20)
            stage={**parts,'m5':env}
        elif family=='jaw':
            tool=hole(x,y,-3,4,26.5)
            stage={'spine':parts['spine'],'jaw_front':parts['jaw_front'],'jaw_back':parts['jaw_back']}
        else:
            tool=hole(x,y,27.5,4,25)
            stage={**parts,'m5':env}
        for name,shape in hw.items():
            # Socket/driver must engage own fastener; bolt inside nut socket allowed.
            if name in {family+'_bolt_'+suffix,family+'_nut_'+suffix}: continue
            stage[name]=shape
        failures=[{'obstacle':name,'volume_mm3':overlap_volume(tool,shape)}
                  for name,shape in stage.items() if overlap_volume(tool,shape)>1e-6]
        results.append({'target':key,'tool':'driver_radius1.3' if kind=='bolt' else 'socket_OD8',
                        'stage':'before M5/retainers' if family=='jaw' and kind=='nut' else 'source absent',
                        'failures':failures})
        assert not failures,(P['static_grip_width'],key,failures)
    return results

def continuous_sweeps(parts,env):
    # Filled outer envelopes conservatively include every point of moving hardware
    # over width10..30. Holes are deliberately filled, so this cannot miss collision
    # with static spine/retainers/M5 or another independently moving fastener group.
    sweeps={}
    for x in [-9,9]:
        for s in [-1,1]:
            shape=None
            for r,z,h in [(1.5,19,14),(3,33,3),(3.2,20.5,3),(4.5,23.5,.5)]:
                component=slot(x,s*14.5,10+2*r,2*r,z,h)
                shape=component if shape is None else shape.union(component)
            sweeps[f'{x}_{s}']=shape
    static={'spine':parts['spine'],'retainer_left':parts['retainer_left'],
            'retainer_right':parts['retainer_right'],'m5':env,
            **{k:v for k,v in hardware().items() if k.startswith('corner')}}
    checks=[]
    for name,shape in sweeps.items():
        for obstacle,other in static.items(): checks.append((name,obstacle,overlap_volume(shape,other)))
    for i,name in enumerate(sweeps):
        for other in list(sweeps)[i+1:]: checks.append((name,other,overlap_volume(sweeps[name],sweeps[other])))
    for side in [-1,1]:
        jaw_sweep=box(26,17,9,0,side*14.5,27)
        for name,shape in hardware().items():
            if name.startswith('corner'):
                checks.append(('jaw_sweep_'+str(side),name,overlap_volume(jaw_sweep,shape)))
        for name,shape in sweeps.items():
            if int(name.rsplit('_',1)[1])!=side:
                checks.append(('jaw_sweep_'+str(side),name,overlap_volume(jaw_sweep,shape)))
    failures=[{'a':a,'b':b,'volume_mm3':v} for a,b,v in checks if v>1e-6]
    assert not failures,failures
    return {'grip_range_mm':[10,30],'method':'continuous conservative capsule sweeps of 4 moving fastener groups',
            'tested_pairs':len(checks),'max_intersection_mm3':max(v for _,_,v in checks),'failures':failures}

def render(parts, exploded=False):
    fig=plt.figure(figsize=(12,8),facecolor='#f4f3ef'); ax=fig.add_subplot(111,projection='3d')
    ax.set_facecolor('#f4f3ef')
    colors=['#485763','#80a49c','#80a49c','#b4bec5','#b4bec5']
    polygons=[]; facecolors=[]
    from matplotlib.colors import to_rgb
    def add_mesh(m,color,shift=np.zeros(3),alpha=1):
        polygons.extend((m.vertices+shift)[m.faces])
        light=np.array([-.3,-.5,.8]); light/=np.linalg.norm(light)
        brightness=.58+.42*np.clip(m.face_normals@light,0,1)
        rgb=np.array(to_rgb(color))
        facecolors.extend([(*np.clip(rgb*b,0,1),alpha) for b in brightness])
    for i,(name,shape) in enumerate(parts.items()):
        m=mesh(shape); shift=np.array([(-1 if i==3 else 1)*9 if exploded and i>=3 else 0,(-1 if i==2 else 1)*8 if exploded and i in [1,2] else 0,18 if exploded and i in [1,2] else (-14 if exploded and i>=3 else 0)])
        add_mesh(m,colors[i],shift)
    if not exploded:
        for shape in hardware().values():
            add_mesh(mesh(shape),'#a7a8a6')
    # Abstract M5 envelope, not a vendor model. Display faces downward.
    env=mesh(box(48,24,15,0,0,2.6+(-6 if exploded else 0)))
    add_mesh(env,'#e49c58')
    ax.add_collection3d(Poly3DCollection(polygons,facecolors=facecolors,edgecolor='none',zsort='average'))
    # Only abstract dashed keep-out, NEVER reconstruct branded source bottle.
    a=np.linspace(0,2*np.pi,100); r=P['hypothetical_rotor_radius']
    ax.plot(r*np.cos(a),r*np.sin(a),np.full(100,P['hypothetical_rotor_bottom']),color='#9a609a',ls='--',lw=1.3)
    ax.text2D(.04,.85,'SOURCE OMITTED\nFit not verified',transform=ax.transAxes,fontsize=10,color='#7a417a')
    ax.text2D(.68,.85,'M5 48 x 24 x 15\nScreen faces DOWN',transform=ax.transAxes,fontsize=9)
    ax.set(xlim=(-40,40),ylim=(-36,36),zlim=(-16 if exploded else -3,68),xlabel='X / mm',ylabel='Y / mm',zlabel='Z / mm')
    ax.set_box_aspect((80,72,84 if exploded else 71)); ax.view_init(24,-65)
    ax.set_title('PRESS / SPIN SADDLE — '+('EXPLODED' if exploded else 'ASSEMBLY')+'\nOriginal accessory only | purple = assumed motion envelope',fontsize=14,pad=20)
    plt.tight_layout(); fig.savefig(OUT/('exploded.png' if exploded else 'assembly.png'),dpi=180); plt.close(fig)

def grip_diagram():
    from matplotlib.patches import Rectangle, FancyArrowPatch
    fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='#f4f3ef')
    for ax in axes:
        ax.set_facecolor('#f4f3ef'); ax.set_aspect('equal'); ax.set_xlim(-43,43); ax.set_ylim(-15,86)
        ax.axis('off')
    ax=axes[0]
    for x,y,w,h,col in [(-27,24,54,3,'#485763'),(-27,2,6,22,'#485763'),(21,2,6,22,'#485763'),(-24,2.6,48,15,'#e49c58'),(-13,27,26,4,'#80a49c')]:
        ax.add_patch(Rectangle((x,y),w,h,color=col))
    ax.add_patch(Rectangle((-28,41),56,35,fill=False,ls='--',lw=1.5,edgecolor='#9a609a'))
    ax.text(0,60,'UNKNOWN SOURCE\nR28 / H35 example only',ha='center',fontsize=9,color='#7a417a')
    ax.annotate('Thumb: press / turn',xy=(0,76),xytext=(-39,82),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.annotate('Hold structural posts',xy=(-25,14),xytext=(-40,-10),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.text(0,9,'M5 screen DOWN',ha='center',fontsize=9)
    ax.set_title('SIDE / FIDGET POSTURE\n54 x 48 x 39 mm incl. screw heads',fontsize=12)
    ax=axes[1]
    ax.add_patch(Rectangle((-27,8),54,48,fill=False,lw=2,edgecolor='#485763'))
    ax.add_patch(Rectangle((-24,20),48,24,facecolor='#e49c58',alpha=.7))
    for x in [-25.2,22.2]: ax.add_patch(Rectangle((x,12),3,40,color='#b4bec5'))
    ax.text(0,32,'M5 front envelope\n44.4 mm opening\nControl positions unverified',ha='center',va='center',fontsize=9)
    ax.annotate('USB end corridor\n12 mm wide',xy=(-27,32),xytext=(-40,65),arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.text(0,-1,'Flip whole assembly to read.\nDo not hold or squeeze glass.',ha='center',fontsize=10)
    ax.set_title('UNDERSIDE / STATUS POSTURE\nNo source geometry reproduced',fontsize=12)
    fig.suptitle('CONDITIONAL CONCEPT — stationary source mounting face NOT verified',fontsize=13)
    plt.tight_layout(); fig.savefig(OUT/'grip.png',dpi=180); plt.close(fig)

def main():
    parts=build(); report={'parameters_mm':P,'source_fit_verified':False,'physical_print_tested':False,'parts':{}}
    for name,shape in parts.items():
        cq.exporters.export(shape,str(OUT/(name+'.step')))
        # Print parts translated to bed, retain XY assembly coordinates for rebuild.
        # Flip spine so 4 mm seat points down. Local supports under deck required.
        printable=shape.rotate((0,0,0),(1,0,0),180) if name=='spine' else shape
        b=printable.val().BoundingBox(); printable=printable.translate((0,0,-b.zmin))
        cq.exporters.export(printable,str(OUT/(name+'.stl')),tolerance=.08,angularTolerance=.12)
        m=trimesh.load(OUT/(name+'.stl'),force='mesh')
        report['parts'][name]={'watertight':bool(m.is_watertight),'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist(),'solid_count':len(shape.solids().vals()),'cad_valid':shape.val().isValid()}
        assert m.is_watertight and m.volume>0 and shape.val().isValid() and len(shape.solids().vals())==1
    env=box(48,24,15,0,0,2.6)
    report['m5_intersection_mm3']={k:float(v.intersect(env).val().Volume()) if v.intersect(env).vals() else 0 for k,v in parts.items()}
    assert all(v<1e-6 for v in report['m5_intersection_mm3'].values())
    report['hardware_m5_intersection_mm3']={}
    for name,shape in hardware().items():
        overlap=shape.intersect(env); volume=overlap.val().Volume() if overlap.vals() else 0
        report['hardware_m5_intersection_mm3'][name]=volume
        assert volume<1e-6
    report['part_pair_intersection_mm3']={}
    names=list(parts)
    for i,k in enumerate(names):
        for l in names[i+1:]:
            inter=parts[k].intersect(parts[l]); volume=inter.val().Volume() if inter.vals() else 0
            report['part_pair_intersection_mm3'][k+' / '+l]=volume
            assert volume<1e-6
    # Motion clearance is against an assumed generic cylindrical volume only.
    rotor=hole(0,0,P['hypothetical_rotor_bottom'],P['hypothetical_rotor_radius'],35)
    report['hypothetical_rotor_intersection_mm3']={k:(v.intersect(rotor).val().Volume() if v.intersect(rotor).vals() else 0) for k,v in {**parts,'m5_envelope':env}.items()}
    assert all(v<1e-6 for v in report['hypothetical_rotor_intersection_mm3'].values())
    # Sweep adjustment: jaw centers 9.5..19.5 => padded clear grip 10..30 mm.
    report['conditional_grip_range_mm']=[10,30]
    report['jaw_range_check']=[]
    nominal=P['static_grip_width']
    report['full_hardware_range_check']=[]
    for width in range(10,31):
        P['static_grip_width']=width
        trial=build()
        volumes=[]
        for name in ['jaw_front','jaw_back']:
            overlap=trial['spine'].intersect(trial[name])
            volumes.append(overlap.val().Volume() if overlap.vals() else 0)
        # Every 3.4 mm bolt bore remains fully above its 15 x 3.4 mm slot.
        # Slot straight center span = 15 - 3.4 = 11.6, center +/-14.
        center=width/2+1+3.5
        assert 8.2-1e-6<=center<=19.8+1e-6
        assert max(volumes)<1e-6
        report['jaw_range_check'].append({'grip_mm':width,'spine_intersection_mm3':volumes,'bolt_center_y_mm':center})
        report['full_hardware_range_check'].append({'grip_mm':width,
            'interference':validate_hardware(trial,env),'tool_paths':tool_paths(trial,env)})
        print('validated grip',width,'mm',flush=True)
    P['static_grip_width']=nominal
    report['continuous_hardware_sweep']=continuous_sweeps(parts,env)
    report['thread_stack_mm']={
        'pitch':.5,'minimum_protrusion_two_pitches':1.,
        'corner':{'bolt_underhead_length':32.,'printed_stack':27.,'washer':.5,'nut':3.,
                  'protrusion':1.5,'protruding_pitches':3.,'nut_full_engagement':3.},
        'jaw':{'bolt_underhead_length':14.,'printed_stack':9.,'washer':.5,'nut':3.,
               'protrusion':1.5,'protruding_pitches':3.,'nut_full_engagement':3.},
        'tolerance_condition':'PASS only if measured L - printed_stack - washer - nut >= 1.0 mm; nominal margin 0.5 mm; full threaded bolts required',
        'threads':'cylindrical major-diameter envelope only; no helical thread/contact/friction simulation'}
    for family in ['corner','jaw']:
        chain=report['thread_stack_mm'][family]
        chain['protrusion']=chain['bolt_underhead_length']-chain['printed_stack']-chain['washer']-chain['nut']
        chain['protruding_pitches']=chain['protrusion']/report['thread_stack_mm']['pitch']
        assert chain['protruding_pitches']>=2
    report['nominal_device_side_clearance_mm']=.6
    report['jaw_screw_tip_to_m5_mm']=19-17.6
    report['printed_assembly_bounds_mm']=[[-27,-24,0],[27,24,36]]
    report['accessory_with_hardware_bounds_mm']=[[-27,-24,-3],[27,24,36]]
    report['hypothetical_system_bounds_mm']=[[-28,-28,-3],[28,28,76]]
    report['source_motion_status']='UNKNOWN: assumed R28, bottom Z41, height35 is not a measured source model.'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    asm=cq.Assembly()
    for name,shape in parts.items(): asm.add(shape,name=name)
    asm.export(str(OUT/'accessory_assembly.step'))
    hw_asm=cq.Assembly()
    for i,(name,shape) in enumerate(hardware().items()): hw_asm.add(shape,name='hardware_'+str(i))
    hw_asm.export(str(OUT/'hardware_reference.step'))
    render(parts); render(parts,True); grip_diagram()
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
