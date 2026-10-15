import bpy, os, sys, json
import numpy as np

project_dir = r"c:\Users\mouli\OneDrive\Desktop\cga_project"
review_dir = os.path.join(project_dir, "enhancement_review")
sys.path.insert(0, review_dir)
from audit_lib import snapshot

ids = json.load(open(os.path.join(review_dir, "original_ids.json")))

# 1. Baseline
bpy.ops.wm.open_mainfile(filepath=os.path.join(review_dir, "original.blend"))
orig_data = snapshot(*ids)

# 2. Enhanced Forest project
forest_blend = os.path.join(project_dir, "main_enhanced_forest.blend")
bpy.ops.wm.open_mainfile(filepath=forest_blend)
forest_scene = bpy.context.scene
forest_data = snapshot(*ids)

checks = {
    "1_characters_and_props_identical": (forest_data["objects"] == orig_data["objects"]),
    "2_actions_and_keyframes_identical": (forest_data["actions"] == orig_data["actions"]),
    "3_all_550_frames_motion_identical": (forest_data["motion_all_550_frames"] == orig_data["motion_all_550_frames"]),
    "4_timeline_frame_range_identical": (forest_scene.frame_start == 1 and forest_scene.frame_end == 550),
    "5_fps_identical": (forest_scene.render.fps == orig_data["settings"]["fps"]),
    "6_resolution_identical": (forest_scene.render.resolution_x == 1920 and forest_scene.render.resolution_y == 1080),
}

# Check environmental enhancements
env_col = bpy.data.collections.get("Rainy Night | Environment Additions")
checks["7_environment_collection_exists"] = env_col is not None
if env_col:
    checks["7_env_object_names"] = [o.name for o in env_col.objects]
    total_env_polys = sum(len(o.data.polygons) for o in env_col.objects if o.type == 'MESH')
    checks["8_total_env_polygons"] = total_env_polys
    
    # Clearance check
    cx, cy = -1.3, 0.25
    min_dist = float('inf')
    for o in env_col.objects:
        if o.type == 'MESH':
            step = max(1, len(o.data.vertices) // 100)
            for i in range(0, len(o.data.vertices), step):
                v = o.data.vertices[i]
                p = o.matrix_world @ v.co
                dist = ((p.x - cx)**2 + (p.y - cy)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
    checks["9_nearest_env_vertex_dist"] = round(min_dist, 2)
    checks["9_safe_margin"] = round(min_dist - orig_data.get("character_max_xy_radius", 2.31), 2)

print("=== FOREST AUDIT SUMMARY START ===")
print(json.dumps(checks, indent=2))
print("=== FOREST AUDIT SUMMARY END ===")
