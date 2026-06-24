import wx

from views import navigator
from views import themes as theme

DECKS = [
    {
        "category": "English",
        "decks": [
            {"name": "Grammar", "new": 5, "learning": 12, "review": 3},
            {"name": "To be", "new": 0, "learning": 8, "review": 7},
        ],
    },
    {
        "category": "Data Structures & Algorithms",
        "decks": [
            {"name": "Tipos de Datos", "new": 10, "learning": 4, "review": 1},
            {"name": "Recursion", "new": 3, "learning": 6, "review": 0},
            {"name": "Búsqueda", "new": 7, "learning": 2, "review": 4},
            {"name": "Ordenar", "new": 0, "learning": 9, "review": 2},
        ],
    },
    {
        "category": "Java Programming",
        "decks": [
            {"name": "Tipos Primitivos", "new": 8, "learning": 1, "review": 5},
            {"name": "Clases", "new": 2, "learning": 14, "review": 0},
            {"name": "Memoria y punteros", "new": 6, "learning": 3, "review": 9},
        ],
    },
]


class DeckRow(wx.Panel):
    def __init__(self, parent, deck: dict):
        super().__init__(parent)
        self.deck = deck
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.BG_CARD)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(32)

        name_lbl = wx.StaticText(self, label=self.deck["name"])
        name_lbl.SetForegroundColour(theme.FG_PRIMARY)
        name_lbl.SetFont(theme.font(10))
        sizer.Add(name_lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 8)

        for count, color, tip in [
            (self.deck["new"], theme.CLR_NEW, "Nuevas"),
            (self.deck["learning"], theme.CLR_LEARNING, "Aprendiendo"),
            (self.deck["review"], theme.CLR_REVIEW, "Repasar"),
        ]:
            lbl = wx.StaticText(self, label=str(count))
            lbl.SetForegroundColour(color if count > 0 else theme.FG_SECONDARY)
            lbl.SetFont(
                theme.font(10, wx.FONTWEIGHT_BOLD) if count > 0 else theme.font(10)
            )
            lbl.SetToolTip(tip)
            sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 24)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_PAINT, self._on_paint)

        for widget in [self] + list(self.GetChildren()):
            widget.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
            widget.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
            widget.Bind(wx.EVT_LEFT_UP, self._on_click)

    def _on_enter(self, _):
        self.SetBackgroundColour(theme.BG_CARD_HOVER)
        self.Refresh()

    def _on_leave(self, _):
        self.SetBackgroundColour(theme.BG_CARD)
        self.Refresh()

    def _on_click(self, _):
        wx.MessageBox(f"Abriendo {self.deck['name']}...", "Mazo")

    def _on_paint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        w, h = self.GetSize()
        dc.SetPen(wx.Pen(theme.CLR_ACCENT, 1))
        dc.DrawLine(32, h - 1, w, h - 1)


class CategoryPanel(wx.Panel):
    def __init__(self, parent, group: dict):
        super().__init__(parent)
        self.group = group
        self.expanded = True
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.BG_DARK)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header = wx.Panel(self)
        self.header.SetBackgroundColour(theme.BG_CATEGORY)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.arrow = wx.StaticText(self.header, label="▼")
        self.arrow.SetForegroundColour(theme.FG_CATEGORY)
        self.arrow.SetFont(theme.font(9))
        h_sizer.Add(self.arrow, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)

        title = wx.StaticText(self.header, label=self.group["category"])
        title.SetForegroundColour(theme.FG_CATEGORY)
        title.SetFont(theme.font(10, wx.FONTWEIGHT_BOLD))
        h_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 7)

        self.header.SetSizer(h_sizer)
        self.main_sizer.Add(self.header, 0, wx.EXPAND)

        self.rows_panel = wx.Panel(self)
        self.rows_panel.SetBackgroundColour(theme.BG_DARK)
        rows_sizer = wx.BoxSizer(wx.VERTICAL)
        for deck in self.group["decks"]:
            rows_sizer.Add(DeckRow(self.rows_panel, deck), 0, wx.EXPAND)
        self.rows_panel.SetSizer(rows_sizer)
        self.main_sizer.Add(self.rows_panel, 0, wx.EXPAND)

        self.SetSizer(self.main_sizer)

        for widget in [self.header, self.arrow, title]:
            widget.Bind(wx.EVT_LEFT_UP, self._toggle)
            widget.Bind(
                wx.EVT_ENTER_WINDOW,
                lambda e: (
                    self.header.SetBackgroundColour(theme.BG_CARD_HOVER)
                    or self.header.Refresh()
                ),
            )
            widget.Bind(
                wx.EVT_LEAVE_WINDOW,
                lambda e: (
                    self.header.SetBackgroundColour(theme.BG_CATEGORY)
                    or self.header.Refresh()
                ),
            )

    def _toggle(self, _):
        self.expanded = not self.expanded
        self.rows_panel.Show(self.expanded)
        self.arrow.SetLabel("▼" if self.expanded else "▶")
        self.GetParent().Layout()
        self.GetParent().FitInside()


class MainFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.BG_DARK)
        outer = wx.BoxSizer(wx.VERTICAL)

        header = wx.Panel(self)
        header.SetBackgroundColour(theme.BG_DARK)
        hdr_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(header, label="Mis Mazos")
        title.SetForegroundColour(theme.FG_PRIMARY)
        title.SetFont(theme.font(18, wx.FONTWEIGHT_BOLD))
        hdr_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, theme.PAD_LG)

        for label, color in [
            ("Nuevas", theme.CLR_NEW),
            ("Aprendiendo", theme.CLR_LEARNING),
            ("Repasar", theme.CLR_REVIEW),
        ]:
            lbl = wx.StaticText(header, label=label)
            lbl.SetForegroundColour(color)
            lbl.SetFont(theme.font(9))
            hdr_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 24)

        header.SetSizer(hdr_sizer)
        outer.Add(header, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, theme.PAD_MD)

        scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        scroll.SetScrollRate(0, 12)
        scroll.SetBackgroundColour(theme.BG_DARK)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        for group in DECKS:
            scroll_sizer.Add(CategoryPanel(scroll, group), 0, wx.EXPAND | wx.BOTTOM, 2)

        scroll.SetSizer(scroll_sizer)
        scroll.FitInside()
        outer.Add(scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, theme.PAD_MD)

        footer = wx.Panel(self)
        footer.SetBackgroundColour(theme.BG_NAVBAR)
        ftr_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.import_btn = wx.Button(footer, label="Importar")
        self.import_btn.SetFont(theme.font(10))
        self.import_btn.Bind(wx.EVT_BUTTON, self._on_import)
        ftr_sizer.Add(
            self.import_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP | wx.BOTTOM, theme.PAD_MD
        )

        footer.SetSizer(ftr_sizer)
        outer.Add(footer, 0, wx.EXPAND)

        self.SetSizer(outer)

    def _on_import(self, _):
        from views.frames.import_frame import ImportFrame

        navigator.show_frame(ImportFrame)
