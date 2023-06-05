# !/usr/bin/python
# coding=utf-8
from tentacle.slots.blender import *
from tentacle.slots.vfx import Vfx


class Vfx_blender(Vfx, SlotsBlender):
    def __init__(self, *args, **kwargs):
        SlotsBlender.__init__(self, *args, **kwargs)
        Vfx.__init__(self, *args, **kwargs)

        cmb = self.sb.vfx.draggableHeader.ctx_menu.cmb000
        items = [""]
        cmb.addItems_(items, "")

    def cmb000(self, *args, **kwargs):
        """Editors"""
        cmb = self.sb.vfx.draggableHeader.ctx_menu.cmb000

        if index > 0:
            text = cmb.items[index]
            if text == "":
                pass
            cmb.setCurrentIndex(0)


# module name
print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
