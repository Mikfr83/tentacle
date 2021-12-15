# !/usr/bin/python
# coding=utf-8
import sys

from PySide2 import QtCore, QtWidgets

try: from pymxs import runtime as rt
except ImportError as e: print(e)

from tentacle import Tcl, Instance



class Tcl_max(Tcl):
	'''Tcl class overridden for use with Autodesk 3ds max.

	:Parameters:
		parent = main application top level window object.
	'''
	qApp = QtWidgets.QApplication

	def __init__(self, parent=None, *args, **kwargs):
		'''
		'''
		if not parent:
			try:
				parent = self.getMainWindow()

			except Exception as error:
				print(self.__class__.__name__, error)

		super().__init__(parent, *args, **kwargs)


	def getMainWindow(self):
		'''Get the 3DS MAX main window.

		Returns:
			PySide2.QtWidgets.QMainWindow: 'QMainWindow' 3DS MAX main window.
		'''
		# import qtmax
		# main_window = qtmax.GetQMaxMainWindow()

		main_window = next((w.window() for w in self.qApp.instance().topLevelWidgets()
			if w.inherits('QMainWindow') and w.metaObject().className()=='QmaxApplicationWindow'), 
				lambda: (_ for _ in ()).throw(RuntimeError('Count not find QmaxApplicationWindow instance.'))
			)

		if not main_window.objectName():
			main_window.setObjectName('MaxWindow')

		return main_window


	def keyPressEvent(self, event):
		'''
		:Parameters:
			event = <QEvent>
		'''
		if not event.isAutoRepeat():
			modifiers = self.qApp.keyboardModifiers()

			if event.key()==self.key_undo and modifiers==QtCore.Qt.ControlModifier:
				import pymxs
				pymxs.undo(True)

		return Tcl.keyPressEvent(self, event)


	def showEvent(self, event):
		'''
		:Parameters:
			event = <QEvent>
		'''
		try:
			rt.enableAccelerators = False

		except Exception as error:
			print(error)

		return Tcl.showEvent(self, event) #super().showEvent(event)


	def hideEvent(self, event):
		'''
		:Parameters:
			event = <QEvent>
		'''
		try:
			rt.enableAccelerators = True

		except Exception as error:
			print(error)

		if __name__ == "__main__":
			self.qApp.instance().quit()
			sys.exit() #assure that the sys processes are terminated.

		return Tcl.hideEvent(self, event) #super().hideEvent(event)


	# import contextlib
	# @contextlib.contextmanager
	# def performAppUndo(self, enabled=True, message=''):
	# 	'''
	# 	Uses pymxs's undo mechanism, but doesn't silence exceptions raised
	# 	in it.

	# 	:Parameter:
	# 		enabled (bool) = Turns undo functionality on.
	# 		message (str) = Label for the undo item in the undo menu.
	# 	'''
	# 	print('undo')
	# 	import pymxs
	# 	import traceback
	# 	e = None
	# 	with pymxs.undo(enabled, message):
	# 		try:
	# 			yield
	# 		except Exception as e:
	# 			# print error, raise error then run undo 
	# 			print(traceback.print_exc())
	# 			raise(e)
	# 			pymxs.run_undo()


class Instance(Instance):
	'''Manage multiple instances of Tcl_max.
	'''
	def __init__(self, *args, **kwargs):
		'''
		'''
		super().__init__(*args, **kwargs)
		self.Class = Tcl_max









if __name__ == "__main__":
	app = QtWidgets.QApplication.instance() #get the qApp instance if it exists.
	if not app:
		app = QtWidgets.QApplication(sys.argv)

	#create a parent object to run the code outside of max.
	dummyParent = QtWidgets.QWidget()
	dummyParent.setObjectName('MaxWindow')

	import cProfile
	cProfile.run("Instance(dummyParent).show('init')")
	# Instance(dummyParent).show_() #Tcl_max(p).show()
	sys.exit(app.exec_())



# -----------------------------------------------
# Notes
# -----------------------------------------------

# macroScript main_max
# category: "_macros.ui"
# silentErrors: false
# autoUndoEnabled: false
# (
# 	python.Execute "if 'tentacle' not in {**locals(), **globals()}: from tentacle_max import Instance; tentacle = Instance(key_show='key_F12')" --create an instance
# 	python.Execute "tentacle.show('init');"
# )