# !/usr/bin/python
# coding=utf-8
from slots.maya import *
from slots.symmetry import Symmetry
from ui.static.maya.symmetry_ui_maya import Symmetry_ui_maya



class Symmetry_maya(Slots_maya):
	def __init__(self, *args, **kwargs):
		Slots_maya.__init__(self, *args, **kwargs)
		Symmetry_ui_maya.__init__(self, *args, **kwargs)
		Symmetry.__init__(self, *args, **kwargs)


	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.symmetry_ui.draggable_header


	def cmb000(self, index=-1):
		'''Editors
		'''
		cmb = self.symmetry_ui.draggable_header.contextMenu.cmb000

		# if index>0:
		# 	if index==cmd.items.index(''):
		# 		pass
		# 	cmb.setCurrentIndex(0)


	def setSymmetry(self, state, axis):
		space = "world" #workd space
		if self.symmetry_ui.chk004.isChecked(): #object space
			space = "object"
		elif self.symmetry_ui.chk005.isChecked(): #topological symmetry
			space = "topo"

		tolerance = 0.25
		pm.symmetricModelling(edit=True, symmetry=state, axis=axis, about=space, tolerance=tolerance)
		self.viewPortMessage("Symmetry:<hl>"+axis+' '+str(state)+"</hl>")


	@Slots.sync
	def chk000(self, state=None):
		'''Symmetry X
		'''
		self.toggleWidgets(setUnChecked='chk001,chk002')
		state = self.symmetry_ui.chk000.isChecked() #symmetry button state
		self.setSymmetry(state, 'x')


	@Slots.sync
	def chk001(self, state=None):
		'''Symmetry Y
		'''
		self.toggleWidgets(setUnChecked='chk000,chk002')
		state = self.symmetry_ui.chk001.isChecked() #symmetry button state
		self.setSymmetry(state, 'y')


	@Slots.sync
	def chk002(self, state=None):
		'''Symmetry Z
		'''
		self.toggleWidgets(setUnChecked='chk000,chk001')
		state = self.symmetry_ui.chk002.isChecked() #symmetry button state
		self.setSymmetry(state, 'z')


	def chk004(self, state=None):
		'''Symmetry: Object
		'''
		self.symmetry_ui.chk005.setChecked(False) #uncheck symmetry:topological
	

	@Slots.message
	def chk005(self, state=None):
		'''Symmetry: Topo
		'''
		self.symmetry_ui.chk004.setChecked(False) #uncheck symmetry:object space
		if any ([self.symmetry_ui.chk000.isChecked(), self.symmetry_ui.chk001.isChecked(), self.symmetry_ui.chk002.isChecked()]): #(symmetry)
			pm.symmetricModelling(edit=True, symmetry=False)
			self.toggleWidgets(setUnChecked='chk000,chk001,chk002')
			return 'Note: First select a seam edge and then check the symmetry button to enable topographic symmetry'









#module name
print (__name__)
# -----------------------------------------------
# Notes
# -----------------------------------------------