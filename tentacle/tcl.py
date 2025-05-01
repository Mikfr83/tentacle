# !/usr/bin/python
# coding=utf-8
import sys
from qtpy import QtCore, QtWidgets
import pythontk as ptk
from uitk.switchboard import Switchboard
from uitk.events import EventFactoryFilter, MouseTracking
from tentacle.overlay import Overlay


class Tcl(
    QtWidgets.QStackedWidget, ptk.SingletonMixin, ptk.LoggingMixin, ptk.HelpMixin
):
    """Tcl is a marking menu based on a QStackedWidget.
    The various UI's are set by calling 'show' with the intended UI name string. ex. Tcl().show('polygons')

    Parameters:
        parent (QWidget): The parent application's top level window instance. ie. the Maya main window.
        key_show (str): The name of the key which, when pressed, will trigger the display of the marking menu. This should be one of the key names defined in QtCore.Qt. Defaults to 'Key_F12'.
        ui_source (str): The directory path or the module where the UI files are located.
                If the given dir is not a full path, it will be treated as relative to the default path.
                If a module is given, the path to that module will be used.
        slot_source (str): The directory path where the slot classes are located or a class object.
                If the given dir is a string and not a full path, it will be treated as relative to the default path.
                If a module is given, the path to that module will be used.
        log_level (int): Determines the level of logging messages. Defaults to logging.WARNING. Accepts standard Python logging module levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """

    left_mouse_double_click = QtCore.Signal()
    left_mouse_double_click_ctrl = QtCore.Signal()
    middle_mouse_double_click = QtCore.Signal()
    right_mouse_double_click = QtCore.Signal()
    right_mouse_double_click_ctrl = QtCore.Signal()
    key_show_press = QtCore.Signal()
    key_show_release = QtCore.Signal()

    _first_show = True
    _instances = {}

    def __init__(
        self,
        parent=None,
        key_show="F12",
        ui_source="ui",
        slot_source="slots",
        widget_source=None,
        log_level: str = "WARNING",
    ):
        """ """
        super().__init__(parent=parent)
        self.logger.setLevel(log_level)

        self.sb = Switchboard(
            self,
            ui_source=ui_source,
            slot_source=slot_source,
            widget_source=widget_source,
        )

        self.child_event_filter = EventFactoryFilter(
            parent=self,
            forward_events_to=self,
            event_name_prefix="child_",
            event_types={
                "Enter",
                "MouseMove",
                "MouseButtonPress",
                "MouseButtonRelease",
            },
        )

        self.overlay = Overlay(self, antialiasing=True)
        self.mouse_tracking = MouseTracking(self)

        self.key_show = self.sb.convert.to_qkey(key_show)
        self.key_close = QtCore.Qt.Key_Escape
        self._mouse_press_pos = QtCore.QPoint(0, 0)

        # self.sb.app.setDoubleClickInterval(400)
        # self.sb.app.setKeyboardInputInterval(400)

        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoMousePropagation, False)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.resize(600, 600)

        self.sb.app.installEventFilter(self)
        self.sb.app.focusChanged.connect(self._on_focus_changed)

    def eventFilter(self, watched, event):
        """Filter key press/release for show/hide."""
        etype = event.type()

        if etype == QtCore.QEvent.Type.KeyPress:
            if event.key() == self.key_show and not event.isAutoRepeat():
                self.key_show_press.emit()
                self.show()
                return True

        elif etype == QtCore.QEvent.Type.KeyRelease:
            if event.key() == self.key_show and not event.isAutoRepeat():
                self.key_show_release.emit()
                self.hide()
                return True

        return super().eventFilter(watched, event)

    def _on_focus_changed(self, old, new):
        """Handle focus changes between widgets.
        Parameters:
            old (QWidget): The previous widget that had focus.
            new (QWidget): The new widget that has focus.
        """
        # If Tcl is visible, showing a stacked UI, and focus moved outside of Tcl
        if (
            self.isVisible()
            and self.sb.current_ui.has_tags(["startmenu", "submenu"])
            and new is not None
            and not self.isAncestorOf(new)
        ):
            self.logger.debug(f"Tcl focus changed to: {new}. Hiding Tcl.")
            self.hide()

    def _init_ui(self, ui) -> None:
        """Initialize the given UI.

        Parameters:
            ui (QWidget): The UI to initialize.
        """
        if not isinstance(ui, QtWidgets.QWidget):
            raise ValueError(f"Invalid datatype: {type(ui)}, expected QWidget.")

        if ui.has_tags(["startmenu", "submenu"]):  # StackedWidget
            if ui.has_tags("submenu"):
                ui.set_style(theme="dark", style_class="transparentBgNoBorder")
            else:
                ui.set_style(theme="dark", style_class="translucentBgNoBorder")
            self.addWidget(ui)  # add the UI to the stackedLayout.

        else:  # MainWindow
            ui.setParent(self.parent())
            ui.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
            ui.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            ui.set_style(theme="dark", style_class="translucentBgWithBorder")
            try:
                ui.header.config_buttons(menu_button=True, pin_button=True)
            except AttributeError:
                pass
            self.key_show_release.connect(ui.hide)

        # set style before child init (resize).
        self.add_child_event_filter(ui.widgets)
        ui.on_child_registered.connect(lambda w: self.add_child_event_filter(w))

    def _prepare_ui(self, ui) -> QtWidgets.QWidget:
        """Initialize and set the UI without showing it."""
        if not isinstance(ui, (str, QtWidgets.QWidget)):
            raise ValueError(f"Invalid datatype for ui: {type(ui)}")

        found_ui = self.sb.get_ui(ui)

        if not found_ui.is_initialized:
            self._init_ui(found_ui)

        if found_ui.has_tags(["startmenu", "submenu"]):
            if found_ui.has_tags("startmenu"):
                self.move(self.sb.get_cursor_offset_from_center(self))
            self.setCurrentWidget(found_ui)
        else:
            self.hide()

        self.sb.current_ui = found_ui
        return found_ui

    def _show_ui(self) -> None:
        """Show the current UI appropriately, hiding Tcl if needed."""
        current = self.sb.current_ui

        is_stacked_ui = current.has_tags(["startmenu", "submenu"])

        if is_stacked_ui:
            super().show()
        else:
            current.show()
            QtWidgets.QApplication.processEvents()

            widget_before_adjust = current.width()
            current.adjustSize()
            current.resize(widget_before_adjust, current.sizeHint().height())
            current.updateGeometry()
            self.sb.center_widget(current, "cursor", offset_y=25)

        self.raise_()
        self.setFocus()

    def _set_submenu(self, ui, w) -> None:
        """Set the stacked widget's index to the submenu associated with the given widget.
        Positions the new UI to align with the previous UI's widget that triggered the transition.

        Parameters:
            ui (QWidget): The UI submenu to set as current.
            w (QWidget): The widget under the cursor that triggered this submenu.
        """
        if not isinstance(ui, QtWidgets.QWidget):
            raise ValueError(f"Invalid datatype for ui: {type(ui)}, expected QWidget.")

        self.overlay.path.add(ui, w)

        if not ui.is_initialized:
            self._init_ui(ui)

        self._prepare_ui(ui)

        try:
            p1 = w.mapToGlobal(w.rect().center())
            w2 = self.sb.get_widget(w.name, ui)
            w2.resize(w.size())
            p2 = w2.mapToGlobal(w2.rect().center())
            self.move(self.pos() + (p1 - p2))
        except Exception as e:
            self.logger.warning(f"Submenu positioning failed: {e}")

        self._show_ui()

        if ui not in self.sb.ui_history(slice(0, -1), allow_duplicates=True):
            self.overlay.clone_widgets_along_path(ui, self._return_to_startmenu)

    def _return_to_startmenu(self) -> None:
        """Return to the start menu by moving the overlay path back to the start position."""
        start_pos = self.overlay.path.start_pos
        if not isinstance(start_pos, QtCore.QPoint):
            self.logger.warning("_return_to_startmenu called with no valid start_pos.")
            return

        startmenu = self.sb.ui_history(-1, inc="*#startmenu*")
        self._prepare_ui(startmenu)
        self.move(start_pos - self.rect().center())
        self._show_ui()

    # ---------------------------------------------------------------------------------------------
    #   Stacked Widget Event handling:

    def mousePressEvent(self, event) -> None:
        """ """
        if self.sb.current_ui.has_tags(["startmenu", "submenu"]):
            if not event.modifiers():
                if event.button() == QtCore.Qt.LeftButton:
                    self.show("cameras#startmenu")

                elif event.button() == QtCore.Qt.MiddleButton:
                    self.show("editors#startmenu")

                elif event.button() == QtCore.Qt.RightButton:
                    self.show("main#startmenu")

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        """ """
        if self.sb.current_ui.has_tags(["startmenu", "submenu"]):
            if event.button() == QtCore.Qt.LeftButton:
                if event.modifiers() == QtCore.Qt.ControlModifier:
                    self.left_mouse_double_click_ctrl.emit()
                else:
                    self.left_mouse_double_click.emit()

            elif event.button() == QtCore.Qt.MiddleButton:
                self.middle_mouse_double_click.emit()

            elif event.button() == QtCore.Qt.RightButton:
                if event.modifiers() == QtCore.Qt.ControlModifier:
                    self.right_mouse_double_click_ctrl.emit()
                else:
                    self.right_mouse_double_click.emit()

        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """ """
        current_ui = self.sb.current_ui
        if current_ui and current_ui.has_tags(["startmenu", "submenu"]):
            if self.isActiveWindow():
                self.show(force=True)

        super().mouseReleaseEvent(event)

    def show(self, ui="hud#startmenu", force=False) -> None:
        """Sets the widget as visible and shows the specified UI."""
        self._prepare_ui(ui)

        if not force and (QtWidgets.QApplication.mouseButtons() or self.isVisible()):
            return

        if self._first_show:
            self.sb.simulate_key_press(self, self.key_show)
            self._first_show = False

        self._show_ui()

    def hideEvent(self, event):
        """ """
        if QtWidgets.QWidget.keyboardGrabber() is self:
            self.releaseKeyboard()

        if self.mouseGrabber():
            self.mouseGrabber().releaseMouse()

        super().hideEvent(event)

    # ---------------------------------------------------------------------------------------------

    def add_child_event_filter(self, widgets) -> None:
        """Initialize child widgets with an event filter.

        Parameters:
            widgets (str/list): The widget(s) to initialize.
        """
        # Only Install the event filter for the following widget types.
        filtered_types = [
            QtWidgets.QMainWindow,
            QtWidgets.QWidget,
            QtWidgets.QAction,
            QtWidgets.QLabel,
            QtWidgets.QPushButton,
            QtWidgets.QCheckBox,
            QtWidgets.QRadioButton,
        ]

        for w in ptk.make_iterable(widgets):
            try:  # If not correct type, skip it.
                if (w.derived_type not in filtered_types) or (
                    not w.ui.has_tags(["startmenu", "submenu"])
                ):
                    continue
            except AttributeError:  # Or not initialized yet.
                continue

            if w.derived_type in (
                QtWidgets.QPushButton,
                QtWidgets.QLabel,
                QtWidgets.QCheckBox,
                QtWidgets.QRadioButton,
            ):
                self.sb.center_widget(w, padding_x=25)
                if w.base_name == "i":
                    w.ui.set_style(widget=w)

            if w.type == self.sb.registered_widgets.Region:
                w.visible_on_mouse_over = True

            self.child_event_filter.install(w)

    def child_enterEvent(self, w, event) -> None:
        """Handle child enterEvent properly."""
        if w.derived_type == QtWidgets.QPushButton:
            if w.base_name == "i":
                submenu_name = f"{w.accessibleName()}#submenu"
                if submenu_name != w.ui.name:
                    submenu = self.sb.get_ui(submenu_name)
                    if submenu:
                        self._set_submenu(submenu, w)

        if w.base_name == "chk" and w.ui.has_tags("submenu") and self.isVisible():
            w.click()

        # Safe default: call original enterEvent
        if hasattr(w, "enterEvent"):
            super_event = getattr(super(type(w), w), "enterEvent", None)
            if callable(super_event):
                super_event(event)

    def child_mouseButtonPressEvent(self, w, event) -> None:
        self._mouse_press_pos = event.globalPos()
        self.__mouseMovePos = event.globalPos()
        w.mousePressEvent(event)

    def child_mouseButtonReleaseEvent(self, w, event) -> bool:
        if w.underMouse():
            if w.derived_type == QtWidgets.QPushButton:
                if w.base_name == "i":
                    menu_name = w.accessibleName()
                    new_menu_name = self.clean_tag_string(menu_name)
                    menu = self.sb.get_ui(new_menu_name)
                    if menu:
                        self.hide_unmatched_groupboxes(menu, menu_name)
                        self.show(menu)

            if hasattr(w, "click"):
                self.hide()
                if w.ui.has_tags(["startmenu", "submenu"]) and w.base_name != "chk":
                    w.click()

        w.mouseReleaseEvent(event)

    def child_mouseMoveEvent(self, w, event) -> None:
        """ """
        try:
            globalPos = event.globalPos()
            self.__mouseMovePos = globalPos
        except AttributeError:
            pass

        w.mouseMoveEvent(event)

    # ---------------------------------------------------------------------------------------------

    @staticmethod
    def get_unknown_tags(tag_string, known_tags=["submenu", "startmenu"]):
        """Extracts all tags from a given string that are not known tags.

        Parameters:
            tag_string (str/list): The known tags in which to derive any unknown tags from.

        Returns:
            list: A list of unknown tags extracted from the tag_string.

        Note:
            Known tags are defined as 'submenu' and 'startmenu'. Any other tag found in the string
            is considered unknown. Tags are expected to be prefixed by a '#' symbol.
        """
        import re

        # Join known_tags into a pattern string
        known_tags_list = ptk.make_iterable(known_tags)
        known_tags_pattern = "|".join(known_tags_list)
        unknown_tags = re.findall(f"#(?!{known_tags_pattern})[a-zA-Z0-9]*", tag_string)
        # Remove leading '#' from all tags
        unknown_tags = [tag[1:] for tag in unknown_tags if tag != "#"]
        return unknown_tags

    def clean_tag_string(self, tag_string):
        """Cleans a given tag string by removing unknown tags.

        Parameters:
            tag_string (str): The string from which to remove unknown tags.

        Returns:
            str: The cleaned tag string with unknown tags removed.

        Note:
            This function utilizes the get_unknown_tags function to identify and subsequently
            remove unknown tags from the provided string.
        """
        import re

        unknown_tags = self.get_unknown_tags(tag_string)
        # Remove unknown tags from the string
        cleaned_tag_string = re.sub("#" + "|#".join(unknown_tags), "", tag_string)
        return cleaned_tag_string

    def hide_unmatched_groupboxes(self, ui, tag_string) -> None:
        """Hides all QGroupBox widgets in the provided UI that do not match the unknown tags extracted
        from the provided tag string.

        Parameters:
            ui (QObject): The UI object in which to hide unmatched QGroupBox widgets.
            tag_string (str): The string from which to extract unknown tags for comparison.

        Note:
            This function uses the get_unknown_tags function to determine which QGroupBox widgets
            to hide. If a QGroupBox widget's objectName does not match one of the unknown tags,
            the widget will be hidden.
        """
        unknown_tags = self.get_unknown_tags(tag_string)

        # Find all QGroupBox widgets in the UI
        groupboxes = ui.findChildren(QtWidgets.QGroupBox)

        # Hide all groupboxes that do not match the unknown tags
        for groupbox in groupboxes:
            if unknown_tags and groupbox.objectName() not in unknown_tags:
                groupbox.hide()
            else:
                groupbox.show()


# --------------------------------------------------------------------------------------------

if __name__ == "__main__":
    tcl = Tcl(slot_source="slots/maya")
    tcl.show("screen", app_exec=True)


# --------------------------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------------------------
