from harite.gui.views.footer_feedback import (
    ERROR_NONE,
    STATUS_READY,
    format_footer_error,
    format_footer_status,
    footer_error_is_active,
)


def test_trace_state_hides_status_and_error():
    assert format_footer_status(phase="Slideshow", state="started", error=None) == STATUS_READY
    assert format_footer_error(phase="Slideshow", state="started", error=None) == ERROR_NONE


def test_error_param_goes_to_error_row_only():
    assert format_footer_status(phase="Input", state="error", error="boom") == STATUS_READY
    assert format_footer_error(phase="Input", state="error", error="boom") == "Error: boom"


def test_owner_error_level_promotes_message_to_error_row():
    message = "dual-source slideshow requires two detected displays"
    assert (
        format_footer_status(
            phase="Slideshow",
            state=message,
            error=None,
            status_level="error",
        )
        == STATUS_READY
    )
    assert (
        format_footer_error(
            phase="Slideshow",
            state=message,
            error=None,
            status_level="error",
        )
        == f"Error: {message}"
    )


def test_margin_preflight_ready_shows_human_status():
    message = "margin text ready in left top position (1030x80)"
    assert format_footer_status(phase="Margins", state=message, error=None) == f"Status: {message}"
    assert format_footer_error(phase="Margins", state=message, error=None) == ERROR_NONE


def test_dialog_unavailable_maps_to_human_error():
    assert format_footer_error(phase="Input", state="dialog-unavailable", error=None) == (
        "Error: Could not open file dialog"
    )


def test_footer_error_is_active():
    assert footer_error_is_active(ERROR_NONE) is False
    assert footer_error_is_active("Error: failed") is True
