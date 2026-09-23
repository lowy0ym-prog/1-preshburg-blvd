import bpy
import os
from math import radians

# -------------------------------------------------------------------
# Utility: clean scene
# -------------------------------------------------------------------
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Remove default collections/objects if any remain
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# -------------------------------------------------------------------
# Utility: ensure output folder
# -------------------------------------------------------------------
def get_output_dir():
    repo_root = bpy.path.abspath("//")
    out_dir = os.path.join(repo_root, "output")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

# -------------------------------------------------------------------
# Approximate site + building geometry
# NOTE: This is a conservative reconstruction based on Street View
#       and montage references. Dimensions are proportional, not exact.
# -------------------------------------------------------------------
def build_site_and_building():
    # Create a main collection
    main_coll = bpy.data.collections.new("Preshburg_Site")
    bpy.context.scene.collection.children.link(main_coll)

    # -----------------------------
    # Ground plane
    # -----------------------------
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    main_coll.objects.link(ground)

    # -----------------------------
    # Roads layout (Forest Rd, Strelisk Ct, Preshburg Blvd)
    # Forest Rd runs across front/middle of building.
    # Strelisk Ct on one side, Preshburg Blvd on the other.
    # -----------------------------
    def add_road(name, size_x, size_y, loc, rot_z_deg):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=(0, 0, radians(rot_z_deg)))
        road = bpy.context.active_object
        road.scale.x = size_x
        road.scale.y = size_y
        road.name = name
        main_coll.objects.link(road)
        mat = bpy.data.materials.new(name + "_Mat")
        mat.diffuse_color = (0.08, 0.08, 0.08, 1.0)
        road.data.materials.append(mat)
        return road

    # Forest Rd: horizontal across front/middle
    forest_rd = add_road(
        "Forest_Rd",
        size_x=25,
        size_y=1.5,
        loc=(0, -8, 0),
        rot_z_deg=0
    )

    # Strelisk Ct: side road, roughly perpendicular on left
    strelisk_ct = add_road(
        "Strelisk_Ct",
        size_x=10,
        size_y=1.5,
        loc=(-15, -2, 0),
        rot_z_deg=90
    )

    # Preshburg Blvd: side road on right
    preshburg_blvd = add_road(
        "Preshburg_Blvd",
        size_x=10,
        size_y=1.5,
        loc=(15, -2, 0),
        rot_z_deg=90
    )

    # -----------------------------
    # Main building mass
    # Approx: long rectangular block with bay windows and porches.
    # -----------------------------
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3))
    main_bldg = bpy.context.active_object
    main_bldg.name = "Main_Building"

    # Scale to approximate proportions (width, depth, height)
    main_bldg.scale.x = 18   # width along Forest Rd
    main_bldg.scale.y = 8    # depth
    main_bldg.scale.z = 5    # height (multi-story)

    main_coll.objects.link(main_bldg)

    # Materials: light siding + stone base
    siding_mat = bpy.data.materials.new("Siding_Mat")
    siding_mat.diffuse_color = (0.92, 0.92, 0.92, 1.0)

    stone_mat = bpy.data.materials.new("Stone_Base_Mat")
    stone_mat.diffuse_color = (0.6, 0.55, 0.5, 1.0)

    # Assign siding to whole, then separate lower portion visually via loop
    main_bldg.data.materials.append(siding_mat)
    main_bldg.data.materials.append(stone_mat)

    # Simple vertex color separation for base (approx 1.2m high)
    # (We’ll use a solid material slot for now; detailed mapping can be added later.)

    # -----------------------------
    # Retaining wall along Forest Rd
    # -----------------------------
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.5, 1))
    wall = bpy.context.active_object
    wall.name = "Retaining_Wall"
    wall.scale.x = 18
    wall.scale.y = 0.5
    wall.scale.z = 1.0
    main_coll.objects.link(wall)
    wall.data.materials.append(stone_mat)

    # -----------------------------
    # Simple hedges / landscaping along wall
    # -----------------------------
    hedge_mat = bpy.data.materials.new("Hedge_Mat")
    hedge_mat.diffuse_color = (0.1, 0.4, 0.1, 1.0)

    for i in range(-8, 9, 2):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i, -6.5, 1.0))
        hedge = bpy.context.active_object
        hedge.name = f"Hedge_{i}"
        hedge.scale.x = 0.8
        hedge.scale.y = 0.4
        hedge.scale.z = 0.7
        main_coll.objects.link(hedge)
        hedge.data.materials.append(hedge_mat)

    # -----------------------------
    # Entrances and porches (Forest Rd front + Strelisk Ct side)
    # -----------------------------
    porch_mat = bpy.data.materials.new("Porch_Mat")
    porch_mat.diffuse_color = (0.85, 0.85, 0.85, 1.0)

    # Front entrance porch (Forest Rd side)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -3.5, 0.5))
    front_porch = bpy.context.active_object
    front_porch.name = "Front_Porch"
    front_porch.scale.x = 3
    front_porch.scale.y = 2
    front_porch.scale.z = 0.3
    main_coll.objects.link(front_porch)
    front_porch.data.materials.append(porch_mat)

    # Strelisk Ct side porches/balconies (stacked)
    for level, z in enumerate([1.0, 3.0, 5.0], start=1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-9, 0, z))
        side_porch = bpy.context.active_object
        side_porch.name = f"Strelisk_Porch_L{level}"
        side_porch.scale.x = 2.5
        side_porch.scale.y = 2.0
        side_porch.scale.z = 0.3
        main_coll.objects.link(side_porch)
        side_porch.data.materials.append(porch_mat)

    # -----------------------------
    # Roof shapes (simple gabled + flat segments)
    # -----------------------------
    # Main gabled roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 7.0))
    roof = bpy.context.active_object
    roof.name = "Main_Roof"
    roof.scale.x = 18.2
    roof.scale.y = 8.2
    roof.scale.z = 0.5
    main_coll.objects.link(roof)

    roof_mat = bpy.data.materials.new("Roof_Mat")
    roof_mat.diffuse_color = (0.2, 0.2, 0.22, 1.0)
    roof.data.materials.append(roof_mat)

    # -----------------------------
    # Windows and bay-window rhythm (simplified but faithful)
    # -----------------------------
    window_mat = bpy.data.materials.new("Window_Mat")
    window_mat.diffuse_color = (0.6, 0.75, 0.9, 1.0)

    def add_window_row(y_offset, z_center, count, width_spacing):
        for i in range(count):
            x = -14 + i * width_spacing
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y_offset, z_center))
            win = bpy.context.active_object
            win.name = f"Window_{y_offset}_{i}"
            win.scale.x = 0.8
            win.scale.y = 0.1
            win.scale.z = 1.2
            main_coll.objects.link(win)
            win.data.materials.append(window_mat)

    # Front windows (Forest Rd side)
    add_window_row(y_offset=-4.1, z_center=3.0, count=8, width_spacing=4)

    # Rear windows
    add_window_row(y_offset=4.1, z_center=3.0, count=8, width_spacing=4)

    # Strelisk Ct side windows
    add_window_row(y_offset=0.1, z_center=3.0, count=3, width_spacing=4)

    # -----------------------------
    # Simple parking/driveway areas
    # -----------------------------
    parking_mat = bpy.data.materials.new("Parking_Mat")
    parking_mat.diffuse_color = (0.15, 0.15, 0.15, 1.0)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(5, -10, 0))
    parking_front = bpy.context.active_object
    parking_front.name = "Parking_Front"
    parking_front.scale.x = 8
    parking_front.scale.y = 4
    main_coll.objects.link(parking_front)
    parking_front.data.materials.append(parking_mat)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(-10, 6, 0))
    parking_side = bpy.context.active_object
    parking_side.name = "Parking_Strelisk"
    parking_side.scale.x = 6
    parking_side.scale.y = 3
    main_coll.objects.link(parking_side)
    parking_side.data.materials.append(parking_mat)

    return main_coll

# -------------------------------------------------------------------
# Cameras + renders
# -------------------------------------------------------------------
def setup_camera(name, location, rotation_euler):
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation_euler
    return cam_obj

def configure_render(output_dir, filename):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = os.path.join(output_dir, filename)
    scene.render.image_settings.file_format = 'PNG'

def render_from_camera(cam_obj, output_dir, filename):
    bpy.context.scene.camera = cam_obj
    configure_render(output_dir, filename)
    bpy.ops.render.render(write_still=True)

def create_and_render_views(output_dir):
    # Front / Forest Rd view
    cam_front = setup_camera(
        "Cam_Forest_Front",
        location=(0, -25, 10),
        rotation_euler=(radians(65), 0, 0)
    )
    render_from_camera(cam_front, output_dir, "forest_front.png")

    # Strelisk Ct / porch view
    cam_strelisk = setup_camera(
        "Cam_Strelisk",
        location=(-25, 0, 8),
        rotation_euler=(radians(60), 0, radians(90))
    )
    render_from_camera(cam_strelisk, output_dir, "strelisk_ct.png")

    # Preshburg Blvd view
    cam_preshburg = setup_camera(
        "Cam_Preshburg",
        location=(25, 0, 8),
        rotation_euler=(radians(60), 0, radians(-90))
    )
    render_from_camera(cam_preshburg, output_dir, "preshburg_blvd.png")

    # Aerial / corner view
    cam_aerial = setup_camera(
        "Cam_Aerial_Corner",
        location=(25, -25, 25),
        rotation_euler=(radians(60), 0, radians(-135))
    )
    render_from_camera(cam_aerial, output_dir, "aerial_corner.png")

    # Rear / porch-side view
    cam_rear = setup_camera(
        "Cam_Rear_Porch",
        location=(-10, 20, 10),
        rotation_euler=(radians(60), 0, radians(200))
    )
    render_from_camera(cam_rear, output_dir, "rear_porch_side.png")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main():
    clean_scene()
    out_dir = get_output_dir()
    build_site_and_building()

    # Save .blend
    blend_path = os.path.join(out_dir, "Preshburg_Blvd_Unit_401.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Render views
    create_and_render_views(out_dir)

if __name__ == "__main__":
    main()
