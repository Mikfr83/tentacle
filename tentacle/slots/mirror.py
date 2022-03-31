# !/usr/bin/python
# coding=utf-8
from slots import Slots



class Mirror(Slots):
	'''
	'''
	def __init__(self, *args, **kwargs):
		'''
		:Parameters: 
			**kwargs (inherited from this class's respective slot child class, and originating from switchboard.setClassInstanceFromUiName)
				properties:
					tcl (class instance) = The tentacle stacked widget instance. ie. self.tcl
					<name> (ui object) = The ui of <name> ie. self.polygons for the ui of filename polygons. ie. self.polygons
				functions:
					current (lambda function) = Returns the current ui if it is either the parent or a child ui for the class; else, return the parent ui. ie. self.current()
					'<name>' (lambda function) = Returns the class instance of that name.  ie. self.polygons()
		'''
		ctx = self.mirror_ui.draggable_header.contextMenu
		if not ctx.containsMenuItems:
			ctx.add(self.tcl.wgts.ComboBox, setObjectName='cmb000', setToolTip='')

		ctx = self.mirror_ui.tb000.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QCheckBox', setText='-', setObjectName='chk000', setChecked=True, setToolTip='Perform mirror along negative axis.')
			ctx.add('QRadioButton', setText='X', setObjectName='chk001', setChecked=True, setToolTip='Perform mirror along X axis.')
			ctx.add('QRadioButton', setText='Y', setObjectName='chk002', setToolTip='Perform mirror along Y axis.')
			ctx.add('QRadioButton', setText='Z', setObjectName='chk003', setToolTip='Perform mirror along Z axis.')
			ctx.add('QCheckBox', setText='World Space', setObjectName='chk008', setChecked=True, setToolTip='Mirror in world space instead of object space.')
			ctx.add('QCheckBox', setText='Instance', setObjectName='chk004', setToolTip='Instance the mirrored object(s).')
			ctx.add('QCheckBox', setText='Cut', setObjectName='chk005', setToolTip='Perform a delete along specified axis before mirror.')
			ctx.add('QCheckBox', setText='Merge', setObjectName='chk007', setToolTip='Merge the mirrored geometry with the original.')
			ctx.add('QSpinBox', setPrefix='Merge Mode: ', setObjectName='s001', setMinMax_='0-2 step1', setValue=0, setToolTip='0) Do not merge border edges.<br>1) Border edges merged.<br>2) Border edges extruded and connected.')
			ctx.add('QDoubleSpinBox', setPrefix='Merge Threshold: ', setObjectName='s000', setMinMax_='0.000-10 step.001', setValue=0.005, setToolTip='Merge vertex distance.')
			ctx.add('QCheckBox', setText='Delete History', setObjectName='chk006', setChecked=True, setToolTip='Delete non-deformer history on the object before performing the operation.')

			#sync widgets
			ctx.chk008.toggled.connect(lambda state: self.mirror_submenu_ui.chk008.setChecked(state))
			self.mirror_submenu_ui.chk008.toggled.connect(lambda state: ctx.chk008.setChecked(state))

			ctx.chk000.toggled.connect(lambda state: self.mirror_submenu_ui.chk000.setChecked(state))
			self.mirror_submenu_ui.chk000.toggled.connect(lambda state: ctx.chk000.setChecked(state))




	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.mirror_ui.draggable_header









# -----------------------------------------------
# Notes
# -----------------------------------------------



#deprecated:
	# def chk000_3(self):
	# 	'''Set the tb000's text according to the checkstates.

	# 	ex call: self.connect_('chk000-3', 'toggled', self.chk000_3, ctx)
	# 	'''
	# 	axis = self.getAxisFromCheckBoxes('chk000-3', self.mirror_ui.tb000.contextMenu)
	# 	self.mirror_ui.tb000.setText('Mirror '+axis)

		