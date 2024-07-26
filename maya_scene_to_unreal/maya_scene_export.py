import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


# UNSUPPORTED_NODE_TYPES = ['nurbsSurface', 'nurbsCurve', 'nurbsSurface', 'nurbsCurve', 'hairSystem', 'fluidShape',
#                           'particle', 'cluster', 'lattice', 'blendShape', 'rigidBody', 'softBody',
#                           'aiStandardSurface', 'lambert', 'shadingNode', 'subdSurface', 'deformer',
#                           'shadingNetwork', 'volume', 'bifrost', 'nCloth', 'nParticle', 'surfaceShader', 'fluid']

class UnrealExporter(QtWidgets.QWidget):
    UNSUPPORTED_NODE_TYPES = ['nurbsSurface', 'nurbsCurve', 'lattice', 'cluster', 'particle',
                              'nCloth', 'particle', 'blendShape']

    def __init__(self, parent=None):
        super(UnrealExporter, self).__init__(parent)
        self.setWindowTitle("Unreal Exporter")
        self.setGeometry(300, 300, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.export_path_label = QtWidgets.QLabel("Export Path:")
        self.export_path_field = QtWidgets.QLineEdit()
        self.export_path_field.setText("C:/path/to/your/output.fbx")
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_path)

        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.export_path_field)
        path_layout.addWidget(self.browse_button)

        layout.addWidget(self.export_path_label)
        layout.addLayout(path_layout)

        self.mesh_checkbox = QtWidgets.QCheckBox("Export Meshes")
        self.anim_checkbox = QtWidgets.QCheckBox("Export Animation Curves")
        self.skel_checkbox = QtWidgets.QCheckBox("Export Skeletons")
        self.cameras_checkbox = QtWidgets.QCheckBox("Export Cameras")
        self.lights_checkbox = QtWidgets.QCheckBox("Export Lights")
        self.materials_checkbox = QtWidgets.QCheckBox("Export Materials")
        self.textures_checkbox = QtWidgets.QCheckBox("Export Textures")

        # Set all checkboxes to be checked by default
        for checkbox in [self.mesh_checkbox, self.anim_checkbox, self.skel_checkbox,
                         self.cameras_checkbox, self.lights_checkbox, self.materials_checkbox,
                         self.textures_checkbox]:
            checkbox.setChecked(True)

        for checkbox in [self.mesh_checkbox, self.anim_checkbox, self.skel_checkbox,
                         self.cameras_checkbox, self.lights_checkbox, self.materials_checkbox,
                         self.textures_checkbox]:
            layout.addWidget(checkbox)

        self.unsupported_list = QtWidgets.QListWidget()
        self.unsupported_list.setVisible(False)
        self.unsupported_list.itemDoubleClicked.connect(self.select_maya_object)
        layout.addWidget(self.unsupported_list)

        self.check_button = QtWidgets.QPushButton("Check Scene for Unreal")
        self.check_button.clicked.connect(self.run_qc_checks)
        layout.addWidget(self.check_button)

        self.export_button = QtWidgets.QPushButton("Export to FBX")
        self.export_button.clicked.connect(self.show_export_popup)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def browse_path(self):
        file_dialog = QtWidgets.QFileDialog(self, "Select Export Path", "", "FBX Files (*.fbx)")
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            if not file_path.endswith('.fbx'):
                file_path += '.fbx'
            self.export_path_field.setText(file_path)

    def check_scene_for_unreal(self):
        issues = []
        unsupported_nodes = cmds.ls(type=self.UNSUPPORTED_NODE_TYPES)
        if unsupported_nodes:
            issues.append(f"Unsupported node types found: {', '.join(unsupported_nodes)}")
        return unsupported_nodes

    def export_to_fbx(self, output_path):
        try:
            # Set the FBX export settings
            mel.eval('FBXExportSmoothingGroups -v true')
            mel.eval('FBXExportHardEdges -v false')
            mel.eval('FBXExportTangents -v false')
            mel.eval('FBXExportSmoothMesh -v true')
            mel.eval('FBXExportInstances -v false')
            mel.eval('FBXExportBakeComplexAnimation -v false')
            mel.eval('FBXExportConstraints -v false')
            mel.eval('FBXExportCameras -v true')
            mel.eval('FBXExportLights -v true')
            mel.eval('FBXExportEmbeddedTextures -v false')
            mel.eval('FBXExportInputConnections -v true')
            mel.eval('FBXExportUpAxis "y"')

            # Export the selection or the entire scene if nothing is selected
            export_types = []
            if self.mesh_checkbox.isChecked():
                export_types.append('mesh')
            if self.anim_checkbox.isChecked():
                export_types.append('animCurve')
            if self.skel_checkbox.isChecked():
                export_types.append('joint')
            if self.cameras_checkbox.isChecked():
                export_types.append('camera')
            if self.lights_checkbox.isChecked():
                export_types.append('light')
            if self.materials_checkbox.isChecked():
                export_types.append('shadingEngine')
            if self.textures_checkbox.isChecked():
                export_types.append('fileTexture')

            if export_types:
                cmds.select(clear=True)
                for etype in export_types:
                    cmds.select(cmds.ls(type=etype), add=True)

            # Export to FBX
            cmds.file(output_path, force=True, options="v=0", type="FBX export", pr=True, es=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export scene: {e}")

    def run_qc_checks(self):
        issues = self.check_scene_for_unreal()
        self.unsupported_list.clear()
        if issues:
            self.unsupported_list.setVisible(True)
            for issue in issues:
                item = QtWidgets.QListWidgetItem(issue)
                item.setForeground(QtGui.QColor("red"))
                self.unsupported_list.addItem(item)
            # QtWidgets.QMessageBox.warning(self, 'QC Issues Found', 'Unsupported objects found in the scene.')
        else:
            self.unsupported_list.setVisible(False)
            QtWidgets.QMessageBox.information(self, 'QC Passed', 'No issues found. Ready to export.')

    def select_maya_object(self, item):
        if cmds.objExists(item):
            cmds.select(item)
            cmds.viewFit(item)  # Fit the selected object in the view
        else:
            QtWidgets.QMessageBox.warning(self, "Selection Error",
                                          f"Object '{item}' does not exist in the scene.")

    def show_export_popup(self):
        export_path = self.export_path_field.text()
        issues = self.check_scene_for_unreal()

        if issues:
            self.unsupported_list.clear()
            self.unsupported_list.setVisible(True)
            for issue in issues:
                item = QtWidgets.QListWidgetItem(issue)
                item.setForeground(QtGui.QColor("red"))
                self.unsupported_list.addItem(item)

            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle('QC Issues Found')
            msg_box.setText('Unsupported objects found in the scene. Choose an option:')
            msg_box.addButton("Skip Unsupported", QtWidgets.QMessageBox.AcceptRole)
            msg_box.addButton("Export Anyway", QtWidgets.QMessageBox.AcceptRole)
            msg_box.addButton("Close", QtWidgets.QMessageBox.RejectRole)

            reply = msg_box.exec_()

            if reply == 0:  # "Skip Unsupported" button
                self.export_to_fbx(export_path)
                QtWidgets.QMessageBox.information(self, 'Export Successful',
                                                  f'Scene exported successfully to {export_path}')
            elif reply == 1:  # "Export Anyway" button
                self.export_to_fbx(export_path)
                QtWidgets.QMessageBox.information(self, 'Export Successful',
                                                  f'Scene exported successfully to {export_path}')
        else:
            self.unsupported_list.setVisible(False)
            self.export_to_fbx(export_path)
            QtWidgets.QMessageBox.information(self, 'Export Successful',
                                              f'Scene exported successfully to {export_path}')


def show_ui():
    maya_main_window = get_maya_main_window()
    global exporter
    try:
        exporter.close()
    except:
        pass
    exporter = UnrealExporter(parent=maya_main_window)
    exporter.setWindowFlags(QtCore.Qt.Window)
    exporter.show()


if __name__ == '__main__':
    show_ui()
