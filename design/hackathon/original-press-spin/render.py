"""Render actual CAD and exported STL; no generative images."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cad

COLORS={'body':'#334853','m5_tray':'#6c818b','wheel':'#45b7b5','bearing_sleeve':'#d0d4d3',
 'thrust_ring':'#f2cc75','rotor_pin':'#7b999f','rotor_clip':'#e7ae71',
 'press_leaf':'#badd67','press_pin_a':'#97b659','press_pin_b':'#97b659','drawer_key':'#e7ae71'}

def faces(ax,items):
    verts=[]; colors=[]; light=np.array([-.3,-.4,.85]); light/=np.linalg.norm(light)
    for m,color in items:
        verts.extend(m.vertices[m.faces]); rgb=np.array(to_rgb(color))
        shade=.58+.42*np.clip(m.face_normals@light,0,1)
        colors.extend([tuple(rgb*v) for v in shade])
    ax.add_collection3d(Poly3DCollection(verts,facecolors=colors,edgecolor='none',zsort='average'))

def scene(name,explode=False,under=False,metal=False):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk
    from PIL import Image, ImageDraw, ImageFont
    p=cad.parts()
    if metal:
        p={k:v for k,v in p.items() if k not in ['rotor_pin','rotor_clip','press_leaf','press_pin_a','press_pin_b','drawer_key']}
        p.update({k:v for k,v in cad.alternatives().items() if k.startswith('metal')}); p.update(cad.metal_reference())
    shifts={'m5_tray':(-62,0,-4),'wheel':(0,0,15),'bearing_sleeve':(0,0,6),'thrust_ring':(0,0,3),
            'rotor_pin':(0,0,30),'rotor_clip':(0,-30,0),'press_leaf':(0,0,16),
            'press_pin_a':(0,0,29),'press_pin_b':(0,0,29),'drawer_key':(0,36,0)}
    items=[]
    for key,shape in p.items():
        m=cad.mesh(shape)
        if explode: m.apply_translation(shifts.get(key,(0,0,0)))
        items.append((m,COLORS.get(key,'#adb4b5')))
    for shape,color in [(cad.roundbox(48,24,15,3,z=4.8),'#d28e57'),(cad.box(29,16,.1,5,0,4.65),'#131e28')]:
        m=cad.mesh(shape)
        if explode: m.apply_translation((-62,0,0))
        items.append((m,color))
    renderer=vtk.vtkRenderer(); renderer.SetBackground(*to_rgb('#f3f2ed'))
    for m,color in items:
        points=vtk.vtkPoints(); points.SetData(numpy_to_vtk(m.vertices,deep=True))
        cells=vtk.vtkCellArray()
        for face in m.faces:
            cells.InsertNextCell(3)
            for idx in face: cells.InsertCellPoint(int(idx))
        poly=vtk.vtkPolyData(); poly.SetPoints(points); poly.SetPolys(cells)
        mapper=vtk.vtkPolyDataMapper(); mapper.SetInputData(poly)
        actor=vtk.vtkActor(); actor.SetMapper(mapper); prop=actor.GetProperty()
        prop.SetColor(*to_rgb(color)); prop.SetAmbient(.28); prop.SetDiffuse(.72); prop.SetSpecular(.12)
        renderer.AddActor(actor)
    cam=renderer.GetActiveCamera(); cam.ParallelProjectionOn()
    cam.SetPosition(95,-160,-110 if under else 135); cam.SetFocalPoint(-15 if explode else 0,0,20); cam.SetViewUp(0,0,1)
    renderer.ResetCamera(); cam.Zoom(1.05)
    window=vtk.vtkRenderWindow(); window.SetOffScreenRendering(1); window.SetSize(1600,1000); window.AddRenderer(renderer); window.Render()
    capture=vtk.vtkWindowToImageFilter(); capture.SetInput(window); capture.Update()
    writer=vtk.vtkPNGWriter(); writer.SetFileName(str(cad.OUT/name)); writer.SetInputConnection(capture.GetOutputPort()); writer.Write(); window.Finalize()
    im=Image.open(cad.OUT/name).convert('RGB'); draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30); small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    title='EXPLODED / PETG FLEX BUILD' if explode else ('PLA + M3 / ROTATION ONLY' if metal else ('UNDERSIDE / REMOVABLE M5 TRAY' if under else 'ORIGINAL TWIN-ACTION EDC'))
    draw.text((50,35),title,fill='#263d48',font=font)
    draw.text((50,950),'CAD prototype - not physically printed | M5 envelope proxy | '+('64 x 48 x 39.2 mm' if metal else '64 x 46 x 35 mm'),fill='#263d48',font=small)
    im.save(cad.OUT/name)

def print_board():
    files=sorted((cad.OUT/'stl').glob('*.stl')); fig=plt.figure(figsize=(18,13),facecolor='#f3f2ed')
    for i,path in enumerate(files):
        ax=fig.add_subplot(4,6,i+1,projection='3d'); ax.set_facecolor('#f3f2ed')
        m=cad.trimesh.load(path,force='mesh'); faces(ax,[(m,COLORS.get(path.stem,'#79929a'))])
        b=m.bounds; e=m.extents; center=b.mean(axis=0); d=max(e)*.6
        ax.set(xlim=(center[0]-d,center[0]+d),ylim=(center[1]-d,center[1]+d),zlim=(0,2*d)); ax.set_box_aspect((1,1,1)); ax.view_init(28,-55); ax.set_axis_off()
        ax.set_title(path.stem+'\n'+' x '.join(f'{v:.1f}' for v in e)+' mm',fontsize=9)
    fig.suptitle('EXPORTED PRINT ORIENTATIONS — select one kit; alternatives/calibration are not all assembly parts',fontsize=15,y=.98)
    fig.tight_layout(rect=(0,0,1,.96)); fig.savefig(cad.OUT/'print_orientations.png',dpi=140); plt.close(fig)

if __name__=='__main__':
    scene('assembly.png'); scene('exploded.png',explode=True); scene('underside.png',under=True); scene('pla_rotation.png',metal=True); print_board()
