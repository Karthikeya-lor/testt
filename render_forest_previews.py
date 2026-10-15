import bpy
import os

filepath = r"c:\Users\mouli\OneDrive\Desktop\cga_project\main_enhanced_forest.blend"
bpy.ops.wm.open_mainfile(filepath=filepath)
s = bpy.context.scene

s.render.image_settings.media_type = 'IMAGE'
s.render.image_settings.file_format = 'PNG'
s.render.resolution_percentage = 50
review_dir = r"c:\Users\mouli\OneDrive\Desktop\cga_project\enhancement_review"

for frame in [72, 126, 220]:
    s.frame_set(frame)
    s.render.filepath = os.path.join(review_dir, f"forest_preview_{frame:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered forest preview frame {frame} to {s.render.filepath}")
