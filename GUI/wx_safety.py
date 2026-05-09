import platform


def safe_show_dialog(dialog) -> int | None:
    """Show dialogs in a way that avoids macOS modal crashes.

    On macOS, wx modal dialog entry has been crashing in Cocoa after repeated
    repo-view operations. For non-input browsing dialogs, showing modeless is
    safer and good enough for interaction. Callers that require a modal return
    value should keep using ShowModal directly.
    """
    if dialog is None:
        return None
    try:
        if platform.system() == "Darwin":
            dialog.Show()
            safe_raise(dialog)
            return None
        return dialog.ShowModal()
    except RuntimeError:
        return None


def safe_raise(window) -> bool:
    """Best-effort window raise that avoids known macOS wx crashes."""
    if window is None:
        return False
    try:
        if hasattr(window, "IsBeingDeleted") and window.IsBeingDeleted():
            return False
        if hasattr(window, "IsShown") and not window.IsShown():
            return False
        # wx Raise() has been crashing on macOS in some dialog/window states.
        if platform.system() == "Darwin":
            if hasattr(window, "SetFocus"):
                window.SetFocus()
            return False
        window.Raise()
        return True
    except RuntimeError:
        return False
