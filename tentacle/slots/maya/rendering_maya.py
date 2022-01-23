# !/usr/bin/python
# coding=utf-8
from slots.maya import *
from ui.static.maya.rendering_ui_maya import Rendering_ui_maya



class Rendering(Slots_maya):
	def __init__(self, *args, **kwargs):
		Slots_maya.__init__(self, *args, **kwargs)
		Rendering_ui_maya.__init__(self, *args, **kwargs)


	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.rendering_ui.draggable_header


	def cmb000(self, index=-1):
		'''Editors
		'''
		cmb = self.rendering_ui.draggable_header.contextMenu.cmb000

		if index>0:
			text = cmb.items[index]
			if text=='':
				pass
			cmb.setCurrentIndex(0)


	def cmb001(self, index=-1):
		'''Render: camera
		'''
		cmb = self.rendering_ui.cmb001

		# self.cams = [cam for cam in rt.cameras if 'Target' not in str(cam)]
		# if self.cams:
		# 	list_ = [str(cam.name) for cam in self.cams] #camera names
		# 	contents = cmb.addItems_(list_)


	def b000(self):
		'''Render Current Frame
		'''
		cmb = self.rendering_ui.cmb001
		index = cmb.currentIndex()

		try:
			rt.render (camera=self.cams[index]) #render with selected camera
		except:
			mel.eval('RenderIntoNewWindow;')


	def b001(self):
		'''Open Render Settings Window
		'''
		mel.eval('unifiedRenderGlobalsWindow;')


	def b002(self):
		'''Redo Previous Render
		'''
		mel.eval('redoPreviousRender render;')


	def b003(self):
		'''Editor: Render Setup
		'''
		mel.eval('RenderSetupWindow;')


	def b004(self):
		'''Editor: Rendering Flags
		'''
		mel.eval('renderFlagsWindow;')


	def b005(self):
		'''Apply Vray Attributes To Selected Objects
		'''
		selection = pm.ls(selection=1)
		currentID=1
		for obj in selection:
			# get renderable shape nodes relative to transform, iterate through and apply subdivision
			shapes = pm.listRelatives(obj,s=1,ni=1)
			if shapes:
				for shape in shapes:
					mel.eval ("vray addAttributesFromGroup "+shape+" vray_subdivision 1;")
					mel.eval ("vray addAttributesFromGroup "+shape+" vray_subquality 1;")
			# apply object ID to xform. i don't like giving individual shapes IDs.
			mel.eval ("vray addAttributesFromGroup "+obj+" vray_objectID 1;")
			pm.setAttr(obj+'.vrayObjectID',currentID)
			currentID+=1


	@Slots.message
	def b006(self):
		'''Load Vray Plugin
		'''
		vray = ['vrayformaya.mll','vrayformayapatch.mll']
		if pm.pluginInfo ('vrayformaya.mll', query=1, loaded=1):
			try:
				pm.unloadPlugin(vray)
			except:
				pm.unloadPlugin(vray, force=1)
				return '{0}{1}{2}'.format(" Result: Force unloadPlugin:", str(vray), " ")
		else:
			pm.loadPlugin (vray)









#module name
print (__name__)
# -----------------------------------------------
# Notes
# -----------------------------------------------