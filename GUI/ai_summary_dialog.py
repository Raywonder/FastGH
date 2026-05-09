"""Reusable dialog for AI-generated summaries."""

import wx
from . import theme


class AISummaryDialog(wx.Dialog):
    """Show an AI-generated summary in a readable text box."""

    def __init__(self, parent, title: str, summary: str):
        wx.Dialog.__init__(self, parent, title=title, size=(700, 500))
        panel = wx.Panel(self)
        main = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="&Summary:")
        main.Add(label, 0, wx.LEFT | wx.TOP, 10)

        self.summary_text = wx.TextCtrl(
            panel,
            value=summary,
            style=wx.TE_READONLY | wx.TE_MULTILINE,
            size=(660, 380),
        )
        main.Add(self.summary_text, 1, wx.ALL | wx.EXPAND, 10)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        copy_btn = wx.Button(panel, label="&Copy")
        close_btn = wx.Button(panel, wx.ID_CLOSE, label="Cl&ose")
        buttons.Add(copy_btn, 0, wx.RIGHT, 5)
        buttons.Add(close_btn, 0)
        main.Add(buttons, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        panel.SetSizer(main)
        copy_btn.Bind(wx.EVT_BUTTON, self.on_copy)
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.summary_text.SetFocus()
        theme.apply_theme(self)

    def on_copy(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.summary_text.GetValue()))
            wx.TheClipboard.Close()
            wx.MessageBox("Summary copied to clipboard.", "Copied", wx.OK | wx.ICON_INFORMATION)

    def on_close(self, event):
        self.EndModal(wx.ID_CLOSE)
