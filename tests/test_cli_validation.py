import pytest

from harite import cli


def test_parse_resolution_valid():
    assert cli.parse_resolution("1920x1080") == (1920, 1080)
    assert cli.parse_resolution("3840X2160") == (3840, 2160)


def test_parse_resolution_invalid():
    with pytest.raises(ValueError):
        cli.parse_resolution("bad")
    with pytest.raises(ValueError):
        cli.parse_resolution("0x1080")


def test_parse_margins_valid():
    assert cli.parse_margins("10,20,30,40") == (10, 20, 30, 40)


def test_parse_margins_invalid():
    with pytest.raises(ValueError):
        cli.parse_margins("10,20,30")
    with pytest.raises(ValueError):
        cli.parse_margins("10,-5,0,0")


def test_parse_display_valid():
    assert cli.parse_display("1280x720") == (1280, 720)
