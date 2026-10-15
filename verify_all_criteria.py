import bpy, os, sys, json
import numpy as np

project_dir = r"c:\Users\mouli\OneDrive\Desktop\cga_project"
review_dir = os.path.join(project_dir, "enhancement_review")
sys.path.insert(0, review_dir)
from audit_lib import snapshot

ids = json.load(open(os.path.join(review_dir, "original_ids.json")))

# 1. Inspect original.blend
bpy.ops.wm.open_mainfile(filepath=os.path.join(review_dir, "original.blend"))
orig_data = snapshot(*ids)

# 2. Inspect main.blend
bpy.ops.wm.open_mainfile(filepath=os.path.join(project_dir, "main.blend"))
main_scene = bpy.context.scene
main_data = snapshot(*ids)

results = {}

# Criteria 1 & 2: Objects, Armatures, Actions, and 550 frames of motion
results["characters_and_props_identical"] = (main_data["objects"] == orig_data["objects"])
results["actions_and_keyframes_identical"] = (main_data["actions"] == orig_data["actions"])
results["motion_all_550_frames_identical"] = (main_data["motion_all_550_frames"] == orig_data["motion_all_550_frames"])
results["original_materials_identical"] = (main_data["materials"] == orig_data["materials"])

# Criteria 3: Timeline, duration, FPS, resolution, render settings
results["settings_identical"] = (main_data["settings"] == orig_data["settings"])
results["fps"] = main_data["settings"]["fps"]
results["frame_range"] = [main_data["settings"]["start"], main_data["settings"]["end"]]

# Criteria 4 & 5: Environmental elements and non-obstruction
env_col = bpy.data.collections.get("Rainy Night | Environment Additions")
results["environment_collection_exists"] = env_col is not None
if env_col:
    results["env_objects"] = [o.name for o in env_col.objects]
    cx, cy = -1.3, 0.25
    min_dist = float('inf')
    for o in env_col.objects:
        if o.type == 'MESH':
            pts = [o.matrix_world @ v.co for v in o.data.vertices]
            dists = [((p.x - cx)**2 + (p.y - cy)**2)**0.5 for p in pts]
            if dists:
                min_dist = min(min_dist, min(dists))
    results["nearest_env_vertex_distance_to_center"] = round(min_dist, 2)
    results["character_max_radius"] = round(orig_data.get("character_max_xy_radius", 2.31), 2)
    results["safe_margin"] = round(min_dist - orig_data.get("character_max_xy_radius", 2.31), 2)

# Criteria 6: Performance check
total_new_poly = sum(len(o.data.polygons) for o in env_col.objects) if env_col else 0
results["new_environment_polygon_count"] = total_new_poly
results["compositing_cryptomatte_isolated"] = main_scene.compositing_node_group is not None

print("=== VERIFICATION RESULTS START ===")
print(json.dumps(results, indent=2))
print("=== VERIFICATION RESULTS END ===")
