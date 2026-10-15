import bpy

for name in bpy.data.objects:
    if name.name.startswith("cs_"):
        print(f"Object '{name.name}': type={name.type}, loc={name.location}, hide_viewport={name.hide_viewport}, hide_render={name.hide_render}, hide_get={name.hide_get()}")
