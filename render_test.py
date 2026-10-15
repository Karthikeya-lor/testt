import bpy
import os

s = bpy.context.scene
orig_media = s.render.image_settings.media_type
orig_format = s.render.image_settings.file_format

s.render.image_settings.media_type = 'IMAGE'
s.render.image_settings.file_format = 'PNG'
s.render.resolution_percentage = 50
review = r"c:\Users\mouli\OneDrive\Desktop\cga_project\enhancement_review"

for frame in [72, 126, 220]:
    s.frame_set(frame)
    s.render.filepath = os.path.join(review, f"direct_preview_{frame:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered frame {frame} to {s.render.filepath}")
