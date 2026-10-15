import bpy

cx, cy = -1.3, 0.25
col = bpy.data.collections.get("Rainy Night | Environment Additions")
for o in col.objects:
    if o.type == 'MESH':
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        dists = [((p.x - cx)**2 + (p.y - cy)**2)**0.5 for p in pts]
        print(f"Object '{o.name}': min_dist={min(dists):.2f}, max_dist={max(dists):.2f}")
