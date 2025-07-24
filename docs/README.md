[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![Version](https://img.shields.io/badge/Version-0.9.36-blue.svg)](https://pypi.org/project/tentacletk/)

# Tentacle: A Python3/qtpy Marking Menu

Tentacle is a Python3/qtpy marking menu implemented using Qt's QStackedWidget. It is designed for use with Maya, 3ds Max, Blender, and any other DCC app that supports qtpy.  In it's current implementation, it only has slots set up for Maya 2025.

## Design

Tentacle runs on top of [uitk](https://github.com/m3trik/uitk.git), a qtpy dynamic UI loader, which allows for the creation of fully-featured UI with less time and code.

## Example

The following example demonstrates re-opening the last scene, renaming a material, and selecting geometry by that material.

![Example](https://raw.githubusercontent.com/m3trik/tentacle/master/docs/toolkit_demo.gif)

## Structure

The structure of the project is as follows:

![Structure](https://raw.githubusercontent.com/m3trik/tentacle/master/docs/UML_diagram.jpg)

| Module        | Description   |
| ------------- | ------------- |
| [tcl](https://github.com/m3trik/uitk/blob/main/tentacle/tcl.py)         | Handles main GUI construction for the marking menu. |
| [overlay](https://github.com/m3trik/uitk/blob/main/tentacle/overlay.py) | Tracks cursor position and UI hierarchy to generate paint events that overlay its parent widget. |
| [ui](https://github.com/m3trik/uitk/blob/main/tentacle/events.py)       | Location of the dynamic UI files. |
| [slots](https://github.com/m3trik/uitk/blob/main/tentacle/slots)        | Location of the various slot modules. |

## Installation

Tentacle can be installed either using pip directly in the command line or by downloading and running mayapy package manager in Windows.

### Installation via pip

Install via pip in a command line window using:

```bash
path/to/mayapy.exe -m pip install tentacletk
```

### Installation Using Mayapy Package Manager

Alternatively, you can use the mayapy package manager for a streamlined installation process. 
Download the mayapy package manager from [here](https://github.com/m3trik/windows-shell-scripting/blob/master/mayapy-package-manager.bat). (Give your Maya version. Hit 1 to install package. The package name is `tentacletk`)

## Usage

To launch the marking menu:

For Maya, add a macro to a hotkey similar to the following:

```python
from tentacle.tcl_maya import TclMaya
TclMaya.instance(key_show='Z').show()  # Change to match your chosen hotkey.
```
