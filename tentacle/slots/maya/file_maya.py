# !/usr/bin/python
# coding=utf-8
import os

try:
    import pymel.core as pm
except ImportError as error:
    print(__file__, error)
from pythontk import truncate
import pythontk as ptk
import mayatk as mtk
from uitk.switchboard import signals
from tentacle.slots.maya import SlotsMaya


class File_maya(SlotsMaya):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draggableHeader_init(self, widget):
        """ """
        cmb = widget.ctx_menu.add(
            self.sb.ComboBox, setObjectName="cmb000", setToolTip=""
        )
        items = []
        cmb.addItems_(items, "File Editors")

    def cmb002_init(self, widget):
        """ """
        # Get the current autosave state
        autoSaveState = pm.autoSave(q=True, enable=True)
        autoSaveInterval = pm.autoSave(q=True, int=True)
        autoSaveAmount = pm.autoSave(q=True, maxBackups=True)
        # open directory
        widget.option_menu.add(
            "QPushButton",
            setObjectName="b000",
            setText="Open Directory",
            setToolTip="Open the autosave directory.",
        )
        # delete all
        widget.option_menu.add(
            "QPushButton",
            setObjectName="b002",
            setText="Delete All",
            setToolTip="Delete all autosave files.",
        )
        # toggle autosave
        widget.option_menu.add(
            "QCheckBox",
            setText="Autosave",
            setObjectName="chk006",
            setChecked=autoSaveState,
            setToolTip="Set the autosave state as active or disabled.",
        )
        # autosave amount
        widget.option_menu.add(
            "QSpinBox",
            setPrefix="Amount: ",
            setObjectName="s000",
            set_limits="1-100 step1",
            setValue=autoSaveAmount,
            set_height=20,
            setToolTip="The number of autosave files to retain.",
        )
        # autosave interval
        widget.option_menu.add(
            "QSpinBox",
            setPrefix="Interval: ",
            setObjectName="s001",
            set_limits="1-60 step1",
            setValue=autoSaveInterval / 60,
            set_height=20,
            setToolTip="The autosave interval in minutes.",
        )
        widget.option_menu.chk006.toggled.connect(
            lambda s: pm.autoSave(enable=s, limitBackups=True)
        )
        widget.option_menu.s000.valueChanged.connect(
            lambda v: pm.autoSave(maxBackups=v, limitBackups=True)
        )
        widget.option_menu.s001.valueChanged.connect(
            lambda v: pm.autoSave(int=v * 60, limitBackups=True)
        )
        widget.addItems_(
            mtk.get_recent_autosave(format="timestamp|standard"),
            "Recent Autosave",
            clear=True,
        )

    def cmb003_init(self, widget):
        """ """
        widget.addItems_(
            [
                "Import file",
                "Import Options",
                "FBX Import Presets",
                "Obj Import Presets",
            ],
            "Import",
        )

    def cmb004_init(self, widget):
        """ """
        items = [
            "Export Selection",
            "Send to Unreal",
            "Send to Unity",
            "GoZ",
            "Send to 3dsMax: As New Scene",
            "Send to 3dsMax: Update Current",
            "Send to 3dsMax: Add to Current",
            "Export to Offline File",
            "Export Options",
            "FBX Export Presets",
            "Obj Export Presets",
        ]
        widget.addItems_(items, "Export")

    def cmb005_init(self, widget):
        """ """
        widget.option_menu.add(
            "QPushButton",
            setObjectName="b001",
            setText="Last",
            setToolTip="Open the most recent file.",
        )
        widget.addItems_(
            mtk.get_recent_files(slice(0, 20), format="timestamp|standard"),
            "Recent Files",
            clear=True,
        )

    def cmb006_init(self, widget):
        """ """
        self.cmb006()  # init workspace items to reflect the current workspace.

        widget.option_menu.add(
            self.sb.ComboBox,
            setObjectName="cmb001",
            setToolTip="Current project directory root.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setObjectName="lbl000",
            setText="Set",
            setToolTip="Set the project directory.",
        )
        widget.option_menu.add(
            self.sb.Label,
            setObjectName="lbl004",
            setText="Root",
            setToolTip="Open the project directory.",
        )
        widget.option_menu.cmb001.addItems_(
            mtk.get_recent_projects(slice(0, 20), format="timestamp|standard"),
            "Recent Projects",
            clear=True,
        )

    def list000_init(self, widget):
        """ """
        widget.position = "top"
        widget.sublist_y_offset = 18
        widget.fixed_item_height = 18
        recentFiles = mtk.get_recent_files(slice(0, 6))
        w1 = widget.add("Recent Files")
        truncated = truncate(recentFiles, 65)
        w1.sublist.add(truncated, recentFiles)
        widget.setVisible(bool(recentFiles))

    @signals("on_item_interacted")
    def list000(self, item):
        """ """
        data = item.item_data()

        pm.openFile(data, open=True, force=True)

    def cmb000(self, *args, **kwargs):
        """Editors"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:
            text = cmb.items[index]
            if text == "":
                pass
            cmb.setCurrentIndex(0)

    def cmb001(self, *args, **kwargs):
        """Recent Projects"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:
            pm.mel.setProject(cmb.items[index])
            cmb.setCurrentIndex(0)

    def cmb002(self, *args, **kwargs):
        """Recent Autosave"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:
            file = cmb.items[index]
            pm.openFile(file, open=1, force=True)
            cmb.setCurrentIndex(0)

    def cmb003(self, *args, **kwargs):
        """Import"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:  # hide then perform operation
            self.sb.parent().hide(force=1)
            if index == 1:  # Import
                pm.mel.Import()
            elif index == 2:  # Import options
                pm.mel.ImportOptions()
            elif index == 3:  # FBX Import Presets
                pm.mel.FBXUICallBack(-1, "editImportPresetInNewWindow", "fbx")
            elif index == 4:  # Obj Import Presets
                pm.mel.FBXUICallBack(-1, "editImportPresetInNewWindow", "obj")
            cmb.setCurrentIndex(0)

    def cmb004(self, *args, **kwargs):
        """Export"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:  # hide then perform operation
            self.sb.parent().hide(force=1)
            if index == 1:  # Export selection
                pm.mel.ExportSelection()
            elif index == 2:  # Unreal
                pm.mel.SendToUnrealSelection()
            elif index == 3:  # Unity
                pm.mel.SendToUnitySelection()
            elif index == 4:  # GoZ
                pm.mel.eval(
                    'print("GoZ"); source"C:/Users/Public/Pixologic/GoZApps/Maya/GoZBrushFromMaya.mel"; source "C:/Users/Public/Pixologic/GoZApps/Maya/GoZScript.mel";'
                )
            elif index == 5:  # Send to 3dsMax: As New Scene
                pm.mel.SendAsNewScene3dsMax()  # OneClickMenuExecute ("3ds Max", "SendAsNewScene"); doMaxFlow { "sendNew","perspShape","1" };
            elif index == 6:  # Send to 3dsMax: Update Current
                pm.mel.UpdateCurrentScene3dsMax()  # OneClickMenuExecute ("3ds Max", "UpdateCurrentScene"); doMaxFlow { "update","perspShape","1" };
            elif index == 7:  # Send to 3dsMax: Add to Current
                pm.mel.AddToCurrentScene3dsMax()  # OneClickMenuExecute ("3ds Max", "AddToScene"); doMaxFlow { "add","perspShape","1" };
            elif index == 8:  # Export to Offline File
                pm.mel.ExportOfflineFileOptions()  # ExportOfflineFile
            elif index == 9:  # Export options
                pm.mel.ExportSelectionOptions()
            elif index == 10:  # FBX Export Presets
                pm.mel.FBXUICallBack(-1, "editExportPresetInNewWindow", "fbx")
            elif index == 11:  # Obj Export Presets
                pm.mel.FBXUICallBack(-1, "editExportPresetInNewWindow", "obj")
            cmb.setCurrentIndex(0)

    def cmb005(self, *args, **kwargs):
        """Recent Files"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        if index > 0:
            force = True
            # if sceneName prompt user to save; else force open
            force if str(pm.mel.file(query=1, sceneName=1, shortName=1)) else not force
            print(cmb.items[index])
            pm.openFile(cmb.items[index], open=1, force=force)
            cmb.setCurrentIndex(0)

    def cmb006(self, *args, **kwargs):
        """Workspace"""
        cmb = kwargs.get("widget")
        index = kwargs.get("index")

        path = ptk.File.format_path(
            pm.workspace(query=1, rd=1)
        )  # current project path.
        items = [f for f in os.listdir(path)]
        # add current project path string to label. strip path and trailing '/'
        project = ptk.File.format_path(path, "dir")

        cmb.addItems_(items, header=project, clear=True)

        if index > 0:
            os.startfile(path + items[index - 1])
            cmb.setCurrentIndex(0)

    def lbl000(self):
        """Set Workspace"""
        newProject = pm.mel.SetProject()
        self.cmb006()  # refresh project items to reflect new workspace.
        # refresh reference items to reflect new workspace.
        self.referenceSceneMenu(clear=True)

    def lbl004(self):
        """Open current project root"""
        dir_ = pm.workspace(query=1, rd=1)  # current project path.
        os.startfile(ptk.File.format_path(dir_))

    def lbl005(self):
        """Reference"""
        self.referenceSceneMenu().show()

    def b000(self, *args, **kwargs):
        """Autosave: Open Directory"""
        # dir1 = str(pm.workspace(query=1, rd=1))+'autosave' #current project path.
        # get autosave dir path from env variable.
        dir2 = os.environ.get("MAYA_AUTOSAVE_FOLDER").split(";")[0]

        try:
            # os.startfile(self.format_path(dir1))
            os.startfile(ptk.File.format_path(dir2))

        except FileNotFoundError:
            self.sb.message_box("The system cannot find the file specified.")

    @SlotsMaya.hideMain
    def b001(self, *args, **kwargs):
        """Recent Files: Open Last"""
        self.cmb005(index=1)

    def b002(self, *args, **kwargs):
        """Autosave: Delete All"""
        files = mtk.get_recent_autosave()
        for file in files:
            try:
                os.remove(file)

            except Exception as error:
                print(error)

    @SlotsMaya.hideMain
    def b007(self, *args, **kwargs):
        """Import file"""
        self.cmb003(index=1)

    @SlotsMaya.hideMain
    def b008(self, *args, **kwargs):
        """Export Selection"""
        self.cmb004(index=1)

    def b015(self, *args, **kwargs):
        """Remove String From Object Names."""
        # asterisk denotes startswith*, *endswith, *contains*
        from_ = str(self.sb.file.t000.text())
        to = str(self.sb.file.t001.text())
        replace = self.sb.file.chk004.isChecked()
        selected = self.sb.file.chk005.isChecked()

        objects = pm.ls(from_)  # Stores a list of all objects starting with 'from_'
        if selected:  # get user selected objects instead
            objects = pm.ls(selection=1)
        from_ = from_.strip("*")  # strip modifier asterisk from user input

        for obj in objects:  # Get a list of it's direct parent
            relatives = pm.listRelatives(obj, parent=1)
            # If that parent starts with group, it came in root level and is pasted in a group, so ungroup it
            if "group*" in relatives:
                relatives[0].ungroup()

            newName = to
            if replace:
                newName = obj.replace(from_, to)
            pm.rename(obj, newName)  # Rename the object with the new name

    def referenceSceneMenu(self, clear=False):
        """ """
        try:
            if clear:
                del self._referenceSceneMenu
            return self._referenceSceneMenu

        except AttributeError:
            menu = self.sb.Menu(self.sb.file.lbl005)
            for i in mtk.get_workspace_scenes(
                fullPath=True
            ):  # zip(mtk.get_workspace_scenes(fullPath=False), mtk.get_workspace_scenes(fullPath=True)):
                chk = menu.add(self.sb.CheckBox, setText=i)
                chk.toggled.connect(
                    lambda state, scene=i: mtk.reference_scene(scene, not state)
                )

            self._referenceSceneMenu = menu
            return self._referenceSceneMenu


# module name
print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------


# deprecated: -----------------------------------


# def lbl001(self):
#     """Minimize Main Application"""
#     pm.mel.eval("minimizeApp;")
#     self.sb.parent().hide(force=1)

# def lbl002(self):
#     """Restore Main Application"""
#     pass

# def lbl003(self):
#     """Close Main Application"""
#     # force=false #pymel has no attribute quit error.
#     # exitcode=""
#     # if sceneName prompt user to save; else force close
#     sceneName = str(pm.mel.file(query=1, sceneName=1, shortName=1))
#     # pm.quit (force=force, exitcode=exitcode)
#     pm.mel.quit() if sceneName else pm.mel.quit(force=True)

# def tb000(self, *args, **kwargs):
#     """Save"""
#     tb = self.sb.file.draggableHeader.ctx_menu.tb000

#     wireframe = tb.option_menu.chk000.isChecked()
#     increment = tb.option_menu.chk001.isChecked()
#     quit = tb.option_menu.chk002.isChecked()

#     if wireframe:
#         pm.mel.DisplayWireframe()

#     if increment:
#         pm.mel.IncrementAndSave()
#     else:
#         # type: mayaAscii, mayaBinary, mel, OBJ, directory, plug-in, audio, move, EPS, Adobe(R) Illustrator(R)
#         filetype = "mayaAscii"
#         pm.saveFile(force=1, preSaveScript="", postSaveScript="", type=filetype)

#     if quit:  # quit maya
#         import time

#         for timer in range(5):
#             mtk.viewport_message("Shutting Down:<hl>" + str(timer) + "</hl>")
#             time.sleep(timer)
#         pm.mel.quit()  # pm.Quit()


# def tb000(self, *args, **kwargs):
#   '''
#   Save
#   '''
#   tb = self.sb.file.tb000
#   if state=='setMenu':
#       tb.option_menu.add('QCheckBox', setText='ASCII', setObjectName='chk003', setChecked=True, setToolTip='Toggle ASCII or binary file type.')
#       tb.option_menu.add('QCheckBox', setText='Wireframe', setObjectName='chk000', setChecked=True, setToolTip='Set view to wireframe before save.')
#       tb.option_menu.add('QCheckBox', setText='Increment', setObjectName='chk001', setChecked=True, setToolTip='Append and increment a unique integer value.')
#       tb.option_menu.add('QCheckBox', setText='Quit', setObjectName='chk002', setToolTip='Quit after save.')
#       return

#   increment = tb.option_menu.chk001.isChecked()
#   ASCII = tb.option_menu.chk003.isChecked()
#   wireframe = tb.option_menu.chk000.isChecked()
#   quit = tb.option_menu.chk002.isChecked()

#   preSaveScript = ''
#   postSaveScript = ''

#   type_ = 'mayaBinary'
#   if ASCII: #toggle ascii/ binary
#       type_ = 'mayaAscii' #type: mayaAscii, mayaBinary, mel, OBJ, directory, plug-in, audio, move, EPS, Adobe(R) Illustrator(R)

#   if wireframe:
#       pm.mel.eval('DisplayWireframe;')

#   #get scene name and file path
#   fullPath = str(pm.mel.eval('file -query -sceneName;')) #ie. O:/Cloud/____Graphics/______project_files/elise.proj/elise.scenes/.maya/elise_mid.009.mb
#   index = fullPath.rfind('/')+1
#   curFullName = fullPath[index:] #ie. elise_mid.009.mb
#   path = fullPath[:index] #ie. O:/Cloud/____Graphics/______project_files/elise.proj/elise.scenes/.maya/

#   if increment: #increment filename
#       newName = self.incrementFileName(curFullName)
#       self.deletePreviousFiles(curFullName, path)
#       pm.saveAs (path+newName, force=1, preSaveScript=preSaveScript, postSaveScript=postSaveScript, type=type_)
#       print('{0} {1}'.format('Result:', path+newName))
#   else:   #save without renaming
#       pm.saveFile (force=1, preSaveScript=preSaveScript, postSaveScript=postSaveScript, type=type_)
#       print('{0} {1}'.format('Result:', path+currentName,))

#   if quit: #quit maya
#       import time
#       for timer in range(5):
#           mtk.viewport_message('Shutting Down:<hl>'+str(timer)+'</hl>')
#           time.sleep(timer)
#       pm.mel.eval("quit;")
#       # pm.Quit()


# @staticmethod
# def incrementFileName(fileName):
#   '''
#   Increment the given file name.

#   Parameters:
#       fileName (str): file name with extension. ie. elise_mid.ma

#   Returns:
#       (str) incremented name. ie. elise_mid.000.ma
#   '''
#   import re

#   #remove filetype extention
#   currentName = fileName[:fileName.rfind('.')] #name without extension ie. elise_mid.009 from elise_mid.009.mb
#   #get file number
#   numExt = re.search(r'\d+$', currentName) #check if the last chars are numberic
#   if numExt is not None:
#       name = currentName[:currentName.rfind('.')] #strip off the number ie. elise_mid from elise_mid.009
#       num = int(numExt.group())+1 #get file number and add 1 ie. 9 becomes 10
#       prefix = '000'[:-len(str(num))]+str(num) #prefix '000' removing zeros according to num length ie. 009 becomes 010
#       newName = name+'.'+prefix #ie. elise_mid.010

#   else:
#       newName = currentName+'.001'

#   return newName


# @staticmethod
# def deletePreviousFiles(fileName, path, numberOfPreviousFiles=5):
#   '''
#   Delete older files.

#   Parameters:
#       fileName (str): file name with extension. ie. elise_mid.ma
#       numberOfPreviousFiles (int): Number of previous copies to keep.
#   '''
#   import re, os

#   #remove filetype extention
#   currentName = fileName[:fileName.rfind('.')] #name without extension ie. elise_mid.009 from elise_mid.009.mb
#   #get file number
#   numExt = re.search(r'\d+$', currentName) #check if the last chars are numberic
#   if numExt is not None:
#       name = currentName[:currentName.rfind('.')] #strip off the number ie. elise_mid from elise_mid.009
#       num = int(numExt.group())+1 #get file number and add 1 ie. 9 becomes 10

#       oldNum = num-numberOfPreviousFiles
#       oldPrefix = '000'[:-len(str(oldNum))]+str(oldNum) #prefix the appropriate amount of zeros in front of the old number
#       oldName = name+'.'+oldPrefix #ie. elise_mid.007
#       try: #search recursively through the project folder and delete any old folders with the old filename
#           dir_ =  os.path.abspath(os.path.join(path, "../.."))
#           for root, directories, files in os.walk(dir_):
#               for filename in files:
#                   if all([filename==oldName+ext for ext in ('.ma','.ma.swatches','.mb','.mb.swatches')]):
#                       try:
#                           import os
#                           os.remove(filename)
#                       except:
#                           pass
#       except OSError:
#           print('{0} {1}'.format('Error: Could not delete', path+oldName))
#           pass
