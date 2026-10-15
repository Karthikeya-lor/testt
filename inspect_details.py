import bpy
import json

def inspect_details():
    scene = bpy.context.scene
    print(f"Scene: {scene.name}, FPS: {scene.render.fps}, Frame Range: {scene.frame_start} to {scene.frame_end}")
    print(f"Render Engine: {scene.render.engine}, Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
    print(f"Active Camera: {scene.camera.name if scene.camera else None}")

    print("\n--- COLLECTIONS & OBJECTS ---")
    for col in bpy.data.collections:
        print(f"\nCollection: '{col.name}' (hide_viewport={col.hide_viewport}, hide_render={col.hide_render})")
        for obj in col.objects:
            has_anim = obj.animation_data is not None and (obj.animation_data.action is not None or len(obj.animation_data.nla_tracks) > 0)
            anim_type = "None"
            if obj.animation_data:
                if obj.animation_data.action:
                    anim_type = f"Action: {obj.animation_data.action.name}"
                elif len(obj.animation_data.nla_tracks) > 0:
                    anim_type = f"NLA: {len(obj.animation_data.nla_tracks)} tracks"
            print(f"  - [{obj.type}] '{obj.name}' | Loc: {tuple(round(v, 2) for v in obj.location)} | Anim: {anim_type} | Mat: {[s.material.name for s in obj.material_slots if s.material]}")

    print("\n--- ROOT OBJECTS (Not in any sub-collection or in Scene Collection) ---")
    for obj in scene.collection.objects:
        print(f"  - [{obj.type}] '{obj.name}'")

    print("\n--- MATERIALS ---")
    for mat in bpy.data.materials:
        print(f"  Material: '{mat.name}' (use_nodes={mat.use_nodes})")

    print("\n--- ACTIONS ---")
    for act in bpy.data.actions:
        print(f"  Action: '{act.name}' (frame range: {act.frame_range[0]} - {act.frame_range[1]})")

inspect_details()
