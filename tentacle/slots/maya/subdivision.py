# !/usr/bin/python
# coding=utf-8
import maya.cmds as cmds
import maya.mel as mel
import mayatk as mtk
from tentacle.slots.maya._slots_maya import SlotsMaya


class Subdivision(SlotsMaya):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = self.sb.loaded_ui.subdivision
        self.submenu = self.sb.loaded_ui.subdivision_submenu

    def cmb001(self, index, widget):
        """Smooth Proxy"""
        text = widget.items[index]
        if text == "Create Subdiv Proxy":
            mel.eval("SmoothProxyOptions")
        elif text == "Remove Subdiv Proxy Mirror":
            mel.eval("UnmirrorSmoothProxyOptions")
        elif text == "Crease Tool":
            mel.eval("polyCreaseProperties")
        elif text == "Toggle Subdiv Proxy Display":
            mel.eval("SmoothingDisplayToggle")
        elif text == "Both Proxy and Subdiv Display":
            mel.eval("SmoothingDisplayShowBoth")

    def cmb002(self, index, widget):
        """Maya Subdivision Operations"""
        if index is widget.items.index("Reduce Polygons"):
            mel.eval("ReducePolygonOptions")
        elif index is widget.items.index("Add Divisions"):
            mel.eval("SubdividePolygonOptions")
        elif index is widget.items.index("Smooth"):
            mel.eval("performPolySmooth 1")

    def s000(self, value: int, widget: object) -> None:
        """Division Level"""
        shapes = cmds.ls(selection=True, dag=True, leaf=True) or []
        transforms = cmds.listRelatives(shapes, parent=True) or []
        for obj in transforms:
            if cmds.attributeQuery("smoothLevel", node=obj, exists=True):
                # Correctly pass attributes as keyword arguments
                mtk.Attributes.set_attributes(obj, smoothLevel=value)
                # SubDivision proxy options: 'divisions'
                cmds.optionVar(intValue=("proxyDivisions", value))
                cmds.inViewMessage(
                    statusMessage=f"{obj}: Division Level: <hl>{value}</hl>",
                    pos="topCenter",
                    fade=True,
                )

    def s001(self, value: int, widget: object) -> None:
        """Tesselation Level"""
        shapes = cmds.ls(selection=True, dag=True, leaf=True) or []
        transforms = cmds.listRelatives(shapes, parent=True) or []
        for obj in transforms:
            if cmds.attributeQuery("smoothLevel", node=obj, exists=True):
                # Correctly pass attributes as keyword arguments
                mtk.Attributes.set_attributes(obj, smoothTessLevel=value)
                cmds.inViewMessage(
                    statusMessage=f"{obj}: Tesselation Level: <hl>{value}</hl>",
                    pos="topCenter",
                    fade=True,
                )

    def b000(self):
        """Quadrangulate"""
        mel.eval("performPolyQuadrangulate 0")

    def b001(self):
        """Triangulate"""
        mel.eval("polyTriangulate")

    def b005(self):
        """Reduce"""
        selection = cmds.ls(sl=1, objectsOnly=1, type="transform") or []
        if not selection:
            return

        cmds.polyReduce(
            selection,
            ver=1,
            trm=0,
            shp=0,
            keepBorder=1,
            keepMapBorder=1,
            keepColorBorder=1,
            keepFaceGroupBorder=1,
            keepHardEdge=1,
            keepCreaseEdge=1,
            keepBorderWeight=0.5,
            keepMapBorderWeight=0.5,
            keepColorBorderWeight=0.5,
            keepFaceGroupBorderWeight=0.5,
            keepHardEdgeWeight=0.5,
            keepCreaseEdgeWeight=0.5,
            useVirtualSymmetry=0,
            symmetryTolerance=0.01,
            sx=0,
            sy=1,
            sz=0,
            sw=0,
            preserveTopology=1,
            keepQuadsWeight=1,
            vertexMapName="",
            cachingReduce=1,
            ch=1,
            p=50,
            vct=0,
            tct=0,
            replaceOriginal=1,
        )

    def b008(self):
        """Add Divisions - Subdivide Mesh"""
        mel.eval("SubdividePolygon")

    def b009(self):
        """Smooth"""
        mel.eval("SmoothPolygon")

    def b011(self):
        """Apply Smooth Preview"""
        mel.eval("performSmoothMeshPreviewToPolygon")

    def b028(self):
        """Quad Draw"""
        mel.eval("dR_quadDrawTool")

    @staticmethod
    def smoothProxy():
        """Subdiv Proxy"""
        global polySmoothBaseMesh
        polySmoothBaseMesh = []
        # disable creating seperate layers for subdiv proxy
        cmds.optionVar(intValue=("polySmoothLoInLayer", 0))
        cmds.optionVar(intValue=("polySmoothHiInLayer", 0))
        # query smooth proxy state.
        sel = mel.eval('polyCheckSelection "polySmoothProxy" "o" 0') or []

        if len(sel) == 0 and len(polySmoothBaseMesh) == 0:
            return "Error: Nothing selected."

        if len(sel) != 0:
            del polySmoothBaseMesh[:]
            for object_ in sel:
                polySmoothBaseMesh.append(object_)
        elif len(polySmoothBaseMesh) != 0:
            sel = polySmoothBaseMesh

        transform = cmds.listRelatives(sel[0], fullPath=1, parent=1) or []
        if not transform:
            return
        shape = cmds.listRelatives(transform[0], pa=1, shapes=1) or []
        if not shape:
            return

        # check shape for an existing output to a smoothProxy
        attachedSmoothProxies = cmds.listConnections(
            shape[0], type="polySmoothProxy", s=0, d=1
        ) or []
        if len(attachedSmoothProxies) != 0:  # subdiv off
            mel.eval("smoothingDisplayToggle 0")

        # toggle performSmoothProxy
        mel.eval("performSmoothProxy 0")  # toggle SubDiv Proxy


# --------------------------------------------------------------------------------------------

# module name
# print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
