"""3-D beam-frame model of the tower (pillars + rib diaphragms) -> first lateral natural frequencies.
Pad+coin masses lumped on the pillars around them.  Fixed at the base plate.  E is a conservative layer-bond value."""
import sys, math, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
sys.path.insert(0, '..')
import coin_tower as ct

def beam_K(L, E, G, A, Iy, Iz, J):
    k = np.zeros((12, 12)); a = E*A/L
    k[0,0]=k[6,6]=a; k[0,6]=k[6,0]=-a
    t = G*J/L; k[3,3]=k[9,9]=t; k[3,9]=k[9,3]=-t
    def bend(I, idx, sgn):
        v, th = idx
        c1=12*E*I/L**3; c2=6*E*I/L**2; c3=4*E*I/L; c4=2*E*I/L
        m = np.array([[c1, sgn*c2, -c1, sgn*c2],[sgn*c2, c3, -sgn*c2, c4],[-c1, -sgn*c2, c1, -sgn*c2],[sgn*c2, c4, -sgn*c2, c3]])
        ids = [v, th, v+6, th+6]
        for i in range(4):
            for j in range(4): k[ids[i], ids[j]] += m[i, j]
    bend(Iz, (1, 5), 1)      # bending in xy plane (about z)
    bend(Iy, (2, 4), -1)     # bending in xz plane (about y)
    return k

def rot(p0, p1, up=np.array([0,0,1.0])):
    ex = (p1-p0); L = np.linalg.norm(ex); ex = ex/L
    if abs(ex@up) > 0.99: ey = np.array([0,1.0,0]); 
    else: ey = np.cross(up, ex); ey/=np.linalg.norm(ey)
    if abs(ex@up) > 0.99: ey = np.cross(np.array([1.0,0,0]), ex); ey/=np.linalg.norm(ey)
    ez = np.cross(ex, ey); R = np.array([ex, ey, ez]); T = np.zeros((12,12))
    for i in range(4): T[3*i:3*i+3, 3*i:3*i+3] = R
    return L, T

def modes(cols, rows, levels, E=2.0e3, nu=0.35, rho=1.24e-3, nm=6):
    coins = ct.layout(cols, rows)
    dirs, edges, pill = ct.network(coins)
    P = sorted(pill); idx = {p:i for i,p in enumerate(P)}
    zs = [0.0] + [ct.BASE + ct.GAP + k*ct.PITCH - ct.GAP - ct.TP/2 for k in range(1, levels)] + [ct.BASE + ct.GAP + (levels-1)*ct.PITCH + ct.TC + ct.GAP + ct.CAP/2]
    nl = len(zs); N = len(P)*nl; G = E/(2*(1+nu))
    Apil=math.pi*ct.R_PILLAR**2; Ipil=math.pi*ct.R_PILLAR**4/4; Jpil=2*Ipil
    b, h = ct.RIB_W, ct.TP
    rows_, cols_, vals = [], [], []
    def add(i, j, k, T):
        kg = T.T @ k @ T; ids = list(range(6*i,6*i+6))+list(range(6*j,6*j+6))
        for a in range(12):
            for c in range(12): rows_.append(ids[a]); cols_.append(ids[c]); vals.append(kg[a,c])
    nid = lambda p, l: l*len(P)+idx[p]
    for l in range(nl-1):
        for p in P:
            p0=np.array([*p, zs[l]]); p1=np.array([*p, zs[l+1]]); L,T = rot(p0,p1)
            add(nid(p,l), nid(p,l+1), beam_K(L,E,G,Apil,Ipil,Ipil,Jpil), T)
    for l in range(1, nl):
        for (a, c) in edges.values():
            p0=np.array([*a, zs[l]]); p1=np.array([*c, zs[l]]); L,T = rot(p0,p1)
            hh = ct.CAP if l == nl-1 else h
            add(nid(a,l), nid(c,l), beam_K(L,E,G,b*hh,b*hh**3/12,hh*b**3/12,0.3*b*hh**3), T)
    K = sp.coo_matrix((vals,(rows_,cols_)), shape=(6*N,6*N)).tocsr()
    # masses (tonne-less units: g -> use mm, N, so mass in tonne; use rho in t/mm3 => 1.24e-9)
    m = np.zeros(N)
    for l in range(nl):
        for p in P:
            mp = Apil*(ct.PITCH if 0<l<nl-1 else ct.PITCH/2)*1.24e-9
            m[nid(p,l)] += mp
    padmass = (1.24e-9)*(math.pi*ct.R_PAD**2*ct.TP + 2.25e3)   # pad + coin
    for l in range(1, nl-1):
        for (x,y) in coins:
            ring=[p for p in ct.ring_pts((x,y)) if p in idx]
            for p in ring: m[nid(p,l)] += padmass/len(ring)
    for (x,y) in coins:   # level-0 coin and top coin
        ring=[p for p in ct.ring_pts((x,y)) if p in idx]
        for p in ring: m[nid(p,nl-1)] += 1.24e-9*2.25e3/len(ring)
    Md = np.repeat(m, 6); Md[Md==0] = 1e-14
    free = np.array([i for i in range(6*N) if i >= 6*len(P)])     # fix level-0 nodes (base plate)
    Kf = K[free][:,free]; Mf = sp.diags(Md[free])
    w2, v = sla.eigsh(Kf, k=nm, M=Mf, sigma=0, which='LM')
    f = np.sqrt(np.abs(w2))/(2*math.pi)
    return sorted(f), sum(m)*1e9*1e-3   # Hz, total mass grams-ish
if __name__ == "__main__":
    c, r, l = map(int, sys.argv[1:4])
    f, M = modes(c, r, l); print(f"{c}x{r}x{l}: first modes Hz {[round(x,1) for x in f[:4]]}   (model mass {M:.0f} g)")
