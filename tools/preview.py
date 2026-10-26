import numpy as np, sys
from PIL import Image
from rig import *
from raster import render, project
d=np.load('out/mesh_cache.npz'); Vmc,Nmc,UV,F,bidx,bw=[d[k] for k in ['Vmc','Nmc','UV','F','bidx','bw']]
atlas=Image.open('out/assets/labrador_puppy.png')
def posed(limb,dist,age,hy=0,hp=0):
    P=pose_params(limb,dist,age,hy,hp); W=world_mats(P)
    V,N=skin(Vmc,Nmc,None,bidx,bw,W); return from_mc(V)
def frame(V,view,size,bounds):
    return render(V,F,UV,np.zeros(len(F),int),[atlas],view=view,size=size,bounds=bounds,shade=0.4)
def bnds(view,pad=0.1):
    sx,sy,_=project(from_mc(Vmc),view); w=sx.max()-sx.min(); h=sy.max()-sy.min()
    return (sx.min()-w*pad,sx.max()+w*pad,sy.min()-h*pad,sy.max()+h*pad)
if __name__=='__main__':
    which=sys.argv[1]; n=int(sys.argv[2]); size=(380,270)
    bs=bnds('side'); bq=bnds('q40')
    frames=[]
    for k in range(n):
        if which=='walk':
            limb=(k/n)*2*np.pi/0.8; V=posed(limb,1.0,k*(20*1.0/n*0+1)*0+k*60/n)
        else:
            V=posed(0.0,0.0,k*(112/n))      # 5.6 s idle loop
        a=frame(V,'side',size,bs); b=frame(V,'q40',size,bq)
        frames.append(Image.fromarray(np.concatenate([a,b],1)))
        print(k,end=' ',flush=True)
    frames[0].save(f'out/preview_{which}.gif',save_all=True,append_images=frames[1:],duration=int(1000*(0.9 if which=='walk' else 5.6)/n),loop=0,optimize=False)
    # contact sheet
    sel=[frames[int(i*n/4)] for i in range(4)]
    sheet=Image.new('RGB',(sel[0].width,sel[0].height*4)); [sheet.paste(f,(0,i*f.height)) for i,f in enumerate(sel)]
    sheet.save(f'out/sheet_{which}.png')
