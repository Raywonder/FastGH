"""FastGH - A fast GitHub client."""

import sys
sys.dont_write_bytecode = True

import platform
import os

# On Windows, redirect stderr to errors.log
if platform.system() != "Darwin":
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        f = open(os.path.join(app_dir, "errors.log"), "a")
        sys.stderr = f
    except:
        pass

import wx

# Create wx.App first
wx_app = wx.App(redirect=False)

# Prevent multiple instances
instance_checker = wx.SingleInstanceChecker("FastGH-" + wx.GetUserId())
if instance_checker.IsAnotherRunning():
    wx.MessageBox("Another instance of FastGH is already running.", "FastGH", wx.OK | wx.ICON_WARNING)
    sys.exit(1)

# Import and initialize application
import application
from application import get_app
from GUI import main, theme

# Load application (initializes accounts, preferences)
fastgh_app = get_app()
fastgh_app.load()

# Create main window
main.create_window()

# Apply theme
theme.apply_theme(main.window)

# A user-initiated app launch should always present the main window. The
# saved window_shown flag is only used for close/quit-to-tray behavior after
# startup, not to suppress all windows on launch.
fastgh_app.prefs.window_shown = True
wx.CallAfter(main.window.Show)
wx.CallAfter(main.window._focus_current_list)

# Start main loop
wx_app.MainLoop()
