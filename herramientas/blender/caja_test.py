# Prueba 1 del taller 3D de laOra: caja de acero cepillado en un estudio virtual.
# Objetivo: juzgar material y luz, no la forma. Sin esfera, sin agujas, sin correa.
#   blender --background --python herramientas/blender/caja_test.py
# Unidades: 1 unidad Blender = 1 mm.

import bpy, bmesh, math, sys, os

SALIDA = sys.argv[sys.argv.index('--salida') + 1] if '--salida' in sys.argv else '/tmp/caja.png'
LADO = int(sys.argv[sys.argv.index('--lado') + 1]) if '--lado' in sys.argv else 1024
MUESTRAS = int(sys.argv[sys.argv.index('--muestras') + 1]) if '--muestras' in sys.argv else 128

# ── escena limpia ──────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
esc = bpy.context.scene
esc.unit_settings.system = 'METRIC'
esc.unit_settings.scale_length = 0.001          # 1 unidad = 1 mm

# ── perfil de la sección de la caja, revolucionado ─────────────────────────
# (radio, altura) en mm. Caja de 38 mm de diámetro y 11 de alto.
PERFIL = [
    (0.0,  0.0), (15.5, 0.0), (17.2, 0.7),      # fondo y su chaflán
    (19.0, 2.4), (19.0, 8.4),                    # flanco recto de la caja
    (18.5, 9.5), (17.4, 10.5),                   # chaflán y cara del bisel: fino
    (16.9, 10.5), (16.9, 9.5),                   # asiento del cristal
    (16.6, 9.3), (16.6, 8.5), (0.0, 8.5),        # rehaut y suelo de la esfera
]

def revolucion(nombre, perfil, segmentos=256):
    m = bpy.data.meshes.new(nombre)
    o = bpy.data.objects.new(nombre, m)
    bpy.context.collection.objects.link(o)
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in perfil]
    for a, b in zip(verts, verts[1:]):
        bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], axis=(0, 0, 1),
                   cent=(0, 0, 0), dvec=(0, 0, 0), angle=math.tau,
                   steps=segmentos, use_merge=True)
    bm.to_mesh(m); bm.free()
    suaviza(o, 30)          # por ángulo: el flanco redondea, el chaflán no
    return o


def suaviza(obj, grados):
    """Suavizado por ángulo. Sin esto, las tapas planas heredan la normal del
    canto y el cristal actúa como lente convexa: la esfera se ve encogida."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(grados))
    obj.select_set(False)

caja = revolucion('caja', PERFIL)

# corona a las 3
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=2.6, depth=3.0,
                                    location=(20.4, 0, 5.4), rotation=(0, math.pi / 2, 0))
corona = bpy.context.object
corona.name = 'corona'
bpy.ops.object.modifier_add(type='BEVEL')
corona.modifiers['Bevel'].width = 0.25
corona.modifiers['Bevel'].segments = 3
suaviza(corona, 40)

# cristal de zafiro
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=16.85, depth=1.2, location=(0, 0, 10.1))
cristal = bpy.context.object
cristal.name = 'cristal'
suaviza(cristal, 20)        # la cara del cristal tiene que ser PLANA de verdad

# esfera negra, lisa: aquí solo sirve de fondo para el cristal
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=16.55, depth=0.4, location=(0, 0, 8.7))
dial = bpy.context.object
dial.name = 'esfera'

# ── materiales ─────────────────────────────────────────────────────────────
def material(nombre, **kw):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items():
        if k in p.inputs:
            p.inputs[k].default_value = v
    return m

# acero cepillado: la anisotropía es lo que lo separa de un metal de videojuego
acero = material('acero cepillado',
                 **{'Base Color': (0.56, 0.57, 0.58, 1.0), 'Metallic': 1.0,
                    'Roughness': 0.22, 'Anisotropic': 0.85, 'IOR': 2.5})
# tangente radial, para que el cepillado gire con la caja
nt = acero.node_tree
tan = nt.nodes.new('ShaderNodeTangent'); tan.direction_type = 'RADIAL'; tan.axis = 'Z'
nt.links.new(tan.outputs['Tangent'], nt.nodes['Principled BSDF'].inputs['Tangent'])
# cepillado: ruido estiradísimo en una dirección, en bump y en rugosidad
coord_a = nt.nodes.new('ShaderNodeTexCoord')
map_a = nt.nodes.new('ShaderNodeMapping')
map_a.inputs['Scale'].default_value = (900.0, 900.0, 4.0)
ruido = nt.nodes.new('ShaderNodeTexNoise')
ruido.inputs['Detail'].default_value = 2.0
ruido.inputs['Roughness'].default_value = 0.75
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.055
rug = nt.nodes.new('ShaderNodeMapRange')
rug.inputs['To Min'].default_value = 0.16
rug.inputs['To Max'].default_value = 0.30
nt.links.new(coord_a.outputs['Object'], map_a.inputs['Vector'])
nt.links.new(map_a.outputs['Vector'], ruido.inputs['Vector'])
nt.links.new(ruido.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
nt.links.new(ruido.outputs['Fac'], rug.inputs['Value'])
nt.links.new(rug.outputs['Result'], nt.nodes['Principled BSDF'].inputs['Roughness'])

# zafiro CON tratamiento antirreflejo: sin él, el cristal devuelve el estudio
# entero y la esfera se ve blanca. Es lo que separa un render de reloj de un
# render de bola de cristal.
zafiro = material('zafiro AR', **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0,
                                  'IOR': 1.05, 'Transmission Weight': 1.0})
# IOR 1.05 en vez de 1.77: el zafiro crudo devuelve el estudio entero y la esfera
# se ve gris. Bajarlo al del aire imita el tratamiento antirreflejo real.
negro = material('esfera negra', **{'Base Color': (0.006, 0.006, 0.0063, 1.0),
                                    'Roughness': 0.92, 'Metallic': 0.0})

for o, m in ((caja, acero), (corona, acero), (cristal, zafiro), (dial, negro)):
    o.data.materials.append(m)

# ── estudio: caja de luz cilíndrica alrededor ──────────────────────────────
# El metal no tiene color propio: refleja lo que le rodea. Sin entorno sale negro.
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=260, depth=420, location=(0, 0, 0))
softbox = bpy.context.object
softbox.name = 'caja de luz'
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.normals_make_consistent(inside=True)   # emite hacia dentro
bpy.ops.object.mode_set(mode='OBJECT')
mem = bpy.data.materials.new('luz de estudio'); mem.use_nodes = True
nt = mem.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.2
grad = nt.nodes.new('ShaderNodeTexGradient'); grad.gradient_type = 'LINEAR'
coord = nt.nodes.new('ShaderNodeTexCoord')
mapa = nt.nodes.new('ShaderNodeMapping'); mapa.inputs['Rotation'].default_value = (0, math.radians(90), 0)
rampa = nt.nodes.new('ShaderNodeValToRGB')
rampa.color_ramp.elements[0].position = 0.44; rampa.color_ramp.elements[0].color = (0.015, 0.015, 0.018, 1)
rampa.color_ramp.elements[1].position = 0.80; rampa.color_ramp.elements[1].color = (1, 1, 1, 1)
sal = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(coord.outputs['Object'], mapa.inputs['Vector'])
nt.links.new(mapa.outputs['Vector'], grad.inputs['Vector'])
nt.links.new(grad.outputs['Color'], rampa.inputs['Fac'])
nt.links.new(rampa.outputs['Color'], em.inputs['Color'])
nt.links.new(em.outputs['Emission'], sal.inputs['Surface'])
softbox.data.materials.append(mem)
softbox.visible_camera = False          # ilumina y se refleja, pero no sale en la foto

# softbox principal, arriba y algo al frente
bpy.ops.object.light_add(type='AREA', location=(0, -70, 150))
key = bpy.context.object
key.data.shape = 'RECTANGLE'; key.data.size = 200; key.data.size_y = 140
key.data.energy = 225000
key.rotation_euler = (math.radians(26), 0, 0)

# relleno lateral suave
bpy.ops.object.light_add(type='AREA', location=(-140, -40, 40))
fill = bpy.context.object
fill.data.size = 160; fill.data.energy = 55000
fill.rotation_euler = (math.radians(75), 0, math.radians(-62))

# ── cámara ortográfica frontal ─────────────────────────────────────────────
bpy.ops.object.camera_add(location=(0, 0, 300), rotation=(0, 0, 0))
cam = bpy.context.object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 46          # deja aire alrededor de los 38 mm
esc.camera = cam

# ── render ─────────────────────────────────────────────────────────────────
esc.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for d in prefs.devices:
    d.use = (d.type == 'METAL')
esc.cycles.device = 'GPU'
esc.cycles.samples = MUESTRAS
esc.cycles.use_denoising = True
esc.cycles.caustics_reflective = True
esc.render.resolution_x = esc.render.resolution_y = LADO
esc.render.film_transparent = True          # fondo transparente de salida
esc.render.image_settings.file_format = 'PNG'
esc.render.image_settings.color_mode = 'RGBA'
esc.render.filepath = SALIDA
bpy.ops.render.render(write_still=True)
print('RENDER LISTO:', SALIDA)
