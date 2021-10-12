###### *A Python3/PySide marking menu style toolkit for Maya, 3ds Max, and Blender.
*work in progress..*

## Design:
######
*This is a cross-platform, modular, marking menu style ui based on a QStackedWidget. Constructed dynamically, naming convention and directory structure allow for a stacked ui to be constructed, and signals added/removed as needed. A master dictionary (switchboard module) provides convenience methods that allow for getting/setting of relevant data across modules.*

![alt text](https://raw.githubusercontent.com/m3trik/tentacle/master/docs/toolkit_demo.gif)
*Example re-opening the last scene, renaming a material, and selecting geometry by that material.


##
-----------------------------------------------
 Structure:
-----------------------------------------------

![alt text](https://raw.githubusercontent.com/m3trik/tentacle/master/docs/dependancy_graph.jpg)


#### tentacle_main:
###### *handles main gui construction.*

#### childEvents:
###### *event handling for child widgets.*

#### overlay:
###### *tracks cursor position and ui hierarchy to generate paint events that overlay the main widget.*

#### switchboard:
###### *contains a master dictionary for widget related info as well as convienience classes for interacting with the dict.*

#### slots:
###### *parent class holding methods that are inherited across all parent app specific slot class modules.*



##
-----------------------------------------------
 Installation:
-----------------------------------------------
######
For Maya:
add these lines to a startup script:
```
sys.path.append('path to /tentacle') --append the dir containing 'append_to_path.py' to the python path.
import append_to_path as ap
ap.appendPaths('maya', verbose=0)
```
to launch the menu, add a macro like the following:
```
def hk_main_show():
	'''
	hk_main_show
	Display main marking menu.
	'''
	if 'tentacle' not in {**locals(), **globals()}:
		from tentacle_maya import Instance
		tentacle = Instance(key_show='key_Z') #holding the Z key will show the menu.

	main.show_()
```

For 3ds Max:
add these lines to a startup script:
```
python.Init() --initalize python
python.Execute("import sys; sys.path.append('path to /tentacle')") --append the dir containing 'append_to_path.py' to the python path.
python.Execute("import append_to_path as ap; ap.appendPaths('max', verbose=0)")
```
to launch the menu, add a macro like the following:
```
macroScript main_max
category: "_macros.ui"
silentErrors: false
autoUndoEnabled: false
(
	python.Execute "if 'tentacle' not in {**locals(), **globals()}: from tentacle_max import Instance; tentacle = Instance(key_show='key_Z')" --create an instance
	python.Execute "tentacle.show('init');"
)
```
