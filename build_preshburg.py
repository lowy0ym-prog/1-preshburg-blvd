import bpy, os, math
from mathutils import Vector

OUT=os.path.join(os.environ.get("GITHUB_WORKSPACE",bpy.path.abspath("//")),"output")
os.makedirs(OUT,exist_ok=True)

def mat(n,c,r=.7,m=0):
    x=bpy.data.materials.new(n); x.use_nodes=True
    b=x.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*c,1); b.inputs["Roughness"].default_value=r; b.inputs["Metallic"].default_value=m
    return x

SIDING=mat("warm white siding",(.86,.86,.82),.82)
STONE=mat("light stone",(.43,.40,.35),.92)
WALL=mat("retaining wall",(.34,.30,.27),.95)
TRIM=mat("white trim",(.95,.95,.91),.58)
GLASS=mat("blue gray glass",(.08,.17,.21),.18)
ROOF=mat("dark gray shingles",(.17,.17,.16),.94)
WOOD=mat("porch wood",(.42,.37,.29),.9)
RAIL=mat("dark metal",(.07,.08,.07),.48,.2)
ROAD=mat("asphalt",(.075,.078,.075),.98)
CONCRETE=mat("concrete",(.55,.54,.51),.96)
HEDGE=mat("evergreen",(.045,.16,.055),.96)

def cube(n,loc,d,ma,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=n; o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    if bevel:
        q=o.modifiers.new("edge bevel","BEVEL"); q.width=bevel; q.segments=2
    return o

def beam(n,a,b,r,ma):
    a,b=Vector(a),Vector(b); v=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=v.length,location=(a+b)/2)
    o=bpy.context.object; o.name=n; o.rotation_mode="QUATERNION"; o.rotation_quaternion=v.to_track_quat("Z","Y"); o.data.materials.append(ma); return o

def front_window(n,x,y,z,w=1.0,h=1.65):
    fy=y-.12
    cube(n+"_glass",(x,fy,z),(w,.10,h),GLASS,.01)
    cube(n+"_top",(x,fy,z+h/2),(w+.18,.09,.10),TRIM)
    cube(n+"_bot",(x,fy,z-h/2),(w+.18,.09,.10),TRIM)
    cube(n+"_l",(x-w/2,fy,z),(.10,.09,h+.12),TRIM)
    cube(n+"_r",(x+w/2,fy,z),(.10,.09,h+.12),TRIM)
    cube(n+"_mid",(x,fy-.03,z),(.055,.05,h),TRIM)

def side_window(n,x,y,z,w=1.0,h=1.65):
    fx=x-.12
    cube(n+"_glass",(fx,y,z),(.10,w,h),GLASS,.01)
    cube(n+"_top",(fx,y,z+h/2),(.09,w+.18,.10),TRIM)
    cube(n+"_bot",(fx,y,z-h/2),(.09,w+.18,.10),TRIM)
    cube(n+"_l",(fx,y-w/2,z),(.09,.10,h+.12),TRIM)
    cube(n+"_r",(fx,y+w/2,z),(.09,.10,h+.12),TRIM)

def roads():
    # Exact relationship required by the reference map: Forest Rd is the front road;
    # Strelisk Ct is west/left; Preshburg Blvd is east/right.
    cube("Forest_Rd",(0,-15,0),(62,6,.18),ROAD)
    cube("Strelisk_Ct",(-23,-3,0),(6,25,.18),ROAD)
    cube("Preshburg_Blvd",(23,-3,0),(6,29,.18),ROAD)
    cube("Forest_sidewalk",(0,-11.4,.10),(62,1.6,.18),CONCRETE)
    cube("Strelisk_sidewalk",(-19.2,-3,.10),(1.6,25,.18),CONCRETE)
    cube("Preshburg_sidewalk",(19.2,-3,.10),(1.6,29,.18),CONCRETE)

def model():
    W,D=35,18; base=2.2; upper=13.8
    cube("stone_ground",(0,0,base/2),(W,D,base),STONE,.06)
    cube("white_main_mass",(0,0,base+upper/2),(W,D,upper),SIDING,.06)
    cube("main_roof",(0,0,base+upper+.35),(36,19,.55),ROOF,.05)

    # Forest Rd facade: repeated projecting bay/window stacks, matching the supplied photo.
    for i,x in enumerate([-13,-6.5,0,6.5,13]):
        for j,z in enumerate([4.0,6.9,9.8,12.7,15.35]):
            cube(f"bay_{i}_{j}",(x,-9.45,z),(2.5,.75,2.25),SIDING,.03)
            front_window(f"bay_{i}_{j}_c",x,-9.86,z,.72,1.62)
            front_window(f"bay_{i}_{j}_l",x-.78,-9.86,z,.45,1.62)
            front_window(f"bay_{i}_{j}_r",x+.78,-9.86,z,.45,1.62)
            cube(f"bay_cap_{i}_{j}",(x,-9.52,z+1.18),(2.8,.82,.12),TRIM,.02)

    # Side facing Strelisk Ct: stacked porches/balconies are a major feature of the real photos.
    for j,z in enumerate([4.0,6.9,9.8,12.7,15.35]):
        for k,y in enumerate([-6.0,-1.9,2.2,6.0]):
            cube(f"porch_{j}_{k}",(-18.1,y,z-1.0),(3.3,3.1,.24),WOOD,.03)
            if j<2: cube(f"awning_{j}_{k}",(-18.1,y,z+.45),(3.4,3.0,.18),ROOF,.02)
            for yy in (y-1.4,y+1.4):
                beam("side_rail",(-19.7,yy,z-.05),(-16.5,yy,z-.05),.055,RAIL)
                beam("side_post",(-19.7,yy,z-1.0),(-19.7,yy,z-.05),.045,RAIL)
            side_window(f"side_window_{j}_{k}",-17.82,y,z+.15,.95,1.65)

    # Preshburg side: simpler vertical window rhythm.
    for j,z in enumerate([4.0,6.9,9.8,12.7,15.35]):
        for k,y in enumerate([-6,-2,2.2,6]):
            side_window(f"east_{j}_{k}",17.82,y,z,.95,1.65)

    # Forest Rd entry/canopy.
    cube("entry_steps",(0,-10,.4),(5.5,2.4,.75),CONCRETE,.04)
    cube("entry_landing",(0,-9.55,1.0),(4.8,1.5,.22),CONCRETE,.03)
    cube("entry_canopy",(0,-9.65,3.1),(5.0,2.2,.25),ROOF,.03)
    for x in (-2.1,2.1): beam("entry_column",(x,-10,1.0),(x,-10,3.05),.10,TRIM)
    cube("entry_door",(0,-10.02,1.85),(1.45,.12,2.1),RAIL,.02)

    # Raised planting/retaining wall along Forest Rd.
    cube("retaining_wall",(0,-9.55,1.45),(35,.72,2.9),WALL,.04)
    for x in [-16,-14,-12,-10,-8,-6,-4,-2,0,2,4,6,8,10,12,14,16]:
        bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.62,radius2=.22,depth=3.1,location=(x,-8.55,4.55))
        bpy.context.object.data.materials.append(HEDGE)

    # Rear balconies/porches visible from Strelisk Ct and the back side.
    for j,z in enumerate([4.0,6.9,9.8,12.7,15.35]):
        for k,x in enumerate([-12,-4,4,12]):
            cube(f"rear_porch_{j}_{k}",(x,9.65,z-1.0),(3.0,2.2,.22),WOOD,.03)
            beam("rear_top",(x-1.45,10.7,z-.05),(x+1.45,10.7,z-.05),.055,RAIL)
            for xx in (x-1.35,x,x+1.35): beam("rear_post",(xx,10.7,z-1.0),(xx,10.7,z-.05),.045,RAIL)
            front_window(f"rear_window_{j}_{k}",x,9.15,z,.95,1.65)

def setup():
    world=bpy.data.worlds.new("World"); bpy.context.scene.world=world; world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=(.62,.70,.80,1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=.42
    for loc,energy,size in [((-12,-18,28),1800,14),((18,8,18),900,12)]:
        bpy.ops.object.light_add(type="AREA",location=loc)
        l=bpy.context.object; l.data.energy=energy; l.data.shape="DISK"; l.data.size=size
        l.rotation_euler=(math.radians(25),0,math.radians(-25))

def cam(name,loc,target,lens):
    d=bpy.data.cameras.new(name); d.lens=lens
    o=bpy.data.objects.new(name,d); bpy.context.scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler(); return o

def render():
    s=bpy.context.scene; s.render.engine="BLENDER_EEVEE_NEXT"
    s.render.resolution_x=1200; s.render.resolution_y=850; s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    views=[
      ("forest_front.png",(0,-34,10),(0,0,8),52),
      ("strelisk_ct.png",(-32,-4,11),(-8,0,8),52),
      ("preshburg_blvd.png",(32,-4,11),(8,0,8),52),
      ("aerial_corner.png",(31,-31,28),(0,0,7),50),
      ("rear_porch_side.png",(-31,25,12),(-8,2,9),52)]
    for fn,loc,target,lens in views:
        s.camera=cam("Camera_"+fn,loc,target,lens)
        s.render.filepath=os.path.join(OUT,fn); bpy.ops.render.render(write_still=True)

def main():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    roads(); model(); setup(); render()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"Preshburg_Blvd_Unit_401.blend"))
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,"Preshburg_Blvd_Unit_401.glb"),export_format="GLB",use_selection=False)

if __name__=="__main__": main()
