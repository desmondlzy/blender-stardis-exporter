# blender -b -P blender_headless_addon_enable.py

import bpy

bpy.ops.preferences.addon_install(
	filepath="./blender_stardis_exporter.py",
	overwrite=True,
)

bpy.ops.preferences.addon_enable(module="blender_stardis_exporter")

bpy.ops.wm.save_userpref()

print(bpy.types.Object.stardis_object_properties)
