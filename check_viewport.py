import bpy

for window in bpy.context.window_manager.windows:
    screen = window.screen
    print(f"Screen: {screen.name}")
    for area in screen.areas:
        print(f"  Area type: {area.type}")
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    shading = space.shading
                    print(f"    Viewport shading type: {shading.type}")
                    print(f"    Viewport color type: {shading.color_type}")
