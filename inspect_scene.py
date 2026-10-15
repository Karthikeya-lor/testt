import bpy
import json
import sys

def safe_serialize(obj):
    try:
        return json.dumps(obj, indent=2)
    except Exception as e:
        return str(obj)

def inspect():
    scene = bpy.context.scene
    info = {
        "scene_name": scene.name,
        "render_engine": scene.render.engine,
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "fps": scene.render.fps,
        "fps_base": scene.render.fps_base,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "objects": []
    }
    
    # World details
    if scene.world and scene.world.node_tree:
        nodes = [f"{n.name} ({n.type})" for n in scene.world.node_tree.nodes]
        info["world_nodes"] = nodes
    elif scene.world:
        info["world_color"] = list(scene.world.color)

    # Collections
    info["collections"] = [c.name for c in bpy.data.collections]

    for obj in bpy.data.objects:
        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation_euler": [round(v, 4) for v in obj.rotation_euler] if hasattr(obj, "rotation_euler") else None,
            "scale": [round(v, 4) for v in obj.scale],
            "parent": obj.parent.name if obj.parent else None,
            "visible": not obj.hide_viewport,
            "render": not obj.hide_render,
            "has_animation": False,
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
            "modifiers": [f"{m.name} ({m.type})" for m in obj.modifiers],
        }
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            obj_info["has_animation"] = True
            obj_info["action"] = action.name
            if hasattr(action, "frame_range"):
                obj_info["action_frame_range"] = [action.frame_range[0], action.frame_range[1]]

        if obj.type in ('GPENCIL', 'GREASEPENCIL'):
            layers = []
            if hasattr(obj.data, 'layers'):
                for l in obj.data.layers:
                    layers.append(getattr(l, 'info', getattr(l, 'name', 'unnamed')))
            obj_info["gp_layers"] = layers
        elif obj.type == 'MESH':
            obj_info["vertices_count"] = len(obj.data.vertices)
            obj_info["polygons_count"] = len(obj.data.polygons)
        elif obj.type == 'ARMATURE':
            obj_info["bones"] = [b.name for b in obj.data.bones]
        elif obj.type == 'CAMERA':
            cam = obj.data
            obj_info["cam_type"] = cam.type
            obj_info["lens"] = getattr(cam, 'lens', None)
            obj_info["ortho_scale"] = getattr(cam, 'ortho_scale', None)
        
        info["objects"].append(obj_info)
    
    print("=== INSPECTION DATA START ===")
    print(safe_serialize(info))
    print("=== INSPECTION DATA END ===")

if __name__ == "__main__":
    inspect()
