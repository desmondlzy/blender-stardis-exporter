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
	

class AddStardisObjectProperty(bpy.types.Operator):
	bl_idname = "object.add_stardis_object_property"
	bl_label = "Add Stardis Object Property"

	def execute(self, context):
		obj = context.object
		obj.stardis_object_properties.add()
		return {'FINISHED'}
	

class RemoveStardisObjectProperty(bpy.types.Operator):
	bl_idname = "object.remove_stardis_object_property"
	bl_label = "Remove Stardis Object Property"

	index: bpy.props.IntProperty()

	def execute(self, context):
		obj = context.object
		obj.stardis_object_properties.remove(self.index)
		return {'FINISHED'}


# Define the enum items
property_items = [
	('SOLID', "Solid", ""),
	('DIRICHLET', "Dirichlet", ""),
	('ROBIN_SOLID', "RobinSolid", ""),
	('ROBIN_FLUID', "RobinFluid", ""),
]

# Main Panel: Custom Object Settings
class StardisObjectPropertyPanel(bpy.types.Panel):
	bl_label = "Stardis Object Properties"
	bl_idname = "StardisObjectPropertyPanel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "object"

	def draw(self, context):
		layout = self.layout
		obj = context.object

		# display the number of properties
		row = layout.row()
		row.label(text="Number of Properties: " + str(len(obj.stardis_object_properties)))

		# Add a button to add a new property
		row = layout.row()
		row.operator("object.add_stardis_object_property", text="Add Stardis Object Property")

		# Iterate through the properties and display them one by one
		for i, prop in enumerate(obj.stardis_object_properties):
			# create a subpanel for each property
			panel = layout.box()
			row = panel.row()
			row.prop(prop, "stardis_object_type", text="Type")

			row.operator("object.remove_stardis_object_property", text="", icon='X').index = i

			# Display the properties based on the type
			if prop.stardis_object_type == 'SOLID':
				solid = prop.solid

				row = panel.row()
				row.prop(solid, "conductivity")
				row = panel.row()
				row.prop(solid, "rho")
				row = panel.row()
				row.prop(solid, "capacity")

				row = panel.row()
				col = row.split()
				col.prop(solid, "delta")
				col.prop(solid, "delta_auto", text="Auto")

				row = panel.row()
				col = row.split()
				col.prop(solid, "imposed_temp")
				col.prop(solid, "imposed_temp_unknown", text="Unknown")

				row = panel.row()
				row.prop(solid, "initial_temp")
				row = panel.row()
				row.prop(solid, "volumic_power")
				col = panel.column()
				col.props_enum(solid, "triangle_sides")
			
			elif prop.stardis_object_type == 'DIRICHLET':
				dirichlet = prop.dirichlet

				row = panel.row()
				row.prop(dirichlet, "temp")

			elif prop.stardis_object_type in ['ROBIN_SOLID', 'ROBIN_FLUID']:
				robin = prop.robin
				row = panel.row()
				row.prop(robin, "emissivity")
				row = panel.row()
				row.prop(robin, "specular_fraction")
				row = panel.row()
				row.prop(robin, "hc")
				row = panel.row()
				row.prop(robin, "outside_temp")
			
			else:
				row = panel.row()
				row.label(text="No properties available for this type")


class StardisSolidProperty(bpy.types.PropertyGroup):
	conductivity: bpy.props.FloatProperty(
		name="Conductivity",
		description="Conductivity",
		default=1.0,
		min=0.0
	)

	rho: bpy.props.FloatProperty(
		name="Rho",
		description="Rho",
		default=1.0,
		min=0.0
	)

	capacity: bpy.props.FloatProperty(
		name="Capacity",
		description="Capacity",
		default=1.0,
		min=0.0
	)

	delta_auto: bpy.props.BoolProperty(
		name="Delta Auto",
		description="Delta Auto",
		default=True
	)

	delta: bpy.props.FloatProperty(
		name="Delta",
		description="Delta",
		default=1.0,
		min=0.0
	)

	imposed_temp: bpy.props.FloatProperty(
		name="Imposed Temp",
		description="Imposed Temp",
		default=300.0,
		min=0.0
	)

	imposed_temp_unknown: bpy.props.BoolProperty(
		name="Imposed Temp Unknown",
		description="Imposed Temp Unknown",
		default=True,
	)

	initial_temp: bpy.props.FloatProperty(
		name="Initial Temp",
		description="Initial Temp",
		default=300.0,
		min=0.0
	)

	volumic_power: bpy.props.FloatProperty(
		name="Volumic Power",
		description="Volumic Power",
		default=1.0,
		min=0.0
	)

	triangle_sides: bpy.props.EnumProperty(
		name="Triangle Sides",
		description="Triangle Sides",
		items=[
			('FRONT', "Front", ""),
			('BACK', "Back", ""),
			('BOTH', "Both", ""),
		],
		default='BOTH',
	)

class StardisDirichletProperty(bpy.types.PropertyGroup):
	temp: bpy.props.FloatProperty(
		name="Temperature",
		description="Temperature",
		default=300.0,
		min=0.0
	)

class StardisRobinSolidProperty(bpy.types.PropertyGroup):	
	emissivity: bpy.props.FloatProperty(
		name="Emissivity",
		description="Emissivity",
		default=1.0,
		min=0.0,
		max=1.0
	)

	specular_fraction: bpy.props.FloatProperty(
		name="Specular Fraction",
		description="Specular Fraction",
		default=1.0,
		min=0.0,
		max=1.0
	)

	hc: bpy.props.FloatProperty(
		name="hc",
		description="Convective Heat Transfer Coefficient",
		default=1.0,
		min=0.0
	)

	outside_temp: bpy.props.FloatProperty(
		name="Outside Temp",
		description="Outside Temp",
		default=300.0,
		min=0.0
	)


class StardisRobinFluidProperty(bpy.types.PropertyGroup):
	pass



class StardisObjectProperty(bpy.types.PropertyGroup):
	stardis_object_type: bpy.props.EnumProperty(
		name="Stardis Object Type",
		description="Stardis Object Type",
		items=property_items,
		default='SOLID'
	)

	solid: bpy.props.PointerProperty(type=StardisSolidProperty)
	dirichlet: bpy.props.PointerProperty(type=StardisDirichletProperty)
	robin_solid: bpy.props.PointerProperty(type=StardisRobinSolidProperty)
	robin_fluid: bpy.props.PointerProperty(type=StardisRobinFluidProperty)


# Define custom properties for objects
def register_custom_properties():
	bpy.utils.register_class(StardisSolidProperty)
	bpy.utils.register_class(StardisDirichletProperty)
	bpy.utils.register_class(StardisRobinSolidProperty)
	bpy.utils.register_class(StardisRobinFluidProperty)

	bpy.utils.register_class(StardisObjectProperty)

	bpy.types.Object.stardis_object_properties = bpy.props.CollectionProperty(type=StardisObjectProperty)


# Register and Unregister classes and properties
def register_custom_properties_panel():
	register_custom_properties()
	bpy.utils.register_class(StardisObjectPropertyPanel)

def unregister_custom_properties_panel():
	bpy.utils.unregister_class(StardisObjectProperty)
	bpy.utils.unregister_class(StardisSolidProperty)
	bpy.utils.unregister_class(StardisDirichletProperty)
	bpy.utils.unregister_class(StardisRobinSolidProperty)
	bpy.utils.unregister_class(StardisRobinFluidProperty)

	del bpy.types.Object.stardis_object_properties

	bpy.utils.unregister_class(StardisObjectPropertyPanel)



# Add the export option to the export menu
def menu_func_export(self, context):
	self.layout.operator(ExportCustomFormatOperator.bl_idname, text="Stardis Export")

# Register and unregister functions
def register():
	bpy.utils.register_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

	bpy.utils.register_class(AddStardisObjectProperty)
	bpy.utils.register_class(RemoveStardisObjectProperty)

	register_custom_properties_panel()

def unregister():
	bpy.utils.unregister_class(ExportCustomFormatOperator)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

	bpy.utils.unregister_class(AddStardisObjectProperty)
	bpy.utils.unregister_class(RemoveStardisObjectProperty)
	
	unregister_custom_properties_panel()

if __name__ == "__main__":
	register()
