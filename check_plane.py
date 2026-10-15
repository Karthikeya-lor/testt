import bpy

orig = bpy.data.objects.get("Plane")
if orig:
    print(f"Plane location: {orig.location}, scale: {orig.scale}, dim: {orig.dimensions}")
    print(f"Plane materials: {[s.material.name for s in orig.material_slots if s.material]}")
    if orig.material_slots and orig.material_slots[0].material:
        mat = orig.material_slots[0].material
        print(f"Material name: {mat.name}")
        if mat.node_tree:
            for n in mat.node_tree.nodes:
                print(f"  Node: {n.name} ({n.type})")
