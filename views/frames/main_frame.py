import wx

from controllers.main_controller import load_deck_groups
from views import navigator
from views import themes as theme


class DeckRow(wx.Panel):
    def __init__(self, parent, deck: dict):
        super().__init__(parent)
        self.deck = deck
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.PALET["BG_DARK"])
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(32)

        name_lbl = wx.StaticText(self, label=self.deck["name"])
        name_lbl.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        name_lbl.SetFont(theme.font(10))
        sizer.Add(name_lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 8)

        for count, color, tip in [
            (self.deck["new"], theme.PALET["CLR_NEW"], "Nuevas"),
            (self.deck["learning"], theme.PALET["CLR_LEARNING"], "Aprendiendo"),
            (self.deck["review"], theme.PALET["CLR_REVIEW"], "Repasar"),
        ]:
            lbl = wx.StaticText(self, label=str(count))
            lbl.SetForegroundColour(color if count > 0 else theme.PALET["FG_SECONDARY"])
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
        self.SetBackgroundColour(theme.PALET["BG_CARD_HOVER"])
        self.Refresh()

    def _on_leave(self, _):
        self.SetBackgroundColour(theme.PALET["BG_DARK"])
        self.Refresh()

    def _on_click(self, _):
        from views.frames.study_frame import StudyFrame
        navigator.show_frame(StudyFrame, deck_title=self.deck['name'], deck_id=self.deck['id'])

    def _on_paint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        w, h = self.GetSize()
        dc.SetPen(wx.Pen(theme.PALET["CLR_ACCENT"], 1))
        dc.DrawLine(32, h - 1, w, h - 1)


class CategoryPanel(wx.Panel):
    def __init__(self, parent, group: dict):
        super().__init__(parent)
        self.group = group
        self.expanded = True
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.PALET["BG_DARK"])
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header = wx.Panel(self)
        self.header.SetBackgroundColour(theme.PALET["BG_CATEGORY"])
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.arrow = wx.StaticText(self.header, label="▼")
        self.arrow.SetForegroundColour(theme.PALET["BG_CATEGORY"])
        self.arrow.SetFont(theme.font(9))
        h_sizer.Add(self.arrow, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)

        title = wx.StaticText(self.header, label=self.group["category"])
        title.SetForegroundColour(theme.PALET["FG_CATEGORY"])
        title.SetFont(theme.font(10, wx.FONTWEIGHT_BOLD))
        h_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 7)

        self.header.SetSizer(h_sizer)
        self.main_sizer.Add(self.header, 0, wx.EXPAND)

        self.rows_panel = wx.Panel(self)
        self.rows_panel.SetBackgroundColour(theme.PALET["BG_DARK"])
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
                    self.header.SetBackgroundColour(theme.PALET["BG_CARD_HOVER"])
                    or self.header.Refresh()
                ),
            )
            widget.Bind(
                wx.EVT_LEAVE_WINDOW,
                lambda e: (
                    self.header.SetBackgroundColour(theme.PALET["BG_CARD_HOVER"])
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
        self.SetBackgroundColour(theme.PALET["BG_DARK"])
        outer = wx.BoxSizer(wx.VERTICAL)

        header = wx.Panel(self)
        header.SetBackgroundColour(theme.PALET["BG_DARK"])
        hdr_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(header, label="Mis Mazos")
        title.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        title.SetFont(theme.font(18, wx.FONTWEIGHT_BOLD))
        hdr_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, theme.SPACING["PAD_LG"])

        for label, color in [
            ("Nuevas", theme.PALET["CLR_NEW"]),
            ("Aprendiendo", theme.PALET["CLR_LEARNING"]),
            ("Repasar", theme.PALET["CLR_REVIEW"]),
        ]:
            lbl = wx.StaticText(header, label=label)
            lbl.SetForegroundColour(color)
            lbl.SetFont(theme.font(9))
            hdr_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 24)

        header.SetSizer(hdr_sizer)
        outer.Add(header, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, theme.SPACING["PAD_MD"])

        scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        scroll.SetScrollRate(0, 12)
        scroll.SetBackgroundColour(theme.PALET["BG_DARK"])
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        groups = load_deck_groups()
        if groups:
            for group in groups:
                scroll_sizer.Add(
                    CategoryPanel(scroll, group), 0, wx.EXPAND | wx.BOTTOM, 2
                )
        else:
            empty_lbl = wx.StaticText(
                scroll,
                label="No hay mazos.\nCreá un mazo o importalo desde Anki o NotebookLM",
                style=wx.ALIGN_CENTER_HORIZONTAL,
            )
            empty_lbl.SetForegroundColour(theme.PALET["FG_SECONDARY"])
            empty_lbl.SetFont(theme.font(12))
            scroll_sizer.Add(empty_lbl, 1, wx.ALIGN_CENTER | wx.ALL, theme.SPACING["PAD_LG"])

        scroll.SetSizer(scroll_sizer)
        scroll.FitInside()
        outer.Add(scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, theme.SPACING["PAD_MD"])

        footer = wx.Panel(self)
        footer.SetBackgroundColour(theme.PALET["BG_NAVBAR"])
        ftr_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.import_btn = wx.Button(footer, label="Importar")
        self.import_btn.SetFont(theme.font(10))
        self.import_btn.Bind(wx.EVT_BUTTON, self._on_import)
        ftr_sizer.Add(
            self.import_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP | wx.BOTTOM, theme.SPACING["PAD_MD"]
        )

        self.create_deck_btn = wx.Button(footer, label="Crear mazo")
        self.create_deck_btn.SetFont(theme.font(10))
        self.create_deck_btn.Bind(wx.EVT_BUTTON, self._on_create)
        ftr_sizer.Add(
            self.create_deck_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP | wx.BOTTOM, theme.SPACING["PAD_MD"]
        )

        self.delete_deck = wx.Button(footer, label="Borrar mazo")
        self.delete_deck.SetFont(theme.font(10))
        self.delete_deck.Bind(wx.EVT_BUTTON, self._on_delete)
        ftr_sizer.Add(
            self.delete_deck, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP | wx.BOTTOM, theme.SPACING["PAD_MD"]
        )

        footer.SetSizer(ftr_sizer)
        outer.Add(footer, 0, wx.EXPAND)

        self.SetSizer(outer)

    def _on_import(self, _):
        with wx.FileDialog(
            self,
            "Seleccionar mazo de Anki",
            wildcard="Anki packages (*.apkg|*.apkg)",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            selected_path = dlg.GetPath()

        from views.frames.import_frame import ImportFrame

        navigator.show_frame(ImportFrame, selected_path=selected_path)

    def _on_create(self, _) :
        from ..components.deck_dialog import DeckDialog

        dialog = DeckDialog(self, "Crear mazo")

        if dialog.ShowModal() == wx.ID_OK :
            from views.frames.deck_frame import DeckFrame

            dialog.Destroy()
            navigator.show_frame(DeckFrame)

    def _on_delete(self, _) :
        from ..components.delete_deck import DeleteDeck

        dialog = DeleteDeck(self, "Borrar mazo")

        if dialog.ShowModal() == wx.ID_OK :
            dialog.Destroy()

        navigator.show_frame(MainFrame)