# !/usr/bin/python
# coding=utf-8
import os.path

from maya_init import *



class Create(Init):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	def draggable_header(self, state=None):
		'''Context menu
		'''
		dh = self.create_ui.draggable_header

		if state=='setMenu':
			dh.contextMenu.add(self.tcl.wgts.ComboBox, setObjectName='cmb000', setToolTip='')
			return


	def cmb000(self, index=-1):
		'''Editors
		'''
		cmb = self.create_ui.draggable_header.contextMenu.cmb000
		
		if index=='setMenu':
			list_ = ['']
			cmb.addItems_(list_, '')
			return

		if index>0:
			text = cmb.items[index]
			if text=='':
				pass
			cmb.setCurrentIndex(0)


	def cmb001(self, index=-1):
		'''
		'''
		cmb = self.create_ui.cmb001

		if index=='setMenu':
			list_ = ['Polygon', 'NURBS', 'Light']
			cmb.addItems_(list_)
			return

		if index>=0:
			self.cmb002(index)


	def cmb002(self, index=-1):
		'''
		'''
		cmb = self.create_ui.cmb002

		if index=='setMenu':
			list_ = ["Cube", "Sphere", "Cylinder", "Plane", "Circle", "Cone", "Pyramid", "Torus", "Tube", "GeoSphere", "Platonic Solids", "Text"]
			cmb.addItems_(list_)
			return

		polygons = ["Cube", "Sphere", "Cylinder", "Plane", "Circle", "Cone", "Pyramid", "Torus", "Tube", "GeoSphere", "Platonic Solids", "Text"]
		nurbs = ["Cube", "Sphere", "Cylinder", "Cone", "Plane", "Torus", "Circle", "Square"]
		lights = ["Ambient", "Directional", "Point", "Spot", "Area", "Volume", "VRay Sphere", "VRay Dome", "VRay Rect", "VRay IES"]

		if index==0: #shared menu. later converted to the specified type.
			cmb.addItems_(polygons, clear=True)

		if index==1:
			cmb.addItems_(nurbs, clear=True)

		if index==2:
			cmb.addItems_(lights, clear=True)


	@Slots.hideMain
	@Init.attr
	def b000(self):
		'''Create Object
		'''
		axis = [0,90,0]
		type_ = self.create_ui.cmb001.currentText()
		index = self.create_ui.cmb002.currentIndex()

		selection = pm.ls(selection=1)

		#polygons
		if type_=='Polygon':
			if index==0: #cube:
				node = pm.polyCube(axis=axis, width=5, height=5, depth=5, subdivisionsX=1, subdivisionsY=1, subdivisionsZ=1)
			elif index==1: #sphere:
				node = pm.polySphere(axis=axis, radius=5, subdivisionsX=12, subdivisionsY=12)
			elif index==2: #cylinder:
				node = pm.polyCylinder(axis=axis, radius=5, height=10, subdivisionsX=12, subdivisionsY=1, subdivisionsZ=1)
			elif index==3: #plane:
				node = pm.polyPlane(axis=axis, width=5, height=5, subdivisionsX=1, subdivisionsY=1)
			elif index==4: #circle:
				node = self.createCircle(axis=axis, numPoints=12, radius=5, mode=0)
			elif index==5: #Cone:
				node = pm.polyCone(axis=axis, radius=5, height=5, subdivisionsX=1, subdivisionsY=1, subdivisionsZ=1)
			elif index==6: #Pyramid
				node = pm.polyPyramid(axis=axis, sideLength=5, numberOfSides=5, subdivisionsHeight=1, subdivisionsCaps=1)
			elif index==7: #Torus:
				node = pm.polyTorus(axis=axis, radius=10, sectionRadius=5, twist=0, subdivisionsX=5, subdivisionsY=5)
			elif index==8: #Pipe
				node = pm.polyPipe(axis=axis, radius=5, height=5, thickness=2, subdivisionsHeight=1, subdivisionsCaps=1)
			elif index==9: #Soccer ball
				node = pm.polyPrimitive(axis=axis, radius=5, sideLength=5, polyType=0)
			elif index==10: #Platonic solids
				node = mel.eval("performPolyPrimitive PlatonicSolid 0;")

		#nurbs
		elif type_=='NURBS':
			if index==0: #Cube
				node = pm.nurbsCube(ch=1, d=3, hr=1, p=(0, 0, 0), lr=1, w=1, v=1, ax=(0, 1, 0), u=1)
			elif index==1: #Sphere
				node = pm.sphere(esw=360, ch=1, d=3, ut=0, ssw=0, p=(0, 0, 0), s=8, r=1, tol=0.01, nsp=4, ax=(0, 1, 0))
			elif index==2: #Cylinder
				node = pm.cylinder(esw=360, ch=1, d=3, hr=2, ut=0, ssw=0, p=(0, 0, 0), s=8, r=1, tol=0.01, nsp=1, ax=(0, 1, 0))
			elif index==3: #Cone
				node = pm.cone(esw=360, ch=1, d=3, hr=2, ut=0, ssw=0, p=(0, 0, 0), s=8, r=1, tol=0.01, nsp=1, ax=(0, 1, 0))
			elif index==4: #Plane
				node = pm.nurbsPlane(ch=1, d=3, v=1, p=(0, 0, 0), u=1, w=1, ax=(0, 1, 0), lr=1)
			elif index==5: #Torus
				node = pm.torus(esw=360, ch=1, d=3, msw=360, ut=0, ssw=0, hr=0.5, p=(0, 0, 0), s=8, r=1, tol=0.01, nsp=4, ax=(0, 1, 0))
			elif index==6: #Circle
				node = pm.circle(c=(0, 0, 0), ch=1, d=3, ut=0, sw=360, s=8, r=1, tol=0.01, nr=(0, 1, 0))
			elif index==7: #Square
				node = pm.nurbsSquare(c=(0, 0, 0), ch=1, d=3, sps=1, sl1=1, sl2=1, nr=(0, 1, 0))

		#lights
		elif type_=='Light':
			if index==0: #Ambient
				node = pm.ambientLight() #defaults: 1, 0.45, 1,1,1, "0", 0,0,0, "1"
			elif index==1: #Directional
				node = pm.directionalLight() #1, 1,1,1, "0", 0,0,0, 0
			elif index==2: #Point
				node = pm.pointLight() #1, 1,1,1, 0, 0, 0,0,0, 1
			elif index==3: #Spot
				node = pm.spotLight() #1, 1,1,1, 0, 40, 0, 0, 0, 0,0,0, 1, 0
			elif index==4: #Area
				node = pm.areaLight() #1, 1,1,1, 0, 0, 0,0,0, 1, 0
			elif index==5: #Volume
				node = pm.volumeLight() #1, 1,1,1, 0, 0, 0,0,0, 1
			# elif index==6: #VRay Sphere
			# 	node = pm.
			# elif index==7: #VRay Dome
			# 	node = pm.
			# elif index==8: #VRay Rect
			# 	node = pm.
			# elif index==9: #VRay IES
			# 	node = pm.

		if selection: #if there is a current selection, move the object to that selection's bounding box center.
			center_pos = Init.getCenterPoint(selection)
			pm.xform(node, translation=center_pos, worldSpace=1, absolute=1)
			boundingBoxScale = Init.matchScale(node, selection)

		pm.selectMode(object=1) #place scene select type in object mode.
		pm.select(node) #select the transform node so that you can see any edits

		return self.getHistoryNode(node)


	def createPrimitive(self, catagory1, catagory2):
		'''ie. createPrimitive('Polygons', 'Cube')
		:Parameters:
			type1 (str) = 
			type2 (str) = 
		'''
		cmb001 = self.create_ui.cmb001
		cmb002 = self.create_ui.cmb002

		cmb001.setCurrentIndex(cmb001.findText(catagory1))
		cmb002.setCurrentIndex(cmb002.findText(catagory2))
		self.b000()


	def b001(self):
		'''Create poly cube
		'''
		self.createPrimitive('Polygon', 'Cube')


	def b002(self):
		'''Create poly sphere
		'''
		self.createPrimitive('Polygon', 'Sphere')


	def b003(self):
		'''Create poly cylinder
		'''
		self.createPrimitive('Polygon', 'Cylinder')


	def b004(self):
		'''Create poly plane
		'''
		self.createPrimitive('Polygon', 'Plane')









#module name
print(os.path.splitext(os.path.basename(__file__))[0])
# -----------------------------------------------
# Notes
# -----------------------------------------------



# deprecated:

	# self.rotation = {'x':[90,0,0], 'y':[0,90,0], 'z':[0,0,90], '-x':[-90,0,0], '-y':[0,-90,0], '-z':[0,0,-90], 'last':[]}
	# self.point=[0,0,0]

	# @property
	# def node(self):
	# 	'''Get the Transform Node
	# 	'''
	# 	transform = Init.getTransformNode()
	# 	if transform:
	# 		if not self.create_ui.txt003.text()==transform[0].name(): #make sure the same field reflects the current working node.
	# 			self.create_ui.txt003.setText(transform[0].name())

	# 	return transform

	# def rotateAbsolute(self, axis, node):
	# 	'''undo previous rotation and rotate on the specified axis.
	# 	uses an external rotation dictionary.

	# 	:Parameters:
	# 		axis (str) = axis to rotate on. ie. '-x'
	# 		node (obj) = transform node.
	# 	'''
	# 	axis = self.rotation[axis]

	# 	rotateOrder = pm.xform(node, query=1, rotateOrder=1)
	# 	pm.xform(node, preserve=1, rotation=axis, rotateOrder=rotateOrder, absolute=1)
	# 	self.rotation['last'] = axis

	# def txt003(self):
	# 	'''Set Name
	# 	'''
	# 	if self.node:
	# 		pm.rename(self.node.name(), self.create_ui.txt003.text())

	# def getAxis(self):
	# 	''''''
	# 	if self.create_ui.chk000.isChecked():
	# 		axis = 'x'
	# 	elif self.create_ui.chk001.isChecked():
	# 		axis = 'y'
	# 	elif self.create_ui.chk002.isChecked():
	# 		axis = 'z'
	# 	if self.create_ui.chk003.isChecked(): #negative
	# 		axis = '-'+axis
	# 	return axis


	# def chk000(self, state=None):
	# 	'''Rotate X Axis
	# 	'''
	# 	self.toggleWidgets(setChecked='chk000', setUnChecked='chk001, chk002')
	# 	if self.node:
	# 		self.rotateAbsolute(self.getAxis(), self.node)


	# def chk001(self, state=None):
	# 	'''Rotate Y Axis
	# 	'''
	# 	self.toggleWidgets(setChecked='chk001', setUnChecked='chk000, chk002')
	# 	if self.node:
	# 		self.rotateAbsolute(self.getAxis(), self.node)


	# def chk002(self, state=None):
	# 	'''Rotate Z Axis
	# 	'''
	# 	self.toggleWidgets(setChecked='chk002', setUnChecked='chk000, chk001')
	# 	if self.node:
	# 		self.rotateAbsolute(self.getAxis(), self.node)


	# def chk003(self, state=None):
	# 	'''Rotate Negative Axis
	# 	'''
	# 	if self.node:
	# 		self.rotateAbsolute(self.getAxis(), self.node)

		# def chk005(self, state=None):
		# '''Set Point
		# '''
		# #add support for averaging multiple components.
		# selection = pm.ls(selection=1, flatten=1)
		# try:
		# 	self.point = pm.xform(selection, query=1, translation=1, worldSpace=1, absolute=1)
		# except:
		# 	self.point = [0,0,0]
		# 	print('Warning: Nothing selected. Point set to origin [0,0,0].')

		# self.create_ui.s000.setValue(self.point[0])
		# self.create_ui.s001.setValue(self.point[1])
		# self.create_ui.s002.setValue(self.point[2])


	# def s000(self, value=None):
	# 	'''Set Translate X
	# 	'''
	# 	if self.node:
	# 		self.point[0] = self.create_ui.s000.value()
	# 		pm.xform(self.node, translation=self.point, worldSpace=1, absolute=1)


	# def s001(self, value=None):
	# 	'''Set Translate Y
	# 	'''
	# 	if self.node:
	# 		self.point[1] = self.create_ui.s001.value()
	# 		pm.xform(self.node, translation=self.point, worldSpace=1, absolute=1)


	# def s002(self, value=None):
	# 	'''Set Translate Z
	# 	'''
	# 	if self.node:
	# 		self.point[2] = self.create_ui.s002.value()
	# 		pm.xform (self.node, translation=self.point, worldSpace=1, absolute=1)