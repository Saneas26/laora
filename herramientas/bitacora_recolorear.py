# -*- coding: utf-8 -*-
"""Despiece de la Bitacora en todos los colores del catalogo.

NO es un render nuevo: es el MISMO montaje, recoloreado pixel a pixel.
Regla de oro: el canal alfa se copia tal cual del original. Solo cambia RGB.
Asi ninguna pieza puede moverse ni un pixel.
"""
import os, shutil
import numpy as np
from PIL import Image
from scipy import ndimage

ORIG = 'despiece/despiece-bitacora'
SAL  = 'salida/despiece-bitacora-2026'

# ---------------------------------------------------------------- rampas
def rampa(anclas):
    """Tabla de 256 colores por interpolacion lineal entre anclas (L, RGB)."""
    ls = np.array([a[0] for a in anclas], float)
    cs = np.array([a[1] for a in anclas], float)
    x = np.arange(256, dtype=float)
    return np.stack([np.interp(x, ls, cs[:,c]) for c in range(3)], axis=1)

METAL = {
 'acero-plata': None,                                  # identidad
 'bronce': rampa([(0,(6,4,3)),(40,(38,29,19)),(80,(76,58,38)),(130,(116,90,58)),
                  (175,(152,122,82)),(210,(184,154,110)),(235,(206,180,142)),
                  (255,(228,208,180))]),
 'oro-rosa': rampa([(0,(8,4,3)),(40,(50,30,24)),(80,(100,66,54)),(130,(152,108,90)),
                    (175,(194,150,128)),(210,(224,184,162)),(235,(241,212,195)),
                    (255,(255,240,231))]),
 'oro-amarillo': rampa([(0,(6,4,0)),(40,(48,32,6)),(80,(96,68,16)),(130,(150,112,32)),
                        (175,(196,154,56)),(210,(228,190,100)),(235,(245,218,150)),
                        (255,(255,244,210))]),
 'negro-pvd': rampa([(0,(1,1,1)),(40,(9,9,10)),(80,(20,20,22)),(130,(36,37,39)),
                     (175,(56,57,60)),(210,(84,86,90)),(235,(122,125,130)),
                     (255,(200,204,210))]),
}

ESFERA = {
 'turquesa': None,                                     # identidad
 'blanca': rampa([(0,(10,10,10)),(60,(58,58,57)),(120,(152,152,150)),(175,(216,216,213)),
                  (202,(241,241,238)),(222,(251,251,249)),(255,(255,255,255))]),
 'negra':  rampa([(0,(0,0,0)),(60,(5,5,6)),(120,(14,14,16)),(175,(22,22,25)),
                  (202,(34,34,38)),(222,(52,52,58)),(255,(96,96,104))]),
 'azul':   rampa([(0,(1,3,10)),(60,(6,16,44)),(120,(14,38,94)),(175,(25,64,143)),
                  (202,(33,82,170)),(222,(48,104,196)),(255,(115,165,228))]),
 'cobre':  rampa([(0,(8,3,1)),(60,(44,20,10)),(120,(96,50,28)),(175,(150,86,52)),
                  (202,(178,106,68)),(222,(200,128,90)),(255,(240,190,156))]),
}

# ------------------------------------------------------- utiles de pixel
def carga(ruta):
    a = np.array(Image.open(ruta).convert('RGBA')).astype(np.float32)
    return a[:,:,:3].copy(), a[:,:,3].copy()

def guarda(rgb, alfa, ruta):
    out = np.concatenate([np.clip(np.rint(rgb),0,255), alfa[...,None]], 2).astype(np.uint8)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    Image.fromarray(out).save(ruta, optimize=True)

def limpia_canto(rgb, alfa):
    """Mata el filete blanco: en el canto semitransparente, el color pasa a ser
    el del pixel opaco mas cercano. El alfa no se toca, asi que el recorte
    sigue siendo exactamente el mismo."""
    opaco = alfa >= 250
    if not opaco.any(): return rgb
    idx = ndimage.distance_transform_edt(~opaco, return_indices=True, return_distances=False)
    vecino = rgb[idx[0], idx[1]]
    canto = (alfa > 0) & ~opaco
    r = rgb.copy(); r[canto] = vecino[canto]
    return r

def luz(rgb):
    return 0.299*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]

def aplica(rgb, tabla, peso=None):
    """Mapa de degradado: la luminancia elige el color de la rampa."""
    if tabla is None: return rgb
    L = np.clip(luz(rgb), 0, 255)
    i = np.floor(L).astype(np.int32); f = (L - i)[...,None]
    i1 = np.minimum(i+1, 255)
    nuevo = tabla[i]*(1-f) + tabla[i1]*f
    if peso is None: return nuevo
    p = peso[...,None]
    return rgb*(1-p) + nuevo*p

def desatura(rgb, peso):
    gris = np.repeat(luz(rgb)[...,None], 3, axis=2)
    p = peso[...,None] if peso.ndim==2 else peso
    return rgb*(1-p) + gris*p

def croma(rgb):
    return rgb.max(2) - rgb.min(2)

def suave(v, a, b):
    t = np.clip((v-a)/(b-a), 0, 1)
    return t*t*(3-2*t)

# ------------------------------------------------------------- las piezas
def brazaletes(mask_centros):
    rgb, alfa = carga(f'{ORIG}/01-brazalete-norte-sur.png')
    rgb = limpia_canto(rgb, alfa)
    rgb = desatura(rgb, suave(croma(rgb), 5, 22))
    m = np.array(Image.fromarray((mask_centros*255).astype(np.uint8))
                 .filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(1.6)), np.float32)/255.
    for nom, metal, solo_centros in [
        ('acero-plata',                 'acero-plata',  False),
        ('acero-centros-oro-rosa',      'oro-rosa',     True),
        ('acero-centros-oro-amarillo',  'oro-amarillo', True),
        ('oro-rosa',                    'oro-rosa',     False),
        ('negro-pvd',                   'negro-pvd',    False),
    ]:
        out = aplica(rgb, METAL[metal], peso=(m if solo_centros else None))
        guarda(out, alfa, f'{SAL}/01-brazalete-norte-sur-{nom}.png')
        print('  01-brazalete-norte-sur-%s.png' % nom)

def cabezas():
    rgb, alfa = carga(f'{ORIG}/02-cabeza-hueca.png')
    rgb = limpia_canto(rgb, alfa)
    # el corte trae un resto de esfera turquesa pegado al bisel: se apaga para
    # que la caja valga con las cinco esferas
    rgb = desatura(rgb, suave(croma(rgb), 5, 22))
    for nom in ['acero-plata','bronce','oro-rosa','negro-pvd']:
        guarda(aplica(rgb, METAL[nom]), alfa, f'{SAL}/02-cabeza-hueca-{nom}.png')
        print('  02-cabeza-hueca-%s.png' % nom)

def esferas():
    rgb, alfa = carga('base/03-esfera-base26.png')      # ya lleva el 26
    rgb = limpia_canto(rgb, alfa)
    peso = suave(croma(rgb), 18, 45)      # 0 en indices y fecha, 1 en el fondo
    neutro = desatura(rgb, np.ones(rgb.shape[:2], np.float32))   # sin rastro turquesa
    for nom in ['turquesa','blanca','negra','azul','cobre']:
        base = rgb if nom == 'turquesa' else neutro
        guarda(aplica(base, ESFERA[nom], peso=peso), alfa, f'{SAL}/03-esfera-sin-agujas-{nom}.png')
        print('  03-esfera-sin-agujas-%s.png' % nom)

def agujas():
    os.makedirs(SAL, exist_ok=True)
    shutil.copyfile(f'{ORIG}/04-agujas-exactas.png', f'{SAL}/04-agujas-exactas.png')
    print('  04-agujas-exactas.png (copia exacta)')

if __name__ == '__main__':
    import centros
    print('mascara de los centros del brazalete...')
    mc = centros.construir(avisar=False)
    print('brazaletes...');  brazaletes(mc)
    print('cabezas...');     cabezas()
    print('esferas...');     esferas()
    print('agujas...');      agujas()
    print('hecho ->', SAL)
