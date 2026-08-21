import json, math, numpy as np
from PIL import Image
FONDO=(234,232,232)
ARCOS=[(225,315),(20,70),(110,160)]   # izquierda limpia; arriba-dcha y abajo-dcha entre asas y pulsadores
def bisel_ext(im, c0=(631,571), r_ini=300):
    a=np.asarray(im.convert('RGB')).astype(float); lum=a.mean(axis=2); H,W=lum.shape
    cx,cy=c0
    for vuelta in range(3):
        pts=[]
        for lo,hi in ARCOS:
            for g in range(lo,hi+1,2):
                t=math.radians(g); dx,dy=math.sin(t),-math.cos(t)
                r=r_ini; enNegro=False; hit=None
                while r<430:
                    x,y=int(round(cx+dx*r)),int(round(cy+dy*r))
                    if not(0<=x<W and 0<=y<H): break
                    v=lum[y,x]
                    if v<70: enNegro=True
                    elif enNegro and v>120:
                        # acero sostenido 14 px
                        ok=True
                        for j in range(1,15):
                            xx,yy=int(round(cx+dx*(r+j))),int(round(cy+dy*(r+j)))
                            if not(0<=xx<W and 0<=yy<H) or lum[yy,xx]<110: ok=False; break
                        if ok: hit=r; break
                    r+=1
                if hit: pts.append((cx+dx*hit,cy+dy*hit))
        P=np.array(pts,float)
        for _ in range(2):
            A=np.stack([P[:,0],P[:,1],np.ones(len(P))],1); c=np.linalg.lstsq(A,(P**2).sum(1),rcond=None)[0]
            ncx,ncy=c[0]/2,c[1]/2; R=math.sqrt(c[2]+ncx*ncx+ncy*ncy)
            err=np.abs(np.hypot(P[:,0]-ncx,P[:,1]-ncy)-R); P=P[err<np.percentile(err,70)]
        cx,cy=ncx,ncy
    return cx,cy,R,float(err.mean()),len(P)
if __name__=='__main__':
    ref=Image.open('assets/img/lunar-config/heads/cab-acero-bnegro-agujas-plateadas.webp').convert('RGBA')
    bg=Image.new('RGBA',ref.size,FONDO+(255,)); bg.alpha_composite(ref)
    print('CABEZA ref   bisel ext centro=(%.1f,%.1f) R=%.1f err=%.1f n=%d'%bisel_ext(bg))
    for n in ['cab-acero-bazul-esfblanca-agujas-azules','cab-acero-bnegro-esf26-negra-dorada','cab-acero-bnegro-esf44-racing-naranja']:
        im=Image.open('assets/img/lunar-config/heads/%s.webp'%n).convert('RGBA'); b=Image.new('RGBA',im.size,FONDO+(255,)); b.alpha_composite(im)
        print('%-44s centro=(%.1f,%.1f) R=%.1f err=%.1f n=%d'%((n,)+bisel_ext(b)))
    m=json.load(open('assets/img/lunar-config/manifest.json'))
    for k in ['brazalete-acero-316l-cinco-columnas','nato-pasadores-verde-militar','caucho-negro-naranja','piel-italiana-azul','brazalete-negro-pvd','piel-negra-perforada-pespunte-blanco']:
        im=Image.open('.'+m['straps'][k]['src'].split('?')[0])
        print('%-44s centro=(%.1f,%.1f) R=%.1f err=%.1f n=%d'%((k,)+bisel_ext(im)))
