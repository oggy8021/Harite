from harite.gui.views.drawer_window_resize import (
    grow_window_after_drawer_expand,
    restore_window_height_after_drawer_collapse,
    shrink_window_after_drawer_collapse,
    sync_drawer_window_height,
)


class _Window:
    def __init__(self, *, width: int = 900, height: int = 640, compact_height: int = 620):
        self._width = width
        self._height = height
        self._compact_height = compact_height
        self._minimum_height = 0
        self.resize_calls: list[tuple[int, int]] = []
        self.adjust_calls = 0

    def setMinimumHeight(self, height: int) -> None:
        self._minimum_height = int(height)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def minimumSizeHint(self):
        return _SizeHint(self._compact_height)

    def adjustSize(self):
        self.adjust_calls += 1
        self._height = self._compact_height

    def resize(self, width, height):
        self._width = int(width)
        self._height = int(height)
        self.resize_calls.append((self._width, self._height))


class _SizeHint:
    def __init__(self, height: int):
        self._height = height

    def height(self):
        return self._height


def test_restore_shrinks_taller_window_to_content_fit_without_adjust_size():
    class _GtkStyleWindow:
        def __init__(self):
            self._width = 900
            self._height = 900
            self._compact_height = 622
            self.resize_calls: list[tuple[int, int]] = []

        def width(self):
            return self._width

        def height(self):
            return self._height

        def minimumSizeHint(self):
            return _SizeHint(self._compact_height)

        def resize(self, width, height):
            self._width = int(width)
            self._height = int(height)
            self.resize_calls.append((self._width, self._height))

    window = _GtkStyleWindow()
    backend = type("B", (), {"_objects": {"main_window": window}})()
    state_attr = "_test_drawer_saved_window_height"

    restore_window_height_after_drawer_collapse(backend, state_attr=state_attr)

    assert window.height() == 622
    assert window.resize_calls == [(900, 622)]


def test_restore_prefers_explicit_resize_over_adjust_size():
    window = _Window(height=900, compact_height=623)
    backend = type("B", (), {"_objects": {"main_window": window}})()

    restore_window_height_after_drawer_collapse(backend, state_attr="_test_drawer_saved_window_height")

    assert window.height() == 623
    assert window.resize_calls == [(900, 623)]
    assert window.adjust_calls == 0


def test_grow_window_when_drawer_needs_more_height():
    window = _Window(height=640, compact_height=980)
    backend = type("B", (), {"_objects": {"main_window": window}})()

    grow_window_after_drawer_expand(backend)

    assert window.height() == 980
    assert window.resize_calls == [(900, 980)]


def test_grow_by_tab_content_delta_when_window_already_tall():
    class _Tab:
        def __init__(self):
            self._height = 252

        def minimumSizeHint(self):
            return _SizeHint(self._height)

    class _Window:
        def __init__(self):
            self._height = 640
            self.resize_calls: list[tuple[int, int]] = []

        def width(self):
            return 900

        def height(self):
            return self._height

        def minimumSizeHint(self):
            return _SizeHint(622)

        def resize(self, width, height):
            self._height = int(height)
            self.resize_calls.append((int(width), int(height)))

    tab = _Tab()
    window = _Window()
    backend = type(
        "B",
        (),
        {
            "_objects": {"main_window": window, "slideshow_tab_box": tab},
            "slideshow_tab_box_drawer_compact_hint": 252,
        },
    )()

    tab._height = 394
    grow_window_after_drawer_expand(
        backend,
        state_attr="_test_drawer_saved_window_height",
        tab_attr="slideshow_tab_box",
    )

    assert window.height() == 782
    assert window.resize_calls == [(900, 782)]


def test_grow_saves_pre_expand_height_for_restore():
    window = _Window(height=640, compact_height=980)
    backend = type("B", (), {"_objects": {"main_window": window}})()
    state_attr = "_test_drawer_saved_window_height"

    grow_window_after_drawer_expand(backend, state_attr=state_attr)

    assert getattr(backend, state_attr) == 640


def test_grow_skips_when_window_already_tall_enough():
    window = _Window(height=980, compact_height=980)
    backend = type("B", (), {"_objects": {"main_window": window}})()

    grow_window_after_drawer_expand(backend)

    assert window.height() == 980
    assert window.resize_calls == []


def test_margins_drawer_open_close_cycle():
    class _DynamicWindow(_Window):
        def __init__(self):
            super().__init__(height=640, compact_height=640)
            self._expanded = False

        def minimumSizeHint(self):
            height = 980 if self._expanded else 640
            return _SizeHint(height)

    window = _DynamicWindow()
    backend = type("B", (), {"_objects": {"main_window": window}})()
    state_attr = "_test_drawer_saved_window_height"

    window._expanded = True
    grow_window_after_drawer_expand(backend, state_attr=state_attr)
    assert window.height() == 980
    assert getattr(backend, state_attr) == 640

    window._expanded = False
    shrink_window_after_drawer_collapse(backend, state_attr=state_attr)
    assert window.height() == 640
    assert not hasattr(backend, state_attr)


def test_shrink_restores_saved_height_when_layout_hint_lags():
    class _LaggyWindow(_Window):
        def __init__(self):
            super().__init__(height=1000, compact_height=1000)
            self._expanded = True

        def minimumSizeHint(self):
            height = 1000 if self._expanded else 622
            return _SizeHint(height)

    window = _LaggyWindow()
    backend = type("B", (), {"_objects": {"main_window": window}})()
    state_attr = "_test_drawer_saved_window_height"
    setattr(backend, state_attr, 640)

    window._expanded = False
    shrink_window_after_drawer_collapse(backend, state_attr=state_attr)

    assert window.height() == 640
    assert not hasattr(backend, state_attr)


def test_sync_on_close_only():
    window = _Window(height=880, compact_height=640)
    backend = type("B", (), {"_objects": {"main_window": window}})()
    state_attr = "_test_drawer_saved_window_height"

    sync_drawer_window_height(backend, expanded=True, state_attr=state_attr)
    assert window.height() == 880

    sync_drawer_window_height(backend, expanded=False, state_attr=state_attr)
    assert window.height() == 640
