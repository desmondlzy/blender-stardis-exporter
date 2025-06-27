import bpy
import random
import os

# === CONFIG ===
OUTPUT_PATH = os.path.join(bpy.path.abspath("//"), "render_output.png")
TEMP_MAT_PREFIX = "Temp_UniqueColor_"
original_materials = {}
world_node_backup = {}

def generate_unique_color(index):
    random.seed(index)
    return (random.random(), random.random(), random.random(), 1)

def backup_world_nodes():
    """Serializes the World node tree into a plain dict."""
    global world_node_backup
    world = bpy.context.scene.world
    if not world or not world.use_nodes:
        world_node_backup = {}
        return

    node_tree = world.node_tree
    nodes_data = []
    for node in node_tree.nodes:
        node_info = {
            "name": node.name,
            "type": node.bl_idname,
            "location": node.location[:],
            "inputs": {}
        }

        for inp in node.inputs:
            if hasattr(inp, "default_value"):
                try:
                    val = inp.default_value
                    node_info["inputs"][inp.name] = list(val) if isinstance(val, (list, tuple)) else val
                except:
                    continue  # Skip uncopyable inputs

        nodes_data.append(node_info)

    links_data = []
    for link in node_tree.links:
        links_data.append({
            "from_node": link.from_node.name,
            "from_socket": link.from_socket.name,
            "to_node": link.to_node.name,
            "to_socket": link.to_socket.name,
        })

    world_node_backup = {
        "nodes": nodes_data,
        "links": links_data,
    }

def replace_world_with_white_background():
    """Overrides the World node tree with a constant white background."""
    world = bpy.context.scene.world
    tree = world.node_tree
    tree.nodes.clear()

    bg = tree.nodes.new(type='ShaderNodeBackground')
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = 1.0

    output = tree.nodes.new(type='ShaderNodeOutputWorld')
    tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

def restore_world_nodes():
    """Rebuilds the World node tree from the plain dict."""
    global world_node_backup
    if not world_node_backup:
        return

    world = bpy.context.scene.world
    tree = world.node_tree
    tree.nodes.clear()

    name_to_node = {}

    for node_info in world_node_backup["nodes"]:
        node = tree.nodes.new(type=node_info["type"])
        node.name = node_info["name"]
        node.location = node_info.get("location", (0, 0))
        name_to_node[node.name] = node

        for input_name, value in node_info.get("inputs", {}).items():
            if input_name in node.inputs:
                print("----------")
                print(type(node))
                input_socket = node.inputs.get(input_name)
                print(input_socket)
                print(type(input_socket))
                print("type of value", type(value))
                input_socket = node.inputs[input_name]
                if hasattr(input_socket, "default_value"):
                    try:
                        if isinstance(input_socket.default_value, float):
                            input_socket.default_value = float(value)
                        elif isinstance(input_socket.default_value, (int, bool)):
                            input_socket.default_value = value
                        elif isinstance(input_socket.default_value, (list, tuple)):
                            input_socket.default_value = list(value)
                        else:
                            pass  # unhandled type
                    except Exception as e:
                        print(f"⚠️ Could not assign '{input_name}': {e}") 
                # node.inputs[input_name].default_value = value
                # try:
                #     node.inputs[input_name].default_value = value
                # except:
                #     continue  # Skip bad assignments

    for link in world_node_backup["links"]:
        from_node = name_to_node.get(link["from_node"])
        to_node = name_to_node.get(link["to_node"])
        if from_node and to_node:
            try:
                tree.links.new(
                    from_node.outputs[link["from_socket"]],
                    to_node.inputs[link["to_socket"]]
                )
            except:
                continue

def setup_render_settings():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 512

    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = OUTPUT_PATH
    scene.render.film_transparent = False

    backup_world_nodes()
    replace_world_with_white_background()

    # Disable indirect lighting and shadows
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False

    for light in [obj for obj in bpy.data.objects if obj.type == 'LIGHT']:
        light.hide_render = True

def assign_temp_materials():
    for i, obj in enumerate(bpy.data.objects):
        if obj.type == 'MESH':
            original_materials[obj.name] = [slot.material for slot in obj.material_slots]

            color = generate_unique_color(i)

            mat = bpy.data.materials.new(name=f"{TEMP_MAT_PREFIX}{i}")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()

            emission = nodes.new(type='ShaderNodeEmission')
            emission.inputs['Color'].default_value = color
            emission.inputs['Strength'].default_value = 1.0

            output = nodes.new(type='ShaderNodeOutputMaterial')
            links.new(emission.outputs['Emission'], output.inputs['Surface'])

            if not obj.material_slots:
                obj.data.materials.append(mat)
            else:
                for j in range(len(obj.material_slots)):
                    obj.material_slots[j].material = mat

def restore_original_materials():
    for obj_name, materials in original_materials.items():
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.type == 'MESH':
            obj.data.materials.clear()
            for mat in materials:
                if mat:
                    obj.data.materials.append(mat)

def delete_temp_materials():
    temp_mats = [mat for mat in bpy.data.materials if mat.name.startswith(TEMP_MAT_PREFIX)]
    for mat in temp_mats:
        bpy.data.materials.remove(mat, do_unlink=True)

# === MAIN EXECUTION ===
setup_render_settings()
assign_temp_materials()

bpy.ops.render.render(write_still=True)

restore_original_materials()
restore_world_nodes()
delete_temp_materials()

print(f"✅ Render complete.\n🖼️ Output saved to: {OUTPUT_PATH}\n🧹 Cleaned up temporary data.")
