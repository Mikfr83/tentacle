# !/usr/bin/python
# coding=utf-8
import pymel.core as pm

from node_tools_maya import Node_tools_maya



class GetComponents():
	'''
	'''

	@classmethod
	def convertComponentType(cls, components, componentType):
		'''
		'''
		d = {'vtx':'toVertex', 'e':'toEdge', 'uv':'toUV', 'f':'toFace'}
		typ = cls.convertComponentName(componentType, returnType='abv') #get the correct componentType variable from possible args.
		components = pm.polyListComponentConversion(components, **{d[typ.lower()]:True})
		return components


	@classmethod
	def convertComponentName(cls, componentType, returnType='abv'):
		'''Return an alternate component alias for the given alias. ie. a hex value of 0x0001 for 'vertex'
		If nothing is found, a value of 'None' will be returned.

		:Parameters:
			componentType (str) = Component type as a string.
			returnType (str) = The desired returned alias. (valid: 'abv', 'singular', 'plural', 'full', 'int', 'hex')

		:Return:
			(str)(int)(hex)(None) dependant on returnType argument.

		ex. call: convertComponentName('control vertex', 'hex')
		'''
		rtypes = ('abv', 'singular', 'plural', 'full', 'int', 'hex')
		types = [
			('vtx', 'vertex', 'vertices', 'Polygon Vertex', 31, 0x0001),
			('e', 'edge', 'edges', 'Polygon Edge', 32, 0x8000),
			('f', 'face', 'faces', 'Polygon Face', 34, 0x0008),
			('cv', 'control vertex', 'control vertices', 'Control Vertex', 28, 0x0010),
			('uv', 'texture', 'texture coordinates', 'Polygon UV', 35, 0x0010),
		]

		result = None
		for t in types:
			if componentType in t:
				index = rtypes.index(returnType)
				result = t[index]
				break

		return result


	@classmethod
	def convertReturnType(cls, objects, returnType='str', returnNodeType='shape', flatten=False):
		'''Convert objects to/from <obj>, 'strings', integers.

		:Parameters:
			objects (str)(obj)(list) = The object(s) to convert.
			returnType (str) = The desired returned object type. (valid: 'str', 'obj', 'int') ('int' valid only at sub-object level).
			returnNodeType (str) = Specify whether objects are returned with transform or shape nodes (valid only with str returnTypes). (valid: 'transform', 'shape'(default)) ex. 'pCylinder1.f[0]' or 'pCylinderShape1.f[0]'
			flatten (bool) = Flattens the returned list of objects so that each component is identified individually.

		:Return:
			(list)(dict) Dependant on flags.

		ex. call: convertReturnType(<edges>, 'str', flatten=True) #returns a list of string object names from a list of edge objects.
		'''
		if returnType=='str':
			objects = pm.ls(objects, flatten=flatten)
			result = [str(c) for c in objects]

			if returnNodeType=='transform':
				result = [str(''.join(c.rsplit('Shape', 1))) for c in result]


		elif returnType=='obj':
			result = pm.ls(objects, flatten=flatten)

		else: #returnType=='int':
			result={}
			for c in pm.ls(objects, flatten=True):
				obj = pm.ls(c, objectsOnly=1)[0]
				num = c.split('[')[-1].rstrip(']')

				try:
					if flatten:
						componentNum = int(num)
					else:
						n = [int(n) for n in num.split(':')]
						componentNum = tuple(n) if len(n)>1 else n[0]

					if obj in result: #append to existing object key.
						result[obj].append(componentNum)
					else:
						result[obj] = [componentNum]
				except ValueError as error: #incompatible object type.
					break; print ('# Error: {}.convertReturnType(): unable to convert {} {} to int. {}. #'.format(__name__, obj, num, error)) 

		return result


	@classmethod
	def getComponents(cls, objects=None, componentType=None, returnType='str', returnNodeType='shape', randomize=0, flatten=False):
		'''Get the components of the given type from the given object(s).
		If no objects are given the current selection will be used.

		:Parameters:
			objects (str)(obj)(list) = The object(s) to get the components of. (Polygon, Polygon components)(default: current selection)
			componentType (str)(int) = The desired component mask. (valid: any type allowed in the 'convertComponentName' method)
			returnType (str) = The desired returned object type. (valid: 'str', 'obj', 'int')
			returnNodeType (str) = Specify whether the components are returned with the transform or shape nodes (valid only with str returnTypes). (valid: 'transform', 'shape'(default)) ex. 'pCylinder1.f[0]' or 'pCylinderShape1.f[0]'
			randomize (float) = If a 0.1-1 value is given, random components will be returned with a quantity determined by the given ratio. A value of 0.5 will return a 50% of the components of an object in random order.
			flatten (bool) = Flattens the returned list of objects so that each component is it's own element.

		:Return:
			(list)(dict) Dependant on flags.

		ex. getComponents(componentType='faces' returnType='obj', randomize=0.5) #return random faces from the selected object.
		'''
		if objects is None:
			objects = pm.ls(orderedSelection=1)

		transforms = pm.ls(objects, transforms=1)

		if transforms:
			typ = componentType if componentType else Node_tools_maya.getType(transforms) #get component type from the current selection if it is not explicitly given.
			formattedType = cls.convertComponentName(typ, returnType='abv') #get the correct componentType variable from possible args.
			components = ['{}.{}[*]'.format(i, formattedType) for i in transforms] #get ALL components, for each given transform object.
		else: #the given objects are components.
			components = cls.convertComponentType(objects, componentType) if componentType else objects

		if randomize:
			from math_tools import Math_tools
			components = Math_tools.randomize(pm.ls(components, flatten=1), randomize)

		result = cls.convertReturnType(components, returnType=returnType, returnNodeType=returnNodeType, flatten=flatten)

		return result



class Component_tools_maya(GetComponents):
	'''
	'''
	@staticmethod
	def getContigiousEdges(edges):
		'''Get a list containing sets of adjacent edges.

		:Parameters:
			edges (list) = Polygon edges to be filtered for adjacent.

		:Return:
			(list) adjacent edge sets.
		'''
		sets=[]
		edges = pm.ls(edges, flatten=1)
		for edge in edges:
			vertices = pm.polyListComponentConversion(edge, fromEdge=1, toVertex=1)
			connEdges = pm.polyListComponentConversion(vertices, fromVertex=1, toEdge=1)
			edge_set = set([e for e in pm.ls(connEdges, flatten=1) if e in edges]) #restrict the connected edges to the original edge pool.
			sets.append(edge_set)

		result=[]
		while len(sets)>0: #combine sets in 'sets' that share common elements.
			first, rest = sets[0], sets[1:] #python 3: first, *rest = sets
			first = set(first)

			lf = -1
			while len(first)>lf:
				lf = len(first)

				rest2 = []
				for r in rest:
					if len(first.intersection(set(r)))>0:
						first |= set(r)
					else:
						rest2.append(r)     
				rest = rest2

			result.append(first)
			sets = rest

		return result


	@staticmethod
	def getContigiousIslands(faces, faceIslands=[]):
		'''Get a list containing sets of adjacent polygon faces grouped by islands.

		:Parameters:
			faces (list) = Polygon faces to be filtered for adjacent.
			faceIslands (list) = optional. list of sets. ability to add faces from previous calls to the return value.

		:Return:
			(list) of sets of adjacent faces.
		'''
		sets=[]
		faces = pm.ls(faces, flatten=1)
		for face in faces:
			edges = pm.polyListComponentConversion(face, fromFace=1, toEdge=1)
			borderFaces = pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toFace=1), flatten=1)
			set_ = set([str(f) for f in borderFaces if f in faces])
			if set_:
				sets.append(set_)

		while len(sets)>0: #combine sets in 'sets' that share common elements.
			first, rest = sets[0], sets[1:] #python 3: first, *rest = sets
			first = set(first)

			lf = -1
			while len(first)>lf:
				lf = len(first)

				rest2 = []
				for r in rest:
					if len(first.intersection(set(r)))>0:
						first |= set(r)
					else:
						rest2.append(r)     
				rest = rest2

			faceIslands.append(first)
			sets = rest

		return faceIslands


	@staticmethod
	def getIslands(obj, returnType='str'):
		'''Get the group of components in each separate island of a combined mesh.

		:parameters:
			obj (str)(obj)(list) = The object to get shells from.
			returnType (bool) = Return the shell faces as a list of type: 'str' (default), 'int', or 'obj'.

		:return:
			(list)
		'''
		num_shells = pm.polyEvaluate(obj, shell=True)
		num_faces = pm.polyEvaluate(obj, face=True)

		unprocessed = set(range(num_faces))

		shells=[]
		while unprocessed:
			index = next(iter(unprocessed)) #face_index
			faces = pm.polySelect(obj, extendToShell=index, noSelection=True) #shell faces

			if returnType=='str':
				yield ["{}.f[{}]".format(obj, index) for index in faces]

			elif returnType=='int':
				yield [index for index in faces]

			elif returnType=='obj':
				yield [pm.ls("{}.f[{}]".format(obj, index))[0] for index in faces]

			unprocessed.difference_update(faces)


	@classmethod
	def getBorderComponents(cls, x, returnCompType='default', borderType='object', returnType='str', flatten=False):
		'''Get any object border components from given component(s) or a polygon object.

		:Parameters:
			x (obj)(list) = Component(s) (or a polygon object) to find any border components for.
			returnCompType (str) = The desired returned component type. (valid: 'vertices','edges','faces','default'(the returnCompType will be the same as the given component type, or edges if an object is given))
			borderType (str) = Get the components that border given components, or components on the border of an object. (valid: 'component', 'object'(default))
			returnType (str) = Return objects or string names of the components. (valid: 'str', 'obj')
			flatten (bool) = Flattens the returned list of objects so that each component is identified individually.

		:Return:
			(list)

		ex. borderVertices = getBorderComponents(selection, returnCompType='vertices', borderType='component', flatten=True)
		'''
		x = pm.ls(x)
		if not x:
			print ('# Error: Operation requires an selected object or components. #')
			return []

		object_type = Node_tools_maya.getType(x[0])
		if object_type=='Polygon':
			x = cls.getComponents(x, 'edges')
		elif object_type=='Polygon Vertex':
			x = pm.polyListComponentConversion(x, fromVertex=1, toEdge=1)
		elif object_type=='Polygon Face':
			x = pm.polyListComponentConversion(x, fromFace=1, toEdge=1)

		result=[]
		edges = pm.ls(x, flatten=1)

		if borderType=='object': #get edges that form the border of the object.
			for edge in edges:
				attachedFaces = pm.ls(pm.polyListComponentConversion(edge, fromEdge=1, toFace=1), flatten=1)
				if len(attachedFaces)==1:
					result.append(edge)

		elif borderType=='component' and not object_type=='Polygon': #get edges that form the border of the given components.
			for edge in edges:
				attachedFaces = pm.polyListComponentConversion(edge, fromEdge=1, toFace=1)
				attachedEdges = pm.ls(pm.polyListComponentConversion(attachedFaces, fromFace=1, toEdge=1), flatten=1)
				for e in attachedEdges:
					if e not in edges:
						result.append(edge)
						break

		if returnCompType=='default': #if no returnCompType is specified, return the same type of component as given. in the case of 'Polygon' object, edges will be returned.
			returnCompType = object_type if not object_type=='Polygon' else 'Polygon Edge'
		#convert back to the original component type and flatten /un-flatten list.
		if returnCompType in ('Polygon Vertex', 'vertices', 'vertex', 'vtx'):
			result = pm.ls(pm.polyListComponentConversion(result, fromEdge=1, toVertex=1), flatten=flatten) #vertices.
		elif returnCompType in ('Polygon Edge', 'edges', 'edge', 'e'):
			result = pm.ls(pm.polyListComponentConversion(result, fromEdge=1, toEdge=1), flatten=flatten) #edges.
		elif returnCompType in ('Polygon Face', 'faces', 'face', 'f'):
			result = pm.ls(pm.polyListComponentConversion(result, fromEdge=1, toFace=1), flatten=flatten) #faces.

		if returnType=='str':
			result = [str(i) for i in result]

		return result


	@staticmethod
	def getClosestVerts(set1, set2, tolerance=1000):
		'''Find the two closest vertices between the two sets of vertices.

		:Parameters:
			set1 (str)(list) = The first set of vertices.
			set2 (str)(list) = The second set of vertices.
			tolerance (int) = Maximum search distance.

		:Return:
			(list) closest vertex pairs by order of distance (excluding those not meeting the tolerance). (<vertex from set1>, <vertex from set2>).

		ex. verts1 = getComponents('pCube1', 'vertices')
			verts2 = getComponents(pCube2', 'vertices')
			closestVerts = getClosestVerts(verts1, verts2)
		'''
		set1 = [str(i) for i in pm.ls(set1, flatten=1)]
		set2 = [str(i) for i in pm.ls(set2, flatten=1)]
		vertPairsAndDistance={}
		for v1 in set1:
			v1Pos = pm.pointPosition(v1, world=1)
			for v2 in set2:
				v2Pos = pm.pointPosition(v2, world=1)
				from math_tools import Math_tools
				distance = Math_tools.getDistanceBetweenTwoPoints(v1Pos, v2Pos)
				if distance<tolerance:
					vertPairsAndDistance[(v1, v2)] = distance

		import operator
		sorted_ = sorted(vertPairsAndDistance.items(), key=operator.itemgetter(1))

		vertPairs = [i[0] for i in sorted_]

		return vertPairs


	@staticmethod
	def getClosestVertex(vertices, obj, tolerance=0.0, freezeTransforms=False):
		'''Find the closest vertex of the given object for each vertex in the list of given vertices.

		:Parameters:
			vertices (list) = A set of vertices.
			obj (obj) = The reference object in which to find the closest vertex for each vertex in the list of given vertices.
			tolerance (float) = Maximum search distance. Default is 0.0, which turns off the tolerance flag.
			freezeTransforms (bool) = Reset the selected transform and all of its children down to the shape level.

		:Return:
			(dict) closest vertex pairs {<vertex from set1>:<vertex from set2>}.

		ex. obj1, obj2 = selection
			vertices = getComponents(obj1, 'vertices')
			closestVerts = getClosestVertex(vertices, obj2, tolerance=10)
		'''
		vertices = [str(i) for i in pm.ls(vertices, flatten=1)]
		pm.undoInfo(openChunk=True)

		if freezeTransforms:
			pm.makeIdentity(obj, apply=True)

		obj2Shape = pm.listRelatives(obj, children=1, shapes=1)[0] #pm.listRelatives(obj, fullPath=False, shapes=True, noIntermediate=True)

		cpmNode = pm.ls(pm.createNode('closestPointOnMesh'))[0] #create a closestPointOnMesh node.
		pm.connectAttr(obj2Shape.outMesh, cpmNode.inMesh, force=1) #object's shape mesh output to the cpm node.

		closestVerts={}
		for v1 in vertices: #assure the list of vertices is a flattened list of stings. prevent unhashable type error when closestVerts[v1] = v2.  may not be needed with python versions 3.8+
			v1Pos = pm.pointPosition(v1, world=True)
			pm.setAttr(cpmNode.inPosition, v1Pos[0], v1Pos[1], v1Pos[2], type="double3") #set a compound attribute

			index = pm.getAttr(cpmNode.closestVertexIndex) #vertex Index. | ie. result: [34]
			v2 = obj2Shape.vtx[index]

			v2Pos = pm.pointPosition(v2, world=True)
			distance = Slots.getDistanceBetweenTwoPoints(v1Pos, v2Pos)

			if not tolerance:
				closestVerts[v1] = v2
			elif distance < tolerance:
				closestVerts[v1] = v2

		pm.delete(cpmNode)
		pm.undoInfo(closeChunk=True)

		return closestVerts


	@classmethod
	def getEdgePath(cls, components, returnType='edgeLoop'):
		'''Query the polySelect command for the components along different edge paths.
		Supports components from a single object.

		:Parameters:
			components (str)(obj)(list) = The components used for the query (dependant on the operation type).
			returnType (str) = The desired return type. 'shortestEdgePath', 'edgeRing', 'edgeRingPath', 'edgeLoop', 'edgeLoopPath'.

		:Return:
			(list) The components comprising the path.
		'''
		obj = pm.ls(components, objectsOnly=1)[0]

		result=[]
		componentNumbers = list(cls.convertReturnType(components, returnType='int', flatten=1).values())[0] #get the vertex numbers as integer values. ie. [818, 1380]

		if returnType=='shortestEdgePath':
			edgesLong = pm.polySelect(obj, query=1, shortestEdgePath=(componentNumbers[0], componentNumbers[1])) #(vtx, vtx)

		elif returnType=='edgeRing':
			edgesLong = pm.polySelect(obj, query=1, edgeRing=componentNumbers) #(e..)

		elif returnType=='edgeRingPath':
			edgesLong = pm.polySelect(obj, query=1, edgeRingPath=(componentNumbers[0], componentNumbers[1])) #(e, e)

		elif returnType=='edgeLoop':
			edgesLong = pm.polySelect(obj, query=1, edgeLoop=componentNumbers) #(e..)

		elif returnType=='edgeLoopPath':
			edgesLong = pm.polySelect(obj, query=1, edgeLoopPath=(componentNumbers[0], componentNumbers[1])) #(e, e)

		if not edgesLong:
			print('# Error: Unable to find edge path: {}. #'.format(obj))

		[result.append('{}.e[{}]'.format(obj.name(), int(edge))) for edge in edgesLong]

		return result


	@classmethod
	def getShortestPath(cls, components=None):
		'''Get the shortest path between to vertices or edges.

		:Parameters:
			components (obj) = A Pair of vertices or edges.

		:Return:
			(list) the components that comprise the path as strings.
		'''
		type_ = Node_tools_maya.getType(components[0])

		result=[]
		objects = set(pm.ls(components, objectsOnly=1))
		for obj in objects:

			if type_=='Polygon Edge':
				components = [pm.ls(pm.polyListComponentConversion(e, fromEdge=1, toVertex=1), flatten=1) for e in components]
				try:
					closestVerts = cls.getClosestVerts(components[0], components[1])[0]
				except IndexError as error:
					print ('# Error: Operation requires exactly two selected edges. #')
					return
				edges = cls.getEdgePath(closestVerts, 'shortestEdgePath')
				[result.append(e) for e in edges]

			elif type_=='Polygon Vertex':
				closestVerts = cls.getClosestVerts(components[0], components[1])[0]
				edges = cls.getEdgePath(closestVerts, 'shortestEdgePath')
				vertices = pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toVertex=1), flatten=1)
				[result.append(v) for v in vertices]

		return result


	@classmethod
	def getPathAlongLoop(cls, components=None):
		'''Get the shortest path between to vertices or edges along an edgeloop.

		:Parameters:
			components (obj) = A Pair of vertices, edges, or faces.

		:Return:
			(list) the components that comprise the path as strings.
		'''
		type_ = Node_tools_maya.getType(components[0])

		result=[]
		objects = set(pm.ls(components, objectsOnly=1))
		for obj in objects:

			if type_=='Polygon Vertex':
				vertices=[]
				for component in components:
					edges = pm.ls(pm.polyListComponentConversion(component, fromVertex=1, toEdge=1), flatten=1)
					_vertices = pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toVertex=1), flatten=1)
					vertices.append(_vertices)

				closestVerts = cls.getClosestVerts(vertices[0], vertices[1])[0]
				_edges = pm.ls(pm.polyListComponentConversion(list(components)+list(closestVerts), fromVertex=1, toEdge=1), flatten=1)

				edges=[]
				for edge in _edges:
					verts = pm.ls(pm.polyListComponentConversion(edge, fromEdge=1, toVertex=1), flatten=1)
					if closestVerts[0] in verts and components[0] in verts or closestVerts[1] in verts and components[1] in verts:
						edges.append(edge)

				edges = cls.getEdgePath(edges, 'edgeLoopPath')

				vertices = [pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toVertex=1), flatten=1)]
				[result.append(v) for v in vertices]


			elif type_=='Polygon Edge':
				edges = cls.getEdgePath(components, 'edgeLoopPath')
				[result.append(e) for e in edges]


			elif type_=='Polygon Face':
				vertices=[]
				for component in components:
					edges = pm.ls(pm.polyListComponentConversion(component, fromFace=1, toEdge=1), flatten=1)
					_vertices = pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toVertex=1), flatten=1)
					vertices.append(_vertices)

				closestVerts1 = cls.getClosestVerts(vertices[0], vertices[1])[0]
				closestVerts2 = cls.getClosestVerts(vertices[0], vertices[1])[1] #get the next pair of closest verts

				_edges = pm.ls(pm.polyListComponentConversion(closestVerts1+closestVerts2, fromVertex=1, toEdge=1), flatten=1)
				edges=[]
				for edge in _edges:
					verts = pm.ls(pm.polyListComponentConversion(edge, fromEdge=1, toVertex=1), flatten=1)
					if closestVerts1[0] in verts and closestVerts2[0] in verts or closestVerts1[1] in verts and closestVerts2[1] in verts:
						edges.append(edge)

				edges = cls.getEdgePath(edges, 'edgeRingPath')

				faces = pm.ls(pm.polyListComponentConversion(edges, fromEdge=1, toFace=1), flatten=1)
				[result.append(f) for f in faces]

		return result


	@classmethod
	def getEdgesByNormalAngle(cls, objects, lowAngle=50, highAngle=130, returnType='str', flatten=False):
		'''Get a list of edges having normals between the given high and low angles using maya's polySelectConstraint.

		:Parameters:
			objects (str)(list)(obj) = The object(s) to get edges of.
			lowAngle (int) = Normal angle low range.
			highAngle (int) = Normal angle high range.
			returnType (str) = The desired returned object type. (valid: 'unicode'(default), 'str', 'int', 'object')
			flatten (bool) = Flattens the returned list of objects so that each component is identified individually.

		:Return:
			(list) Polygon edges.
		'''
		orig_selection = pm.ls(sl=1) #get currently selected objects in order to re-select them after the contraint operation.

		pm.polySelectConstraint(angle=True, anglebound=(lowAngle, highAngle), mode=3, type=0x8000) #Constrain that selection to only edges of a certain Angle
		pm.selectType(polymeshEdge=True)
		edges = cls.getComponents(objects, 'edges', selection=1, returnType=returnType, flatten=flatten)

		pm.polySelectConstraint(mode=0) #Remove the selection constraint.
		pm.select(orig_selection) #re-select any originally selected objects.

		return edges


	@staticmethod
	def getComponentsByNumberOfConnected(components, num_of_connected=(0,2), connectedType=None, returnType='str', flatten=False):
		'''Get a list of components filtered by the number of their connected components.

		:Parameters:
			components (str)(list)(obj) = The components to filter.
			num_of_connected (int)(tuple) = The number of connected components. Can be given as a range. (Default: (0,2))
			connectedType (str)(int) = The desired component mask. (valid: 'vtx','vertex','vertices','Polygon Vertex',31,0x0001(vertices), 'e','edge','edges','Polygon Edge',32,0x8000(edges), 'f','face','faces','Polygon Face',34,0x0008(faces), 'uv','texture','texture coordinates','Polygon UV',35,0x0010(texture coordiantes).
			returnType (str) = The desired returned object type. (valid: 'unicode'(default), 'str', 'int', 'object')
			flatten (bool) = Flattens the returned list of objects so that each component is identified individually.

		:Return:
			(list) Polygon vertices.

		ex. components = getComponents(objects, 'faces', selection=1)
			faces = getComponentsByNumberOfConnected(components, 4, 'Polygon Edge') #returns faces with four connected edges (four sided faces).

		ex. components = getComponents(objects, 'vertices', selection=1)
			verts = getComponentsByNumberOfConnected(components, (0,2), 'Polygon Edge') #returns vertices with up to two connected edges.
		'''
		if connectedType in ('vtx', 'vertex', 'vertices', 'Polygon Vertex', 31, 0x0001):
			connectedType = 'Polygon Vertex'
		elif connectedType in ('e', 'edge', 'edges', 'Polygon Edge', 32, 0x8000):
			connectedType = 'Polygon Edge'
		elif connectedType in ('f', 'face', 'faces', 'Polygon Face', 34, 0x0008):
			connectedType = 'Polygon Face'

		if isinstance(num_of_connected, (tuple, list, set)):
			lowRange, highRange = num_of_connected
		else:
			lowRange = highRange = num_of_connected

		component_type = Node_tools_maya.getType(components)
		if not connectedType:
			connectedType = component_type

		result=[]
		for c in pm.ls(components, flatten=1):
			fm = {'Polygon Vertex':'fromVertex', 'Polygon Edge':'fromEdge', 'Polygon Face':'fromFace'}
			to = {'Polygon Vertex':'toVertex', 'Polygon Edge':'toEdge', 'Polygon Face':'toFace'}
			kwargs = {'fromVertex':False, 'fromEdge':False, 'fromFace':False, 'toVertex':False, 'toEdge':False, 'toFace':False}

			kwargs[fm[component_type]] = True #ex. kwargs['fromVertex'] = True
			kwargs[to[connectedType]] = True #ex. kwargs['toEdge'] = True

			num = len(pm.ls(pm.polyListComponentConversion(c, **kwargs), flatten=1))
			if num>=lowRange and num<=highRange:
				result.append(c)

		return result









# print (__name__) #module name
# -----------------------------------------------
# Notes
# -----------------------------------------------

#deprecated:

	# @classmethod
	# def getComponents(cls, objects=None, selection=False, componentType=None, returnType='str', returnNodeType='shape', flatten=False):
	# 	'''Get the components of the given type.

	# 	:Parameters:
	# 		objects (str)(obj)(list) = The object(s) to get the components of.
	# 		selection (bool) = Filter to currently selected objects.
	# 		componentType (str)(int) = The desired component mask. (valid: any type allowed in the 'convertComponentName' method)
	# 		returnType (str) = The desired returned object type. (valid: 'str', 'obj', 'int')
	# 		returnNodeType (str) = Specify whether the components are returned with the transform or shape nodes (valid only with str returnTypes). (valid: 'transform', 'shape'(default)) ex. 'pCylinder1.f[0]' or 'pCylinderShape1.f[0]'
	# 		flatten (bool) = Flattens the returned list of objects so that each component is it's own element.

	# 	:Return:
	# 		(list)(dict) Dependant on flags.

	# 	ex. getComponents(objects, 'faces' returnType='object')
	# 	'''
	# 	if not componentType: #get component type from the current selection.
	# 		if selection:
	# 			componentType = Node_tools_maya.getType(pm.ls(sl=1))
	# 			if componentType=='Polygon': #object level selection.
	# 				all_components = [cls.getComponents(objects, typ) for typ in ('vtx', 'e', 'f', 'cv')]
	# 				return all_components
	# 		else:
	# 			return

	# 	componentType = cls.convertComponentName(componentType, returnType='abv') #get the correct componentType variable from possible args.
	# 	mask = cls.convertComponentName(componentType, returnType='int')

	# 	components=[]
	# 	if selection:
	# 		if objects:
	# 			transforms = pm.ls(objects, sl=1, transforms=1)
	# 			if transforms: #get ALL selected components, FILTERING for those of the given transform object(s).
	# 				selected_shapes=[]
	# 				for obj in transforms:
	# 					selected_shapes+=pm.ls('{}.{}[*]'.format(obj, componentType), flatten=flatten)
	# 			else: #get selected components, FILTERING for those of the given tranform object(s).
	# 				shapes = Node_tools_maya.getShapeNode(objects)
	# 				selected_shapes = pm.ls(shapes, sl=1)
	# 			components = pm.filterExpand(selected_shapes, selectionMask=mask, expand=flatten)
	# 		else:
	# 			transforms = pm.ls(sl=1, transforms=1)
	# 			if transforms:
	# 				for obj in transforms: #get ALL selected components, for each selected transform object.
	# 					components+=pm.ls('{}.{}[*]'.format(obj, componentType), flatten=flatten)
	# 			else: #get selected components.
	# 				components = pm.filterExpand(selectionMask=mask, expand=flatten)
	# 	else:
	# 		for obj in pm.ls(objects):
	# 			components+=pm.ls('{}.{}[*]'.format(obj, componentType), flatten=flatten)

	# 	# if not components:
	# 	# 	components=[]

	# 	result = cls.convertReturnType(components, returnType=returnType, returnNodeType=returnNodeType, flatten=flatten)

	# 	return result