import bpy

s = bpy.context.scene
orig_start = s.frame_start
orig_end = s.frame_end
orig_res = s.render.resolution_percentage
orig_filepath = s.render.filepath

s.frame_start = 115
s.frame_end = 140
s.render.resolution_percentage = 40
s.render.filepath = r"c:\Users\mouli\OneDrive\Desktop\cga_project\preview_rain_lightning.mp4"
s.render.image_settings.media_type = 'VIDEO'
s.render.image_settings.file_format = 'FFMPEG'
s.render.ffmpeg.format = 'MPEG4'
s.render.ffmpeg.codec = 'H264'

print("Rendering video preview from frame 115 to 140...")
bpy.ops.render.render(animation=True)
print("Finished video preview render!")

# Restore original project settings
s.frame_start = orig_start
s.frame_end = orig_end
s.render.resolution_percentage = orig_res
s.render.filepath = orig_filepath
bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\mouli\OneDrive\Desktop\cga_project\main.blend")
