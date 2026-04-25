#!/usr/bin/python
# coding=utf-8
"""Regression tests for tentacle.slots.maya.hud WarningsMixin gating.

Bug: warnings (e.g. autosave-off, default-framerate) fired on brand-new
untitled scenes during initial setup, creating noise. The mixin now
short-circuits when chk_warn_skip_unsaved is enabled (default) AND no
scene file exists on disk yet.
"""
import os
import tempfile
import unittest

from tentacle.slots.maya import hud


class _FakePm:
    def __init__(self, scene_name: str):
        self._scene_name = scene_name

    def sceneName(self):
        return self._scene_name


class _FakeCheckbox:
    def __init__(self, checked: bool):
        self._checked = checked

    def isChecked(self):
        return self._checked


class _FakePrefs:
    def __init__(self, **flags):
        for k, v in flags.items():
            setattr(self, k, _FakeCheckbox(v))


class _FakeLoadedUi:
    def __init__(self, prefs):
        self.preferences = prefs


class _FakeSb:
    def __init__(self, prefs):
        self.loaded_ui = _FakeLoadedUi(prefs)


class _GateOnlyHarness(hud.WarningsMixin):
    """Strip WARNING_DEFS so we test only the unsaved-scene gate, not real checks."""

    WARNING_DEFS = (
        {
            "key": "chk_warn_dummy",
            "icon": "!",
            "color": "Red",
            "label": "Dummy",
            "check": lambda self: True,
            "describe": lambda self: "dummy",
        },
    )


class TestUnsavedSceneGate(unittest.TestCase):
    _SENTINEL = object()

    def setUp(self):
        self._original_pm = getattr(hud, "pm", self._SENTINEL)

    def tearDown(self):
        if self._original_pm is self._SENTINEL:
            if hasattr(hud, "pm"):
                delattr(hud, "pm")
        else:
            hud.pm = self._original_pm

    def _make(self, scene_name, skip_unsaved, dummy=True):
        instance = _GateOnlyHarness.__new__(_GateOnlyHarness)
        instance.sb = _FakeSb(
            _FakePrefs(chk_warn_skip_unsaved=skip_unsaved, chk_warn_dummy=dummy)
        )
        hud.pm = _FakePm(scene_name)
        return instance

    def test_gate_blocks_when_scene_untitled_and_skip_enabled(self):
        instance = self._make("", skip_unsaved=True)
        self.assertEqual(instance.evaluate_warnings(), [])

    def test_gate_blocks_when_scene_path_does_not_exist(self):
        instance = self._make("C:/nope/missing.ma", skip_unsaved=True)
        self.assertEqual(instance.evaluate_warnings(), [])

    def test_gate_off_lets_warnings_through_on_untitled(self):
        instance = self._make("", skip_unsaved=False)
        self.assertEqual(len(instance.evaluate_warnings()), 1)

    def test_gate_with_real_saved_scene_lets_warnings_through(self):
        with tempfile.NamedTemporaryFile(suffix=".ma", delete=False) as tmp:
            path = tmp.name
        try:
            instance = self._make(path, skip_unsaved=True)
            self.assertEqual(len(instance.evaluate_warnings()), 1)
        finally:
            os.unlink(path)

    def test_default_pref_value_is_checked(self):
        """The .ui must ship chk_warn_skip_unsaved checked by default."""
        ui_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tentacle", "ui", "preferences.ui",
        )
        with open(ui_path, "r", encoding="utf-8") as f:
            content = f.read()
        idx = content.find('name="chk_warn_skip_unsaved"')
        self.assertNotEqual(idx, -1, "chk_warn_skip_unsaved missing from preferences.ui")
        widget_end = content.find("</widget>", idx)
        widget_block = content[idx:widget_end]
        self.assertIn("<bool>true</bool>", widget_block,
                      "chk_warn_skip_unsaved must default to checked")


if __name__ == "__main__":
    unittest.main()
