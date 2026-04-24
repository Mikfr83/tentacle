# tentacle

**Role**: Desktop app. Slots architecture integrates Maya / Max / Standalone DCCs.

**Nav**: [← root](../CLAUDE.md) · **Deps**: [pythontk](../pythontk/CLAUDE.md) · [uitk](../uitk/CLAUDE.md) · [mayatk](../mayatk/CLAUDE.md)

## Architecture

- `tentacle/slots/<dcc>/*.py` — DCC-specific slot handlers (e.g. `slots/maya/rendering.py`).
- `tentacle/tcl_maya/` — Maya integration entry + MarkingMenu.
- **UI**: Qt via [uitk](../uitk/CLAUDE.md). Widget naming: `tb###`, `b###`, `list###`, etc.

## Conventions

- Slot classes inherit from the DCC base; slot methods are named after their widget (`tb000`, `b005`).
- UI files pair with slot files (same basename). Enforced by `test_ui_integrity.py`.
- Heavy scenes: prefer `maya.cmds` over PyMEL in hot paths; suspend viewport refresh around bulk edits.

## Tests

Structural suite: `test_package.py`, `test_slot_integrity.py`, `test_ui_integrity.py` (runs in CI — `.github/workflows/tests.yml`).

See [CHANGELOG.md](CHANGELOG.md) for history.
