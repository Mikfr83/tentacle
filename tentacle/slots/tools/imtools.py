# !/usr/bin/python
# coding=utf-8

import sys, os

try:
	import numpy as np

	from PIL import Image
	from PIL.ImageChops import invert
except ImportError as error:
	print (__file__, error)

from PySide2 import QtWidgets

import tools



class Imtools():
	'''Helper methods for working with image file formats.
	'''

	@property
	def mapTypes(self):
		'''Get map type from filename suffix.
		'''
		return {
			'Base_Color':('Base_Color', 'BaseColor', '_BC'),
			'Roughness':('Roughness', 'Rough', '_R'),
			'Metallic':('Metallic', 'Metal', '_M', 'Metalness'),
			'Ambient_Occlusion':('Mixed_AO', 'AmbientOcclusion', 'Ambient_Occlusion', '_AO'),
			'Normal':('Normal', 'Norm', '_N'),
			'Normal_DirectX':('Normal_DirectX', 'NormalDirectX', 'NormalDX', '_NDX'),
			'Normal_OpenGL':('Normal_OpenGL', 'NormalOpenGL', 'NormalGL', '_NGL'),
			'Height':('Height', '_H', 'High'),
			'Emissive':('Emissive', 'Emit', '_E'),
			'Diffuse':('Diffuse', '_DF', '_D', 'Diff', 'Dif'),
			'Specular':('Specular', '_S', 'Spec'),
			'Glossiness':('Glossiness', 'Gloss', 'Glos', 'Glo', '_G'),
			'Displacement':('Displacement', '_DP', 'Displace', 'Disp', 'Dis', '_D'),
			'Refraction':('_IOR', 'Refraction', 'IndexofRefraction'),
			'Reflection':('Reflection', '_RF'),
		}

	@property
	def mapBackgrounds(self):
		'''Get default map backgrounds in RGBA format from map type.
		'''
		return {
			'Base_Color':(127, 127, 127, 255),
			'Roughness':(255, 255, 255, 255),
			'Metallic':(0, 0, 0, 255),
			'Ambient_Occlusion':(255, 255, 255, 255),
			'Normal':(127, 127, 255, 255),
			'Normal_DirectX':(127, 127, 255, 255),
			'Normal_OpenGL':(127, 127, 255, 255),
			'Height':(127, 127, 127, 255),
			'Emissive':(0, 0, 0, 255),
			'Diffuse':(0, 0, 0, 255),
			'Specular':(0, 0, 0, 255),
			'Glossiness':(0, 0, 0, 255),
			'Displacement':(0, 0, 0, 255),
			'Refraction':(0, 0, 0, 255),
			'Reflection':(0, 0, 0, 255),
		}

	@property
	def mapModes(self):
		'''Get default map mode from map type.
		'''
		return {
			'Base_Color':'RGB',
			'Roughness':'L',
			'Metallic':'L',
			'Ambient_Occlusion':'L',
			'Normal':'RGB',
			'Normal_DirectX':'RGB',
			'Normal_OpenGL':'RGB',
			'Height':'I', #I 32bit mode conversion from rgb not currently working.
			'Emissive':'L',
			'Diffuse':'RGB',
			'Specular':'L',
			'Glossiness':'L',
			'Displacement':'L',
			'Refraction':'L',
			'Reflection':'L',
		}


	@property
	def bitDepth(self):
		'''Get bit depth from mode.
		'''
		return {
			'1': 1, 
			'L': 8, 
			'P': 8, 
			'RGB': 24, 
			'RGBA': 32, 
			'CMYK': 32, 
			'YCbCr': 24, 
			'LAB': 24, 
			'HSV': 24, 
			'I': 32, 
			'F': 32, 
			'I;16': 16, 
			'I;16B': 16, 
			'I;16L': 16, 
			'I;16S': 16, 
			'I;16BS': 16, 
			'I;16LS': 16, 
			'I;32': 32, 
			'I;32B': 32, 
			'I;32L': 32, 
			'I;32S': 32, 
			'I;32BS': 32, 
			'I;32LS': 32
		}


	@staticmethod
	def getImageDirectory():
		'''
		'''
		image_dir = QtWidgets.QFileDialog.getExistingDirectory(None, 
			"Select a directory containing image files", "/home")

		return image_dir


	@staticmethod
	def getImageFiles():
		'''
		'''
		files = QtWidgets.QFileDialog.getOpenFileNames(None, 
			"Select one or more image files to open", "/home", "Images (*.png *.jpg *.bmp *.tga *.tiff *.gif)")

		return {i:Image.open(i) for i in files[0]} #return fileNames:PIL image from: [fileNames, selectedFilter]. selectedFilter ex: "Images (*.png *.jpg *.bmp)"


	@staticmethod
	def getImages(image_dir, image_types=['png', 'jpg', 'bmp', 'tga', 'tiff', 'gif']):
		'''Get bitmap images from a given directory as PIL images.

		:Parameters:
			image_dir (string) = A full path to a directory containing images with the given image_types.
			image_types (list) = The extensions of image types to include.

		:Return:
			(dict) full file path:image object
		'''
		exts = ['.'+e for e in image_types]

		images={}
		for f in tools.Txtools.getDirectoryContents(image_dir, returnType='filePaths'):

			if any(map(f.endswith, exts)):
				fullpath = tools.Txtools.formatFilepath(f)
				filename = tools.Txtools.formatFilepath(f, 'file')
				filename = min(map(filename.rstrip, exts), key=len)

				im = Image.open(fullpath)
				images[fullpath] = im

		return images


	@staticmethod
	def invertChannels(image, channels='RGB'):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		alpha = None

		try:
			r, g, b = im.split()
		except ValueError as error:
			r, g, b, a = im.split()

		r = invert(r) if 'r' in channels.lower() else r
		g = invert(g) if 'g' in channels.lower() else g
		b = invert(b) if 'b' in channels.lower() else b

		return Image.merge('RGB', (r, g, b))# if alpha else Image.merge('RGB', (red, green, blue))


	@staticmethod
	def getImageBackground(image, mode=None, average=False):
		'''Sample the pixel values of each corner of an image and if they are uniform, return the result.

		:Parameters:
			image (str)(obj) = 
			mode (str) = Image color mode. ex. 'RGBA'
			average (bool) = Average the sampled pixel values.

		:Return:
			(tuple) ex. (211, 211, 211, 255)
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		if mode:
			im = im.convert(mode)

		width, height = im.size

		tl = im.getpixel((0, 0)) #get the pixel value at top left coordinate.
		tr = im.getpixel((width-1, 0)) #			""	 top right coordinate.
		br = im.getpixel((0, height-1)) #			""	 bottom right coordinate.
		bl = im.getpixel((width-1, height-1)) #		""	 bottom left coordinate.

		if len(set([tl, tr, br, bl]))==1: #list of pixel values are all identical.
			return tl

		elif average:
			return tuple(int(np.mean(i)) for i in zip(*[tl, tr, br, bl]))

		else:
			return None #non-uniform background.


	@classmethod
	def createMasks(cls, images, *args, **kwargs):
		'''
		'''
		masks=[]
		for im in images:
			mask = cls.createMask(im, *args, **kwargs)
			masks.append(mask)

		return masks


	@staticmethod
	def createMask(image, mask, background=(0, 0, 0, 255), foreground=(255, 255, 255, 255)):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		im = im.convert('RGBA')
		width, height = im.size
		data = np.array(im)

		r1, g1, b1, a1 = mask if len(mask)==4 else mask+(None,)

		r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

		bool_list = ((r==r1) & (g==g1) & (b==b1) & (a==a1)) if len(mask)==4 else ((r==r1) & (g==g1) & (b==b1))

		data[:,:,:4][bool_list.any()] = foreground
		data[:,:,:4][bool_list] = background

		#set the border to background color:
		data[0, 0] = background #get the pixel value at top left coordinate.
		data[width-1, 0] = background #			""	 top right coordinate.
		data[0, height-1] = background #			""	 bottom right coordinate.
		data[width-1, height-1] = background #		""	 bottom left coordinate.

		return Image.fromarray(data).convert('L')


	@staticmethod
	def fill(image, color=(0, 0, 0, 0)):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		draw = ImageDraw.Draw(im)
		draw.rectangle([(0,0), im.size], fill=color)

		return im


	@classmethod
	def fillMaskedArea(cls, image, color, mask):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		mode = im.mode
		im = im.convert('RGBA')

		background = cls.createImage(mode=im.mode, size=im.size, rgba=color)

		return Image.composite(im, background, mask).convert(mode)


	@staticmethod
	def convert_rgb_to_gray(data):
		'''Convert an RGB Image data array to grayscale.

		:Paramters:
			image (array) = Image data as numpy array.

		:Return:
			(array)

		# gray_data = np.average(data, weights=[0.299, 0.587, 0.114], axis=2)
		# gray_data = (data[:,:,:3] * [0.2989, 0.5870, 0.1140]).sum(axis=2)
		'''
		gray_data = np.dot(data[...,:3], [0.2989, 0.5870, 0.1140])

		# array = gray_data.reshape(gray_data.shape[0], gray_data.shape[1], 1)
		#print (array.shape)

		return gray_data


	@staticmethod
	def convert_to_32bit_I(image):
		'''Under construction.
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		data = np.array(im)

		try: #convert from 'I'
			im32 = data.astype(np.int32)
			return Image.fromarray(im32, mode='I')

		except ValueError as error: #convert from 'RGB'
			
			# data = self.convert_rgb_to_gray(data)

			# im32 = data.astype(np.int32)
			# return Image.fromarray(im32, mode='I')

			# from PIL import ImageMath
			# return ImageMath.eval('im >> 32', im=im.convert('I'))
			return im.convert('RGB')


	@staticmethod
	def convert_I_to_L(image):
		'''Convert to 8 bit 'L' grayscale.

		:Parameters:
			image (str)(obj) = The PIL image to convert.

		:Return:
			(obj) PIL image.
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		data = np.array(im)

		data = np.asarray(data, np.uint8) #np.uint8(data / 256)
		return Image.fromarray(data)


	@staticmethod
	def setPixelColor(image, x, y, color):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		im.putpixel((x, y), color)


	@staticmethod
	def replaceColor(image, from_color=(0, 0, 0, 0), to_color=(0, 0, 0, 0), mode=None):
		'''

		:Parameters:
			image (str)(obj) = 
			from_color (tuple) = 
			to_color (tuple) = 
			mode (str) = The image is converted to rgba for the operation specify the returned image mode. the original image mode will be returned if None is given. ex. 'RGBA' to return in rgba format.

		:Return:
			(obj) image.
		'''
		im = Image.open(image) if (isinstance(image, str)) else image
		mode = mode if mode else im.mode
		im = im.convert('RGBA')
		data = np.array(im)

		r1, g1, b1, a1 = from_color if len(from_color)==4 else from_color+(None,)

		r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

		mask = ((r==r1) & (g==g1) & (b==b1) & (a==a1)) if len(from_color)==4 else ((r==r1) & (g==g1) & (b==b1))
		data[:,:,:4][mask] = to_color if len(to_color)==4 else to_color+(255,)

		return Image.fromarray(data).convert('RGBA')


	@staticmethod
	def setContrast(image, level=255):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		factor = (259 * (level + 255)) / (255 * (259 - level))
		_contrast = lambda c: int(max(0, min(255, 128 + factor * (c - 128)))) #make sure the contrast filter only return values within the range [0-255].

		return im.point(_contrast)


	@classmethod
	def isNormalMap(cls, type_):
		'''Check the map type for one of the normal values in mapTypes.
		'''
		return any((type_ in cls.mapTypes['Normal_DirectX'], 
				type_ in cls.mapTypes['Normal_OpenGL'], 
				type_ in cls.mapTypes['Normal']))


	@staticmethod
	def all_pixels_identical(img):
		'''Check if all pixels of an image are of the same pixel value.
		As soon as any value is different from the first one; return False, else; True.
		'''
		bits = img.constBits()
		a = bits[0]
		return all(a==b for b in bits)


	@classmethod
	def getImageType(cls, filename, key=False):
		'''
		:Parameters:
			filename (str) = Filename, filepath, or map type suffix.
			key (bool) = Get the corresponding key from the type in self.mapTypes. ie. Base_Color from <filename>_BC or BC.

		:Return:
			(str)
		'''
		name = tools.Txtools.formatFilepath(filename, 'name')

		if key:
			return next((k for k, v in cls.mapTypes.items() for i in v if name.lower().endswith(i.lower())), None)

		return next((i for v in cls.mapTypes.values() for i in v if name.lower().endswith(i.lower())), (''.join(name.split('_')[-1]) if '_' in name else None))


	@classmethod
	def sortImagesByTag(cls, files):
		'''
		:Parameters:
			

		:Return:
			(dict)
		'''
		sorted_images={}
		for file, image in files.items():
			type_ = cls.getImageType(file)
			if not type_:
				continue

			try:
				sorted_images[type_].append((file, image))
			except KeyError as error:
				sorted_images[type_] = [(file, image)]

		return sorted_images


	@staticmethod
	def resizeImage(image, x, y):
		'''
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		im.resize((x, y))


	@staticmethod
	def createImage(mode='RGBA', size=(4096, 4096), rgba=(0, 0, 0, 255)):
		'''
		'''
		return Image.new(mode, size, rgba)


	@staticmethod
	def saveImageFile(image, name):
		'''
		:Parameters:
			image (obj) = PIL image object.
			name (str) = Path + filename including extension. ie. new_image.png
		'''
		im = Image.open(image) if (isinstance(image, str)) else image

		im.save(name)









if __name__ == "__main__":
	pass


# --------------------------------
# Notes
# --------------------------------



# Deprecated -----------------------------------------------


# def getBitDepth(self, image):
# 		'''
# 		'''
# 		im = Image.open(image) if (isinstance(image, str)) else image
# 		data = np.array(im)

# 		bitDepth = {'uint8':8, 'uint16':16, 'uint32':32, 'uint64':64}

# 		return bitDepth[str(data.dtype)]


# width, height = im.size
 
		# for i in range(0, width):# process all pixels
		# 	for ii in range(0, height):
		# 		data = im.getpixel((i, ii))
		# 		# data[0] = Red,  [1] = Green, [2] = Blue
		# 		# data[0,1,2] range = 0~255
		# 		if data==mask:
		# 		# if data[0] > 150 and data[1] < 50 and data[2] < 50 :
		# 			im.putpixel((i, ii), (0, 0, 0))
		# 		else :
		# 			im.putpixel((i, ii), (255, 255, 255))

		# return im.convert(mode)


	# def isolateColor(self, image, color):
	# 	'''Return an image with only pixels of the given color retained.
	# 	'''
	# 	im = Image.open(image) if (isinstance(image, str)) else image
	# 	data = np.array(im)

	# 	r, g, b =  color[:3]
	# 	array = np.where(data == r, g, b)

	# 	return Image.fromarray(array.astype('uint8')) #Image.fromarray(converted.astype('uint8'))


	# def createMask(self, image, mask):
	# 	'''
	# 	'''
	# 	im = Image.open(image) if (isinstance(image, str)) else image

	# 	im = self.replaceColor(im, from_color=mask, to_color=(0, 177, 64, 255))

	# 	# background = self.createImage(mode='RGBA', size=im.size, rgba=(0, 177, 64, 255))
	# 	# im = Image.alpha_composite(background, im) #(background, foreground)

	# 	# im = self.isolateColor(im, (0, 177, 64))
	# 	# im = self.replaceColor(im, from_color=(0, 177, 64), to_color=(255, 255, 255, 255), background_color=(0, 0, 0, 255))
	# 	# im = self.setContrast(im, 255)
	# 	return im



	# def convertDXToGL(self):
	# 	'''
	# 	'''
	# 	files = self.getImageFiles()
	# 	for file, image in files.items():
	# 		inverted_image = self.invertChannels(image, 'g')
	# 		# name = self.formatFilePath(file, remove='_DirectX', append='_OpenGL')
	# 		# self.saveImageFile(inverted_image, name)


	# def convertGLToDX(self):
	# 	'''
	# 	'''
	# 	files = self.getImageFiles()
	# 	for file, image in files.items():
	# 		inverted_image = self.invertChannels(image, 'g')
	# 		# name = self.formatFilePath(file, remove='_OpenGL', append='_DirectX')
	# 		# self.saveImageFile(inverted_image, name)



	# def changeColorDepth(self, image, depth):
	# 	'''
	# 	'''
		# return image.convert(image.mode, colors=depth)

		# import math

		# grayscale_color_count = 256
		# rgb_color_count = 256

		# if image.mode=='L':
		# 	raito = grayscale_color_count / colorCount
		# 	change = lambda value: math.trunc(value/raito)*raito
		# 	return image.point(change)

		# if image.mode=='RGB' or image.mode=='RGBA':
		# 	raito = rgb_color_count / colorCount
		# 	change = lambda value: math.trunc(value/raito)*raito
		# 	return Image.eval(image, change)

		# raise ValueError('invalid image mode: {mode}'.format(mode=image.mode))






		# appended = '{}{}.{}'.format(''.join(string.split('.')[:-1]), append, ''.join(string.split('.')[-1]))
		# removed = appended.replace(remove, '')

		# return '{}/{}'.format(path, removed)