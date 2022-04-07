bl_info = {
    "name": "Kaedim 3D Artist Utilities",
    "author": "Chris Kinch - Kaedim",
    "version": (1, 4),
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

class Settings(PropertyGroup):
    obj_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .obj",
        default= False)
    fbx_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .fbx",
        default= False)
    glb_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as .glb",
        default= False)
    gltf_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Export as glTF",
        default= False)
    embed_textures_bool: BoolProperty(
        name= "Enable or Disable",
        description= "Set Path Mode to 'Copy' and embed textures in fbx binary file",
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
                        use_selection=True, path_mode='COPY', embed_textures=True
                        )
                else:
                    bpy.ops.export_scene.fbx(
                        filepath=os.path.join(folder_path, context.active_object.name + ".fbx"),
                        use_selection=True, path_mode='AUTO', embed_textures=False
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
        row.label(text = "FBX Embed Texture:", icon= "TEXTURE")
        row = layout.row()
        row.prop(mytool, "embed_textures_bool", text="Embed")
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

classes = (Settings, ImportPanel, ExportPanel, ImportFunction, ExportFunction)
     
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.my_tool = PointerProperty(type= Settings)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.my_tool
    
if __name__ == "__main__":
    register()


