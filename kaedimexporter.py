bl_info = {
    "name": "Kaedim 3D Artist Utilities",
    "author": "Kaedim",
    "version": (1, 4, 4),
    "blender": (3, 1, 0),
    "location": "View3D > Toolbar(N) > Kaedim Exporter",
    "description": "Tools to make.",
    "warning": "",
    "wiki_url": "",
    "category": "Export"
}

import bpy
import os
import glob
import os.path
from bpy.props import (StringProperty, BoolProperty, PointerProperty)
from bpy.types import (Panel, Operator, AddonPreferences, PropertyGroup)

def checkWatertight():
    watertight=False
    edit=False
    if bpy.context.active_object.mode != 'EDIT':
        edit=True
        bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=True)
    selectedEdges = [e for e in bpy.context.active_object.data.edges if e.select]
    print(len(selectedEdges))
    if(len(selectedEdges)>0):
        watertight=True
    if edit:
        bpy.ops.object.editmode_toggle()
    return watertight


class Settings(PropertyGroup):
    obj_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .obj",
        default= True)
    fbx_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .fbx",
        default= True)
    glb_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .glb",
        default= True)
    gltf_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as glTF",
        default= True)
    embed_textures_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Set Path Mode to 'Copy' and embed textures in fbx binary file",
        default= False)
    normals_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Automatically recalculates normals upon export",
        default= False)
    file_path: StringProperty(
        name="Export To",
        description="Export location",
        default="",
        maxlen=1024,
        subtype="FILE_PATH")
    import_file_path: StringProperty(
        name="Import From",
        description="Folder to look for reference image.",
        default="",
        maxlen=1024,
        subtype="FILE_PATH")

class ExportFunction(Operator):
    bl_idname = "object.export_operator"
    bl_label = "Simple Object Operator"
    
    def execute(self, context):
        files_to_export = []
        gltf_formats = []
        
        if len(bpy.context.selected_objects) <1:
            raise Exception("No objects selected for export. Please make a selection before clicking EXPORT.")
        
        print("-"*30)
        checkWatertight()
        if checkWatertight():
            bpy.context.space_data.overlay.show_face_orientation = True
            raise Exception("Not Watertight")

        print("-"*30)
        
        
        bpy.ops.object.editmode_toggle()
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.object.editmode_toggle()
        
        if context.scene.my_tool.normals_bool == True:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()

        if context.scene.my_tool.obj_bool == True:
            files_to_export.append("obj")
            
        if context.scene.my_tool.fbx_bool == True:
            files_to_export.append("fbx")

        if context.scene.my_tool.gltf_bool == True:
            files_to_export.append("gltf")
            gltf_formats.append("GLTF_EMBEDDED")

        if context.scene.my_tool.glb_bool == True:
            if "gltf" not in files_to_export:
                files_to_export.append("gltf")
            gltf_formats.append("GLB")
        
        path = context.scene.my_tool.file_path
        folder_path = bpy.path.abspath(path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for type in files_to_export:
            if type == "obj":
                bpy.ops.export_scene.obj(
                    filepath=os.path.join(folder_path, context.active_object.name + ".obj"),
                    use_selection=True
                    )
            elif type == "fbx":
                if context.scene.my_tool.embed_textures_bool == True:
                    bpy.ops.export_scene.fbx(
                        filepath=os.path.join(folder_path, context.active_object.name + ".fbx"),
                        use_selection=True, path_mode='COPY', embed_textures=True, global_scale=0.01,
                        )
                else:
                    bpy.ops.export_scene.fbx(
                        filepath=os.path.join(folder_path, context.active_object.name + ".fbx"),
                        use_selection=True, path_mode='AUTO', embed_textures=False, global_scale=0.01,
                        )
            else:
                for format in gltf_formats:
                    bpy.ops.export_scene.gltf(
                        filepath=os.path.join(folder_path, context.active_object.name + ".gltf"),
                        use_selection=True,
                        export_format = format
                        )
        return {'FINISHED'}

class ImportFunction(Operator):
    bl_idname = "object.import_operator"
    bl_label = "Imports Reference Image"

    def execute(self, context):
        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                bpy.ops.view3d.view_axis(override, type='FRONT')
                break
    
        path = context.scene.my_tool.import_file_path
        folder_path = bpy.path.abspath(path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        types = ('*jpg', '*jpeg', '*png') # the tuple of file types
        files = []
        for type in types:
            files.extend(glob.glob(folder_path + type))
            
        max_file = max(files, key=os.path.getctime)
        bpy.ops.object.load_reference_image(filepath=max_file)

        return {'FINISHED'}

class ExportPanel(bpy.types.Panel):
    bl_label = "Exporter"
    bl_idname = "PT_TestPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Kaedim Export"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        row = layout.row()
        row.label(text = "Extras:", icon= "TEXTURE")
        row = layout.row()
        row.prop(mytool, "embed_textures_bool", text="Embed FBX Texture")
        row = layout.row()
        row.prop(mytool, "normals_bool", text="Recalculate Normals")
        row = layout.row()
        row.label(text = "Select file types:", icon= "CHECKMARK")
        row = layout.row()
        row.prop(mytool, "obj_bool", text=".obj")
        row.prop(mytool, "fbx_bool", text=".fbx")
        row = layout.row()
        row.prop(mytool, "glb_bool", text=".glb")
        row.prop(mytool, "gltf_bool", text=".glTF")
        row = layout.row()
        row.label(text = "Specify file path:", icon= "FILEBROWSER")
        row = layout.row()
        row.prop(mytool, "file_path")
        row = layout.row()
        row.operator(ExportFunction.bl_idname, text="EXPORT", icon="CONSOLE")
        
class ImportPanel(bpy.types.Panel):
    bl_label = "Reference Import"
    bl_idname = "Ref_Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Kaedim Export"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        row = layout.row()
        row.label(text = "Specify file path:", icon= "FILEBROWSER")
        row = layout.row()
        row.prop(mytool, "import_file_path")
        row = layout.row()
        row.operator(ImportFunction.bl_idname, text="IMPORT", icon="CONSOLE")

class WaterTightPanel(bpy.types.Panel):
    bl_label = "water tight"
    bl_idname = "water tight_id"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Kaedim Export'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Water tight ", icon="OUTLINER_OB_FORCE_FIELD")
        row = layout.row()


        row.operator('watertight.operator', text="fill gaps")
        row = layout.row()

class Watertight(bpy.types.Operator):
    bl_label = "l1"
    bl_idname = 'watertight.operator'

    def execute(self, context):

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_interior_faces()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True,        use_multi_face=False,                  use_non_contiguous=False, use_verts=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.fill_holes(sides=0)
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False,       use_multi_face=False,                  use_non_contiguous=False, use_verts=True)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.fill_holes(sides=0)
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False,       use_multi_face=False,                  use_non_contiguous=False, use_verts=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.fill_holes(sides=0)
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False,       use_multi_face=False,                  use_non_contiguous=False, use_verts=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.print3d_clean_non_manifold()
       
        return {'FINISHED'}


class deimate_panel(bpy.types.Panel):
    bl_label = "Quick Decimater"
    bl_idname = "decimate_id"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Kaedim Export'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Quick decimate", icon="SEQ_HISTOGRAM")
        row = layout.row()


        row.operator('deci.operator_1', text="Decimate 50%")
        row = layout.row()
        row.operator('deci.operator_2', text="Decimate 65%")
        row = layout.row()
        row.operator('deci.operator_3', text="Decimate 80%")
        row = layout.row()
        row.operator('deci.apply', text="Apply")
        row.operator('deci.clear', text="Clear")


# operator for level 1 decimation
class level1(bpy.types.Operator):
    bl_label = "l1"
    bl_idname = 'deci.operator_1'

    def execute(self, context):
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
        bpy.context.object.modifiers["Decimate"].iterations = 1

        return {'FINISHED'}


# operator for level 2 decimation
class level2(bpy.types.Operator):
    bl_label = "l2"
    bl_idname = 'deci.operator_2'

    def execute(self, context):
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
        bpy.context.object.modifiers["Decimate"].iterations = 2

        return {'FINISHED'}

# operator for level 2 decimation
class level3(bpy.types.Operator):
    bl_label = "l3"
    bl_idname = 'deci.operator_3'

    def execute(self, context):
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
        bpy.context.object.modifiers["Decimate"].iterations = 3

        return {'FINISHED'}

#apply mod operator
class apply(bpy.types.Operator):
    bl_label="apply"
    bl_idname='deci.apply'

    def execute(self,context):
        bpy.ops.object.apply_all_modifiers()


        return {'FINISHED'}

#clear mod operator
class clear(bpy.types.Operator):
    bl_label = "clear"
    bl_idname = 'deci.clear'

    def execute(self, context):
        bpy.ops.object.delete_all_modifiers()

        return {'FINISHED'}


classes = (Settings, ImportPanel, ExportPanel, ImportFunction, ExportFunction, WaterTightPanel, Watertight,deimate_panel,level1,level2,level3,apply,clear)
     
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.my_tool = PointerProperty(type= Settings)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.my_tool