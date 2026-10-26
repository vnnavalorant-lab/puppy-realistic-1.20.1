import numpy as np, struct, os
from PIL import Image
from rig import *

parts = build_mesh()
body, eye = parts

# ---- atlas: 512x320 (body 512x256 on top, eye 64x64 below-left) ----
AW, AH = 512, 320
body_tex = Image.open('textures/gltf_embedded_1.png').convert('RGB')
eye_tex = Image.open('textures/gltf_embedded_2.png').convert('RGBA')
atlas = Image.new('RGBA', (AW, AH), (230, 225, 215, 255))
atlas.paste(body_tex.convert('RGBA'), (0, 0))
bg = Image.new('RGBA', eye_tex.size, (255, 255, 255, 255)); bg.alpha_composite(eye_tex)
atlas.paste(bg, (0, 256))
os.makedirs('out/assets', exist_ok=True)
atlas.save('out/assets/labrador_puppy.png')

def remap(uv, w, h, ox, oy):
    x = uv[:, 0] * w + ox
    y = (1 - uv[:, 1]) * h + oy          # source file stores v upward -> image row = (1-v)*h
    return np.stack([x / AW, y / AH], 1)

uv_b = remap(body['uv'], 512, 256, 0, 0)
uv_e = remap(eye['uv'], 64, 64, 0, 256)

V = np.concatenate([body['V'], eye['V']])
N = np.concatenate([body['N'], eye['N']])
UV = np.concatenate([uv_b, uv_e])
F = np.concatenate([body['F'], eye['F'] + len(body['V'])])

Wt = np.zeros((len(V), NB)); Wt[:len(body['V'])] = compute_weights(body['V']); Wt[len(body['V']):, BI['head']] = 1.0
bidx, bw = top4(Wt)

Vmc = to_mc(V)
Nmc = np.stack([N[:, 0], -N[:, 1], -N[:, 2]], 1)

# ---- binary ----
buf = bytearray()
buf += struct.pack('<ii', 0x4D505550, 1)
buf += struct.pack('<i', NB)
for i, (name, parent, piv) in enumerate(BONES):
    p = PIV_MC[i]; buf += struct.pack('<i3f', parent, *p)
buf += struct.pack('<ii', len(V), len(F))
for i in range(len(V)):
    buf += struct.pack('<8f', *Vmc[i], *Nmc[i], *UV[i])
    buf += bytes(bidx[i].tolist()) + struct.pack('<4f', *bw[i])
for f in F: buf += struct.pack('<3i', *f)
os.makedirs('out/assets', exist_ok=True)
open('out/assets/puppy_mesh.bin', 'wb').write(buf)
print('verts', len(V), 'tris', len(F), 'bytes', len(buf), 'bones', NB)
np.savez('out/mesh_cache.npz', Vmc=Vmc, Nmc=Nmc, UV=UV, F=F, bidx=bidx, bw=bw)

# ---- install into the mod ----
import shutil
res = '../src/main/resources/assets/labrador_puppy'
os.makedirs(res + '/mesh', exist_ok=True); os.makedirs(res + '/textures/entity', exist_ok=True)
shutil.copy('out/assets/puppy_mesh.bin', res + '/mesh/puppy_mesh.bin')
shutil.copy('out/assets/labrador_puppy.png', res + '/textures/entity/labrador_puppy.png')
print('installed into', res)
