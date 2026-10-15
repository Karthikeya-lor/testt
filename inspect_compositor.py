import bpy

s = bpy.context.scene
nt = s.compositing_node_group
print("Compositor Node Tree:", nt.name if nt else None)
if nt:
    for n in nt.nodes:
        print(f"  Node: '{n.name}' ({n.type}) | Inputs: {[i.name for i in n.inputs]} | Outputs: {[o.name for o in n.outputs]}")
        for out in n.outputs:
            for l in out.links:
                print(f"    Link: {n.name}.{out.name} -> {l.to_node.name}.{l.to_socket.name}")
