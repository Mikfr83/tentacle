#!/usr/bin/python
# coding=utf-8
"""Regression tests for tentacle.slots.maya.rendering."""

import unittest

try:
    from tentacle.slots.maya import rendering
    _MAYA_AVAILABLE = True
except ImportError:
    rendering = None
    _MAYA_AVAILABLE = False


class _FakeMel:
    def __init__(self):
        self.evaluated = []

    def eval(self, expression):
        self.evaluated.append(expression)


class _FakeCmds:
    def __init__(self):
        self.set_attr_calls = []

    def ls(self, selection=False):
        if selection:
            return ["pCube1"]
        return []

    def listRelatives(self, obj, s=1, ni=1):
        return ["pCubeShape1"]

    def setAttr(self, attr, value):
        self.set_attr_calls.append((attr, value))


class _FakeMtk:
    def __init__(self):
        self.query_called = False
        self.load_called = False

    def vray_plugin(self, load=False, unload=False, query=False):
        if query:
            self.query_called = True
            return False
        if load:
            self.load_called = True


@unittest.skipUnless(_MAYA_AVAILABLE, "Requires maya.cmds")
class TestRenderingVrayAttributes(unittest.TestCase):
    def test_b005_uses_mayatk_vray_plugin(self):
        instance = rendering.Rendering.__new__(rendering.Rendering)

        original_cmds = rendering.cmds
        original_mel = rendering.mel
        original_mtk = rendering.mtk
        fake_cmds = _FakeCmds()
        fake_mel = _FakeMel()
        fake_mtk = _FakeMtk()
        try:
            rendering.cmds = fake_cmds
            rendering.mel = fake_mel
            rendering.mtk = fake_mtk

            instance.b005()

            self.assertTrue(fake_mtk.query_called, "Expected VRay query call")
            self.assertTrue(fake_mtk.load_called, "Expected VRay load call")
            self.assertEqual(fake_cmds.set_attr_calls, [("pCube1.vrayObjectID", 1)])
            # Three vray attribute-group calls per shape, plus one per object id.
            self.assertEqual(len(fake_mel.evaluated), 3)
        finally:
            rendering.cmds = original_cmds
            rendering.mel = original_mel
            rendering.mtk = original_mtk


if __name__ == "__main__":
    unittest.main()
