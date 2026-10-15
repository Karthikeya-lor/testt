import bpy

def check_visibility():
    scene = bpy.context.scene
    print(f"Active View Layer: {bpy.context.view_layer.name}")
    for vl in scene.view_layers:
        print(f"\nView Layer: {vl.name}")
        for child in vl.layer_collection.children:
            print(f"  Collection '{child.name}': exclude={child.exclude}, hide_viewport={child.hide_viewport}")
    
    col = bpy.data.collections.get("Rainy Night | Environment Additions")
    if col:
        print(f"\nCollection 'Rainy Night | Environment Additions': hide_viewport={col.hide_viewport}, hide_render={col.hide_render}")
        for o in col.objects:
            print(f"  Object '{o.name}': hide_viewport={o.hide_viewport}, hide_render={o.hide_render}, hide_get={o.hide_get()}")

    print(f"\nScene World: {scene.world.name if scene.world else None}")
    if scene.world and scene.world.node_tree:
        for node in scene.world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                print(f"  World Background color: {list(node.inputs['Color'].default_value)}")

    print(f"\nScene use_nodes (Compositor): {scene.use_nodes}")

check_visibility()
