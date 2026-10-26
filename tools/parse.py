import json,struct,numpy as np
def load(path='source/labrador_retriever_puppy.glb'):
    f=open(path,'rb').read()
    clen,_=struct.unpack('<I4s',f[12:20])
    j=json.loads(f[20:20+clen])
    off=20+clen
    blen,_=struct.unpack('<I4s',f[off:off+8]); binb=f[off+8:off+8+blen]
    ct={5126:np.float32,5123:np.uint16,5125:np.uint32}
    nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
    def acc(i):
        a=j['accessors'][i]; bv=j['bufferViews'][a['bufferView']]
        n=a['count']; c=nc[a['type']]; dt=ct[a['componentType']]
        o=bv.get('byteOffset',0)+a.get('byteOffset',0)
        stride=bv.get('byteStride')
        if stride and stride!=c*np.dtype(dt).itemsize:
            raw=np.frombuffer(binb,dtype=np.uint8,count=n*stride,offset=o).reshape(n,stride)
            return np.frombuffer(raw[:,:c*np.dtype(dt).itemsize].tobytes(),dtype=dt).reshape(n,c)
        return np.frombuffer(binb,dtype=dt,count=n*c,offset=o).reshape(n,c)
    prims=[]
    for m in j['meshes']:
        for p in m['primitives']:
            at=p['attributes']
            prims.append(dict(pos=acc(at['POSITION']).astype(np.float64),nor=acc(at['NORMAL']).astype(np.float64),
                              uv=acc(at['TEXCOORD_0']).astype(np.float64),idx=acc(p['indices']).reshape(-1) if 'indices' in p else None,
                              mat=p['material']))
    return j,prims
if __name__=='__main__':
    j,prims=load()
    print(j['accessors'][0]); 
    for k,p in enumerate(prims):
        P=p['pos']; 
        print(k,'verts',len(P),'idx',None if p['idx'] is None else len(p['idx']),'mat',p['mat'])
        print('  min',P.min(0),'max',P.max(0))
        print('  uv min',p['uv'].min(0),'max',p['uv'].max(0))
