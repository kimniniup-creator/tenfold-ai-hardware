"""Depth-correct offscreen CAD views. VTK is supplied by CadQuery. No source assets exported."""
from pathlib import Path
import argparse, json
import numpy as np
import trimesh as tm
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,default=Path(__file__).parent);ap.add_argument('--reference',type=Path)
args=ap.parse_args();ROOT=args.directory
names=['01_base','02_rotor','03_capture_ring','04_m5_cradle','05_face_frame']
colors=[(.17,.23,.27),(.69,.81,.24),(.43,.54,.58),(.80,.79,.73),(.25,.34,.38)]
report=json.loads((ROOT/'verification.json').read_text(encoding='utf-8'))
def actor(mesh,color):
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.asarray(mesh.vertices),deep=True))
    cells=vtk.vtkCellArray();arr=np.column_stack([np.full(len(mesh.faces),3),mesh.faces]).ravel().astype(np.int64)
    cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(arr,deep=True))
    data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(45);normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(color);a.GetProperty().SetInterpolationToPhong();a.GetProperty().SetSpecular(.2)
    return a
def text(renderer,content,x,y,size=22,color=(.12,.16,.18)):
    t=vtk.vtkTextActor();t.SetInput(content);t.SetPosition(x,y);p=t.GetTextProperty();p.SetFontSize(size);p.SetColor(color);renderer.AddActor2D(t)
ref=args.reference or Path(__file__).parent/'_reference'/'StickS3.stl'
if ref.exists():
    m5=tm.util.concatenate([c for c in tm.load(ref).split() if c.bounds[1,0]<25])
    m5.apply_translation([-12,-24.059725,26.077364])
else:
    m5=tm.creation.box([24,48,15]);m5.apply_translation([0,0,19.5])
def view(kind):
    ren=vtk.vtkRenderer();ren.SetBackground(.955,.949,.925)
    exploded=kind=='exploded'; shift=[0,12,24,38,70] if exploded else [0]*5
    for n,c,z in zip(names,colors,shift):
        m=tm.load(ROOT/(n+'.stl'));m.apply_translation([0,0,z+report['parts'][n]['stl_to_assembly_translation_z']]);ren.AddActor(actor(m,c))
    m=m5.copy();m.apply_translation([0,0,53 if exploded else 0]);ren.AddActor(actor(m,(.85,.39,.11)))
    # Manufacturer STL contains enclosures, not the LCD glass. This plane is visual only.
    display=tm.creation.box([15,25,.15]);display.apply_translation([0,7.5,26.0+(53 if exploded else 0)])
    ren.AddActor(actor(display,(.035,.06,.07)))
    for sx in [-1,1]:
        for sy in [-1,1]:
            shaft=tm.creation.cylinder(radius=1.5,height=28.3,sections=36);shaft.apply_translation([sx*16.5+(44 if exploded else 0),sy*20,14.15])
            ren.AddActor(actor(shaft,(.12,.15,.16)))
            head=tm.creation.cylinder(radius=2.95,height=.1,sections=48);head.apply_translation([sx*16.5+(44 if exploded else 0),sy*20,29.95])
            ren.AddActor(actor(head,(.12,.15,.16)))
    if kind=='grip':
        palm=tm.creation.icosphere(subdivisions=3);palm.apply_scale([43,47,10]);palm.apply_translation([0,0,-11])
        ren.AddActor(actor(palm,(.76,.60,.45)))
        # Indicative thumb alongside outer ring. Not a measured ergonomic hand model.
        thumb=tm.creation.icosphere(subdivisions=3);thumb.apply_scale([10,19,9]);thumb.apply_translation([37,-8,7])
        ren.AddActor(actor(thumb,(.76,.60,.45)))
    camera=ren.GetActiveCamera();camera.SetPosition(110,-145,110 if not exploded else 115)
    camera.SetFocalPoint(0,0,8 if kind=='grip' else 14 if not exploded else 49);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(62 if kind=='grip' else 54 if not exploded else 71)
    text(ren,'ORBIT-10  /  CAPTIVE ROTARY EDC',45,945,28)
    text(ren,'75 mm diameter x 30 mm thick | assembled M5 shown in orange',45,905,19)
    text(ren,{'assembly':'Turn the outer ring; the device and base remain stationary.',
              'exploded':'Base > rotor > capture ring > cradle > M5 > face frame; 4 through screws.',
              'grip':'Palm supports the base; thumb rolls the ring. Hand volumes are schematic.'}[kind],45,72,19)
    text(ren,('Official enclosure' if ref.exists() else 'BOX ENVELOPE ONLY')+' + illustrative LCD / not physically printed',45,35,17)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(1250,1000);win.SetMultiSamples(4);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(ROOT/(kind+'.png')));writer.SetInputConnection(capture.GetOutputPort());writer.Write();win.Finalize()
for kind in ['assembly','exploded','grip']:view(kind)
