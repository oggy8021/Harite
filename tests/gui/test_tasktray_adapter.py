from pathlib import Path

import pytest

from harite.gui.adapters import tasktray_adapter
from harite.gui.adapters.tasktray_adapter import GtkTaskTrayAdapter


class _FakeIndicator:
    def __init__(self):
        self.calls = []

    def set_icon(self, icon_name):
        self.calls.append(("set_icon", icon_name))


class _TypeErrorIndicator(_FakeIndicator):
    def set_icon_full(self, _icon_name, _desc):
        raise TypeError("legacy signature mismatch")


class _RuntimeErrorIndicator(_FakeIndicator):
    def set_icon_full(self, _icon_name, _desc):
        raise RuntimeError("indicator backend failed")


class _MenuItem:
    def __init__(self):
        self.label = ""
        self.sensitive = True

    def set_label(self, label):
        self.label = label

    def set_sensitive(self, enabled):
        self.sensitive = bool(enabled)


class _Window:
    def is_visible(self):
        return True


class _SignalBackend:
    _watch_running = False


def _build_adapter(indicator):
    adapter = GtkTaskTrayAdapter(
        gtk_module=object(),
        glib_module=object(),
        indicator_module=object(),
        binding_name="AyatanaAppIndicator3",
        signal_backend=_SignalBackend(),
        window=_Window(),
    )
    adapter._indicator = indicator
    adapter._visible_item = _MenuItem()
    adapter._watch_start_item = _MenuItem()
    adapter._watch_stop_item = _MenuItem()
    return adapter


def test_tasktray_refresh_falls_back_to_set_icon_on_set_icon_full_typeerror():
    indicator = _TypeErrorIndicator()
    adapter = _build_adapter(indicator)

    adapter.refresh()

    assert len(indicator.calls) == 1
    assert indicator.calls[0][0] == "set_icon"
    assert Path(indicator.calls[0][1]).name == "harite_off.svg"


def test_tasktray_refresh_propagates_real_set_icon_full_failure():
    indicator = _RuntimeErrorIndicator()
    adapter = _build_adapter(indicator)

    with pytest.raises(RuntimeError, match="indicator backend failed"):
        adapter.refresh()


def test_tasktray_current_icon_name_falls_back_when_product_icon_is_missing(monkeypatch):
    class _MissingResource:
        def joinpath(self, *_parts):
            return self

        def is_file(self):
            return False

    adapter = _build_adapter(_FakeIndicator())
    monkeypatch.setattr(tasktray_adapter, "files", lambda _package: _MissingResource())

    assert adapter._current_icon_name(watch_running=False) == "media-playback-pause"
    assert adapter._current_icon_name(watch_running=True) == "applications-graphics"


def test_tasktray_current_icon_name_propagates_unexpected_resource_lookup_failure(monkeypatch):
    adapter = _build_adapter(_FakeIndicator())
    monkeypatch.setattr(tasktray_adapter, "files", lambda _package: (_ for _ in ()).throw(RuntimeError("resource lookup failed")))

    with pytest.raises(RuntimeError, match="resource lookup failed"):
        adapter._current_icon_name(watch_running=False)


def test_initialize_tasktray_propagates_unexpected_runtime_error_from_gtk_probe(monkeypatch):
    def fake_import_module(name):
        if name == "gi":
            raise RuntimeError("gtk probe failed")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(tasktray_adapter, "import_module", fake_import_module)

    with pytest.raises(RuntimeError, match="gtk probe failed"):
        tasktray_adapter.initialize_tasktray(object())