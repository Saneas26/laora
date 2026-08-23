# Caja del Trinchera (reloj de campo, 38 mm) para el taller 3D de laOra.
#   blender --background --python herramientas/blender/khaki.py -- --salida x.png
#
# Unidades: 1 unidad Blender = 1 mm. Medidas de un campo de 38:
#   caja 38,0 · alto 11,0 · entrecuernos 20,0 · de asa a asa 46,5
#
# La clave del realismo NO es la forma, es que convivan tres acabados: el
# granallado mate del cuerpo, el cepillado de la cara del bisel y el PULIDO de
# los chaflanes. Esa línea de luz viva contra el mate es la firma de un reloj
# bien acabado; sin ella las asas parecen cartón. Se reparten por programa,
# clasificando cada cara por la inclinación de su normal.

import bpy, bmesh, math, sys

arg = lambda n, d: (type(d)(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d)
SALIDA   = arg('--salida', '/tmp/khaki.png')
LADO     = arg('--lado', 1200)
MUESTRAS = arg('--muestras', 200)
GIRO     = arg('--giro', 0.0)        # grados de inclinación de la cámara

bpy.ops.wm.read_factory_settings(use_empty=True)
esc = bpy.context.scene
esc.unit_settings.system = 'METRIC'
esc.unit_settings.scale_length = 0.001

GRANALLADO, CEPILLADO, PULIDO = 0, 1, 2      # índices de material


def suaviza(obj, grados):
    """Por ángulo: el flanco redondea y el chaflán se queda vivo. El suavizado
    global convierte la cara del cristal en lente convexa."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(grados))
    obj.select_set(False)


def reparte_acabados(obj, z_bisel=10.0):
    """Un chaflán es una cara inclinada: ni horizontal ni vertical. Eso basta
    para encontrarlos y darles el pulido, sin marcarlos a mano."""
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me)
    for f in bm.faces:
        nz = abs(f.normal.z)
        z = f.calc_center_median().z
        if nz > 0.80:
            f.material_index = CEPILLADO if z > z_bisel else GRANALLADO
        elif nz > 0.22:
            f.material_index = PULIDO            # chaflán: la línea de luz
        else:
            f.material_index = GRANALLADO
    bm.to_mesh(me); bm.free()


# ── cuerpo de la caja ──────────────────────────────────────────────────────
# (radio, altura). El flanco NO es recto: se estrecha hacia el fondo, y el
# bisel lleva su chaflán antes de la cara plana.
PERFIL = [
    (0.0,   0.00), (13.5, 0.00),                 # fondo
    (15.2,  0.35), (16.4, 1.15),                 # chaflán del fondo
    (17.6,  2.00), (18.55, 3.30), (19.0, 4.60),  # flanco, estrechándose
    (19.0,  7.90),                               # radio máximo
    (18.72, 8.80), (18.15, 9.55),                # chaflán del bisel: PULIDO
    (17.45, 10.35), (17.05, 10.52),              # cara del bisel: cepillada
    (16.92, 10.52), (16.90, 10.10),              # asiento del cristal
    (16.90, 9.55), (16.62, 9.35),                # rehaut
    (16.38, 8.62), (16.30, 8.45), (0.0, 8.45),   # y suelo de la esfera
]


def revolucion(nombre, perfil, segmentos=320):
    m = bpy.data.meshes.new(nombre)
    o = bpy.data.objects.new(nombre, m)
    bpy.context.collection.objects.link(o)
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0.0, z)) for r, z in perfil]
    for a, b in zip(vs, vs[1:]):
        bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], axis=(0, 0, 1),
                   cent=(0, 0, 0), dvec=(0, 0, 0), angle=math.tau,
                   steps=segmentos, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(m); bm.free()
    return o


caja = revolucion('caja', PERFIL)

# ── asas ───────────────────────────────────────────────────────────────────
# Curvatura compuesta: bajan hacia la muñeca Y se cierran hacia dentro, con la
# sección adelgazando. Cada sección es un hexágono con dos chaflanes arriba.
#   (y, z centro, alto, semiancho, x centro, chaflán)
SECCIONES = [
    (10.0, 4.95, 5.5, 2.30, 12.25, 0.30),   # nace dentro de la caja
    (15.0, 4.85, 5.2, 2.28, 12.24, 0.42),
    (18.5, 4.60, 4.7, 2.22, 12.15, 0.50),
    (21.0, 4.10, 4.0, 2.12, 11.98, 0.52),
    (22.6, 3.55, 3.4, 2.00, 11.80, 0.50),
    (23.3, 3.05, 2.9, 1.90, 11.68, 0.42),   # punta, cortada casi recta
]


def seccion(bm, y, z, alto, semi, xc, ch, sx, sy):
    """Hexágono: rectángulo con las dos aristas de arriba chafladas."""
    h, x = alto / 2, xc * sx
    pts = [(-semi, -h), (semi, -h), (semi, h - ch), (semi - ch, h),
           (-semi + ch, h), (-semi, h - ch)]
    return [bm.verts.new((x + dx, y * sy, z + dz)) for dx, dz in pts]


def asa(nombre, sx, sy):
    m = bpy.data.meshes.new(nombre)
    o = bpy.data.objects.new(nombre, m)
    bpy.context.collection.objects.link(o)
    bm = bmesh.new()
    anillos = [seccion(bm, y, z, a, s, xc, ch, sx, sy)
               for y, z, a, s, xc, ch in SECCIONES]
    n = len(anillos[0])
    for a, b in zip(anillos, anillos[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(anillos[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=0.16,
                    segments=3, affect='EDGES', profile=0.6)
    bm.to_mesh(m); bm.free()
    return o


asas = [asa('asa%d' % i, sx, sy) for i, (sx, sy) in
        enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1)))]

# ── corona ─────────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=2.75, depth=3.3,
                                    location=(20.6, 0, 5.3), rotation=(0, math.pi / 2, 0))
corona = bpy.context.object; corona.name = 'corona'
bm = bmesh.new(); bm.from_mesh(corona.data)
bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.45, segments=4,
                affect='EDGES', profile=0.5)
bm.to_mesh(corona.data); bm.free()

# ── cristal y esfera ───────────────────────────────────────────────────────
bpy.ops.mesh.primitive_cylinder_add(vertices=320, radius=16.85, depth=1.2, location=(0, 0, 10.15))
cristal = bpy.context.object; cristal.name = 'cristal'
suaviza(cristal, 20)                 # la cara del cristal, PLANA de verdad

bpy.ops.mesh.primitive_cylinder_add(vertices=320, radius=16.4, depth=0.4, location=(0, 0, 8.65))
dial = bpy.context.object; dial.name = 'esfera'

# ── materiales ─────────────────────────────────────────────────────────────
def material(nombre, **kw):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items():
        if k in p.inputs:
            p.inputs[k].default_value = v
    return m


def con_grano(mat, escala, fuerza, rug_min, rug_max):
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']
    co = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = escala
    ru = nt.nodes.new('ShaderNodeTexNoise')
    ru.inputs['Detail'].default_value = 6.0
    ru.inputs['Roughness'].default_value = 0.6
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = fuerza
    rg = nt.nodes.new('ShaderNodeMapRange')
    rg.inputs['To Min'].default_value = rug_min
    rg.inputs['To Max'].default_value = rug_max
    nt.links.new(co.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], ru.inputs['Vector'])
    nt.links.new(ru.outputs['Fac'], bu.inputs['Height'])
    nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(ru.outputs['Fac'], rg.inputs['Value'])
    nt.links.new(rg.outputs['Result'], b.inputs['Roughness'])
    return mat


GRIS = (0.552, 0.556, 0.562, 1.0)
granallado = con_grano(material('acero granallado', **{'Base Color': GRIS, 'Metallic': 1.0,
                                'Roughness': 0.36, 'IOR': 2.5}), (300, 300, 300), 0.13, 0.30, 0.44)
cepillado = material('acero cepillado', **{'Base Color': GRIS, 'Metallic': 1.0,
                     'Roughness': 0.17, 'Anisotropic': 0.85, 'IOR': 2.5})
nt = cepillado.node_tree
tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'RADIAL'; tg.axis = 'Z'
nt.links.new(tg.outputs['Tangent'], nt.nodes['Principled BSDF'].inputs['Tangent'])
con_grano(cepillado, (700, 700, 12), 0.05, 0.13, 0.22)
pulido = material('acero pulido', **{'Base Color': (0.585, 0.59, 0.60, 1.0),
                  'Metallic': 1.0, 'Roughness': 0.045, 'IOR': 2.5})

# IOR 1,05 en vez de 1,77: imita el antirreflejo. Con el del zafiro crudo el
# cristal devuelve el estudio entero y la esfera se ve gris.
zafiro = material('zafiro AR', **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0,
                                  'IOR': 1.05, 'Transmission Weight': 1.0})
negro = material('esfera negra', **{'Base Color': (0.006, 0.006, 0.0063, 1.0),
                                    'Roughness': 0.92, 'Metallic': 0.0})

for o in [caja, corona] + asas:
    for m in (granallado, cepillado, pulido):
        o.data.materials.append(m)
    reparte_acabados(o, z_bisel=10.0 if o is caja else 99)
    suaviza(o, 26)
corona.data.materials[CEPILLADO] = pulido      # la corona va pulida
cristal.data.materials.append(zafiro)
dial.data.materials.append(negro)

# ── estudio ────────────────────────────────────────────────────────────────
# El metal no tiene color: refleja lo que le rodea. Y necesita BANDAS, no un
# degradado liso: son los bordes entre panel y hueco los que le dan forma.
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=260, depth=420)
softbox = bpy.context.object; softbox.name = 'caja de luz'
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.normals_make_consistent(inside=True)
bpy.ops.object.mode_set(mode='OBJECT')
mem = bpy.data.materials.new('luz de estudio'); mem.use_nodes = True
nt = mem.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.5
grad = nt.nodes.new('ShaderNodeTexGradient')
co = nt.nodes.new('ShaderNodeTexCoord')
mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, math.radians(90), 0)
ra = nt.nodes.new('ShaderNodeValToRGB')
ra.color_ramp.interpolation = 'B_SPLINE'
while len(ra.color_ramp.elements) > 1:
    ra.color_ramp.elements.remove(ra.color_ramp.elements[-1])
BANDAS = [(0.00, 0.010), (0.30, 0.020), (0.40, 0.85), (0.52, 0.35),
          (0.63, 1.00), (0.76, 0.10), (0.86, 1.00), (1.00, 0.55)]
e0 = ra.color_ramp.elements[0]; e0.position, v = BANDAS[0]
e0.color = (v, v, v * 1.02, 1)
for pos, v in BANDAS[1:]:
    el = ra.color_ramp.elements.new(pos); el.color = (v, v, v * 1.02, 1)
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(co.outputs['Object'], mp.inputs['Vector'])
nt.links.new(mp.outputs['Vector'], grad.inputs['Vector'])
nt.links.new(grad.outputs['Color'], ra.inputs['Fac'])
nt.links.new(ra.outputs['Color'], em.inputs['Color'])
nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
softbox.data.materials.append(mem)
softbox.visible_camera = False

bpy.ops.object.light_add(type='AREA', location=(0, -70, 150))
key = bpy.context.object
key.data.shape = 'RECTANGLE'; key.data.size = 200; key.data.size_y = 140
key.data.energy = 225000
key.rotation_euler = (math.radians(26), 0, 0)

bpy.ops.object.light_add(type='AREA', location=(-140, -40, 40))
fill = bpy.context.object
fill.data.size = 160; fill.data.energy = 55000
fill.rotation_euler = (math.radians(75), 0, math.radians(-62))

# Anillo de luz a la altura del canto. El flanco es vertical: refleja el
# estudio a SU misma altura, y ahí la rampa está oscura, así que salía negro.
bpy.ops.mesh.primitive_torus_add(location=(0, 0, 5.2), major_radius=95,
                                 minor_radius=13, major_segments=96, minor_segments=16)
anillo = bpy.context.object; anillo.name = 'anillo de luz'
man = bpy.data.materials.new('anillo'); man.use_nodes = True
ntr = man.node_tree; ntr.nodes.clear()
eem = ntr.nodes.new('ShaderNodeEmission')
eem.inputs['Strength'].default_value = 9.0  # anillo a la altura del canto
eem.inputs['Color'].default_value = (1, 1, 1, 1)
oo = ntr.nodes.new('ShaderNodeOutputMaterial')
ntr.links.new(eem.outputs['Emission'], oo.inputs['Surface'])
anillo.data.materials.append(man)
anillo.visible_camera = False

for lado in (1, -1):                      # rasantes, para modelar el canto
    bpy.ops.object.light_add(type='AREA', location=(120 * lado, 20, 6))
    r = bpy.context.object
    r.data.shape = 'RECTANGLE'; r.data.size = 60; r.data.size_y = 160
    r.data.energy = 40000
    r.rotation_euler = (math.radians(90), 0, math.radians(90 * lado))

# ── cámara ─────────────────────────────────────────────────────────────────
a = math.radians(GIRO)
d = 300
bpy.ops.object.camera_add(location=(0, -d * math.sin(a), d * math.cos(a)),
                          rotation=(a, 0, 0))
cam = bpy.context.object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 54
esc.camera = cam

esc.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'; prefs.get_devices()
for dv in prefs.devices:
    dv.use = (dv.type == 'METAL')
esc.cycles.device = 'GPU'
esc.cycles.samples = MUESTRAS
esc.cycles.use_denoising = True
esc.render.resolution_x = esc.render.resolution_y = LADO
esc.render.film_transparent = True
esc.render.image_settings.file_format = 'PNG'
esc.render.image_settings.color_mode = 'RGBA'
esc.render.filepath = SALIDA
bpy.ops.render.render(write_still=True)
print('RENDER LISTO:', SALIDA)
