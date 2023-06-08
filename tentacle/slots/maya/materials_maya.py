# !/usr/bin/python
# coding=utf-8
try:
    import pymel.core as pm
except ImportError as error:
    print(__file__, error)
import pythontk as ptk
import mayatk as mtk
from tentacle.slots.maya import SlotsMaya


class Materials_maya(SlotsMaya):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.randomMat = None

    def draggableHeader_init(self, widget):
        """ """
        widget.ctx_menu.add(
            self.sb.Label,
            setText="Material Attributes",
            setObjectName="lbl004",
            setToolTip="Show the material attributes in the attribute editor.",
        )
        self.sb.materials_submenu.b003.setVisible(False)

    def cmb002_init(self, widget):
        """ """
        widget.clear()
        widget.is_initialized = False
        widget.option_menu.add(
            "QComboBox",
            setObjectName="cmb001",
            addItems=["Scene Materials", "ID Map Materials", "Favorite Materials"],
            setToolTip="Filter materials list based on type.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setText="Open in Editor",
            setObjectName="lbl000",
            setToolTip="Open material in editor.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setText="Rename",
            setObjectName="lbl001",
            setToolTip="Rename the current material.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setText="Delete",
            setObjectName="lbl002",
            setToolTip="Delete the current material.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setText="Delete All Unused Materials",
            setObjectName="lbl003",
            setToolTip="Delete All unused materials.",
        )
        widget.returnPressed.connect(lambda: self.lbl001(setEditable=False))
        # set the popup title to be the current materials name.
        widget.currentIndexChanged.connect(
            lambda: widget.option_menu.setTitle(widget.currentText())
        )
        # set the groupbox title to reflect the current filter.
        widget.option_menu.cmb001.currentIndexChanged.connect(
            lambda: self.sb.materials.group000.setTitle(
                widget.option_menu.cmb001.currentText()
            )
        )
        # refresh cmb002 contents.
        widget.option_menu.cmb001.currentIndexChanged.connect(self.cmb002)
        # initialize the materials list
        self.cmb002_init(widget.ui.cmb002)

    def tb000_init(self, widget):
        """ """
        widget.option_menu.add(
            "QCheckBox",
            setText="All Objects",
            setObjectName="chk003",
            setToolTip="Search all scene objects, or only those currently selected.",
        )
        widget.option_menu.add(
            "QCheckBox",
            setText="Shell",
            setObjectName="chk005",
            setToolTip="Select entire shell.",
        )
        widget.option_menu.add(
            "QCheckBox",
            setText="Invert",
            setObjectName="chk006",
            setToolTip="Invert Selection.",
        )

    def tb002_init(self, widget):
        """ """
        widget.option_menu.add(
            "QRadioButton",
            setText="Current Material",
            setObjectName="chk007",
            setChecked=True,
            setToolTip="Re-Assign the current stored material.",
        )
        widget.option_menu.add(
            "QRadioButton",
            setText="New Material",
            setObjectName="chk009",
            setToolTip="Assign a new material.",
        )
        widget.option_menu.add(
            "QRadioButton",
            setText="New Random Material",
            setObjectName="chk008",
            setToolTip="Assign a new random ID material.",
        )
        widget.option_menu.chk007.clicked.connect(
            lambda state: widget.setText("Assign Current")
        )
        widget.option_menu.chk009.clicked.connect(
            lambda state: widget.setText("Assign New")
        )
        widget.option_menu.chk008.clicked.connect(
            lambda state: widget.setText("Assign Random")
        )

    def cmb002(self, index, widget):
        """Material list

        Parameters:
                index (int): parameter on activated, currentIndexChanged, and highlighted signals.
        """
        b = self.sb.materials_submenu.b003

        mode = widget.option_menu.cmb001.currentText()
        if mode == "Scene Materials":
            materials = self.getSceneMaterials(exc="standardSurface")

        elif mode == "ID Map Materials":
            materials = self.getSceneMaterials(inc="ID_*")

        if mode == "Favorite Materials":
            fav_materials = self.getFavoriteMaterials()
            currentMats = {
                matName: matName for matName in sorted(list(set(fav_materials)))
            }
        else:
            currentMats = {
                mat.name(): mat
                for mat in sorted(list(set(materials)))
                if hasattr(mat, "name")
            }

        widget.addItems_(currentMats, clear=True)

        # create and set icons with color swatch
        for i, mat in enumerate(widget.items):
            icon = self.getColorSwatchIcon(mat)
            widget.setItemIcon(i, icon) if icon else None

        # set submenu assign material button attributes
        b.setText("Assign " + widget.currentText())
        icon = self.getColorSwatchIcon(widget.currentText(), [15, 15])
        b.setIcon(icon) if icon else None
        b.setMinimumWidth(b.minimumSizeHint().width() + 25)
        b.setVisible(True if widget.currentText() else False)

    def tb000(self, widget):
        """Select By Material Id"""
        mat = self.sb.materials.cmb002.currentData()
        if not mat:
            self.sb.message_box("No Material Selection.")
            return

        shell = widget.option_menu.chk005.isChecked()  # Select by material: shell
        invert = widget.option_menu.chk006.isChecked()  # Select by material: invert
        allObjects = widget.option_menu.chk003.isChecked()  # Search all scene objects

        objects = pm.ls(sl=1, objectsOnly=1) if not allObjects else None

        self.selectByMaterialID(mat, objects, shell=shell, invert=invert)

    def tb002(self, widget):
        """Assign Material"""
        selection = pm.ls(sl=True, flatten=1)
        if not selection:
            self.sb.message_box("No renderable object is selected for assignment.")
            return

        assignCurrent = widget.option_menu.chk007.isChecked()
        assignRandom = widget.option_menu.chk008.isChecked()
        assignNew = widget.option_menu.chk009.isChecked()

        if assignCurrent:  # Assign current mat
            mat = self.sb.materials.cmb002.currentData()
            if isinstance(mat, str):  # new mat type as a string:
                self.assignMaterial(selection, pm.createNode(mat))
            else:  # existing mat object:
                self.assignMaterial(selection, mat)

        elif assignRandom:  # Assign New random mat ID
            mat = self.createRandomMaterial(prefix="ID_")
            self.assignMaterial(selection, mat)

            self.randomMat = mat

            self.cmb002_init(widget.ui.cmb002)  # refresh the materials list comboBox
            self.sb.materials.cmb002.setCurrentItem(
                mat.name()
            )  # set the combobox index to the new mat #self.cmb002.setCurrentIndex(self.cmb002.findText(name))

        elif assignNew:  # Assign New Material
            pm.mel.buildObjectMenuItemsNow(
                "MainPane|viewPanes|modelPanel4|modelPanel4|modelPanel4|modelPanel4ObjectPop"
            )
            pm.mel.createAssignNewMaterialTreeLister("")

    def lbl000(self):
        """Open material in editor"""
        try:
            mat = self.sb.materials.cmb002.currentData()  # get the mat obj from cmb002
            pm.select(mat)
        except Exception:
            self.sb.message_box("No stored material or no valid object selected.")
            return

        pm.mel.HypershadeWindow()  # open the hypershade editor

    def lbl001(self, setEditable=True):
        """Rename Material: Set cmb002 as editable and disable wgts."""
        cmb = self.sb.materials.cmb002

        if setEditable:
            self._mat = self.sb.materials.cmb002.currentData()
            cmb.setEditable(True)
            self.sb.toggle_widgets(
                self.sb.materials, setDisabled="b002,lbl000,tb000,tb002"
            )
        else:
            mat = self._mat
            newMatName = cmb.currentText()
            self.renameMaterial(mat, newMatName)
            cmb.setEditable(False)
            self.sb.toggle_widgets(
                self.sb.materials, setEnabled="b002,lbl000,tb000,tb002"
            )

    def lbl002(self):
        """Delete Material"""
        mat = self.sb.materials.cmb002.currentData()
        mat = pm.delete(mat)

        index = self.sb.materials.cmb002.currentIndex()
        self.sb.materials.cmb002.setItemText(
            index, "None"
        )  # self.sb.materials.cmb002.removeItem(index)

    def lbl003(self, widget):
        """Delete Unused Materials"""
        pm.mel.hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")
        self.cmb002_init(widget.ui.cmb002)  # refresh the materials list comboBox

    def lbl004(self):
        """Material Attributes: Show Material Attributes in the Attribute Editor."""
        mat = self.sb.materials.cmb002.currentData()
        try:
            pm.mel.showSG(mat.name())
        except Exception as error:
            print(error)

    def b000(self, *args, **kwargs):
        """Material List: Delete"""
        self.lbl002()

    def b001(self, *args, **kwargs):
        """Material List: Edit"""
        self.lbl000()

    def b002(self, widget):
        """Set Material: Set the currently selected material as the current material."""
        selection = pm.ls(sl=True)
        if not selection:
            self.sb.message_box("Nothing selected.")
            return

        mat = self.getMaterial()
        # set the combobox to show all scene materials
        self.sb.materials.cmb002.option_menu.cmb001.setCurrentIndex(0)
        self.cmb002_init(widget.ui.cmb002)  # refresh the materials list comboBox
        self.sb.materials.cmb002.setCurrentItem(mat.name())

    def b003(self, widget):
        """Assign: Assign Current"""
        self.sb.materials.tb002.option_menu.chk007.setChecked(True)
        self.sb.materials.tb002.setText("Assign Current")
        self.tb002_init(widget.ui.tb002)

    def b004(self, widget):
        """Assign: Assign Random"""
        self.sb.materials.tb002.option_menu.chk008.setChecked(True)
        self.sb.materials.tb002.setText("Assign Random")
        self.tb002_init(widget.ui.tb002)

    def b005(self, widget):
        """Assign: Assign New"""
        self.sb.materials.tb002.option_menu.chk009.setChecked(True)
        self.sb.materials.tb002.setText("Assign New")
        self.tb002_init(widget.ui.tb002)

    def getColorSwatchIcon(self, mat, size=[20, 20]):
        """Get an icon with a color fill matching the given materials RBG value.

        Parameters:
                mat (obj)(str): The material or the material's name.
                size (list): Desired icon size.

        Returns:
                (obj) pixmap icon.
        """
        from PySide2.Gui import QPixmap, QColor, QIcon

        try:
            # get the string name if a mat object is given.
            matName = mat.name() if not isinstance(mat, (str)) else mat
            # convert from 0-1 to 0-255 value and then to an integer
            r = int(pm.getAttr(matName + ".colorR") * 255)
            g = int(pm.getAttr(matName + ".colorG") * 255)
            b = int(pm.getAttr(matName + ".colorB") * 255)
            pixmap = QPixmap(size[0], size[1])
            pixmap.fill(QColor.fromRgb(r, g, b))

            return QIcon(pixmap)

        except Exception:
            pass

    def renameMaterial(self, mat, newMatName):
        """Rename material"""
        cmb = self.sb.materials.cmb002  # scene materials

        curMatName = mat.name()
        if curMatName != newMatName:
            cmb.setItemText(cmb.currentIndex(), newMatName)
            try:
                print(curMatName, newMatName)
                pm.rename(curMatName, newMatName)

            except RuntimeError as error:
                cmb.setItemText(cmb.currentIndex(), str(error).strip("\n"))

    def selectByMaterialID(
        self, material=None, objects=None, shell=False, invert=False
    ):
        """Select by material Id

        material (obj): The material to search and select for.
        objects (list): Faces or mesh objects as a list. If no objects are given, all geometry in the scene will be searched.
        shell (bool): Select the entire shell.
        invert (bool): Invert the final selection.R

        #ex call:
        selectByMaterialID(material)
        """
        if pm.nodeType(material) == "VRayMultiSubTex":  # if not a multimaterial
            self.sb.message_box("If material is a multimaterial, select a submaterial.")
            return

        if not material:
            if not pm.ls(sl=1):
                self.sb.message_box(
                    "Nothing selected. Select an object face, or choose the option: current material."
                )
                return
            material = self.getMaterial()

        pm.select(material)
        pm.hyperShade(
            objects=""
        )  # select all with material. "" defaults to currently selected materials.

        if objects:
            [
                pm.select(i, deselect=1)
                for i in pm.ls(sl=1)
                if i.split(".")[0] not in objects
            ]

        faces = pm.filterExpand(selectionMask=34, expand=1)
        transforms = pm.listRelatives(
            faces, p=True
        )  # [node.replace('Shape','') for node in pm.ls(sl=1, objectsOnly=1, visible=1)] #get transform node name from shape node

        if shell or invert:  # deselect so that the selection can be modified.
            pm.select(faces, deselect=1)

        if shell:
            for shell in transforms:
                pm.select(shell, add=1)

        if invert:
            for shell in transforms:
                allFaces = [
                    shell + ".f[" + str(num) + "]"
                    for num in range(pm.polyEvaluate(shell, face=1))
                ]  # create a list of all faces per shell
                pm.select(
                    list(set(allFaces) - set(faces)), add=1
                )  # get inverse of previously selected faces from allFaces

    def getSceneMaterials(self, inc=[], exc=[]):
        """Get all materials from the current scene.

        Parameters:
                inc (str)(int)(obj/list): The objects(s) to include.
                                supports using the '*' operator: startswith*, *endswith, *contains*
                                Will include all items that satisfy ANY of the given search terms.
                                meaning: '*.png' and '*Normal*' returns all strings ending in '.png' AND all
                                strings containing 'Normal'. NOT strings satisfying both terms.
                exc (str)(int)(obj/list): The objects(s) to exclude. Similar to include.
                                exlude take precidence over include.
        Returns:
                (list) materials.
        """
        matList = pm.ls(mat=1, flatten=1)

        # convert to dictionary to filter material names and types.
        d = {m.name(): pm.nodeType(m) for m in matList}
        filtered = ptk.Iter.filter_dict(d, inc, exc, keys=True, values=True)

        # use the filtered results to reconstruct a filtered list of actual materials.
        return [m for m in matList if m.name() in filtered]

    def getFavoriteMaterials(self):
        """Get Maya favorite materials list.

        Returns:
                (list) materials.
        """
        import maya.app.general.tlfavorites as _fav, os.path

        path = os.path.expandvars(
            r"%USERPROFILE%/Documents/maya/2022/prefs/renderNodeTypeFavorites"
        )
        renderNodeTypeFavorites = _fav.readFavorites(path)
        materials = [i for i in renderNodeTypeFavorites if "/" not in i]
        del _fav

        return materials

    def getMaterial(self, obj=""):
        """Get the material from the selected face.

        Parameters:
                (str/obj): The obj with the material.

        Returns:
                (list) material
        """
        pm.hyperShade(
            obj, shaderNetworksSelectMaterialNodes=1
        )  # selects the material node
        mats = pm.ls(sl=True, materials=1)  # now add the selected node to a variable

        return mats[0]

    def createRandomMaterial(self, name="", prefix=""):
        """Creates a random material.

        Parameters:
                name (str): material name.
                prefix (str): Optional string to be appended to the beginning of the name.

        Returns:
                (obj) material.
        """
        import random

        rgb = [
            random.randint(0, 255) for _ in range(3)
        ]  # generate a list containing 3 values between 0-255

        name = "{}{}_{}_{}_{}".format(
            prefix, name, str(rgb[0]), str(rgb[1]), str(rgb[2])
        )

        # create shader
        mat = pm.shadingNode("lambert", asShader=1, name=name)
        # convert RGB to 0-1 values and assign to shader
        convertedRGB = [round(float(v) / 255, 3) for v in rgb]
        pm.setAttr(name + ".color", convertedRGB)
        # assign to selected geometry
        # pm.select(selection) #initial selection is lost upon node creation
        # pm.hyperShade(assign=mat)

        return mat

    @mtk.undo
    def assignMaterial(self, objects, mat):
        """Assign material

        objects (list): Faces or mesh objects as a list.
        material (obj): The material to search and select for.
        """
        if not mat:
            self.sb.message_box("Material Not Assigned. No material given.")
            return

        try:  # if the mat is a not a known type; try and create the material.
            pm.nodeType(mat)
        except Exception:
            mat = pm.shadingNode(mat, asShader=1)

        # pm.undoInfo(openChunk=1)
        for obj in pm.ls(objects):
            pm.select(obj)  # hyperShade works more reliably with an explicit selection.
            pm.hyperShade(obj, assign=mat)
        # pm.undoInfo(closeChunk=1)


# module name
print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------

# depricated


# @property
# def currentMat(self):
#   '''Get the current material using the current index of the materials combobox.
#   '''
#   text = self.sb.materials.cmb002.currentText()

#   try:
#       result = self.currentMats[text]
#   except:
#       result = None

#   return result

# elif storedMaterial:
#   mat = self.currentMat
#   if not mat:
#       cmb.addItems_(['Stored Material: None'])
#       return

#   matName = mat.name()

#   if pm.nodeType(mat)=='VRayMultiSubTex':
#       subMaterials = pm.hyperShade(mat, listUpstreamShaderNodes=1) #get any connected submaterials
#       subMatNames = [s.name() for s in subMaterials if s is not None]
#   else:
#       subMatNames=[]

#   contents = cmb.addItems_(subMatNames, matName)

#   if index is None:
#       index = cmb.currentIndex()
#   if index!=0:
#       self.currentMat = subMaterials[index-1]
#   else:
#       self.currentMat = mat

# def cmb000(self, *args, **kwargs):
#   '''
#   Existing Materials

#   '''
#   cmb = self.sb.materials.draggableHeader.ctx_menu.cmb000

#   mats = [m for m in pm.ls(materials=1)]
#   matNames = [m.name() for m in mats]

#   contents = cmb.addItems_(matNames, "Scene Materials")

#   if index is None:
#       index = cmb.currentIndex()
#   if index!=0:
#       print contents[index]

#       self.currentMat = mats[index-1] #store material
#       self.cmb002() #refresh combobox

#       cmb.setCurrentIndex(0)


# assign random
# pm.mel.eval('''
#       string $selection[] = `ls -selection`;

#       int $d = 2; //decimal places to round to
#       $r = rand (0,1);
#       $r = trunc($r*`pow 10 $d`+0.5)/`pow 10 $d`;
#       $g = rand (0,1);
#       $g = trunc($g*`pow 10 $d`+0.5)/`pow 10 $d`;
#       $b = rand (0,1);
#       $b = trunc($b*`pow 10 $d`+0.5)/`pow 10 $d`;

#       string $rgb = ("_"+$r+"_"+$g+"_"+$b);
#       $rgb = substituteAllString($rgb, "0.", "");

#       $name = ("ID_"+$rgb);

#       string $ID_ = `shadingNode -asShader lambert -name $name`;
#       setAttr ($name + ".colorR") $r;
#       setAttr ($name + ".colorG") $g;
#       setAttr ($name + ".colorB") $b;

#       for ($object in $selection)
#           {
#           select $object;
#           hyperShade -assign $ID_;
#           }
#        ''')

# re-assign random
# pm.mel.eval('''
# string $objList[] = `ls -selection -flatten`;
# $material = `hyperShade -shaderNetworksSelectMaterialNodes ""`;
# string $matList[] = `ls -selection -flatten`;

# hyperShade -objects $material;
# string $selection[] = `ls -selection`;
# //delete the old material and shader group nodes
# for($i=0; $i<size($matList); $i++)
#   {
#   string $matSGplug[] = `connectionInfo -dfs ($matList[$i] + ".outColor")`;
#   $SGList[$i] = `match "^[^\.]*" $matSGplug[0]`;
#   print $matList; print $SGList;
#   delete $matList[$i];
#   delete $SGList[$i];
#   }
# //create new random material
# int $d = 2; //decimal places to round to
# $r = rand (0,1);
# $r = trunc($r*`pow 10 $d`+0.5)/`pow 10 $d`;
# $g = rand (0,1);
# $g = trunc($g*`pow 10 $d`+0.5)/`pow 10 $d`;
# $b = rand (0,1);
# $b = trunc($b*`pow 10 $d`+0.5)/`pow 10 $d`;

# string $rgb = ("_"+$r+"_"+$g+"_"+$b+"");
# $rgb = substituteAllString($rgb, "0.", "");

# $name = ("ID_"+$rgb);

# string $ID_ = `shadingNode -asShader lambert -name $name`;
# setAttr ($name + ".colorR") $r;
# setAttr ($name + ".colorG") $g;
# setAttr ($name + ".colorB") $b;

# for ($object in $selection)
#   {
#   select $object;
#   hyperShade -assign $ID_;
#   }
# ''')
