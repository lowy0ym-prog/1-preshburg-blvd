import bpy
import os
from math import radians

ROOT = bpy.path.abspath('//')
OUT = os.path.join(os.environ.get('GITHUB_WORKSPACE', ROOT), 'output')

def mat(name, color, rough=0.65, metallic=0.0):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    return m

WHITE=mat('White vinyl siding',(0.83,0.84,0.82),.78)
STONE=mat('Warm gray stone base',(0.38,0.34,0.30),.9)
STONE2=mat('Retaining wall stone',(0.30,0.27,0.24),.95)
ROOF=mat('Roof shingles',(0.16,0.15,0.14),.95)
TRIM=mat('Window trim',(0.93,0.93,0.90),.65)
GLASS=mat('Window glass',(0.16,0.28,0.34),.22)
DARK=mat('Dark asphalt',(0.055,0.055,0.055),1.0)
SIDEWALK=mat('Concrete sidewalk',(0.47,0.46,0.43),.95)
WOOD=mat('Weathered porch wood',(0.43,0.39,0.32),.9)
METAL=mat('Dark railing metal',(0.10,0.11,0.10),.5,.15)
HEDGE=mat('Evergreen hedge',(0.045,0.17,0.055),.95)
SIGN=mat('Sign dark',(0.045,0.045,0.04),.7)

def cube(name,loc,scale,material,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=2
    return o

def cylinder(name,loc,radius,depth,material,verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def beam_between(name,a,b,radius,material):
    import mathutils
    a=mathutils.Vector(a); b=mathutils.Vector(b); vec=b-a
    o=cylinder(name,(a+b)/2,radius,vec.length,material,10)
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=vec.to_track_quat('Z','Y'); return o

def clean():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT,exist_ok=True)

def make_roads():
    cube('Forest_Rd',(0,-13.2,-.08),(55,5.2,.16),DARK)
    cube('Strelisk_Ct',(-22,-3.5,-.08),(5,24,.16),DARK)
    cube('Preshburg_Blvd',(22,-2.5,-.08),(5,28,.16),DARK)
    cube('Forest_sidewalk',(0,-10.25,.02),(55,1.15,.10),SIDEWALK)
    cube('Strelisk_sidewalk',(-19.15,-2.5,.02),(1.15,26,.10),SIDEWALK)
    cube('Preshburg_sidewalk',(19.15,-2.5,.02),(1.15,28,.10),SIDEWALK)

def make_building():
    W,D=32.0,14.5; base_h=2.2; upper_h=11.6
    cube('Stone_lower_level',(0,0,base_h/2),(W,D,base_h),STONE,.08)
    cube('White_upper_mass',(0,0,base_h+upper_h/2),(W,D,upper_h),WHITE,.06)
    cube('West_end_mass',(-15.9,.2,7.6),(1.1,13.5,10.8),WHITE,.04)
    cube('East_end_mass',(15.9,.2,7.6),(1.1,13.5,10.8),WHITE,.04)
    roof_z=base_h+upper_h+.35
    cube('Main_roof',(0,0,roof_z),(33.2,15.7,.7),ROOF,.06)
    cube('Roof_ridge',(0,0,roof_z+.42),(30.5,1.0,.25),ROOF)
    for z in [4.7,7.6,10.5,13.35]:
        cube(f'Siding_course_{z}',(0,-7.27,z),(31.2,.025,.025),TRIM)
        cube(f'Siding_course_back_{z}',(0,7.27,z),(31.2,.025,.025),TRIM)

def window(name,loc,w=.95,h=1.65,front=True):
    y=loc[1]; face_y=y-.11 if front else y+.11
    cube(name+'_glass',loc,(w,.16,h),GLASS,.02)
    for nm,lc,sc in [
        ('top',(loc[0],face_y,loc[2]+h/2),(w+.22,.08,.12)),
        ('bottom',(loc[0],face_y,loc[2]-h/2),(w+.22,.08,.12)),
        ('left',(loc[0]-w/2,face_y,loc[2]),(.10,.08,h+.12)),
        ('right',(loc[0]+w/2,face_y,loc[2]),(.10,.08,h+.12)),
        ('mullion',(loc[0],face_y-.015,loc[2]),(.06,.05,h))]:
        cube(name+'_'+nm,lc,sc,TRIM)
        
def front_windows():
    xs=[-13.2,-9.8,-6.3,-2.8,2.8,6.3,9.8,13.2]
    for li,z in enumerate([3.8,6.7,9.6,12.5]):
        for i,x in enumerate(xs):
            if li==0 and abs(x)<3: continue
            window(f'Forest_window_{li}_{i}',(x,-7.34,z),.95,1.65,True)

def preshburg_windows():
    # Preshburg Blvd is the RIGHT/EAST side (positive X), not the Forest Rd facade.
    for li,z in enumerate([3.8,6.7,9.6,12.5]):
        for i,y in enumerate([-5.2,-1.8,1.8,5.2]):
            cube(f'Preshburg_window_{li}_{i}_glass',(16.42,y,z),(.16,1.05,1.65),GLASS,.02)
            cube(f'Preshburg_window_{li}_{i}_left',(16.32,y-.52,z),(.08,.10,1.80),TRIM)
            cube(f'Preshburg_window_{li}_{i}_right',(16.32,y+.52,z),(.08,.10,1.80),TRIM)
            cube(f'Preshburg_window_{li}_{i}_top',(16.32,y,z+.82),(.08,1.18,.10),TRIM)
            cube(f'Preshburg_window_{li}_{i}_bottom',(16.32,y,z-.82),(.08,1.18,.10),TRIM)
def strelisk_porches():
    for li,z in enumerate([3.4,6.25,9.1,11.95]):
        cube(f'Strelisk_balcony_{li}',(-16.9,0,z-.78),(4.0,3.5,.28),WOOD)
        for yy in [-1.35,1.35]:
            beam_between(f'bal_post_{li}_{yy}',(-18.65,yy,z-.78),(-18.65,yy,z+1.65),.08,WOOD)
        for yy in [-1.65,1.65]:
            beam_between(f'rail_side_{li}_{yy}',(-18.7,yy,z-.05),(-15.2,yy,z-.05),.055,METAL)
        beam_between(f'rail_front_{li}',(-18.7,-1.65,z-.05),(-18.7,1.65,z-.05),.055,METAL)
        for yy in [-1.65,-.55,.55,1.65]:
            beam_between(f'rail_post_{li}_{yy}',(-18.7,yy,z-.75),(-18.7,yy,z-.05),.045,METAL)
        window(f'Strelisk_door_{li}',(-15.95,-7.34,z+.65),1.05,2.0,True)

def front_entry():
    cube('Entry_steps',(0,-8.15,.35),(4.2,3.2,.7),SIDEWALK)
    cube('Entry_landing',(0,-7.55,1.0),(3.4,2.2,.25),SIDEWALK)
    cube('Entry_canopy',(0,-7.45,2.8),(3.8,2.0,.25),ROOF)
    for x in [-1.6,1.6]:
        beam_between('Entry_canopy_post',(x,-8.1,1.1),(x,-8.1,2.8),.08,METAL)
    cube('Entry_door',(0,-7.43,1.8),(1.15,.12,2.05),DARK)

def retaining_wall_and_hedges():
    cube('Forest_retaining_wall',(0,-9.55,1.55),(31.5,.75,3.1),STONE2,.04)
    cube('Planting_strip',(0,-9.05,3.25),(31.5,1.0,.25),STONE)
    for x in [-14.8,-12.4,-10,-7.6,-5.2,-2.8,-.4,2,4.4,6.8,9.2,11.6,14]:
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.58,radius2=.22,depth=2.9,location=(x,-8.55,4.65))
        o=bpy.context.object; o.name=f'Evergreen_{x}'; o.data.materials.append(HEDGE)

def parking_and_driveways():
    cube('Front_drive',(12,-6.2,.03),(9,5,.10),DARK)
    cube('Strelisk_drive',(-18,-5,.03),(4,8,.10),DARK)
    cube('Preshburg_drive',(18,-5,.03),(4,8,.10),DARK)

def signage():
    cube('Business_sign',(17.1,-7.55,3.1),(2.6,.12,1.1),SIGN,.03)

def setup_world():
    world=bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world=world
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.78,.88,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def point_camera(cam,target):
    import mathutils
    cam.rotation_euler=(mathutils.Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()

def camera(name,loc,target,lens=42):
    data=bpy.data.cameras.new(name); data.lens=lens
    ob=bpy.data.objects.new(name,data); bpy.context.scene.collection.objects.link(ob)
    ob.location=loc; point_camera(ob,target); return ob

def render_views():
    scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    for fn,loc,target,lens in [
        ('forest_front.png',(0,-30,9),(0,0,7),48),
        ('strelisk_ct.png',(-29,-1,9),(-8,0,7.5),52),
        ('preshburg_blvd.png',(29,-2,9),(7,0,7.5),52),
        ('aerial_corner.png',(28,-27,28),(0,0,5.5),48),
        ('rear_porch_side.png',(-28,17,10),(-8,1,7.5),52)]:
        cam=camera('Camera_'+fn,loc,target,lens); scene.camera=cam
        scene.render.filepath=os.path.join(OUT,fn); bpy.ops.render.render(write_still=True)

def main():
    clean(); setup_world(); make_roads(); make_building(); front_windows(); preshburg_windows()
    strelisk_porches(); front_entry(); retaining_wall_and_hedges(); parking_and_driveways(); signage()
    render_views()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Preshburg_Blvd_Unit_401.blend'))

if __name__=='__main__':
    main()
