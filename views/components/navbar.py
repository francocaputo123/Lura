import wx

from views import themes


class NavLink(wx.StaticText):
    def __init__(self, parent, label, frame_class):
        super().__init__(parent, label=label)
        self.frame_class = frame_class
        self._active = False

        self.SetFont(themes.font(10))
        self._set_style()

        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def set_active(self, active: bool):
        self._active = active
        self._set_style()
        self.Refresh()

    def _set_style(self):
        if self._active:
            self.SetForegroundColour(themes.PALET["FG_PRIMARY"])
        else:
            self.SetForegroundColour(themes.PALET["FG_SECONDARY"])

    def _on_click(self, _):
        from views.navigator import show_frame

        show_frame(self.frame_class)

    def _on_enter(self, _):
        if not self._active:
            self.SetForegroundColour(themes.PALET["FG_PRIMARY"])
            self.Refresh()

    def _on_leave(self, _):
        if not self._active:
            self.SetForegroundColour(themes.PALET["FG_SECONDARY"])
            self.Refresh()

    def _on_paint(self, event):
        event.Skip()
        if self._active:
            dc = wx.PaintDC(self)
            w, h = self.GetSize()
            dc.SetPen(wx.Pen(themes.PALET["CLR_ACCENT"], 2))
            dc.DrawLine(0, h - 2, w, h - 2)


class Navbar(wx.Panel):
    """Navbar persistente"""

    def __init__(self, parent, routes: list):
        super().__init__(parent)
        self.SetBackgroundColour(themes.PALET["BG_NAVBAR"])
        self._links: list[NavLink] = []

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # App name / logo
        logo = wx.StaticText(self, label="Lura")
        logo.SetFont(themes.font(10, wx.FONTWEIGHT_BOLD))
        logo.SetForegroundColour(themes.PALET["CLR_ACCENT"])
        sizer.Add(logo, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, themes.SPACING["PAD_LG"])
        sizer.AddSpacer(themes.SPACING["PAD_LG"])

        # Nav links
        for label, frame_class in routes:
            link = NavLink(self, label, frame_class)
            sizer.Add(
                link, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, themes.SPACING["PAD_MD"]
            )
            self._links.append(link)

        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.SetMinSize((-1, 44))

    def set_active(self, frame_class):
        for link in self._links:
            link.set_active(link.frame_class == frame_class)
