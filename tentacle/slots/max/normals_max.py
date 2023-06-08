# !/usr/bin/python
# coding=utf-8
from tentacle.slots.max import *
from tentacle.slots.normals import Normals


class Normals_max(Normals, SlotsMax):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sb.normals.b003.setText("Hard Edge Display")

        cmb = self.sb.normals.draggableHeader.ctx_menu.cmb000
        items = [""]
        cmb.addItems_(items, "")

    def cmb000(self, *args, **kwargs):
        """Editors"""
        cmb = self.sb.normals.draggableHeader.ctx_menu.cmb000

        if index > 0:
            text = cmb.items[index]
            if text == "":
                pass
            cmb.setCurrentIndex(0)

    def tb000(self, *args, **kwargs):
        """Display Face Normals"""
        tb = self.sb.normals.tb000

        size = float(tb.option_menu.s001.value())

        self.sb.message_box("No 3ds Version.")
        tb.setDisabled(True)
        # # state = pm.polyOptions (query=True, displayNormal=True)
        # state = ptk.cycle([1,2,3,0], 'displayNormals')
        # if state ==0: #off
        # 	pm.polyOptions (displayNormal=0, sizeNormal=0)
        # 	pm.polyOptions (displayTangent=False)
        # 	return 'Normals Display <hl>Off</hl>.'

        # elif state ==1: #facet
        # 	pm.polyOptions (displayNormal=1, facet=True, sizeNormal=size)
        # 	pm.polyOptions (displayTangent=False)
        # 	return '<hl>Facet</hl> Normals Display <hl>On</hl>.'

        # elif state ==2: #Vertex
        # 	pm.polyOptions (displayNormal=1, point=True, sizeNormal=size)
        # 	pm.polyOptions (displayTangent=False)
        # 	return '<hl>Vertex</hl> Normals Display <hl>On</hl>.'

        # elif state ==3: #tangent
        # 	pm.polyOptions (displayTangent=True)
        # 	pm.polyOptions (displayNormal=0)
        # 	return '<hl>Tangent</hl> Display <hl>On</hl>.'

    def tb001(self, *args, **kwargs):
        """Harden Edge Normals"""
        tb = self.sb.normals.tb001

        maxEval("$.EditablePoly.makeHardEdges 1")

        # hardAngle = tb.option_menu.s002.value()
        # hardenCreased = tb.option_menu.chk001.isChecked()
        # hardenUvBorders = tb.option_menu.chk002.isChecked()
        # softenOther = tb.option_menu.chk000.isChecked()

        # objects = rt.selection

        # for obj in objects:
        # selection = pm.ls(obj, sl=True, l=True)
        # selEdges = pm.ls(pm.polyListComponentConversion(selection, toEdge=1), flatten=1)
        # allEdges = edges = pm.ls(pm.polyListComponentConversion(obj, toEdge=1), flatten=1)

        # if hardenCreased:
        # 	creasedEdges = Normals.getCreasedEdges(allEdges)
        # 	selEdges = selEdges + creasedEdges if not selEdges==allEdges else creasedEdges

        # if hardenUvBorders:
        # 	uv_border_edges = SlotsMax.getUvShellBorderEdges(selection)
        # 	selEdges = selEdges + uv_border_edges if not selEdges==allEdges else uv_border_edges

        # obj.EditablePoly.makeHardEdges(1) #set hard edges.

        # if softenOther:
        # 	invEdges = [e for e in allEdges if e not in selEdges]
        # 	pm.polySoftEdge(invEdges, angle=180, constructionHistory=0) #set soft edges.

        # rt.select(selEdges)

    @Slots.hideMain
    def tb002(self, *args, **kwargs):
        """Set Normal By Angle"""
        tb = self.sb.normals.tb002

        normalAngle = str(tb.option_menu.s000.value())
        subObjectLevel = rt.subObjectLevel

        if subObjectLevel == 4:  # smooth selected faces
            for obj in rt.selection:
                obj.autoSmoothThreshold = normalAngle
                # faceSelection = rt.polyop.getFaceSelection(obj)
                rt.polyop.autoSmooth(obj)
                rt.update(obj)

        else:  # smooth entire mesh
            mod = rt.Smooth()
            mod.autoSmooth = True
            mod.threshold = normalAngle

            for obj in rt.selection:
                rt.modPanel.setCurrentObject(obj.baseObject)
                rt.modPanel.addModToSelection(mod)
                index = [mod for mod in obj.modifiers].index(
                    mod
                ) + 1  # add one to convert index from python to maxscript
                rt.maxOps.CollapseNodeTo(obj, index, False)

    def tb003(self, *args, **kwargs):
        """Lock/Unlock Vertex Normals"""
        tb = self.sb.normals.tb003

        print("# Error: No 3ds Version of this command yet. #")
        tb.setDisabled(True)
        # all_ = tb.option_menu.chk001.isChecked()
        # state = tb.option_menu.chk002.isChecked() #pm.polyNormalPerVertex(vertex, q=True, freezeNormal=1)
        # selection = pm.ls (sl=True, objectsOnly=1)
        # maskObject = pm.selectMode (q=True, object=1)
        # maskVertex = pm.selectType (q=True, vertex=1)

        # if len(selection)>0:
        # 	if (all_ and maskVertex) or maskObject:
        # 		for obj in selection:
        # 			count = pm.polyEvaluate(obj, vertex=1) #get number of vertices
        # 			vertices = [vertices.append(str(obj) + ".vtx ["+str(num)+"]") for num in range(count)] #geometry.vtx[0]
        # 			for vertex in vertices:
        # 				if not state:
        # 					pm.polyNormalPerVertex(vertex, unFreezeNormal=1)
        # 				else:
        # 					pm.polyNormalPerVertex(vertex, freezeNormal=1)
        # 			if not state:
        # 				self.mtk.viewport_message("Normals <hl>UnLocked</hl>.")
        # 			else:
        # 				self.mtk.viewport_message("Normals <hl>Locked</hl>.")
        # 	elif maskVertex and not maskObject:
        # 		if not state:
        # 			pm.polyNormalPerVertex(unFreezeNormal=1)
        # 			self.mtk.viewport_message("Normals <hl>UnLocked</hl>.")
        # 		else:
        # 			pm.polyNormalPerVertex(freezeNormal=1)
        # 			self.mtk.viewport_message("Normals <hl>Locked</hl>.")
        # 	else:
        # 		return 'Warning: Selection must be object or vertex.'
        # else:
        # 	return 'Warning: No object selected.'

    def tb004(self, *args, **kwargs):
        """Average Normals"""
        tb = self.sb.normals.tb004

        byUvShell = tb.option_menu.chk003.isChecked()

        if byUvShell:
            print("# Error: No 3ds Version of this flag yet. #")
            sets_ = SlotsMax.getUvShellSets(obj)
            for set_ in sets_:
                pm.polySetToFaceNormal(set_)
                pm.polyAverageNormal(set_)
        else:
            maxEval('macros.run "PolyTools" "SmoothSelection"')

    @Slots.hideMain
    def b001(self, *args, **kwargs):
        """Soften Edge Normal"""
        maxEval("$.EditablePoly.makeSmoothEdges 1")

    def b003(self, *args, **kwargs):
        """Soft Edge Display"""
        for obj in rt.selection:
            state = obj.hardedgedisplay
            obj.hardedgedisplay = not state

    def b005(self, *args, **kwargs):
        """Adjust Vertex Normals"""
        maxEval("bgAdjustVertexNormalsWin;")

    def b006(self, *args, **kwargs):
        """Set To Face"""
        maxEval('macros.run "PolyTools" "HardSelection"')

    def b010(self, *args, **kwargs):
        """Reverse Normals"""
        for obj in rt.selection:
            rt.modPanel.setCurrentObject(obj.baseObject)

            mod = rt.Normalmodifier()
            mod.flip = True

            rt.modpanel.addModToSelection(mod)

            index = rt.modPanel.getModifierIndex(obj, mod)
            rt.maxOps.CollapseNodeTo(obj, index, False)


# module name
print(__name__)
# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
