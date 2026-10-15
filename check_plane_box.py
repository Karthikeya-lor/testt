import bpy

s = bpy.context.scene
p = bpy.data.objects.get("Plane")
print("Plane dims:", p.dimensions)
print("Plane loc:", p.location)
print("Plane bound_box:")
for b in p.bound_box:
    print(" ", b)
