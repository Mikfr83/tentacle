# !/usr/bin/python
# coding=utf-8
from slots.max import *
from slots.dynLayout import DynLayout



class DynLayout_max(DynLayout, Slots_max):
	def __init__(self, *args, **kwargs):
		Slots_max.__init__(self, *args, **kwargs)
		DynLayout.__init__(self, *args, **kwargs)

		cmb = self.dynLayout_ui.draggable_header.contextMenu.cmb000
		list_ = []
		cmb.addItems_(list_, '')


	def cmb000(self, index=None):
		'''Editors
		'''
		cmb = self.dynLayout_ui.draggable_header.contextMenu.cmb000

		if index>0:
			text = cmb.items[index]
			if text=='':
				pass
			cmb.setCurrentIndex(0)









#module name
print (__name__)
# -----------------------------------------------
# Notes
# -----------------------------------------------