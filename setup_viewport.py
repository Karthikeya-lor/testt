import bpy

def setup_viewport_and_scene():
    s = bpy.context.scene
    
    # 1. Restore Plane to having no materials (100% original state)
    plane = bpy.data.objects.get("Plane")
    if plane:
        plane.data.materials.clear()
        print("Restored Plane to original empty materials list")

    # 2. Ensure Scene World is 'Rainy Night | Camera backdrop'
    world = bpy.data.worlds.get("Rainy Night | Camera backdrop")
    if world:
        s.world = world
        print("Set scene world to Rainy Night | Camera backdrop")

    # 3. Ensure ViewLayer includes both Collection and Rainy Night | Environment Additions
    vl = s.view_layers.get("ViewLayer")
    if vl:
        for child in vl.layer_collection.children:
            child.exclude = False
            child.hide_viewport = False
            print(f"Set view layer collection '{child.name}': exclude=False, hide_viewport=False")

    # 4. Set 3D Viewport in all screens to MATERIAL shading with scene world & lights enabled
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = True
                        print(f"Updated viewport in screen '{screen.name}' to MATERIAL preview with scene lights and world")

    # 5. Restore camera to Camera object
    cam = bpy.data.objects.get("Camera")
    if cam:
        s.camera = cam

    # Save project
    bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\mouli\OneDrive\Desktop\cga_project\main.blend")
    print("Project successfully updated and saved to main.blend!")

setup_viewport_and_scene()
