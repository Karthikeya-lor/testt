import bpy
import math
import random
import os
import sys
import json

project_dir = r"c:\Users\mouli\OneDrive\Desktop\cga_project"
review_dir = os.path.join(project_dir, "enhancement_review")
sys.path.insert(0, review_dir)
from audit_lib import snapshot

# 1. Open main.blend as baseline
bpy.ops.wm.open_mainfile(filepath=os.path.join(project_dir, "main.blend"))
s = bpy.context.scene
orig_frame = s.frame_current

ids = json.load(open(os.path.join(review_dir, "original_ids.json")))
original_names, action_names, material_names = ids

before_snap = snapshot(original_names, action_names, material_names)

print("Baseline snapshot verified. Starting forest upgrade...")

# 2. Setup / clean the Environment Collection
col_name = "Rainy Night | Environment Additions"
env_col = bpy.data.collections.get(col_name)
if not env_col:
    env_col = bpy.data.collections.new(col_name)
    s.collection.children.link(env_col)

# Ensure collection is included in ViewLayer
vl = s.view_layers.get("ViewLayer")
if vl:
    for child in vl.layer_collection.children:
        if child.name == col_name or child.name == "Collection":
            child.exclude = False
            child.hide_viewport = False

# Helper: Lightning driver formula with 3 natural, irregular flashes (frames 124-127, 260-261, 388-390)
flash_expr = (
    "(0.25 if frame == 124 else "
    " 1.0 if frame == 126 else "
    " 0.45 if frame == 127 else "
    " 0.35 if (260 <= frame <= 261) else "
    " 1.0 if frame == 388 else "
    " 0.5 if frame == 389 else "
    " 0.0)"
)

def add_socket_driver(socket, expr):
    f = socket.driver_add('default_value')
    f.driver.expression = expr

def add_prop_driver(obj, prop_path, index, expr):
    f = obj.driver_add(prop_path, index)
    f.driver.expression = expr

# 3. Materials
def create_mat(name, color, is_lit=True, roughness=0.6):
    mat_name = "DF | " + name
    m = bpy.data.materials.get(mat_name)
    if not m:
        m = bpy.data.materials.new(mat_name)
        m.use_nodes = True
        nodes = m.node_tree.nodes
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        e = nodes.new("ShaderNodeEmission")
        e.inputs['Color'].default_value = (*color, 1.0)
        m.node_tree.links.new(e.outputs[0], out.inputs['Surface'])
        if is_lit:
            add_socket_driver(e.inputs['Strength'], f"1.0 + 0.35 * {flash_expr}")
    return m

# Color palette definition
mat_sky_cloud = create_mat("Storm Cloud", (0.015, 0.028, 0.055))
mat_sky_edge = create_mat("Cloud Edge Silver", (0.045, 0.075, 0.115))
mat_moon = create_mat("Pale Silver Moon", (0.82, 0.84, 0.68), is_lit=False)
mat_lightning_core = create_mat("Lightning Core White", (1.0, 1.0, 1.0), is_lit=False)
mat_lightning_edge = create_mat("Lightning Edge IceBlue", (0.45, 0.78, 1.0), is_lit=False)

mat_mountain_far = create_mat("Mountain Ridge Distant", (0.025, 0.055, 0.095))
mat_mountain_near = create_mat("Foothill Teal Shade", (0.018, 0.048, 0.062))

# Forest greens - deep layers
mat_trunk = create_mat("Wet Cedar Bark", (0.038, 0.028, 0.022))
mat_pine_deep = create_mat("Deep Pine Midnight", (0.008, 0.028, 0.022))
mat_pine_mid = create_mat("Dark Forest Green", (0.016, 0.062, 0.042))
mat_pine_teal = create_mat("Blue Green Pine", (0.014, 0.055, 0.065))
mat_pine_edge = create_mat("Moonlit Pine Edge", (0.028, 0.095, 0.072))
mat_bush = create_mat("Undergrowth Bush", (0.012, 0.048, 0.035))

# Foreground details
mat_grass_dark = create_mat("Ground Grass Dark", (0.022, 0.058, 0.032))
mat_grass_tip = create_mat("Ground Grass Highlight", (0.042, 0.095, 0.052))
mat_stone_dark = create_mat("Slate Stone", (0.045, 0.055, 0.062))
mat_stone_light = create_mat("Stone Highlight", (0.082, 0.095, 0.105))
mat_puddle = create_mat("Puddle Reflection", (0.028, 0.065, 0.092))
mat_puddle_rim = create_mat("Puddle Ripple Rim", (0.095, 0.165, 0.21))

# Rain materials
mat_rain_fore = create_mat("Rain Streak Light Blue", (0.35, 0.55, 0.72), is_lit=False)
mat_rain_back = create_mat("Rain Streak Pale Gray", (0.18, 0.28, 0.38), is_lit=False)

# World background
rn_world = bpy.data.worlds.get("Rainy Night | Camera backdrop")
if not rn_world:
    rn_world = bpy.data.worlds.new("Rainy Night | Camera backdrop")
    rn_world.use_nodes = True
s.world = rn_world
nt = rn_world.node_tree
bg = nt.nodes.get("Background")
if bg:
    add_socket_driver(bg.inputs['Strength'], f"1.0 + 0.45 * {flash_expr}")

# Helper geometry builder
class BatchMesh:
    def __init__(self, name):
        self.name = name
        self.verts = []
        self.faces = []
        self.mat_indices = []
        self.mats = []
        self.mat_map = {}

    def get_mat_idx(self, mat):
        if mat.name not in self.mat_map:
            idx = len(self.mats)
            self.mats.append(mat)
            self.mat_map[mat.name] = idx
            return idx
        return self.mat_map[mat.name]

    def add_poly(self, pts, mat):
        mi = self.get_mat_idx(mat)
        start_idx = len(self.verts)
        self.verts.extend(pts)
        self.faces.append(tuple(range(start_idx, start_idx + len(pts))))
        self.mat_indices.append(mi)

    def add_cone(self, x, y, z, r, h, mat, sides=6):
        mi = self.get_mat_idx(mat)
        top = (x, y, z + h)
        for i in range(sides):
            a1 = i * math.tau / sides
            a2 = (i + 1) * math.tau / sides
            p1 = (x + r * math.cos(a1), y + r * math.sin(a1), z)
            p2 = (x + r * math.cos(a2), y + r * math.sin(a2), z)
            self.add_poly([p1, p2, top], mat)

    def add_ellipsoid(self, x, y, z, rx, ry, rz, mat, segs=8, rings=4):
        for j in range(rings):
            p = -math.pi/2 + math.pi*j/rings
            q = -math.pi/2 + math.pi*(j+1)/rings
            for i in range(segs):
                a = i * math.tau / segs
                b = (i + 1) * math.tau / segs
                pts = [
                    (x + rx * math.cos(t) * math.cos(u),
                     y + ry * math.cos(t) * math.sin(u),
                     z + rz * math.sin(t))
                    for t, u in [(p, a), (p, b), (q, b), (q, a)]
                ]
                self.add_poly(pts, mat)

    def build_object(self, col):
        old_obj = bpy.data.objects.get(self.name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        
        for m in self.mats:
            me.materials.append(m)
        for poly, mi in zip(me.polygons, self.mat_indices):
            poly.material_index = mi
            
        obj = bpy.data.objects.new(self.name, me)
        col.objects.link(obj)
        obj.lineart.usage = 'EXCLUDE'
        return obj

# Clear old environmental objects to upgrade with the dense continuous forest
existing_rn_objs = [o for o in env_col.objects if o.name.startswith("RN |") or o.name.startswith("DF |")]
for o in existing_rn_objs:
    bpy.data.objects.remove(o, do_unlink=True)

cx, cy = -1.3, 0.25
random.seed(98765)

# --- 1. DENSE MULTI-LAYER CONTINUOUS FOREST ---
forest_batch = BatchMesh("DF | Dense Deep Pine Forest")

# Layer 1: Distant background forest wall (Radius 24 to 38m, 160 trees)
for i in range(160):
    angle = (i / 160.0) * math.tau + random.uniform(-0.02, 0.02)
    dist = random.uniform(25.0, 38.0)
    x = cx + dist * math.cos(angle)
    y = cy + dist * math.sin(angle)
    h = random.uniform(2.5, 5.0)
    # Trunk
    forest_batch.add_cone(x, y, -0.2, 0.08, h * 0.8, mat_trunk, sides=4)
    # Foliage cones (darker blue-green / midnight in distance)
    forest_batch.add_cone(x, y, h * 0.2, h * 0.28, h * 0.45, mat_pine_deep, sides=5)
    forest_batch.add_cone(x, y, h * 0.45, h * 0.22, h * 0.40, mat_pine_teal, sides=5)
    forest_batch.add_cone(x, y, h * 0.68, h * 0.16, h * 0.35, mat_pine_deep, sides=5)

# Layer 2: Mid-distance dense forest (Radius 16 to 24m, 110 trees)
for i in range(110):
    angle = (i / 110.0) * math.tau + random.uniform(-0.03, 0.03)
    dist = random.uniform(16.0, 24.0)
    x = cx + dist * math.cos(angle)
    y = cy + dist * math.sin(angle)
    h = random.uniform(3.2, 5.8)
    forest_batch.add_cone(x, y, -0.2, 0.10, h * 0.85, mat_trunk, sides=5)
    forest_batch.add_cone(x, y, h * 0.18, h * 0.32, h * 0.50, mat_pine_mid, sides=6)
    forest_batch.add_cone(x, y, h * 0.42, h * 0.25, h * 0.44, mat_pine_teal, sides=6)
    forest_batch.add_cone(x, y, h * 0.65, h * 0.18, h * 0.38, mat_pine_edge, sides=6)

# Layer 3: Nearer background forest edge (Radius 10 to 15m, 65 trees)
for i in range(65):
    angle = (i / 65.0) * math.tau + random.uniform(-0.04, 0.04)
    dist = random.uniform(10.5, 15.0)
    x = cx + dist * math.cos(angle)
    y = cy + dist * math.sin(angle)
    h = random.uniform(3.8, 6.5)
    forest_batch.add_cone(x, y, -0.2, 0.12, h * 0.9, mat_trunk, sides=6)
    forest_batch.add_cone(x, y, h * 0.15, h * 0.36, h * 0.55, mat_pine_mid, sides=6)
    forest_batch.add_cone(x, y, h * 0.38, h * 0.28, h * 0.48, mat_pine_edge, sides=6)
    forest_batch.add_cone(x, y, h * 0.60, h * 0.20, h * 0.40, mat_pine_mid, sides=6)
    forest_batch.add_cone(x, y, h * 0.80, h * 0.12, h * 0.30, mat_pine_edge, sides=5)

forest_batch.build_object(env_col)

# --- 2. UNDERGROWTH BUSHES & VEGETATION CLUMPS ---
bush_batch = BatchMesh("DF | Forest Undergrowth and Bushes")
for i in range(50):
    angle = random.random() * math.tau
    dist = random.uniform(8.5, 20.0)
    x = cx + dist * math.cos(angle)
    y = cy + dist * math.sin(angle)
    rx = random.uniform(0.4, 0.9)
    ry = random.uniform(0.3, 0.7)
    rz = random.uniform(0.25, 0.5)
    bush_batch.add_ellipsoid(x, y, rz * 0.5, rx, ry, rz, mat_bush, segs=6, rings=3)

bush_batch.build_object(env_col)

# --- 3. MOUNTAIN RIDGES & TEAL FOOTHILLS ---
mount_batch = BatchMesh("DF | Distant Mountain Ridges")
# Outer mountains (Radius 50m)
N = 72
heights = [6.5 + 8.5 * (0.3 + 0.7 * random.random()) for _ in range(N)]
for i in range(N):
    a1 = i * math.tau / N
    a2 = (i + 1) * math.tau / N
    x1, y1 = cx + 50 * math.cos(a1), cy + 50 * math.sin(a1)
    x2, y2 = cx + 50 * math.cos(a2), cy + 50 * math.sin(a2)
    mount_batch.add_poly([(x1, y1, -1.0), (x2, y2, -1.0), (x2, y2, heights[(i+1)%N])], mat_mountain_far)
    mount_batch.add_poly([(x1, y1, -1.0), (x2, y2, heights[(i+1)%N]), (x1, y1, heights[i])], mat_mountain_far)

# Rolling teal foothills (Radius 32m)
N_f = 56
h_foot = [2.2 + 3.8 * (0.3 + 0.7 * random.random()) for _ in range(N_f)]
for i in range(N_f):
    a1 = i * math.tau / N_f
    a2 = (i + 1) * math.tau / N_f
    x1, y1 = cx + 32 * math.cos(a1), cy + 32 * math.sin(a1)
    x2, y2 = cx + 32 * math.cos(a2), cy + 32 * math.sin(a2)
    mount_batch.add_poly([(x1, y1, -1.0), (x2, y2, -1.0), (x2, y2, h_foot[(i+1)%N_f])], mat_mountain_near)
    mount_batch.add_poly([(x1, y1, -1.0), (x2, y2, h_foot[(i+1)%N_f]), (x1, y1, h_foot[i])], mat_mountain_near)

mount_batch.build_object(env_col)

# --- 4. FOREGROUND CLUSTERED GRASS, STONES & PUDDLES ---
fg_batch = BatchMesh("DF | Foreground Grass Rocks and Puddles")

# Low-poly rocks & stones
for i in range(48):
    angle = random.random() * math.tau
    dist = random.uniform(4.5, 14.0)
    x = cx + dist * math.cos(angle)
    y = cy + dist * math.sin(angle)
    sz = random.uniform(0.12, 0.45)
    s_mat = mat_stone_dark if (i % 2 == 0) else mat_stone_light
    fg_batch.add_ellipsoid(x, y, sz * 0.25, sz, sz * 0.75, sz * 0.45, s_mat, segs=6, rings=3)

# Clustered grass tufts (placed around rocks and near forest edge, radius 4.4 to 13m)
for i in range(85):
    angle = random.random() * math.tau
    dist = random.uniform(4.4, 13.0)
    gx = cx + dist * math.cos(angle)
    gy = cy + dist * math.sin(angle)
    
    # Each cluster has 3-4 small blade cards
    for b in range(4):
        ba = b * (math.tau / 4.0) + random.uniform(-0.2, 0.2)
        blen = random.uniform(0.12, 0.28)
        bw = random.uniform(0.02, 0.035)
        bh = random.uniform(0.15, 0.35)
        
        dx = math.cos(ba) * blen
        dy = math.sin(ba) * blen
        
        # Blade quad
        pts = [
            (gx - dy * bw, gy + dx * bw, 0.01),
            (gx + dy * bw, gy - dx * bw, 0.01),
            (gx + dx * 0.6, gy + dy * 0.6, bh),
        ]
        g_mat = mat_grass_dark if (b % 2 == 0) else mat_grass_tip
        fg_batch.add_poly(pts, g_mat)

# Small outlying puddles with subtle ripple rings
for i in range(24):
    angle = (i / 24.0) * math.tau + random.uniform(-0.05, 0.05)
    dist = random.uniform(4.3, 10.5)
    px = cx + dist * math.cos(angle)
    py = cy + dist * math.sin(angle)
    rx = random.uniform(0.35, 0.75)
    ry = random.uniform(0.18, 0.40)
    
    # Flat puddle polygon
    fg_batch.add_poly(
        [(px + rx * math.cos(t * math.tau / 16.0), py + ry * math.sin(t * math.tau / 16.0), 0.008) for t in range(16)],
        mat_puddle
    )
    # Ripple border
    for j in range(6):
        a0 = 0.2 + j * 0.25
        a1 = a0 + 0.16
        fg_batch.add_poly([
            (px + rx * math.cos(a0), py + ry * math.sin(a0), 0.009),
            (px + rx * math.cos(a1), py + ry * math.sin(a1), 0.009),
            (px + rx * 0.94 * math.cos(a1), py + ry * 0.94 * math.sin(a1), 0.009),
            (px + rx * 0.94 * math.cos(a0), py + ry * 0.94 * math.sin(a0), 0.009),
        ], mat_puddle_rim)

fg_batch.build_object(env_col)

# --- 5. DRAMATIC CONTRASTING RED GROUND ACCENT GLOW ---
# The prompt explicitly requests: "The existing red ground illumination as a dramatic contrasting light source."
red_accent_obj = bpy.data.objects.get("DF | Red Ground Illumination Accent")
if not red_accent_obj:
    red_light_data = bpy.data.lights.new("DF | Red Ground Illumination", 'POINT')
    red_light_data.color = (1.0, 0.12, 0.08)
    red_light_data.energy = 450.0
    red_light_data.shadow_soft_size = 1.8
    red_accent_obj = bpy.data.objects.new("DF | Red Ground Illumination Accent", red_light_data)
    env_col.objects.link(red_accent_obj)

# Place at low ground level near the perimeter of the arena (-1.3, 0.25, 0.4)
red_accent_obj.location = (-1.3, -2.8, 0.45)
print("Configured dramatic red ground illumination accent")

# --- 6. MOON & STORM CLOUDS ---
moon_batch = BatchMesh("DF | Pale Silver Moon and Storm Clouds")
# Moon (large low-poly sphere in distance)
moon_batch.add_ellipsoid(-24, 65, 28, 4.0, 4.0, 4.0, mat_moon, segs=24, rings=12)

# Storm cloud banks partially veiling the moon
for j in range(5):
    cx_c = -24 + (j - 2) * 5.5
    cy_c = 58 + random.uniform(-2, 2)
    cz_c = 25.5 + random.uniform(-1, 1)
    moon_batch.add_ellipsoid(cx_c, cy_c, cz_c, random.uniform(6, 9), 3.2, 1.4, mat_sky_cloud, segs=10, rings=4)

# Perimeter storm clouds over mountains
for i in range(16):
    a = i * math.tau / 16.0
    r_c = 46.0
    qx = cx + r_c * math.cos(a)
    qy = cy + r_c * math.sin(a)
    qz = random.uniform(16.0, 26.0)
    moon_batch.add_ellipsoid(qx, qy, qz, random.uniform(7.0, 11.0), 4.0, 2.0, mat_sky_cloud, segs=8, rings=3)

moon_batch.build_object(env_col)

# --- 7. IMPROVED BRANCHING DISTANT LIGHTNING ---
bolt_batch = BatchMesh("DF | Branching Distant Lightning")

# Main strike 1: In the deep sky near the mountains
main_nodes = [
    (-18, 42, 26),
    (-17.2, 41.5, 23.5),
    (-18.5, 41.0, 20.8),
    (-17.0, 40.8, 18.2),
    (-18.0, 40.5, 15.5),
    (-16.8, 40.2, 12.0),
    (-17.5, 40.0, 8.5),
]
# Fork 1
fork1_nodes = [
    (-17.2, 41.5, 23.5),
    (-15.8, 41.2, 21.5),
    (-14.9, 41.0, 19.0),
]
# Fork 2
fork2_nodes = [
    (-17.0, 40.8, 18.2),
    (-15.8, 40.5, 16.2),
    (-15.2, 40.3, 13.8),
]

for seg in [main_nodes, fork1_nodes, fork2_nodes]:
    for p, q in zip(seg, seg[1:]):
        w_core = 0.04
        w_edge = 0.12
        # White bright core
        bolt_batch.add_poly([
            (p[0] - w_core, p[1], p[2]),
            (p[0] + w_core, p[1], p[2]),
            (q[0] + w_core, q[1], q[2]),
            (q[0] - w_core, q[1], q[2]),
        ], mat_lightning_core)
        # Icy blue outer halo
        bolt_batch.add_poly([
            (p[0] - w_edge, p[1], p[2]),
            (p[0] + w_edge, p[1], p[2]),
            (q[0] + w_edge, q[1], q[2]),
            (q[0] - w_edge, q[1], q[2]),
        ], mat_lightning_edge)

bolt_obj = bolt_batch.build_object(env_col)
# Drive scale by flash formula
for ax in range(3):
    add_prop_driver(bolt_obj, 'scale', ax, flash_expr)

# --- 8. MULTI-LAYER LIGHTWEIGHT PROCEDURAL RAIN STREAKS ---
rain_batch = BatchMesh("DF | Looping Multi-layer Rain Streaks")

# Foreground light-blue rain streaks
for i in range(140):
    a = random.random() * math.tau
    r_rain = random.uniform(6.5, 22.0)
    rx = cx + r_rain * math.cos(a)
    ry = cy + r_rain * math.sin(a)
    rz = random.uniform(0.0, 6.0)
    rlen = random.uniform(0.28, 0.48)
    rw = random.uniform(0.007, 0.013)
    tx, ty = -math.sin(a) * rw, math.cos(a) * rw
    
    # 5 vertical repeats for continuous looping
    for k in range(-1, 6):
        base_z = rz + k * 6.0
        rain_batch.add_poly([
            (rx - tx, ry - ty, base_z),
            (rx + tx, ry + ty, base_z),
            (rx + tx, ry + ty, base_z + rlen),
            (rx - tx, ry - ty, base_z + rlen),
        ], mat_rain_fore)

# Distant pale-gray rain streaks in front of the forest
for i in range(120):
    a = random.random() * math.tau
    r_rain = random.uniform(22.0, 36.0)
    rx = cx + r_rain * math.cos(a)
    ry = cy + r_rain * math.sin(a)
    rz = random.uniform(0.0, 6.0)
    rlen = random.uniform(0.20, 0.36)
    rw = random.uniform(0.006, 0.010)
    tx, ty = -math.sin(a) * rw, math.cos(a) * rw
    for k in range(-1, 6):
        base_z = rz + k * 6.0
        rain_batch.add_poly([
            (rx - tx, ry - ty, base_z),
            (rx + tx, ry + ty, base_z),
            (rx + tx, ry + ty, base_z + rlen),
            (rx - tx, ry - ty, base_z + rlen),
        ], mat_rain_back)

rain_obj = rain_batch.build_object(env_col)
# Seamless modulo loop driver: 24 frames loop
add_prop_driver(rain_obj, 'location', 2, "-((frame - 1) % 24) / 4.0")

# --- 9. VIEWPORT SHADING & COMPOSITOR ---
for window in bpy.context.window_manager.windows:
    screen = window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True

# Ensure clean composite output directly from ViewLayer
if s.compositing_node_group:
    nt = s.compositing_node_group
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.layer = "ViewLayer"
    rl.location = (0, 0)
    out = nt.nodes.new("NodeGroupOutput")
    out.location = (400, 0)
    nt.links.new(rl.outputs['Image'], out.inputs['Image'])

# Restore frame
s.frame_set(orig_frame)

# --- 10. VERIFY ALL 550 FRAMES OF CHARACTER MOTION & OBJECT INTEGRITY ---
after_snap = snapshot(original_names, action_names, material_names)

assert after_snap['objects'] == before_snap['objects'], "Original objects modified!"
assert after_snap['actions'] == before_snap['actions'], "Original animation actions modified!"
assert after_snap['materials'] == before_snap['materials'], "Original materials modified!"
assert after_snap['settings'] == before_snap['settings'], "Render / camera / FPS settings modified!"
assert after_snap['motion_all_550_frames'] == before_snap['motion_all_550_frames'], "Evaluated character motion changed!"

print("=== ALL AUDIT CHECKS PASSED 100%! ===")

# --- 11. SAVE AS SEPARATE FILE WITHOUT OVERWRITING ORIGINAL ---
separate_filepath = os.path.join(project_dir, "main_enhanced_forest.blend")
bpy.ops.wm.save_as_mainfile(filepath=separate_filepath)
print(f"SUCCESSFULLY SAVED SEPARATE PROJECT: {separate_filepath}")
