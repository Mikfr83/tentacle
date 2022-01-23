# !/usr/bin/python
# coding=utf-8
from slots.max import *
from slots.main import Main
from ui.static.max.main_ui_max import Main_ui_max



class Main(Slots_max):
	def __init__(self, *args, **kwargs):
		Slots_max.__init__(self, *args, **kwargs)
		Main_ui_max.__init__(self, *args, **kwargs)
		Main.__init__(self, *args, **kwargs)

		
	def tree000(self, wItem=None, column=None):
		''''''
		tree = self.main_lower_submenu_ui.tree000

		if not any([wItem, column]): # code here will run before each show event. generally used to refresh tree contents. -----------------------------
			recentCommandInfo = self.tcl.sb.prevCommand(docString=1, toolTip=1, as_list=1) #Get a list of any recent command names and their toolTips
			[tree.add('QLabel', 'Recent Commands', refresh=True, setText=s[0], setToolTip=s[1]) for s in recentCommandInfo]
			return

		# widget = tree.getWidget(wItem, column)
		header = tree.getHeaderFromColumn(column)
		text = tree.getWidgetText(wItem, column)
		index = tree.getIndexFromWItem(wItem, column)

		if header=='Recent Commands':
			recentCommands = self.tcl.sb.prevCommand(method=1, as_list=1) #Get a list of any recent commands
			method = recentCommands[index]
			if callable(method):
				method()

		# if header=='':
		# 	if text=='':
		# 		mel.eval('')
		# 	if text=='':
		# 		mel.eval('')


	def v013(self):
		'''Minimize Main Application

		'''
		self.tcl.sb.getMethod('file', 'b005')()


	def v024(self):
		'''Recent Command: 1
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-1]() #execute command at index


	def v025(self):
		'''Recent Command: 2
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-2]() #execute command at index
			

	def v026(self):
		'''Recent Command: 3
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-3]() #execute command at index


	def v027(self):
		'''Recent Command: 4
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-4]() #execute command at index


	def v028(self):
		'''Recent Command: 5
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-5]() #execute command at index


	def v029(self):
		'''Recent Command: 6
		'''
		self.tcl.sb.prevCommand(method=1, as_list=1)[-6]() #execute command at index







#module name
print (__name__)
# -----------------------------------------------
# Notes
# -----------------------------------------------