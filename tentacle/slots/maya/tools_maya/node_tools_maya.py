# !/usr/bin/python
# coding=utf-8
try:
	import pymel.core as pm
except ImportError as error:
	print (__file__, error)



class Node_tools_maya():
	'''
	'''

	@staticmethod
	def getType(obj, returnType='str'):
		'''Get the type of a given object.

		:Parameters:
			obj (obj) = A single maya component.
			returnType (str) = Specify the desired return value type. (valid: 'str' (default), 'int')
								'str' - will return the object type as a string.
								'int' - will return the maya mask value as an integer.
		:Return:
			(str)(int) dependant on returnType parameter.
		'''
		types = {
			0:'Handle', 9:'Nurbs Curve', 10:'Nurbs Surfaces', 11:'Nurbs Curves On Surface', 12:'Polygon', 
			22:'Locator XYZ', 23:'Orientation Locator', 24:'Locator UV', 28:'Control Vertex', 30:'Edit Point', 
			31:'Polygon Vertex', 32:'Polygon Edge', 34:'Polygon Face', 35:'Polygon UV', 36:'Subdivision Mesh Point', 
			37:'Subdivision Mesh Edge', 38:'Subdivision Mesh Face', 39:'Curve Parameter Point', 40:'Curve Knot', 
			41:'Surface Parameter Point', 42:'Surface Knot', 43:'Surface Range', 44:'Trim Surface Edge', 
			45:'Surface Isoparm', 46:'Lattice Point', 47:'Particle', 49:'Scale Pivot', 50:'Rotate Pivot', 
			51:'Select Handle', 68:'Subdivision Surface', 70:'Polygon Vertex Face', 72:'NURBS Surface Face', 
			73:'Subdivision Mesh UV',
		}

		for k, v in types.items(): #get the matching type from the types dict.
			if pm.filterExpand(obj, sm=k):
				return k if returnType=='int' else v


	@staticmethod
	def getMelGlobals(keyword=None, caseSensitive=False):
		'''Get global MEL variables.

		:Parameters:
			keyword (str) = search string.

		:Return:
			(list)
		'''
		variables = [
			v for v in sorted(mel.eval('env')) 
				if not keyword 
					or (v.count(keyword) if caseSensitive else v.lower().count(keyword.lower()))
		]

		return variables


	@staticmethod
	def getObjectFromComponent(components, returnType='transform'):
		'''Get the object's transform, shape, or history node from the given components.

		:Parameters:
			components (str)(obj(list) = Component(s).
			returnType (str) = The desired returned node type. (valid: 'transform','shape','history')(default: 'transform')

		:Return:
			(dict) {transform node: [components of that node]}
			ie. {'pCube2': ['pCube2.f[21]', 'pCube2.f[22]', 'pCube2.f[25]'], 'pCube1': ['pCube1.f[21]', 'pCube1.f[26]']}
		'''
		result={}
		for component in pm.ls(components):
			shapeNode = pm.listRelatives(component, parent=1)[0] #set(pm.ls(components, transform=1))
			transform = pm.listRelatives(shapeNode, parent=1)[0] #set(pm.ls(components, shape=1))

			if returnType=='transform':
				node = transform
			elif returnType=='shape':
				node = shapeNode
			elif returnType=='history':
				history = pm.listConnections(shapeNode, source=1, destination=0)[0] #get incoming connections: returns list ie. [nt.PolyCone('polyCone1')]
				node = history

			try:
				result[node].append(component)
			except:
				result[node] = [component]

		return result


	@staticmethod
	def isGroup(node):
		'''Check if the given node is a group.
		'''
		for child in node.getChildren():
			if type(child) is not pm.nodetypes.Transform:
				return False
		return True


	@staticmethod
	def getTransformNode(node, attributes=False, regEx=''):
		'''Get the transform node(s).

		:Parameters:
			node (obj) = A relative of a transform Node.
			attributes (bool) = Return the attributes of the node, rather then the node itself.
			regEx (str) = List only the attributes that match the string(s) passed from this flag. String can be a regular expression.

		:Return:
			(list) node(s) or node attributes.

		[pm.PyNode(n).getTransform() for n in objects]
		'''
		transforms = pm.ls(node, type='transform')
		if not transforms: #from shape
			shapeNodes = pm.ls(node, objectsOnly=1)
			transforms = pm.listRelatives(shapeNodes, parent=1)
			if not transforms: #from history
				try:
					transforms = pm.listRelatives(pm.listHistory(node, future=1), parent=1)
				except Exception as error:
					transforms = []

		if attributes:
			transforms = pm.listAttr(transforms, read=1, hasData=1, string=regEx)

		return list(set(transforms))


	@classmethod
	def getShapeNode(cls, node=None, attributes=False, regEx=''):
		'''Get the shape node(s).

		:Parameters:
			node (obj) = A relative of a shape Node.
			attributes (bool) = Return the attributes of the node, rather then the node itself.
			regEx (str) = 	List only the attributes that match the string(s) passed from this flag. String can be a regular expression.

		:Return:
			(list) node(s) or node attributes.

		[pm.PyNode(n).getShape() for n in objects]
		'''
		shapes = pm.listRelatives(node, children=1, shapes=1) #get shape node from transform: returns list ie. [nt.Mesh('pConeShape1')]
		if not shapes:
			shapes = pm.ls(node, type='shape')
			if not shapes: #get shape from transform
				try:
					transforms = pm.listRelatives(pm.listHistory(node, future=1), parent=1)
					shapes = cls.getShapeNode(transforms)
				except Exception as error:
					shapes = []

		if attributes:
			shapes = pm.listAttr(shapes, read=1, hasData=1, string=regEx)

		return list(set(shapes))


	@staticmethod
	def getHistoryNode(node=None, attributes=False, regEx=''):
		'''Get the history node(s).

		:Parameters:
			node (obj) = A relative of a history Node.
			attributes (bool) = Return the attributes of the node, rather then the node itself.
			regEx (str) = 	List only the attributes that match the string(s) passed from this flag. String can be a regular expression.

		:Return:
			(list) node(s) or node attributes.

		[pm.PyNode(n).getHistory() for n in objects]
		'''
		shapes = pm.listRelatives(node, children=1, shapes=1) #get shape node from transform: returns list ie. [nt.Mesh('pConeShape1')]
		connections = pm.listConnections(shapes, source=1, destination=0) #get incoming connections: returns list ie. [nt.PolyCone('polyCone1')]
		if not connections:
			try:
				connections = node.history()[-1]
			except AttributeError as error:
				print ('error:', error)
				connections = [] #object has no attribute 'history'

		if attributes:
			connections = pm.listAttr(connections, read=1, hasData=1, string=regEx)

		return connections


	@staticmethod
	def getAllParents(node):
		'''List ALL parents of an object
		'''
		objects = pm.ls(node, l=1)
		tokens=[]

		return objects[0].split("|")


	@staticmethod
	def getParameterValuesMEL(node, cmd, parameters):
		'''Query a Maya command, and return a key(the parameter):value pair for each of the given parameters.

		:Parameters:
			node (str)(obj)(list) = The object to query attributes of.
			parameters (list) = The command parameters to query. ie. ['enableTranslationX','translationX']

		:Return:
			(dict) {'parameter name':<value>} ie. {'enableTranslationX': [False, False], 'translationX': [-1.0, 1.0]}

		ex. call: attrs = getParameterValuesMEL(obj, 'transformLimits', ['enableTranslationX','translationX'])
		'''
		cmd = getattr(pm, cmd)
		node = pm.ls(node)[0]

		result={}
		for p in parameters:
			values = cmd(node, **{'q':True, p:True}) #query the parameter to get it's value.

			# for n, i in enumerate(values): #convert True|False to 1|0
			# 	if i==True:
			# 		values[n] = 1
			# 	elif i==False:
			# 		values[n] = 0

			result[p] = values

		return result


	@staticmethod
	def setParameterValuesMEL(node, cmd, parameters):
		'''Set parameters using a maya command.

		:Parameters:
			node (str)(obj)(list) = The object to query attributes of.
			parameters (dict) = The command's parameters and their desired values. ie. {'enableTranslationX': [False, False], 'translationX': [-1.0, 1.0]}

		ex. call: setParameterValuesMEL(obj, 'transformLimits', {'enableTranslationX': [False, False], 'translationX': [-1.0, 1.0]})
		'''
		cmd = getattr(pm, cmd)
		node = pm.ls(node)[0]

		for p, v in parameters.items():
		 	cmd(node, **{p:v})


	@staticmethod
	def getAttributesMEL(node, include=[], exclude=[]):
		'''Get node attributes and their corresponding values as a dict.

		:Parameters:
			node (obj) = The node to get attributes for.
			include (list) = Attributes to include. All other will be omitted. Exclude takes dominance over include. Meaning, if the same attribute is in both lists, it will be excluded.
			exclude (list) = Attributes to exclude from the returned dictionay. ie. ['Position','Rotation','Scale','renderable','isHidden','isFrozen','selected']

		:Return:
			(dict) {'string attribute': current value}
		'''
		if not all((include, exclude)):
			exclude = ['message', 'caching', 'frozen', 'isHistoricallyInteresting', 'nodeState', 'binMembership', 'output', 'edgeIdMap', 'miterAlong', 'axis', 'axisX', 'axisY', 
				'axisZ', 'paramWarn', 'uvSetName', 'createUVs', 'texture', 'maya70', 'inputPolymesh', 'maya2017Update1', 'manipMatrix', 'inMeshCache', 'faceIdMap', 'subdivideNgons', 
				'useOldPolyArchitecture', 'inputComponents', 'vertexIdMap', 'binMembership', 'maya2015', 'cacheInput', 'inputMatrix', 'forceParallel', 'autoFit', 'maya2016SP3', 
				'maya2017', 'caching', 'output', 'useInputComp', 'worldSpace', 'taperCurve_Position', 'taperCurve_FloatValue', 'taperCurve_Interp', 'componentTagCreate', 
				'isCollapsed', 'blackBox', 'viewMode', 'templateVersion', 'uiTreatment', 'boundingBoxMinX', 'boundingBoxMinY', 'boundingBoxMinZ', 'boundingBoxMaxX', 'boundingBoxMaxY', 
				'boundingBoxMaxZ', 'boundingBoxSizeX', 'boundingBoxSizeY', 'boundingBoxSizeZ', 'boundingBoxCenterX', 'boundingBoxCenterY', 'boundingBoxCenterZ', 'visibility', 
				'intermediateObject', 'template', 'objectColorR', 'objectColorG', 'objectColorB', 'wireColorR', 'wireColorG', 'wireColorB', 'useObjectColor', 'objectColor', 
				'overrideDisplayType', 'overrideLevelOfDetail', 'overrideShading', 'overrideTexturing', 'overridePlayback', 'overrideEnabled', 'overrideVisibility', 'hideOnPlayback', 
				'overrideRGBColors', 'overrideColor', 'overrideColorR', 'overrideColorG', 'overrideColorB', 'lodVisibility', 'selectionChildHighlighting', 'identification', 
				'layerRenderable', 'layerOverrideColor', 'ghosting', 'ghostingMode', 'ghostPreFrames', 'ghostPostFrames', 'ghostStep', 'ghostFarOpacity', 'ghostNearOpacity', 
				'ghostColorPreR', 'ghostColorPreG', 'ghostColorPreB', 'ghostColorPostR', 'ghostColorPostG', 'ghostColorPostB', 'ghostUseDriver', 'hiddenInOutliner', 'useOutlinerColor', 
				'outlinerColorR', 'outlinerColorG', 'outlinerColorB', 'renderType', 'renderVolume', 'visibleFraction', 'hardwareFogMultiplier', 'motionBlur', 'visibleInReflections', 
				'visibleInRefractions', 'castsShadows', 'receiveShadows', 'asBackground', 'maxVisibilitySamplesOverrider', 'maxVisibilitySamples', 'geometryAntialiasingOverride', 
				'antialiasingLevel', 'shadingSamplesOverride', 'shadingSamples', 'maxShadingSamples','volumeSamplesOverride', 'volumeSamples', 'depthJitter', 'IgnoreSelfShadowing', 
				'primaryVisibility', 'tweak', 'relativeTweak', 'uvPivotX', 'uvPivotY', 'displayImmediate', 'displayColors', 'ignoreHwShader', 'holdOut', 'smoothShading', 
				'boundingBoxScaleX', 'boundingBoxScaleY', 'boundingBoxScaleZ', 'featureDisplacement', 'randomSeed', 'compId', 'weight', 'gravityX', 'gravityY', 'gravityZ', 'attraction', 
				'magnX', 'magnY', 'magnZ', 'maya2012', 'maya2018', 'newThickness', 'compBoundingBoxMinX', 'compBoundingBoxMinY', 'compBoundingBoxMinZ', 'compBoundingBoxMaxX', 
				'compBoundingBoxMaxY', 'compBoundingBoxMaxZ', 'hyperLayout', 'borderConnections', 'isHierarchicalConnection', 'rmbCommand', 'templateName', 'templatePath', 'viewName', 
				'iconName', 'customTreatment', 'creator', 'creationDate', 'containerType', 'boundingBoxMin', 'boundingBoxMax', 'boundingBoxSize', 'matrix', 'inverseMatrix', 'worldMatrix', 
				'worldInverseMatrix', 'parentMatrix', 'parentInverseMatrix', 'instObjGroups', 'wireColorRGB', 'drawOverride', 'overrideColorRGB', 'renderInfo', 'ghostCustomSteps', 
				'ghostsStep', 'ghostFrames', 'ghostOpacityRange', 'ghostColorPre', 'ghostColorPost', 'ghostDriver', 'outlinerColor', 'shadowRays', 'rayDepthLimit', 'centerOfIllumination', 
				'pointCamera', 'pointCameraX', 'pointCameraY', 'pointCameraZ', 'matrixWorldToEye', 'matrixEyeToWorld', 'objectId', 'primitiveId', 'raySampler', 'rayDepth', 'renderState', 
				'locatorScale', 'uvCoord', 'uCoord', 'vCoord', 'uvFilterSize', 'uvFilterSizeX', 'uvFilterSizeY', 'infoBits', 'lightData', 'lightDirectionX', 'lightDirectionY', 'lightDirectionZ', 
				'lightIntensityR', 'lightIntensityG', 'lightIntensityB', 'lightShadowFraction', 'preShadowIntensity', 'lightBlindData', 'opticalFXvisibility', 'opticalFXvisibilityR', 
				'opticalFXvisibilityG', 'opticalFXvisibilityB', 'rayInstance', 'ambientShade', 'objectType', 'shadowRadius', 'castSoftShadows', 'normalCamera', 'normalCameraX', 'normalCameraY', 
				'normalCameraZ', 'color', 'shadowColor', 'decayRate', 'emitDiffuse', 'emitSpecular', 'lightRadius', 'reuseDmap', 'useMidDistDmap', 'dmapFilterSize', 'dmapResolution', 
				'dmapFocus', 'dmapWidthFocus', 'useDmapAutoFocus', 'volumeShadowSamples', 'fogShadowIntensity', 'useDmapAutoClipping', 'dmapNearClipPlane', 'dmapFarClipPlane', 
				'useOnlySingleDmap', 'useXPlusDmap', 'useXMinusDmap', 'useYPlusDmap', 'useYMinusDmap', 'useZPlusDmap', 'useZMinusDmap', 'dmapUseMacro', 'dmapName', 'dmapLightName', 
				'dmapSceneName', 'dmapFrameExt', 'writeDmap', 'lastWrittenDmapAnimExtName', 'useLightPosition', 'lightAngle', 'pointWorld', 'pointWorldX', 'pointWorldY', 'pointWorldZ', 

			]
		# print('node:', node); print('attr:', pm.listAttr(node))
		attributes={} 
		for attr in pm.listAttr(node):
			if not attr in exclude and (attr in include if include else attr not in include): #ie. pm.getAttr('polyCube1.subdivisionsDepth')
				try:
					attributes[attr] = pm.getAttr(getattr(node, attr), silent=True) #get the attribute's value.
				except Exception as error:
					print (error)

		return attributes


	@staticmethod
	def setAttributesMEL(node, attributes):
		'''Set node attribute values using a dict.

		:Parameters:
			node (obj) = The node to set attributes for.
			attributes (dict) = Attributes and their correponding value to set. ie. {'string attribute': value}

		ex call:
		self.setAttributesMEL(obj, {'smoothLevel':1})
		'''
		[pm.setAttr(getattr(node, attr), value)
			for attr, value in attributes.items() 
				if attr and value] #ie. pm.setAttr('polyCube1.subdivisionsDepth', 5)


	@staticmethod
	def connectAttributes(attr, place, file):
		'''A convenience procedure for connecting common attributes between two nodes.

		:Parameters:
			attr () = 
			place () = 
			file () = 

		// Use convenience command to connect attributes which share 
		// their names for both the placement and file nodes.
		self.connectAttributes('coverage', 'place2d', fileNode')
		self.connectAttributes('translateFrame', 'place2d', fileNode')
		self.connectAttributes('rotateFrame', 'place2d', fileNode')
		self.connectAttributes('mirror', 'place2d', fileNode')
		self.connectAttributes('stagger', 'place2d', fileNode')
		self.connectAttributes('wrap', 'place2d', fileNode')
		self.connectAttributes('wrapV', 'place2d', fileNode')
		self.connectAttributes('repeatUV', 'place2d', fileNode')
		self.connectAttributes('offset', 'place2d', fileNode')
		self.connectAttributes('rotateUV', 'place2d', fileNode')

		// These two are named differently.
		connectAttr -f ( $place2d + ".outUV" ) ( $fileNode + ".uv" );
		connectAttr -f ( $place2d + ".outUvFilterSize" ) ( $fileNode + ".uvFilterSize" );
		'''
		pm.connectAttr((place + "." + attr), (file + "." + attr), f=1)


