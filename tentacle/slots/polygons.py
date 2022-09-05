# !/usr/bin/python
# coding=utf-8
from slots import Slots



class Polygons(Slots):
	'''
	'''
	def __init__(self, *args, **kwargs):
		'''
		'''
		ctx = self.sb.polygons.draggable_header.contextMenu
		if not ctx.containsMenuItems:
			ctx.add(self.sb.ComboBox, setObjectName='cmb000', setToolTip='')

		ctx = self.sb.polygons.tb000.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QDoubleSpinBox', setPrefix='Distance: ', setObjectName='s002', setMinMax_='0.0000-10 step.0005', setValue=0.0005, setHeight_=20, setToolTip='Merge Distance.')
			ctx.add('QPushButton', setText='Set Distance', setObjectName='b005', setHeight_=20, setToolTip='Set the distance using two selected vertices.\nElse; return the Distance to it\'s default value')

		ctx = self.sb.polygons.tb001.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QSpinBox', setPrefix='Divisions: ', setObjectName='s003', setMinMax_='0-10000 step1', setValue=0, setHeight_=20, setToolTip='Subdivision Amount.')

		ctx = self.sb.polygons.tb002.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QCheckBox', setText='Merge', setObjectName='chk000', setChecked=True, setHeight_=20, setToolTip='Combine selected meshes and merge any coincident verts/edges.')

		ctx = self.sb.polygons.tb003.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QCheckBox', setText='Keep Faces Together', setObjectName='chk002', setChecked=True, setHeight_=20, setToolTip='Keep edges/faces together.')
			ctx.add('QSpinBox', setPrefix='Divisions: ', setObjectName='s004', setMinMax_='1-10000 step1', setValue=1, setHeight_=20, setToolTip='Subdivision Amount.')

		ctx = self.sb.polygons.tb004.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QDoubleSpinBox', setPrefix='Width: ', setObjectName='s000', setMinMax_='0.00-100 step.05', setValue=0.25, setHeight_=20, setToolTip='Bevel Width.')
			ctx.add('QDoubleSpinBox', setPrefix='Segments: ', setObjectName='s006', setMinMax_='1-100 step1', setValue=1, setHeight_=20, setToolTip='Bevel Segments.')

		ctx = self.sb.polygons.tb005.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QCheckBox', setText='Duplicate', setObjectName='chk014', setChecked=True, setToolTip='Duplicate any selected faces, leaving the originals.')
			ctx.add('QCheckBox', setText='Separate', setObjectName='chk015', setChecked=True, setToolTip='Separate mesh objects after detaching faces.')
			# ctx.add('QCheckBox', setText='Delete Original', setObjectName='chk007', setChecked=True, setToolTip='Delete original selected faces.')

		ctx = self.sb.polygons.tb006.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QDoubleSpinBox', setPrefix='Offset: ', setObjectName='s001', setMinMax_='0.00-100 step.01', setValue=2.00, setHeight_=20, setToolTip='Offset amount.')

		ctx = self.sb.polygons.tb007.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QCheckBox', setText='U', setObjectName='chk008', setChecked=True, setHeight_=20, setToolTip='Divide facet: U coordinate.')
			ctx.add('QCheckBox', setText='V', setObjectName='chk009', setChecked=True, setHeight_=20, setToolTip='Divide facet: V coordinate.')
			ctx.add('QCheckBox', setText='Tris', setObjectName='chk010', setHeight_=20, setToolTip='Divide facet: Tris.')

		ctx = self.sb.polygons.tb008.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QRadioButton', setText='Union', setObjectName='chk011', setHeight_=20, setToolTip='Fuse two objects together.')
			ctx.add('QRadioButton', setText='Difference', setObjectName='chk012', setChecked=True, setHeight_=20, setToolTip='Indents one object with the shape of another at the point of their intersection.')
			ctx.add('QRadioButton', setText='Intersection', setObjectName='chk013', setHeight_=20, setToolTip='Keep only the interaction point of two objects.')

		ctx = self.sb.polygons.tb009.contextMenu
		if not ctx.containsMenuItems:
			ctx.add('QDoubleSpinBox', setPrefix='Tolerance: ', setObjectName='s005', setMinMax_='.000-100 step.05', setValue=10, setToolTip='Set the max Snap Distance. Vertices with a distance exceeding this value will be ignored.')
			ctx.add('QCheckBox', setText='Freeze Transforms', setObjectName='chk016', setChecked=True, setToolTip='Freeze Transformations on the object that is being snapped to.')


	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.sb.polygons.draggable_header


	def chk008(self, state=None):
		'''Divide Facet: Split U
		'''
		self.toggleWidgets(setUnChecked='chk010')


	def chk009(self, state=None):
		'''Divide Facet: Split V
		'''
		self.toggleWidgets(setUnChecked='chk010')


	def chk010(self, state=None):
		'''Divide Facet: Tris
		'''
		self.toggleWidgets(setUnChecked='chk008,chk009')


	def setMergeVertexDistance(self, p1, p2):
		'''Merge Vertices: Set Distance
		'''
		s = self.sb.polygons.tb000.contextMenu.s002
		dist = Slots.getDistanceBetweenTwoPoints(p1, p2)
		s.setValue(dist)