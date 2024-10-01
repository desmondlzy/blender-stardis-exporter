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
def export_custom_format(dirpath):
	# check if the directory exists
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)

	# Get the current scene
	scene = bpy.context.scene

	names = set()

	# Iterate through objects in the scene
	for obj in scene.objects:
		# If the object is a mesh, write vertex data
		if obj.type == 'MESH':
			# select the mesh
			obj.select_set(True)

			# export the mesh data to a file in dirpath, format stl
			if obj.name in names:
				# print a warning
				print("Duplicate object name: " + obj.name)
				continue

			names.add(obj.name)
			filename = os.path.join(dirpath, obj.name + ".stl")
			bpy.ops.export_mesh.stl(filepath=filename, check_existing=False, use_selection=True)

			obj.select_set(False)

# Blender Operator to handle the export
class ExportCustomFormatOperator(bpy.types.Operator):
	"""Export scene to custom format"""
	bl_idname = "export_scene.stardis_input"
	bl_label = "Export Stardis Input Format"
	bl_options = {'PRESET'}

	filepath: bpy.props.StringProperty(subtype='DIR_PATH', default="stardis_export")

	def execute(self, context):
		print(self.filepath)
		actual_path = bpy.path.abspath(self.filepath)
		export_custom_format(actual_path)
		return {'FINISHED'}

	def invoke(self, context, event):
		# Open file browser to choose where to save the file
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


# Define the enum items
property_items = [
	('SOLID', "Solid", ""),
	('DIRICHLET', "Dirichlet", ""),
	('ROBIN_SOLID', "RobinSolid", ""),
	('ROBIN_FLUID', "RobinFluid", ""),
]

# Main Panel: Custom Object Settings
class OBJECT_PT_main_panel(bpy.types.Panel):
	bl_label = "Custom Object Settings"
	bl_idname = "OBJECT_PT_main_panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "object"

	def draw(self, context):
		layout = self.layout
		obj = context.object

		# Enum to select which group of properties is active
		layout.prop(obj, "selected_property_group", text="Type")

		# Conditionally show properties based on the selected group
		if obj.selected_property_group == 'SOLID':
			# Display transform properties
			layout.prop(obj, "conductivity", text="conductivity")
			layout.prop(obj, "rho", text="rho")
			layout.prop(obj, "capacity", text="capacity")
			layout.prop(obj, "delta", text="delta")
			layout.prop(obj, "initial_temp", text="initial_temp")
			layout.prop(obj, "imposed_temp", text="imposed_temp")
			layout.prop(obj, "volumic_power", text="volumic_power")
		elif obj.selected_property_group == 'DIRICHLET':
			# Display custom material properties
			layout.prop(obj, "temp", text="Temperature")

		elif obj.selected_property_group == 'ROBIN_SOLID' or obj.selected_property_group == 'ROBIN_FLUID':
			layout.prop(obj, "emissivity", text="Emissivity")
			layout.prop(obj, "specular_fraction", text="Specular Fraction")
			layout.prop(obj, "hc", text="hc")
			layout.prop(obj, "outside_temp", text="Outside Temp")

		else:
			layout.label(text="No properties available for this group")

# Define custom properties for objects
def register_custom_properties():
	# EnumProperty to select the active property group
	bpy.types.Object.selected_property_group = bpy.props.EnumProperty(
		name="Stardis Object Type",
		description="Stardis Object Type",
		items=property_items,
		default='SOLID'
	)

	# FloatProperty for conductivity
	bpy.types.Object.conductivity = bpy.props.FloatProperty(
		name="Conductivity",
		description="Conductivity",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.rho = bpy.props.FloatProperty(
		name="Rho",
		description="Rho",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.capacity = bpy.props.FloatProperty(
		name="Capacity",
		description="Capacity",
		default=1.0,
		min=0.0
	)

	# delta can be a float or a string "AUTO"
	bpy.types.Object.delta = bpy.props.FloatProperty(
		name="Delta",
		description="Delta",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.initial_temp = bpy.props.FloatProperty(
		name="Initial Temp",
		description="Initial Temp",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.imposed_temp = bpy.props.FloatProperty(
		name="Imposed Temp",
		description="Imposed Temp",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.volumic_power = bpy.props.FloatProperty(
		name="Volumic Power",
		description="Volumic Power",
		default=1.0,
		min=0.0
	)

	bpy.types.Object.temp = bpy.props.FloatProperty(
		name="Temperature",
		description="Temperature",
		default=300.0,
		min=0.0
	)

# Register and Unregister classes and properties
def register_custom_properties_panel():
	register_custom_properties()
	bpy.utils.register_class(OBJECT_PT_main_panel)

def unregister_custom_properties_panel():
	bpy.utils.unregister_class(OBJECT_PT_main_panel)
	del bpy.types.Object.my_custom_color
	del bpy.types.Object.my_custom_shininess
	del bpy.types.Object.my_custom_transparency
	del bpy.types.Object.selected_property_group


# Add the export option to the export menu
def menu_func_export(self, context):
	self.layout.operator(ExportCustomFormatOperator.bl_idname, text="Stardis Export")

# Register and unregister functions
def register():
	bpy.utils.register_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

	register_custom_properties_panel()

def unregister():
	bpy.utils.unregister_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
	
	unregister_custom_properties_panel()

if __name__ == "__main__":
	register()
