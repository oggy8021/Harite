"""Margins options drawer toggle (P-08, P-07 open-state styling parity)."""


class _Drawer:
    def __init__(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def setVisible(self, visible):
        self._visible = bool(visible)


class _Trigger:
    def __init__(self):
        from harite.gui.views.margins_options_drawer import MORE_LABEL

        self.text = MORE_LABEL

    def setText(self, value):
        self.text = value


def test_toggle_qt_style_drawer():
    from harite.gui.views.margins_options_drawer import (
        FEWER_LABEL,
        MORE_LABEL,
        toggle_margins_options_drawer,
    )

    drawer = _Drawer()
    trigger = _Trigger()
    backend = type("B", (), {"_objects": {"margins_options_drawer": drawer, "btn_margins_options_more": trigger}})()

    toggle_margins_options_drawer(backend)
    assert drawer.isVisible()
    assert trigger.text == FEWER_LABEL

    toggle_margins_options_drawer(backend)
    assert not drawer.isVisible()
    assert trigger.text == MORE_LABEL


def test_toggle_restores_window_height_on_close():
    from harite.gui.views.margins_options_drawer import toggle_margins_options_drawer

    class _Window:
        def __init__(self, *, height: int, compact_height: int):
            self._height = height
            self._compact_height = compact_height
            self._minimum_height = 0
            self.resize_calls = []
            self.adjust_calls = 0

        def width(self):
            return 900

        def height(self):
            return self._height

        def setMinimumHeight(self, height: int) -> None:
            self._minimum_height = int(height)

        def minimumSizeHint(self):
            compact = self._compact_height

            class _Hint:
                @staticmethod
                def height():
                    return compact

            return _Hint()

        def adjustSize(self):
            self.adjust_calls += 1
            self._height = self._compact_height

        def resize(self, width, height):
            self._height = height
            self.resize_calls.append((width, height))

    drawer = _Drawer()
    trigger = _Trigger()
    window = _Window(height=860, compact_height=640)
    backend = type(
        "B",
        (),
        {
            "_objects": {
                "main_window": window,
                "margins_options_drawer": drawer,
                "btn_margins_options_more": trigger,
            }
        },
    )()

    toggle_margins_options_drawer(backend)
    toggle_margins_options_drawer(backend)
    assert not drawer.isVisible()
    assert window.height() == 860

    compact_window = _Window(height=640, compact_height=980)
    compact_backend = type(
        "B",
        (),
        {
            "_objects": {
                "main_window": compact_window,
                "margins_options_drawer": drawer,
                "btn_margins_options_more": trigger,
            }
        },
    )()
    toggle_margins_options_drawer(compact_backend)
    assert compact_window.height() == 980
    toggle_margins_options_drawer(compact_backend)
    assert compact_window.height() == 640
