bl_info = {
	"name": "Stardis Exporter",
	"author": "Desmond Liu",
	"version": (1, 0),
	"blender": (4, 0, 0),
	"location": "File > Export > Stardis Input Format Export (.txt)",
	"description": "",
	"category": "Import-Export",
}

import bpy
import os

# Function to write the scene data to a custom format
def export_custom_format(filepath):
	# Open the file for writing
	with open(filepath, 'w') as file:
		# Write a header
		file.write("Custom Scene Export\n")
		file.write("====================\n\n")
		
		# Get the current scene
		scene = bpy.context.scene
		
		# Iterate through objects in the scene
		for obj in scene.objects:
			file.write(f"Object: {obj.name}\n")
			file.write(f"Type: {obj.type}\n")
			file.write(f"Location: {obj.location[0]}, {obj.location[1]}, {obj.location[2]}\n")
			
			# If the object is a mesh, write vertex data
			if obj.type == 'MESH':
				file.write("Mesh data:\n")
				mesh = obj.data
				for vert in mesh.vertices:
					file.write(f"  Vertex: {vert.co[0]}, {vert.co[1]}, {vert.co[2]}\n")
			file.write("\n")

# Blender Operator to handle the export
class ExportCustomFormatOperator(bpy.types.Operator):
	"""Export scene to custom format"""
	bl_idname = "export_scene.stardis_input"
	bl_label = "Export Stardis Input Format"
	bl_options = {'PRESET'}

	filepath: bpy.props.StringProperty(subtype='FILE_PATH', default="stardis.txt")

	def execute(self, context):
		print(self.filepath)
		actual_path = bpy.path.abspath(self.filepath)
		export_custom_format(actual_path)
		return {'FINISHED'}

	def invoke(self, context, event):
		# Open file browser to choose where to save the file
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

# Add the export option to the export menu
def menu_func_export(self, context):
	self.layout.operator(ExportCustomFormatOperator.bl_idname, text="Stardis Export (.txt)")

# Register and unregister functions
def register():
	bpy.utils.register_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
	bpy.utils.unregister_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()
