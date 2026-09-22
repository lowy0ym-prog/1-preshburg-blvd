
import bpy, math
from mathutils import Vector

# Preshburg Blvd / Strelisk Ct building reconstruction
# Research inputs:
# - Address: 1 Preshburg Blvd, Monroe, NY 10950, Unit 401
# - Year built: 2014
# - Public records list 1,393 / 1,539 sq ft unit types in this building.
# - User supplied two Google Street View links; their resolved viewpoints are:
#   41.3374939,-74.1745682 yaw 52.64 pitch -15
#   41.3374252,-74.1739578 yaw 331.72 pitch -8
#
# IMPORTANT: This is a reconstruction, not a survey. The public Street View
# image pixels could not be imported automatically here, so facade dimensions
# and details are intentionally organized as editable parameters.

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------- materials ----------
def mat(name, color, rough=0.65, metallic=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    return m

brick=mat('Brick', (0.38,0.13,0.08))
brick2=mat('Dark Brick', (0.25,0.10,0.07))
siding=mat('Light vinyl siding', (0.60,0.60,0.56))
trim=mat('White trim', (0.90,0.88,0.82))
roof=mat('Roof shingles', (0.16,0.17,0.18))
glass=mat('Dark window glass', (0.05,0.11,0.15), 0.18)
wood=mat('Porch wood', (0.34,0.20,0.10))
metal=mat('Black metal', (0.04,0.04,0.04), 0.35, 0.1)
grass=mat('Grass', (0.16,0.30,0.09))
sidewalk=mat('Concrete', (0.58,0.58,0.56))
asphalt=mat('Asphalt', (0.08,0.09,0.10))
signmat=mat('Street sign green', (0.02,0.28,0.13))
white=mat('Sign white', (0.95,0.95,0.95))

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=(scale[0]/2,scale[1]/2,scale[2]/2)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=2
    return o

def cyl(name, loc, radius, depth, material, verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if material: o.data.materials.append(material)
    return o

def window(name,x,y,z,w=1.15,h=2.2,frame=0.10):
    cube(name+' glass',(x,y,z),(w,0.10,h),glass,0.03)
    cube(name+' left',(x-w/2,y-0.08,z),(frame,0.18,h+0.12),trim)
    cube(name+' right',(x+w/2,y-0.08,z),(frame,0.18,h+0.12),trim)
    cube(name+' top',(x,y-0.08,z+h/2),(w+0.2,0.18,frame),trim)
    cube(name+' bottom',(x,y-0.08,z-h/2),(w+0.2,0.18,frame),trim)
    cube(name+' mullion',(x,y-0.15,z),(0.07,0.18,h),trim)
    cube(name+' sill',(x,y-0.14,z-h/2-0.08),(w+0.3,0.25,0.12),trim)

# ---------- site ----------
# Approximate site block, oriented with Preshburg on west/south and Strelisk on east.
cube('Site',(0,0,-0.12),(72,62,0.24),sidewalk)
cube('Preshburg road',(0,-34,-0.05),(90,14,0.18),asphalt)
cube('Strelisk road',(39,0,-0.05),(14,70,0.18),asphalt)

# sidewalks
cube('Preshburg sidewalk',(0,-25.5,0.02),(80,5,0.15),sidewalk)
cube('Strelisk sidewalk',(33.5,0,0.02),(5,58,0.15),sidewalk)

# ---------- building footprint ----------
# Main U/L-like mass with central courtyard/opening.
# Front mass
cube('Front wing',(0,-11.0,9.0),(56,12,18),brick)
# Left wing
cube('Left wing',(-22,3.0,9.0),(12,28,18),brick)
# Right/rear wing
cube('Rear wing',(18,10.0,9.0),(28,10,18),siding)
# Rear-right return
cube('Rear return',(28,2.0,9.0),(10,18,18),siding)

# roof masses
cube('Front flat roof',(0,-11.0,18.25),(56,12,0.45),roof)
cube('Rear flat roof',(18,10.0,18.25),(28,10,0.45),roof)
cube('Return roof',(28,2.0,18.25),(10,18,0.45),roof)

# front windows
for z in (3.0,7.5,12.0,16.2):
    for x in (-22,-15,-8,-1,6,13,20):
        window(f'Front window {x} {z}',x,-17.08,z,1.35,2.2)

# front entrance
cube('Main entrance surround',(0,-17.35,2.7),(8,0.45,5.2),trim)
cube('Main entrance glass',(0,-17.62,2.7),(4.5,0.15,4.4),glass)
for x in (-1.4,1.4):
    cube('Entrance door frame',(x,-17.72,2.7),(0.12,0.20,4.6),trim)

# left-side windows
for z in (3,7.5,12,16.2):
    for y in (-7,0,7,14):
        window(f'Left window {y} {z}',-28.08,y,z,1.35,2.2)

# Strelisk-facing rear porch/balcony stacks
for floor,z in enumerate((4.0,8.3,12.6,16.9),1):
    for y in (-1,6,13):
        # balcony platform
        cube(f'Porch platform {floor}-{y}',(30.8,y,z-1.2),(6.2,4.6,0.22),wood)
        cube(f'Porch railing front {floor}-{y}',(30.8,y-2.15,z),(6.2,0.12,2.0),wood)
        for x in (28.0,30.8,33.6):
            cube('Porch post',(x,y-2.15,z-1.0),(0.12,0.12,2.0),wood)
        # rear door/window group
        window(f'Rear balcony window {floor}-{y}',30.8,y+2.02,z+0.3,1.7,2.2)

# additional rear windows
for z in (3,7.5,12,16.2):
    for x in (8,14,20):
        window(f'Rear window {x} {z}',x,15.1,z,1.35,2.2)

# side entry from Strelisk Ct
cube('Strelisk entry surround',(33.2,-8,2.5),(5.2,0.5,4.8),trim)
cube('Strelisk entry door',(33.45,-8,2.5),(2.2,0.18,4.0),glass)

# landscaping
for x in (-25,-18,-11,-4,3,10,17,24):
    cyl('Shrub',(x,-21,0.8),0.65,1.6,grass)
for y in (-20,-12,-4,4,12,20):
    cyl('Rear shrub',(26.2,y,0.8),0.65,1.6,grass)

# trees
for x,y in [(-30,-22),(-30,22),(27,23),(39,20),(39,-20)]:
    cyl('Tree trunk',(x,y,2.0),0.22,4,wood,16)
    cyl('Tree crown',(x,y,4.8),1.6,3.2,grass,20)

# parking on Strelisk
for row_y in (22,27):
    for x in (8,14,20,26,32):
        cube('Parking space',(x,row_y,0.06),(4.8,2.2,0.03),white)

# street sign
cube('Sign pole',(36,-25,2.2),(0.10,0.10,4.4),metal)
cube('Preshburg sign',(36,-25,4.0),(3.8,0.16,0.65),signmat)
cube('Strelisk sign',(36,-25,4.8),(3.8,0.16,0.65),signmat)

# ---------- cameras ----------
def camera(name, loc, target):
    bpy.ops.object.camera_add(location=loc)
    c=bpy.context.object; c.name=name
    direction=Vector(target)-c.location
    c.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    c.data.lens=48
    return c

cam1=camera('Preshburg Street View',(62,-60,11),(0,-8,9))
cam2=camera('Strelisk Street View',(62,45,12),(15,5,9))
cam3=camera('Aerial',(62,-60,48),(0,0,8))
cam4=camera('Rear Porches',(48,35,10),(25,8,10))

# lighting/world
bpy.context.scene.world.color=(0.06,0.08,0.11)
bpy.ops.object.light_add(type='AREA', location=(0,-5,45))
bpy.context.object.data.energy=5000
bpy.context.object.data.shape='DISK'
bpy.context.object.data.size=40

# save
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=60

scene.camera=cam3
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath('//Preshburg_Blvd_Unit_401.blend'))
print('Saved Preshburg_Blvd_Unit_401.blend')
