# !/usr/bin/python
# coding=utf-8
from tentacle.slots.max import *
from tentacle.slots.preferences import Preferences


class Preferences_max(Preferences, SlotsMax):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sb.preferences.b010.setText("3dsMax Preferences")

        cmb = self.sb.preferences.draggableHeader.ctx_menu.cmb000
        items = [""]
        cmb.addItems_(items, "")

        cmb = self.sb.preferences.cmb001
        items = [
            "millimeter",
            "centimeter",
            "meter",
            "kilometer",
            "inch",
            "foot",
            "mile",
        ]
        cmb.addItems_(items)
        # index = cmb.items.index(pm.currentUnit(q=True, fullName=1, linear=1)) #get/set current linear value.
        # cmb.setCurrentIndex(index)

        # cmb = self.sb.preferences.cmb002
        # #store a corresponding value for each item in the comboBox items.
        # l = {'15 fps: ':'game','24 fps: ':'film','25 fps: ':'pal','30 fps: ':'ntsc','48 fps: ':'show','50 fps: ':'palf','60 fps: ':'ntscf'}
        # items = [k+v for k,v in l.items()] #ie. ['15 fps: game','24 fps: film', ..etc]
        # values = [i[1] for i in l] #ie. ['game','film', ..etc]
        # cmb.addItems_(items)
        # # index = cmb.items.index(pm.currentUnit(q=True, fullName=1, time=1)) #get/set current time value.
        # # cmb.setCurrentIndex(index)

        # cmb = self.sb.preferences.cmb003
        # from PySide2 import QtWidgets, QtCore
        # items = QtWidgets.QStyleFactory.keys() #get styles from QStyleFactory
        # cmb.addItems_(items)
        # index = self.styleComboBox.findText(QtWidgets.QApplication.instance().style().objectName(), QtCore.Qt.MatchFixedString) #get/set current value
        # cmb.setCurrentIndex(index)

    def cmb000(self, *args, **kwargs):
        """Editors"""
        cmb = self.sb.preferences.draggableHeader.ctx_menu.cmb000

        if index > 0:
            if index == cmb.items.index(""):
                pass
            cmb.setCurrentIndex(0)

    def cmb001(self, *args, **kwargs):
        """Preferences:App - Set Working Units: Linear"""
        cmb = self.sb.preferences.cmb001

        if index is not None:
            if index is "millimeter":
                maxEval("units.SystemType = #Millimeters")
            if index is "centimeter":
                maxEval("units.SystemType = #Centimeters")
            if index is "meter":
                maxEval("units.SystemType = #Meters")
            if index is "kilometer":
                maxEval("units.SystemType = #Kilometers")
            if index is "inch":
                maxEval("units.SystemType = #Inches")
            if index is "foot":
                maxEval("units.SystemType = #Feet")
            if index is "mile":
                maxEval("units.SystemType = #Miles")

    def cmb002(self, *args, **kwargs):
        """Preferences:App - Set Working Units: Time"""
        cmb = self.sb.preferences.cmb002

        if index is not None:
            pm.currentUnit(
                time=cmb.items[index]
            )  # game | film | pal | ntsc | show | palf | ntscf

    def b001(self, *args, **kwargs):
        """Color Settings"""
        maxEval("colorPrefWnd;")

    def b008(self, *args, **kwargs):
        """Hotkeys"""
        maxEval(
            'actionMan.executeAction 0 "59245"'
        )  # Customize User Interface: Hotkey Editor

    def b009(self, *args, **kwargs):
        """Plug-In Manager"""
        maxEval("Plug_in_Manager.PluginMgrAction.show()")

    def b010(self, *args, **kwargs):
        """Settings/Preferences"""
        maxEval('actionMan.executeAction 0 "40108"')


# module name
print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------


# deprecated:
