from harite.gui.views.slideshow_options_drawer import (
    FEWER_LABEL,
    MORE_LABEL,
    toggle_slideshow_options_drawer,
)


class _Drawer:
    def __init__(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def setVisible(self, visible):
        self._visible = bool(visible)


class _Trigger:
    def __init__(self):
        self.text = MORE_LABEL

    def setText(self, value):
        self.text = value


def test_toggle_qt_style_drawer():
    drawer = _Drawer()
    trigger = _Trigger()
    backend = type("B", (), {"_objects": {"slideshow_options_drawer": drawer, "btn_slideshow_options_more": trigger}})()

    toggle_slideshow_options_drawer(backend)
    assert drawer.isVisible()
    assert trigger.text == FEWER_LABEL

    toggle_slideshow_options_drawer(backend)
    assert not drawer.isVisible()
    assert trigger.text == MORE_LABEL


class _Revealer:
    def __init__(self):
        self._revealed = False

    def get_reveal_child(self):
        return self._revealed

    def set_reveal_child(self, revealed):
        self._revealed = bool(revealed)


def test_toggle_gtk_revealer():
    revealer = _Revealer()
    trigger = _Trigger()
    backend = type(
        "B",
        (),
        {"_objects": {"slideshow_options_revealer": revealer, "btn_slideshow_options_more": trigger}},
    )()

    toggle_slideshow_options_drawer(backend)
    assert revealer.get_reveal_child()
    assert trigger.text == FEWER_LABEL


def test_toggle_restores_window_height_on_close():
    from harite.gui.views.slideshow_options_drawer import toggle_slideshow_options_drawer

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
                "slideshow_options_drawer": drawer,
                "btn_slideshow_options_more": trigger,
            }
        },
    )()

    toggle_slideshow_options_drawer(backend)
    toggle_slideshow_options_drawer(backend)
    assert not drawer.isVisible()
    assert window.height() == 860

    compact_window = _Window(height=640, compact_height=820)
    compact_backend = type(
        "B",
        (),
        {
            "_objects": {
                "main_window": compact_window,
                "slideshow_options_drawer": drawer,
                "btn_slideshow_options_more": trigger,
            }
        },
    )()
    toggle_slideshow_options_drawer(compact_backend)
    assert compact_window.height() == 820
    toggle_slideshow_options_drawer(compact_backend)
    assert compact_window.height() == 640
