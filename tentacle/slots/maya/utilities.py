# !/usr/bin/python
# coding=utf-8
import maya.mel as mel
import mayatk as mtk
from tentacle.slots.maya._slots_maya import SlotsMaya


class Utilities(SlotsMaya):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def b000(self):
        """Measure"""
        mel.eval("DistanceTool")

    def b001(self):
        """Annotation"""
        mel.eval("CreateAnnotateNode")

    def b002(self):
        """Calculator"""
        self.sb.handlers.marking_menu.show("calculator")

    def b003(self):
        """Grease Pencil"""
        mel.eval("OpenBluePencil")


# --------------------------------------------------------------------------------------------

# module name
# print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
