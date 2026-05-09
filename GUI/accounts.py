"""Account management dialog."""

import wx
from application import get_app


class AccountsDialog(wx.Dialog):
    """Dialog for managing GitHub accounts."""

    def __init__(self, parent):
        super().__init__(parent, title="Accounts", size=(400, 300))
        self.app = get_app()

        self.init_ui()
        self.load_accounts()
        self.Center()

    def init_ui(self):
        """Initialize the UI."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Account list
        self.account_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        main_sizer.Add(self.account_list, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.switch_btn = wx.Button(panel, label="Switch To")
        self.switch_btn.Bind(wx.EVT_BUTTON, self.on_switch)
        btn_sizer.Add(self.switch_btn, 0, wx.RIGHT, 5)

        self.add_btn = wx.Button(panel, label="Add GitHub")
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        btn_sizer.Add(self.add_btn, 0, wx.RIGHT, 5)

        self.add_self_hosted_btn = wx.Button(panel, label="Add Self-hosted")
        self.add_self_hosted_btn.Bind(wx.EVT_BUTTON, self.on_add_self_hosted)
        btn_sizer.Add(self.add_self_hosted_btn, 0, wx.RIGHT, 5)

        self.remove_btn = wx.Button(panel, label="Remove")
        self.remove_btn.Bind(wx.EVT_BUTTON, self.on_remove)
        btn_sizer.Add(self.remove_btn, 0, wx.RIGHT, 5)

        self.close_btn = wx.Button(panel, wx.ID_CLOSE, label="Close")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.Add(self.close_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        panel.SetSizer(main_sizer)

        # Keyboard shortcuts
        self.account_list.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def load_accounts(self):
        """Load accounts into the list."""
        self.account_list.Clear()

        for i, account in enumerate(self.app.accounts):
            label = account.display_name or account.username
            service = account.prefs.get("service_name", "GitHub")
            if service and service != "GitHub":
                label += f" - {service}"
            if account == self.app.currentAccount:
                label += " (current)"
            self.account_list.Append(label)

        if self.account_list.GetCount() > 0:
            # Select current account
            for i, account in enumerate(self.app.accounts):
                if account == self.app.currentAccount:
                    self.account_list.SetSelection(i)
                    break

    def on_switch(self, event):
        """Switch to selected account."""
        selection = self.account_list.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        self.app.currentAccount = self.app.accounts[selection]
        self.load_accounts()

        # Refresh main window
        from GUI import main
        if hasattr(main, 'window') and main.window:
            main.window.refresh_all()

    def on_add(self, event):
        """Add a new account."""
        try:
            new_index = len(self.app.accounts)
            self.app.prefs.accounts += 1
            self.app.add_session(new_index)
            self.load_accounts()

            # Refresh main window
            from GUI import main
            if hasattr(main, 'window') and main.window:
                main.window.refresh_all()
        except Exception as e:
            wx.MessageBox(f"Failed to add account: {e}", "Error", wx.OK | wx.ICON_ERROR)
            self.app.prefs.accounts -= 1

    def on_add_self_hosted(self, event):
        """Add a self-hosted GitHub-compatible account."""
        try:
            import config
            from github_api import _TokenAuthDialog

            dlg = _TokenAuthDialog(self)
            result = dlg.ShowModal()
            if result != wx.ID_OK:
                dlg.Destroy()
                return
            api_url, web_url, token = dlg.get_values()
            dlg.Destroy()
            if not token:
                wx.MessageBox("Access token is required.", "Missing Token", wx.OK | wx.ICON_WARNING)
                return

            new_index = len(self.app.accounts)
            prefs_name = "account" + str(new_index) if config.is_portable_mode() else "FastGH/account" + str(new_index)
            prefs = config.Config(name=prefs_name, autosave=True)
            prefs.api_base_url = api_url
            prefs.web_base_url = web_url
            prefs.service_name = web_url
            prefs.access_token = token

            self.app.prefs.accounts += 1
            self.app.add_session(new_index)
            self.load_accounts()

            from GUI import main
            if hasattr(main, 'window') and main.window:
                main.window.refresh_all()
        except Exception as e:
            wx.MessageBox(f"Failed to add self-hosted account: {e}", "Error", wx.OK | wx.ICON_ERROR)
            try:
                self.app.prefs.accounts -= 1
            except Exception:
                pass

    def on_remove(self, event):
        """Remove selected account."""
        selection = self.account_list.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        if len(self.app.accounts) <= 1:
            wx.MessageBox("Cannot remove the only account.", "Error", wx.OK | wx.ICON_WARNING)
            return

        account = self.app.accounts[selection]
        result = wx.MessageBox(
            f"Remove account '{account.display_name or account.username}'?",
            "Confirm Removal",
            wx.YES_NO | wx.ICON_QUESTION
        )

        if result == wx.YES:
            self.app.remove_account(selection)
            self.load_accounts()

            # Refresh main window
            from GUI import main
            if hasattr(main, 'window') and main.window:
                main.window.refresh_all()

    def on_close(self, event):
        """Close the dialog."""
        self.EndModal(wx.ID_CLOSE)

    def on_key(self, event):
        """Handle key events in list."""
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.on_switch(None)
        elif key == wx.WXK_DELETE:
            self.on_remove(None)
        else:
            event.Skip()

    def on_char_hook(self, event):
        """Handle global key events."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.on_close(None)
        else:
            event.Skip()
