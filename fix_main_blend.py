import bpy
import math

def fix_project():
    s = bpy.context.scene
    
    # 1. Ensure Camera, Light, Light.001, Plane are in 'Collection'
    main_col = bpy.data.collections.get("Collection")
    ref_col = bpy.data.collections.get("Rainy Night | Original background reference")
    
    for name in ['Plane', 'Light', 'Light.001', 'Camera']:
        obj = bpy.data.objects.get(name)
        if obj and main_col and obj.name not in main_col.objects:
            main_col.objects.link(obj)
        if obj and ref_col and obj.name in ref_col.objects:
            ref_col.objects.unlink(obj)
            
    # Remove unnecessary reference collection if empty
    if ref_col and len(ref_col.objects) == 0:
        bpy.data.collections.remove(ref_col)

    # 2. Set Scene World to the Rainy Night backdrop
    rn_world = bpy.data.worlds.get("Rainy Night | Camera backdrop")
    if rn_world:
        s.world = rn_world
        print(f"Set scene world to: {rn_world.name}")

    # 3. Ensure 'Rainy Night | Environment Additions' is included in ViewLayer
    env_col = bpy.data.collections.get("Rainy Night | Environment Additions")
    view_layer = s.view_layers.get("ViewLayer")
    if view_layer:
        for child in view_layer.layer_collection.children:
            if child.name == "Rainy Night | Environment Additions":
                child.exclude = False
                child.hide_viewport = False
                print(f"Included '{child.name}' in ViewLayer (exclude=False)")
            if child.name == "Collection":
                child.exclude = False
                child.hide_viewport = False
                print(f"Included '{child.name}' in ViewLayer (exclude=False)")

    # 4. Remove extra view layers that were causing confusion
    for vl_name in ["Rainy Night | Background", "Rainy Night | Background reference"]:
        vl = s.view_layers.get(vl_name)
        if vl:
            s.view_layers.remove(vl)
            print(f"Removed helper view layer: {vl_name}")

    # 5. Create / assign Ground material to Plane (Muted brown and gray for rainy ground)
    ground_mat = bpy.data.materials.get("RN | Muted rainy ground")
    if not ground_mat:
        ground_mat = bpy.data.materials.new("RN | Muted rainy ground")
        ground_mat.use_nodes = True
        nodes = ground_mat.node_tree.nodes
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        # Muted dark slate brown-gray
        bsdf.inputs['Base Color'].default_value = (0.045, 0.055, 0.065, 1.0)
        # Wet ground roughness
        bsdf.inputs['Roughness'].default_value = 0.35
        ground_mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        print("Created 'RN | Muted rainy ground' material")
        
    plane_obj = bpy.data.objects.get("Plane")
    if plane_obj:
        if len(plane_obj.material_slots) == 0:
            plane_obj.data.materials.append(ground_mat)
        else:
            plane_obj.material_slots[0].material = ground_mat
        print("Assigned ground material to Plane")

    # 6. Simplify / fix compositor so Render Layers connects directly to Output
    # while preserving any desired tinting
    if s.compositing_node_group:
        nt = s.compositing_node_group
        nt.nodes.clear()
        
        # Simple, robust standard compositor: Render Layers -> Composite Output
        rl = nt.nodes.new("CompositorNodeRLayers")
        rl.layer = "ViewLayer"
        rl.location = (0, 0)
        
        out = nt.nodes.new("NodeGroupOutput")
        out.location = (400, 0)
        
        nt.links.new(rl.outputs['Image'], out.inputs['Image'])
        print("Updated compositor to direct clean composite from ViewLayer")

    # 7. Ensure active camera is set
    cam = bpy.data.objects.get("Camera")
    if cam:
        s.camera = cam

    # Save to main.blend
    bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\mouli\OneDrive\Desktop\cga_project\main.blend")
    print("SAVED main.blend successfully!")

fix_project()
