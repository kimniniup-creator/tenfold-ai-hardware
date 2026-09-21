"""Original twin-action EDC. All dimensions mm. No MakerWorld geometry.
Run python cad.py. STL coordinates are print coordinates; STEP is assembly.
PETG spring/clip/pins required for full printed mode. PLA + M3 spin mode supplied.
"""
from pathlib import Path
import json, math
import cadquery as cq
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parent
RX=-12.; PRESS_X=18.; TRAVEL=1.4

def box(l,w,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(l,w,h,centered=(True,True,False)).translate((x,y,z))
def cyl(r,h,x=0,y=0,z=0):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def ring(ro,ri,h,x=0,y=0,z=0):
    return cyl(ro,h,x,y,z).cut(cyl(ri,h+2,x,y,z-1))
def roundbox(l,w,h,r,x=0,y=0,z=0):
    return box(l,w,h,x,y,z).edges('|Z').fillet(r)
def volume(a,b):
    aa=a.val().BoundingBox(); bb=b.val().BoundingBox()
    if any(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))<1e-8 for k in 'xyz'): return 0.
    v=a.intersect(b); return float(v.val().Volume()) if v.vals() else 0.
def mesh(shape):
    v,f=shape.val().tessellate(.08,.12)
    return trimesh.Trimesh(vertices=[p.toTuple() for p in v],faces=f,process=True)

def body():
    b=roundbox(64,40,3,3,z=24)
    for s in [-1,1]:
        # Drawer rails. Front 6 mm omitted from upper lip for insertion.
        b=b.union(box(64,5.4,1.8,0,s*17.3,0))
        b=b.union(box(54,5.4,1.8,0,s*17.3,5))
        for t in [-1,1]: b=b.union(box(6,4,24,t*29,s*18,0))
    b=b.union(box(2,34,6,28.4,0,0))
    # Rear-shell clearance stops capture M5 after drawer insertion; no flexing
    # board cradle required, so the tray itself may be printed in PLA.
    for sx in [-1,1]:
        for sy in [-1,1]: b=b.union(box(4,4,3.6,sx*21.5,sy*9.5,20.4))
    b=b.cut(box(3.2,50,3.2,-29,0,1.6))
    b=b.cut(cyl(3.4,20,RX,0,18))
    b=b.union(box(16,6,2.6,PRESS_X,14,27))
    for x in [14,22]: b=b.cut(cyl(2.1,12,x,14,22))
    # Two press stops directly below pad tip: 1.4 mm neutral gap.
    slope=1.5*TRAVEL/20
    for x in [14,22]:
        stop=cq.Workplane('YZ').polyline([(-10,27),(-8,27),(-8,28.2+slope),(-10,28.2-slope)]).close().extrude(2).translate((x-1,0,0))
        b=b.union(stop)
    return b

def tray():
    p=roundbox(54,31.2,2,1.2,z=2.2).cut(roundbox(46,22,5,2,z=1))
    for s in [-1,1]:
        for t in [-1,1]:
            p=p.union(box(3,2,.6,s*22.5,t*10.8,4.2))
            p=p.union(box(1.2,2,3,s*25,t*9,4.2))
            # Tie finger to bezel corner; .4 mm X clearance to ideal device.
            p=p.union(box(2.6,2,.6,s*24.3,t*9,4.2))
            p=p.union(box(4,2,2,s*21,t*13.4,4.2))
    return p

def wheel(bore=12.5):
    w=cyl(15,5,RX,0,27.4)
    for k in range(20):
        a=math.tau*k/20
        w=w.cut(cyl(.7,7,RX+15.1*math.cos(a),15.1*math.sin(a),26.4))
    return w.cut(cyl(bore/2,7,RX,0,26.4))

def rotor_pin():
    p=cyl(8,2,RX,0,33).union(cyl(3.2,12,RX,0,21))
    return p.cut(ring(3.3,2.4,2,RX,0,22))

def clip(mouth=4.4):
    # Long fork arms rather than a thick rigid C-ring. Groove diameter4.8;
    # mouth4.4 expands .2 per arm over ~11 mm effective arm length.
    c=box(2,8,1.5,RX-7,0,22.2)
    for s in [-1,1]:
        c=c.union(box(12,1.4,1.5,RX-1,s*3.3,22.2))
        pts=[(RX+1.5,s*mouth/2),(RX+1.5,s*2.6),(RX+4.5,s*2.6)]
        c=c.union(cq.Workplane('XY').polyline(pts).close().extrude(1.5).translate((0,0,22.2)))
    return c

def spring(thickness=1.2,delta=0):
    # Euler-Bernoulli deflected shape for geometric clearance ONLY, no FEA claim.
    root=box(16,6,2.4,PRESS_X,14,29.6)
    for x in [14,22]: root=root.cut(cyl(2.1,4,x,14,28.6))
    L=20.; n=40
    points=[]
    for i in range(n+1):
        # Thin beam ends inside the rigid pad; do not retain a fictitious curved
        # underside under the rigid tip, which would penetrate the matching stop.
        s=16.*i/n; w=delta*s*s*(3*L-s)/(2*L**3)
        points.append((11-s,29.6-w))
    points+= [(y,z+thickness) for y,z in reversed(points)]
    beam=cq.Workplane('YZ').polyline(points).close().extrude(10).translate((PRESS_X-5,0,0))
    # Stiff pad rotates with the free-end tangent, to catch its lower front corner.
    theta=math.degrees(math.atan(1.5*delta/L))
    pad=roundbox(14,9,2.4,1,PRESS_X,-9,29.6)
    pad=pad.rotate((0,-9,29.6),(1,-9,29.6),theta).translate((0,0,-delta))
    return root.union(beam).union(pad)

def press_pin(x):
    p=cyl(3.5,1.6,x,14,32).union(cyl(1.9,11.2,x,14,20.8))
    # Chamfered barb; positive retention shoulder sits below roof at Z23.6.
    barb=cq.Workplane('XY').circle(1.7).workplane(offset=1.2).circle(2.4).loft().translate((x,14,22.4))
    p=p.union(barb).cut(box(.8,7,8,x,14,20.7))
    return p

def drawer_key():
    # Shaft along Y, both head and split barb outside the body walls.
    p=box(2.6,44,2.6,-29,1,1.9).union(box(5,2,4,-29,-22,1.2))
    for s in [-1,1]:
        pts=[(-29+s*1.3,20.3),(-29+s*1.75,20.3),(-29+s*1.3,23)]
        p=p.union(cq.Workplane('XY').polyline(pts).close().extrude(2.6).translate((0,0,1.9)))
    p=p.cut(box(.8,7,5,-29,20,1))
    return p

def metal_reference():
    # Optional PLA rotation build: printed sleeve/cap + M3 low-head bolt.
    h={
      'rotor_M3x16':cyl(1.5,16,RX,0,23.2).union(cyl(2.85,2,RX,0,21.2)),
      'rotor_nut':ring(3.2,1.5,3,RX,0,34.7),
      'rotor_steel_washer':ring(3.5,1.7,.5,RX,0,34.2),
    }
    # Drawer alternative: M3x45 along Y, .5 washers both sides, 3 mm nut.
    shaft=cyl(1.5,45).rotate((0,0,0),(1,0,0),-90).translate((-29,-20.5,3.2))
    head=cyl(2.85,3).rotate((0,0,0),(1,0,0),-90).translate((-29,-23.5,3.2))
    h['drawer_M3x45']=shaft.union(head)
    for name,start,r,ht in [('drawer_washer_left',-20.5,3.5,.5),('drawer_washer_right',20,3.5,.5),('drawer_nut',20.5,3.2,3)]:
        h[name]=ring(r,1.7 if 'washer' in name else 1.5,ht).rotate((0,0,0),(1,0,0),-90).translate((-29,start,3.2))
    return h

def parts():
    return {'body':body(),'m5_tray':tray(),'wheel':wheel(),
       'bearing_sleeve':ring(6,3.4,6,RX,0,27),
       'thrust_ring':ring(8,6.2,.4,RX,0,27),'rotor_pin':rotor_pin(),'rotor_clip':clip(),
       'press_leaf':spring(),'press_pin_a':press_pin(14),'press_pin_b':press_pin(22),
       'drawer_key':drawer_key()}

def alternatives():
    return {'wheel_loose':wheel(12.7),'press_leaf_soft':spring(1.0),
      'metal_rotor_cap':ring(8,1.7,1.2,RX,0,33),
      'metal_rotor_sleeve':ring(3.2,1.7,8.2,RX,0,24),
      'metal_rotor_lower_washer':ring(6,1.7,.8,RX,0,23.2)}

def calibration():
    block=box(54,18,5)
    for i,d in enumerate([12.3,12.5,12.7]): block=block.cut(cyl(d/2,7,(i-1)*17,0,-1))
    sockets=box(38,16,3)
    for x,d in [(-12,4.0),(0,4.2),(12,4.4)]: sockets=sockets.cut(cyl(d/2,5,x,0,-1))
    # Mini M5 fit corner gauge (official ideal envelope; 0.4 mm XY clearance).
    gauge=box(52.8,28.8,3).cut(box(48.8,24.8,5,z=-1))
    return {'cal_axis_holes':block,'cal_axis_plug':cyl(6,6),
       'cal_snap_sockets':sockets,'cal_snap_pin':press_pin(14),
       'cal_m5_frame':gauge,'cal_clip_open':clip(4.6)}

def print_shape(name,shape):
    if name=='body':
        # Stand on +X end: avoids a 32 mm cavity roof and 52 mm rail bridge.
        # Support short terminal posts/mount ledges; bearing sleeve prints separately.
        shape=shape.rotate((0,0,0),(0,1,0),90)
    if name in ['rotor_pin','press_pin_a','press_pin_b','cal_snap_pin']:
        shape=shape.rotate((0,0,0),(1,0,0),180)
    if name=='m5_tray':
        # Printed upright; short inward tabs bridge 2 mm at top.
        pass
    if name=='drawer_key':
        # Flat on its broad XY face.
        pass
    b=shape.val().BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))

def export_all():
    (OUT/'stl').mkdir(exist_ok=True); (OUT/'step').mkdir(exist_ok=True)
    all_parts={**parts(),**alternatives(),**calibration()}; report={}
    for name,p in all_parts.items():
        assert p.val().isValid() and len(p.solids().vals())==1,name
        cq.exporters.export(p,str(OUT/'step'/(name+'.step')))
        pr=print_shape(name,p)
        cq.exporters.export(pr,str(OUT/'stl'/(name+'.stl')),tolerance=.05,angularTolerance=.1)
        m=trimesh.load(OUT/'stl'/(name+'.stl'),force='mesh')
        assert m.is_watertight and m.is_winding_consistent and m.volume>0,name
        report[name]={'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),
          'solid_count':len(p.solids().vals()),'bounds_print_mm':m.bounds.tolist(),'volume_mm3':float(m.volume)}
    a=cq.Assembly()
    for name,p in parts().items(): a.add(p,name=name)
    a.export(str(OUT/'step'/'assembly.step'))
    (OUT/'mesh_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return all_parts

if __name__=='__main__':
    print('exporting original parts',flush=True)
    p=export_all()
    print('PASS mesh exports',len(p),flush=True)
