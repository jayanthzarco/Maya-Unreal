import unreal
from unreal import EditorAssetLibrary, AssetToolsHelpers, EditorUtilityLibrary


class FBXImporterUI:
    def __init__(self):
        self.import_options = {
            'import_mesh': True,
            'import_anim': True,
            'import_skel': True,
            'import_cameras': True,
            'import_lights': True,
            'import_materials': True,
            'import_textures': True,
        }

    def import_fbx(self, file_path, destination_path):
        # Create an import options object
        options = unreal.FbxImportOptions()
        options.import_mesh = self.import_options['import_mesh']
        options.import_animations = self.import_options['import_anim']
        options.import_skeleton = self.import_options['import_skel']
        options.import_cameras = self.import_options['import_cameras']
        options.import_lights = self.import_options['import_lights']
        options.import_materials = self.import_options['import_materials']
        options.import_textures = self.import_options['import_textures']

        # Create an import task
        task = unreal.AssetImportTask()
        task.filename = file_path
        task.destination_path = destination_path
        task.options = options
        task.automated = True

        # Run the import task
        asset_tools = AssetToolsHelpers.get_asset_tools()
        asset_tools.import_asset_tasks([task])

        # Sync browser to the imported assets
        EditorAssetLibrary.sync_browser_to_assets([task.imported_object_paths[0]])

        print(f'FBX file imported successfully from {file_path} to {destination_path}')

    def show_ui(self):
        # Prompt user for FBX file path
        file_dialog = unreal.EditorAssetLibrary.open_file_dialog("Select FBX File", "", "FBX Files (*.fbx)")
        if not file_dialog:
            print("No file selected.")
            return
        file_path = file_dialog[0]

        # Prompt user for destination path
        destination_dialog = unreal.EditorAssetLibrary.open_directory_dialog("Select Destination Path",
                                                                             "/Game/ImportedAssets")
        if not destination_dialog:
            print("No destination path selected.")
            return
        destination_path = destination_dialog[0]

        # Show options dialog
        self.import_options['import_mesh'] = EditorUtilityLibrary.show_yes_no_dialog("Import Meshes",
                                                                                     "Do you want to import meshes?")
        self.import_options['import_anim'] = EditorUtilityLibrary.show_yes_no_dialog("Import Animations",
                                                                                     "Do you want to import animations?")
        self.import_options['import_skel'] = EditorUtilityLibrary.show_yes_no_dialog("Import Skeletons",
                                                                                     "Do you want to import skeletons?")
        self.import_options['import_cameras'] = EditorUtilityLibrary.show_yes_no_dialog("Import Cameras",
                                                                                        "Do you want to import cameras?")
        self.import_options['import_lights'] = EditorUtilityLibrary.show_yes_no_dialog("Import Lights",
                                                                                       "Do you want to import lights?")
        self.import_options['import_materials'] = EditorUtilityLibrary.show_yes_no_dialog("Import Materials",
                                                                                          "Do you want to import materials?")
        self.import_options['import_textures'] = EditorUtilityLibrary.show_yes_no_dialog("Import Textures",
                                                                                         "Do you want to import textures?")

        # Import the FBX file with the selected options
        self.import_fbx(file_path, destination_path)


# Instantiate and run the UI
if __name__ == '__main__':
    importer_ui = FBXImporterUI()
    importer_ui.show_ui()
