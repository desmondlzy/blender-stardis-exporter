import bpy

bpy.ops.preferences.addon_install(
	filepath="blender_stardis_exporter.py",
	overwrite=True,
	enable_on_install=True,
)
