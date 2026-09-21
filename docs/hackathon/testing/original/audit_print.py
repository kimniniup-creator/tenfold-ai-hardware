"""Archive a committed original design and independently inspect/slice named STL parts.

Example: python audit_print.py --ref SHA --path design/hackathon/original-x
 --parts exports/base.stl exports/pin.stl --output report.json
Generated G-code/plots stay in ignored .local; they are not printer-qualified files.
"""
import argparse,hashlib,io,json,pathlib,re,subprocess,zipfile
import numpy as np
import trimesh as tm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser()
p.add_argument('--ref',required=True);p.add_argument('--path',required=True)
p.add_argument('--parts',nargs='+',required=True);p.add_argument('--output',required=True)
p.add_argument('--support',action='store_true')
p.add_argument('--profile',default='docs/hackathon/testing/original/generic-pla.ini')
p.add_argument('--fill-density');p.add_argument('--brim-width',type=float)
p.add_argument('--slicer',default='.local/slicer/prusa296/PrusaSlicer-2.9.6/prusa-slicer-console.exe')
a=p.parse_args(); root=pathlib.Path.cwd()
sha=subprocess.check_output(['git','rev-parse',a.ref],text=True).strip()
dest=root/'.local/original-audit'/sha;dest.mkdir(parents=True,exist_ok=True)
zipfile.ZipFile(io.BytesIO(subprocess.check_output(['git','archive','--format=zip',sha,a.path]))).extractall(dest)
folder=dest/a.path;out=dest/('slice-support' if a.support else 'slice-no-support');out.mkdir(exist_ok=True)
cfg=root/a.profile
report={'sha':sha,'path':a.path,'slicer':'PrusaSlicer 2.9.6','profile':a.profile,'profile_sha256':hashlib.sha256(cfg.read_bytes()).hexdigest(),'fill_density_override':a.fill_density,'brim_width_override':a.brim_width,'supports_enabled':a.support,'physical_print_tested':False,'parts':{}}
def parse_gcode(f):
    x=y=z=e=0.;relative=False;layer=-1;role='';segments=[];layers={};stats={};width=.45
    for line in f.read_text(encoding='utf8',errors='replace').splitlines():
        if line.startswith(';LAYER_CHANGE'):layer+=1
        if line.startswith(';TYPE:'):role=line[6:]
        if line.startswith(';WIDTH:'):
            try:width=float(line[7:])
            except ValueError:pass
        if line.startswith('; estimated printing time') or line.startswith('; filament used'):stats[line.split('=')[0].lstrip('; ').strip()]=line.split('=',1)[-1].strip()
        cmd=line.split(';')[0].strip();values={k:float(v) for k,v in re.findall(r'([XYZEF])(-?\d+(?:\.\d+)?)',cmd)}
        if cmd.startswith('M83'):relative=True
        if cmd.startswith('M82'):relative=False
        if cmd.startswith('G92') and 'E' in values:e=values['E']
        if re.match(r'^G[01](?:\s|$)',cmd):
            nx=values.get('X',x);ny=values.get('Y',y);nz=values.get('Z',z)
            ne=values.get('E',0 if relative else e);de=ne if relative else ne-e
            if de>1e-8 and ((nx-x)**2+(ny-y)**2)>1e-10:
                segments.append((layer,z,x,y,nx,ny,role,width));layers[layer]=layers.get(layer,0)+1
            x,y,z=nx,ny,nz
            if 'E' in values:e=ne if not relative else e+ne
    return segments,{'declared_layers':layer+1,'layers_with_extrusion':len(layers),'empty_declared_layers':[i for i in range(layer+1) if i not in layers],'extrusion_segments':len(segments),'support_segments':sum('Support' in s[6] for s in segments),'roles':sorted(set(s[6] for s in segments)),'summary':stats}
for relative_path in a.parts:
    f=folder/relative_path;m=tm.load_mesh(f);b=m.bounds
    item={'file_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),'volume_mm3':float(m.volume),'bounds_mm':b.round(5).tolist(),'extents_mm':m.extents.round(5).tolist(),'source_zmin_mm':float(b[0,2]),'faces':len(m.faces)}
    # Auxiliary sampling only: small ray distances near corners aren't certified wall minima.
    pts,faces=tm.sample.sample_surface(m,512,seed=7);directions=-m.face_normals[faces]
    loc,ri,_=m.ray.intersects_location(pts+directions*1e-4,directions,multiple_hits=False)
    distances=np.linalg.norm(loc-pts[ri],axis=1)
    item['normal_ray_chord_sample']={'samples':512,'hits':len(ri),'min_mm':float(np.min(distances)) if len(ri) else None,'p05_mm':float(np.quantile(distances,.05)) if len(ri) else None,'below_0p8mm':int(np.sum(distances<.8)),'not_global_minimum_wall_proof':True}
    stem=f.stem;gcode=out/(stem+'.gcode')
    cmd=[str(root/a.slicer),'--datadir',str(root/'.local/slicer/profile'),'--load',str(cfg),'--export-gcode','--output',str(gcode),'--center','110,110']
    if a.support:cmd+=['--support-material']
    if a.fill_density:cmd+=['--fill-density',a.fill_density]
    if a.brim_width is not None:cmd+=['--brim-width',str(a.brim_width)]
    cmd+=[str(f)]
    run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=600)
    log=run.stdout+'\n'+run.stderr;(out/(stem+'.log')).write_text(log,encoding='utf8')
    item['slice_exit']=run.returncode;item['warnings']=[s for s in log.splitlines() if re.search(r'warning|error|repair|empty layer|outside.*(?:bed|volume)|needs? support',s,re.I)]
    if run.returncode==0 and gcode.exists():
        segments,metrics=parse_gcode(gcode);item['toolpath']=metrics
        selected=sorted(set([0,max(0,metrics['declared_layers']//2),max(0,metrics['declared_layers']-1)]))
        fig,axs=plt.subplots(1,len(selected),figsize=(5*len(selected),5),squeeze=False)
        for ax,li in zip(axs[0],selected):
            for s in segments:
                if s[0]==li:ax.plot([s[2],s[4]],[s[3],s[5]],color='#d36931' if 'Support' in s[6] else '#174f66',lw=.6)
            ax.set_aspect('equal');ax.set_title(f'{stem}: layer {li+1}');ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
        fig.tight_layout();fig.savefig(out/(stem+'-layers.png'),dpi=120);plt.close(fig)
    report['parts'][relative_path]=item
    print(relative_path,run.returncode,item.get('toolpath',{}).get('declared_layers'),item['normal_ray_chord_sample'],flush=True)
pathlib.Path(a.output).write_text(json.dumps(report,indent=2),encoding='utf8')
