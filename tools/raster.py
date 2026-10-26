import numpy as np
from PIL import Image

def project(V, view):
    """V: Y-up world (x right when looking from front... ), returns sx, sy, depth (smaller = closer)"""
    if view=='side':   sx=V[:,2];  sy=V[:,1];  d=-V[:,0]     # camera at +x looking -x, front(+z) to the right
    elif view=='front':sx=-V[:,0]; sy=V[:,1];  d=V[:,2]
    elif view=='back': sx=V[:,0];  sy=V[:,1];  d=-V[:,2]
    elif view=='top':  sx=V[:,0];  sy=V[:,2];  d=-V[:,1]
    elif view.startswith('q'):  # three-quarter front-right
        a=np.radians(float(view[1:]) if len(view)>1 else 40); ca,sa=np.cos(a),np.sin(a)
        x2=V[:,0]*ca - V[:,2]*sa;  z2=V[:,0]*sa + V[:,2]*ca
        sx=-x2*(-1); sx=x2; sy=V[:,1]-0.0*z2; d=-z2
        sx=-x2
    return sx,sy,d

def render(V, F, UV, TEXID, textures, view='side', size=(520,360), bounds=None, bg=(235,238,242), light_dir=(0.35,0.8,0.5), shade=0.35, N=None, VC=None):
    W,H=size
    sx,sy,d=project(V,view)
    if bounds is None:
        bounds=(sx.min(),sx.max(),sy.min(),sy.max())
    x0,x1,y0,y1=bounds
    s=min((W-20)/(x1-x0),(H-20)/(y1-y0))
    px=(sx-(x0+x1)/2)*s+W/2; py=H/2-(sy-(y0+y1)/2)*s
    img=np.zeros((H,W,3),np.float32); img[:]=np.array(bg,np.float32)/255
    zb=np.full((H,W),1e9,np.float32)
    texarr=[np.asarray(t.convert('RGBA'),np.float32)/255 for t in textures]
    # face normals for shading
    e1=V[F[:,1]]-V[F[:,0]]; e2=V[F[:,2]]-V[F[:,0]]
    fn=np.cross(e1,e2); fn/=np.linalg.norm(fn,axis=1,keepdims=True)+1e-9
    L=np.array(light_dir)/np.linalg.norm(light_dir)
    lam=np.abs(fn@L)
    for fi,f in enumerate(F):
        xs=px[f]; ys=py[f]; zs=d[f]
        minx=max(int(np.floor(xs.min())),0); maxx=min(int(np.ceil(xs.max())),W-1)
        miny=max(int(np.floor(ys.min())),0); maxy=min(int(np.ceil(ys.max())),H-1)
        if minx>maxx or miny>maxy: continue
        gx,gy=np.meshgrid(np.arange(minx,maxx+1)+0.5,np.arange(miny,maxy+1)+0.5)
        den=(ys[1]-ys[2])*(xs[0]-xs[2])+(xs[2]-xs[1])*(ys[0]-ys[2])
        if abs(den)<1e-9: continue
        a=((ys[1]-ys[2])*(gx-xs[2])+(xs[2]-xs[1])*(gy-ys[2]))/den
        b=((ys[2]-ys[0])*(gx-xs[2])+(xs[0]-xs[2])*(gy-ys[2]))/den
        c=1-a-b
        m=(a>=-1e-4)&(b>=-1e-4)&(c>=-1e-4)
        if not m.any(): continue
        z=a*zs[0]+b*zs[1]+c*zs[2]
        sub=zb[miny:maxy+1,minx:maxx+1]
        mm=m&(z<sub)
        if not mm.any(): continue
        u=a*UV[f[0],0]+b*UV[f[1],0]+c*UV[f[2],0]; v=a*UV[f[0],1]+b*UV[f[1],1]+c*UV[f[2],1]
        if VC is not None:
            col=a[...,None]*VC[f[0]]+b[...,None]*VC[f[1]]+c[...,None]*VC[f[2]]
        else:
            t=texarr[TEXID[fi]]; th,tw,_=t.shape
            ti=np.floor((u%1.0)*tw).astype(int)%tw; tj=np.floor((v%1.0)*th).astype(int)%th
            col=t[tj,ti][...,:3]
        col=col*((1-shade)+shade*lam[fi])
        sub[mm]=z[mm]
        region=img[miny:maxy+1,minx:maxx+1]; region[mm]=col[mm]
    return (np.clip(img,0,1)*255).astype(np.uint8)
