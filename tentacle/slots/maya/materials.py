# !/usr/bin/python
# coding=utf-8
try:
    import pymel.core as pm
except ImportError as error:
    print(__file__, error)
import pythontk as ptk
import mayatk as mtk
from tentacle.slots.maya import SlotsMaya


class MaterialsSlots(SlotsMaya):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sb = kwargs.get("switchboard")
        self.ui = self.sb.loaded_ui.materials
        self.submenu = self.sb.loaded_ui.materials_submenu

        # Set a class attribute to track the last created random material
        self.last_random_material = None

    def header_init(self, widget):
        """ """
        # Add a button to open the hypershade editor.
        widget.menu.add(
            "QPushButton",
            setToolTip="Open the Hypershade Window.",
            setText="Hypershade Editor",
            setObjectName="b007",
        )
        widget.menu.b007.clicked.connect(pm.mel.HypershadeWindow)
        # Add a button to launch stringray arnold shader.
        widget.menu.add(
            "QPushButton",
            setToolTip="Create a stingray material network that can optionally be rendered in Arnold.",
            setText="Create Stingray Shader",
            setObjectName="b009",
        )
        # Add a button to launch the Texture Path Editor.
        widget.menu.add(
            "QPushButton",
            setToolTip="Edit texture paths for materials in the scene.",
            setText="Texture Path Editor",
            setObjectName="b010",
        )
        # Add a button to launch map converter.
        widget.menu.add(
            "QPushButton",
            setToolTip="Convert existing texture maps to another type.",
            setText="Map Converter",
            setObjectName="b016",
        )
        widget.menu.add(
            "QPushButton",
            setText="Map Packer",
            setObjectName="b008",
            setToolTip="Pack up to 4 input grayscale maps into specified RGBA channels.",
        )

        widget.menu.add(
            "QPushButton",
            setText="Reload Textures",
            setObjectName="b013",
            setToolTip="Reload file textures for all scene materials.",
        )
        widget.menu.add(
            "QPushButton",
            setText="Remove Duplicate Materials",
            setObjectName="b014",
            setToolTip="Find duplicate materials, remove duplicates, and reassign them to the original material.",
        )
        widget.menu.add(
            "QPushButton",
            setText="Delete All Unused Materials",
            setObjectName="b015",
            setToolTip="Delete all unused materials.",
        )

    def cmb002_init(self, widget):
        """ """
        print("cmb002_init", widget)
        if not widget.is_initialized:
            widget.refresh_on_show = True  # Call this method on show
            widget.editable = True
            widget.menu.mode = "context"
            widget.menu.setTitle("Material Options")
            widget.menu.add(
                self.sb.registered_widgets.Label,
                setText="Rename",
                setObjectName="lbl005",
                setToolTip="Rename the current material.",
            )
            widget.menu.add(
                self.sb.registered_widgets.Label,
                setText="Delete",
                setObjectName="lbl002",
                setToolTip="Delete the current material.",
            )
            widget.menu.add(
                self.sb.registered_widgets.Label,
                setText="Select Node",
                setObjectName="lbl004",
                setToolTip="Select the material node and show its attributes in the attribute editor.",
            )
            widget.menu.add(
                self.sb.registered_widgets.Label,
                setText="Open in Editor",
                setObjectName="lbl006",
                setToolTip="Open the material in the hypershade editor.",
            )
            # Rename the material after editing has finished.
            widget.on_editing_finished.connect(
                lambda text: pm.rename(widget.currentData(), text)
            )
            # Initialize the widget every time before the popup is shown.
            widget.before_popup_shown.connect(widget.init_slot)
            # Update the assign button with the new material name.
            widget.on_editing_finished.connect(self.submenu.b005.init_slot)
            # Add the current material name to the assign button.
            widget.currentIndexChanged.connect(self.submenu.b005.init_slot)

        # Use 'restore_index=True' to save and restore the index
        materials_dict = mtk.get_scene_mats(
            exc="standardSurface", sort=True, as_dict=True
        )
        widget.add(materials_dict, clear=True, restore_index=True)

        # Create and set icons with color swatch
        for i, mat in enumerate(widget.items):
            icon = mtk.get_mat_swatch_icon(mat)
            if icon:
                widget.setItemIcon(i, icon)

    def tb000_init(self, widget):
        """ """
        widget.menu.add(
            "QCheckBox",
            setText="Shell",
            setObjectName="chk005",
            setToolTip="Select object(s) containing the material.",
        )

    def tb000(self, widget):
        """Select By Material"""
        mat = self.ui.cmb002.currentData()
        if not mat:
            return

        shell = widget.menu.chk005.isChecked()  # Select by material: shell

        selection = pm.ls(sl=True, objectsOnly=True)
        faces_with_mat = mtk.find_by_mat_id(mat, selection, shell=shell)

        pm.select(faces_with_mat)

    def lbl002(self):
        """Delete Material"""
        mat = self.ui.cmb002.currentData()  # get the mat obj from cmb002
        mat = pm.delete(mat)
        self.ui.cmb002.init_slot()  # refresh the materials list comboBox

    def b015(self, widget):
        """Delete Unused Materials"""
        pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")
        self.ui.cmb002.init_slot()  # refresh the materials list comboBox

    def lbl004(self):
        """Select and Show Attributes: Show Material Attributes in the Attribute Editor."""
        mat = self.ui.cmb002.currentData()  # get the mat obj from cmb002
        pm.select(mat, replace=True)
        pm.mel.eval(f'showEditorExact("{mat}")')

    def lbl005(self):
        """Set the current combo box text as editable."""
        self.ui.cmb002.setEditable(True)
        self.ui.cmb002.menu.hide()

    def lbl006(self):
        """Open material in editor"""
        try:
            mat = self.ui.cmb002.currentData()
            pm.select(mat)
        except Exception:
            self.sb.message_box("No stored material or no valid object selected.")
            return

        # # Open the Hypershade window
        print("Opening the Hypershade window ..", pm.mel.HypershadeWindow())

        # Define the deferred command to graph the material
        def graph_material():
            # graphMaterials, addSelected, showUpstream, showDownstream, showUpAndDownstream
            pm.mel.hyperShadePanelGraphCommand(
                "hyperShadePanel1", "showUpAndDownstream"
            )

        # Execute the graph command after the Hypershade window is fully initialized
        self.sb.defer_with_timer(graph_material, ms=500)

    def b002(self, widget):
        """Get Material: Change the index to match the current material selection."""
        selection = pm.ls(sl=True)
        if not selection:
            self.sb.message_box(
                "<hl>Nothing selected</hl><br>Select mesh object(s) or face(s)."
            )
            return

        mat = mtk.get_mats(selection[0])
        if len(mat) != 1:
            self.sb.message_box(
                "<hl>Invalid selection</hl><br>Selection must have exactly one material assigned."
            )
            return

        self.ui.cmb002.init_slot()  # refresh the materials list comboBox
        self.ui.cmb002.setAsCurrent(mat.pop().name())  # pop: mat is a set

    def b004(self, widget):
        """Assign: Assign Random"""
        selection = pm.ls(sl=True, flatten=True)
        if not selection:
            self.sb.message_box("No renderable object is selected for assignment.")
            return

        # Create and assign a new random material
        new_mat = mtk.create_mat("random")
        mtk.assign_mat(selection, new_mat)

        # Check and delete the last random material if it's no longer in use
        if self.last_random_material and self.last_random_material != new_mat:
            # Check all shading engines connected to the last random material
            shading_engines = pm.listConnections(
                self.last_random_material, type="shadingEngine"
            )

            # Iterate through each shading engine to check if any geometry is connected
            is_in_use = False
            for se in shading_engines:
                if pm.listConnections(se, type="mesh"):
                    is_in_use = True
                    break

            # If the last random material is not in use, delete it
            if not is_in_use:
                pm.delete(self.last_random_material)

        # Update the last random material with the newly created one
        self.last_random_material = new_mat

        # Refresh the UI
        self.ui.cmb002.init_slot()
        self.ui.cmb002.setAsCurrent(new_mat.name())

        # Reselect the original selection so that this method can be called again if needed.
        pm.select(selection)

    def b005_init(self, widget):
        """ """
        if not widget.is_initialized:
            widget.refresh_on_show = True  # Call this method on show
            self.ui.cmb002.init_slot()
            self.ui.cmb002.is_initialized = True

        current_material = self.ui.cmb002.currentData()
        text = f"Assign: {current_material}"
        submenu_widget = self.submenu.b005
        submenu_widget.setText(text)
        submenu_widget.setMinimumWidth(submenu_widget.minimumSizeHint().width() + 25)
        if current_material:
            icon = mtk.get_mat_swatch_icon(current_material, [15, 15])
            if icon is not None:
                submenu_widget.setIcon(icon)

    def b005(self, widget):
        """Assign: Assign Current"""
        selection = pm.ls(sl=True, flatten=1)
        if not selection:
            self.sb.message_box("No renderable object is selected for assignment.")
            return

        mat = self.ui.cmb002.currentData()
        mtk.assign_mat(selection, mat)

    def b006(self, widget):
        """Assign: New Material"""
        renderable_objects = pm.ls(sl=True, type="mesh", dag=True, geometry=True)
        if not renderable_objects:
            self.sb.message_box("No renderable object is selected for assignment.")
            return
        pm.mel.eval(
            'buildObjectMenuItemsNow "MainPane|viewPanes|modelPanel4|modelPanel4|modelPanel4|modelPanel4ObjectPop";'
        )
        pm.mel.createAssignNewMaterialTreeLister("")

    def b008(self, widget):
        """Map Packer"""
        from pythontk.img_utils import map_packer

        self.sb.register(
            "map_packer.ui",
            map_packer.MapPackerSlots,
            base_dir=map_packer,
        )

        ui = self.sb.get_ui("map_packer")
        ui.set_attributes(WA_TranslucentBackground=True)
        ui.set_flags(FramelessWindowHint=True)
        ui.style.set(theme="dark", style_class="translucentBgWithBorder")
        ui.header.config_buttons(menu_button=True, hide_button=True)

        # Set the starting directory for the map converter
        source_images_dir = mtk.get_env_info("sourceimages")
        ui.slots.source_dir = source_images_dir

        self.sb.parent().show(ui)

    def b009(self, widget):
        """Create Stingray Shader"""
        ui = mtk.UiManager.instance(self.sb).get("stingray_arnold_shader")
        self.sb.parent().show(ui)

    def b010(self, widget):
        """Texture Path Editor"""
        ui = mtk.UiManager.instance(self.sb).get("texture_path_editor")
        self.sb.parent().show(ui)

    def b013(self):
        """Reload Textures"""
        mtk.reload_textures()  # pm.mel.AEReloadAllTextures()
        confirmation_message = "<html><body><p style='font-size:16px; color:yellow;'>Textures are <strong>reloading ..</strong>.</p></body></html>"
        self.sb.message_box(confirmation_message)

    def b014(self):
        """Remove and Reassign Duplicates"""
        dups = mtk.find_materials_with_duplicate_textures()
        if dups:
            mtk.reassign_duplicate_materials(dups, delete=True)
            self.ui.cmb002.init_slot()

    def b016(self):
        """Map Converter"""
        from pythontk.img_utils import map_converter

        self.sb.register(
            "map_converter.ui",
            map_converter.MapConverterSlots,
            base_dir=map_converter,
        )

        ui = self.sb.get_ui("map_converter")
        ui.set_attributes(WA_TranslucentBackground=True)
        ui.set_flags(FramelessWindowHint=True)
        ui.style.set(theme="dark", style_class="translucentBgWithBorder")
        ui.header.config_buttons(menu_button=True, hide_button=True)

        # Set the starting directory for the map converter
        source_images_dir = mtk.get_env_info("sourceimages")
        ui.slots.source_dir = source_images_dir

        self.sb.parent().show(ui)


# --------------------------------------------------------------------------------------------

# module name
# print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
