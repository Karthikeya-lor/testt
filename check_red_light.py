import bpy

for path, label in [(r"c:\Users\mouli\OneDrive\Desktop\cga_project\original.blend", "ORIGINAL"),
                    (r"c:\Users\mouli\OneDrive\Desktop\cga_project\main.blend", "MAIN")]:
    try:
        bpy.ops.wm.open_mainfile(filepath=path)
        print(f"\n=== {label} FILE ===")
        for l in bpy.data.lights:
            print(f"Light '{l.name}': type={l.type}, color={list(l.color)}, energy={l.energy}")
        for o in bpy.data.objects:
            if o.type == 'LIGHT':
                print(f"Light Obj '{o.name}': loc={o.location}, rot={o.rotation_euler}")
        for m in bpy.data.materials:
            if m.use_nodes and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == 'EMISSION':
                        print(f"Mat '{m.name}' Emission node color: {list(n.inputs['Color'].default_value)}, strength: {n.inputs['Strength'].default_value}")
    except Exception as e:
        print(f"Error reading {path}: {e}")
