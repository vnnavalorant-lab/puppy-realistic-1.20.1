import numpy as np
from PIL import Image
from parse import load

S = 0.2           # blocks per model unit
YOFF = 1.501      # LivingEntityRenderer offset

def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

# ---- skeleton (pivots in Y-up model units; converted to MC space later) ----
BONES = [  # name, parent, pivot (x,y,z)  [x>0 = "L"]
 ('body',   -1, (0, 1.6, 0.0)),
 ('head',    0, (0, 2.25, 1.40)),
 ('ear_l',   1, ( 0.55, 3.00, 1.50)),
 ('ear_r',   1, (-0.55, 3.00, 1.50)),
 ('tail1',   0, (0, 2.10, -1.45)),
 ('tail2',   4, (0, 2.10, -2.20)),
 ('fl_up',   0, ( 0.45, 1.55, 1.25)),
 ('fl_low',  6, ( 0.45, 0.60, 1.40)),
 ('fr_up',   0, (-0.45, 1.55, 1.25)),
 ('fr_low',  8, (-0.45, 0.60, 1.40)),
 ('bl_up',   0, ( 0.45, 1.55, -1.00)),
 ('bl_low', 10, ( 0.45, 0.75, -1.40)),
 ('br_up',   0, (-0.45, 1.55, -1.00)),
 ('br_low', 12, (-0.45, 0.75, -1.40)),
]
BI = {b[0]: i for i, b in enumerate(BONES)}
NB = len(BONES)

def compute_weights(V):
    """V: (N,3) Y-up model units -> (N,NB) weights"""
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    ax = np.abs(x)
    W = np.zeros((len(V), NB))
    lateral = sstep(0.12, 0.38, ax)
    # legs
    frontZ = sstep(0.25, 0.65, z)
    backZ = 1 - sstep(-0.55, -0.05, z)
    legF = frontZ * lateral * sstep(1.75, 1.05, y)
    legB = backZ * lateral * sstep(1.85, 1.00, y)
    lowF = sstep(0.95, 0.60, y)
    lowB = sstep(1.00, 0.65, y)
    left = x >= 0
    for (name_up, name_low, wleg, wlow, side) in [
        ('fl_up', 'fl_low', legF, lowF, left), ('fr_up', 'fr_low', legF, lowF, ~left),
        ('bl_up', 'bl_low', legB, lowB, left), ('br_up', 'br_low', legB, lowB, ~left)]:
        w = wleg * side
        W[:, BI[name_low]] = w * wlow
        W[:, BI[name_up]] = w * (1 - wlow)
    # head / ears
    head = sstep(1.90, 2.35, y) * sstep(1.15, 1.75, z)
    ear = sstep(0.47, 0.60, ax) * sstep(1.10, 1.30, z) * sstep(1.90, 1.65, z) * sstep(2.20, 2.45, y)
    W[:, BI['ear_l']] = ear * left
    W[:, BI['ear_r']] = ear * ~left
    W[:, BI['head']] = head * (1 - ear)
    # tail
    tail = sstep(-1.20, -1.80, z) * sstep(1.60, 1.95, y)
    t2 = tail * sstep(-1.85, -2.45, z)
    W[:, BI['tail2']] = t2
    W[:, BI['tail1']] = tail - t2
    s = W.sum(1)
    over = s > 1
    W[over] /= s[over, None]
    W[:, BI['body']] = 1 - W.sum(1)
    return W

# ---- pose (mirror of the Java code) -------------------------------------
def rot(rx, ry, rz):
    cx, sx_, cy, sy_, cz, sz_ = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    Rx = np.array([[1,0,0],[0,cx,-sx_],[0,sx_,cx]])
    Ry = np.array([[cy,0,sy_],[0,1,0],[-sy_,0,cy]])
    Rz = np.array([[cz,-sz_,0],[sz_,cz,0],[0,0,1]])
    return Rz @ Ry @ Rx

def local_mat(pivot, t=(0,0,0), r=(0,0,0), s=(1,1,1)):
    M = np.eye(4); M[:3,:3] = rot(*r) @ np.diag(s); 
    p = np.array(pivot)
    M[:3,3] = np.array(t) + p - M[:3,:3] @ p
    return M

def pose_params(limb, dist, age, head_yaw_deg, head_pitch_deg):
    """returns dict bone -> dict(t,r,s). Units: blocks / radians. MC model space (Y down, front -Z)."""
    D = min(max(dist, 0), 1); ts = age / 20.0
    phi = limb * 0.8
    P = {b[0]: dict(t=(0,0,0), r=(0,0,0), s=(1,1,1)) for b in BONES}
    # --- body
    bob = -0.022 * D * abs(np.cos(phi))
    breath = np.sin(ts * 2 * np.pi / 2.8)
    P['body']['t'] = (0, bob, 0)
    P['body']['r'] = (0.03 * D * np.sin(2 * phi), 0.05 * D * np.cos(phi), 0.04 * D * np.sin(phi))
    P['body']['s'] = (1 - 0.012 * breath * (1 - D), 1 + 0.03 * breath * (1 - D), 1 - 0.012 * breath * (1 - D))
    # --- legs
    A = 0.62 * D; K = 0.85 * D
    ph = {'fl': phi, 'br': phi, 'fr': phi + np.pi, 'bl': phi + np.pi}
    for leg, p in ph.items():
        P[leg + '_up']['r'] = (A * np.cos(p), 0, 0)
        P[leg + '_low']['r'] = (K * max(0.0, np.sin(p)) + 0.08 * D, 0, 0)
    # --- head
    yaw = np.clip(np.radians(head_yaw_deg), -1.05, 1.05) + 0.14 * np.sin(ts * 0.9) * (1 - D)
    pitch = np.clip(np.radians(head_pitch_deg), -0.7, 0.7) + 0.035 * np.sin(ts * 1.7) * (1 - D) + 0.03 * breath * (1 - D) + 0.05 * D * np.sin(2 * phi)
    P['head']['r'] = (pitch, yaw, -0.04 * D * np.sin(phi))
    # --- tail
    wag = np.sin(ts * 2 * np.pi * 2.2)
    amp = 0.30 + 0.30 * D
    P['tail1']['r'] = (0.15 + 0.20 * D + 0.04 * np.sin(ts * 1.3), amp * wag, 0)
    P['tail2']['r'] = (0.10 * D, amp * 0.9 * np.sin(ts * 2 * np.pi * 2.2 - 0.9), 0)
    # --- ears
    twitch_l = max(0.0, np.sin(ts * 0.7)) ** 12 * 0.30
    twitch_r = max(0.0, np.sin(ts * 0.7 + 2.0)) ** 12 * 0.30
    bounce = 0.14 * D * np.sin(2 * phi + 0.6)
    P['ear_l']['r'] = (bounce + 0.04 * np.sin(ts * 1.3), 0, 0.06 * np.sin(ts * 2.1) + twitch_l)
    P['ear_r']['r'] = (bounce + 0.04 * np.sin(ts * 1.3 + 1), 0, -0.06 * np.sin(ts * 2.1 + 1) - twitch_r)
    return P

def to_mc(p):  # model units Y-up (front +z) -> MC model space
    p = np.asarray(p, float)
    return np.stack([p[..., 0] * S, YOFF - p[..., 1] * S, -p[..., 2] * S], -1)

def from_mc(p):
    return np.stack([p[..., 0] / S, (YOFF - p[..., 1]) / S, -p[..., 2] / S], -1)

PIV_MC = [to_mc(b[2]) for b in BONES]

def world_mats(P):
    W = []
    for i, (name, parent, _) in enumerate(BONES):
        L = local_mat(PIV_MC[i], P[name]['t'], P[name]['r'], P[name]['s'])
        W.append(L if parent < 0 else W[parent] @ L)
    return W

def skin(Vmc, Nmc, weights, bidx, bw, W):
    out = np.zeros_like(Vmc); nout = np.zeros_like(Nmc)
    for k in range(4):
        M = np.stack([W[i] for i in range(NB)])[bidx[:, k]]   # (N,4,4)
        w = bw[:, k:k+1]
        out += w * (np.einsum('nij,nj->ni', M[:, :3, :3], Vmc) + M[:, :3, 3])
        nout += w * np.einsum('nij,nj->ni', M[:, :3, :3], Nmc)
    nout /= np.linalg.norm(nout, axis=1, keepdims=True) + 1e-9
    return out, nout

def top4(Wt):
    idx = np.argsort(-Wt, axis=1)[:, :4]
    w = np.take_along_axis(Wt, idx, 1)
    w /= w.sum(1, keepdims=True)
    return idx.astype(np.uint8), w.astype(np.float32)

def build_mesh():
    j, prims = load()
    parts = []
    for pi, tid in [(1, 'body'), (2, 'eye')]:
        p = prims[pi]; P = p['pos']; N = p['nor']
        V = np.stack([P[:, 0], P[:, 2], -P[:, 1]], 1)      # Z-up -> Y-up
        Nn = np.stack([N[:, 0], N[:, 2], -N[:, 1]], 1)
        uv = p['uv'].copy()
        parts.append(dict(V=V, N=Nn, uv=uv, F=p['idx'].reshape(-1, 3).astype(np.int64), kind=tid))
    return parts
