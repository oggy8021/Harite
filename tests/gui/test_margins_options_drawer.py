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


class _Revealer:
    def __init__(self):
        self._revealed = False

    def get_reveal_child(self):
        return self._revealed

    def set_reveal_child(self, revealed):
        self._revealed = bool(revealed)


def test_toggle_gtk_revealer():
    from harite.gui.views.margins_options_drawer import (
        FEWER_LABEL,
        toggle_margins_options_drawer,
    )

    revealer = _Revealer()
    trigger = _Trigger()
    backend = type(
        "B",
        (),
        {"_objects": {"margins_options_revealer": revealer, "btn_margins_options_more": trigger}},
    )()

    toggle_margins_options_drawer(backend)
    assert revealer.get_reveal_child()
    assert trigger.text == FEWER_LABEL
