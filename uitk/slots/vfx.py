# !/usr/bin/python
# coding=utf-8
from tentacle.slots import Slots



class Vfx(Slots):
	'''
	'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		'''
		'''
		ctx = self.sb.vfx.draggable_header.ctxMenu
		if not ctx.containsMenuItems:
			ctx.add(self.sb.ComboBox, setObjectName='cmb000', setToolTip='')


	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.sb.vfx.draggable_header
