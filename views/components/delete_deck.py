import wx
from views import themes as theme

from models.decks import Model


class DeleteDeck(wx.Dialog) :
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(500, 250))

        self._build()

    def _build(self) :
        self.main_panel = wx.Panel(self)
        self.dialog = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        model = Model()
        self.decks = model.get_decks()

        self.main_panel.SetBackgroundColour(theme.PALET["BG_DARK"])

        self.vbox.AddStretchSpacer(1)

        #titulo y combo
        self.label = wx.StaticText(self.main_panel, label="Borrar mazo")
        self.label.SetFont(theme.font(15))
        self.combo = wx.Choice(self.main_panel, size=(300,-1))

        if not self.decks :
            self.combo.Append("Aún no has creado ningun mazo.")

        for deck in self.decks :
            self.combo.Append(deck['name'], deck['id'])

        if self.decks or not self.decks:
            self.combo.SetSelection(0)

        #botones
        self.confirm_btn = wx.Button(self.main_panel,wx.ID_OK, label="Borrar")

        self.confirm_btn.SetBackgroundColour(theme.PALET["CLR_DANGER"])

        self.confirm_btn.SetForegroundColour(theme.PALET["FG_PRIMARY"])

        self.vbox.Add(self.label, 0, wx.ALL | wx.CENTER, border=10)
        self.vbox.Add(self.combo, 0, wx.ALL | wx.CENTER, border=10)
        self.vbox.Add(self.confirm_btn, 0, wx.ALL | wx.CENTER, border=10)

        self.vbox.AddStretchSpacer(1)
        self.main_panel.SetSizer(self.vbox)

        #bindeo de eventos
        self.confirm_btn.Bind(wx.EVT_BUTTON, self._on_accept)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Cancelar")

        self.dialog.Add(self.main_panel, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(self.dialog)

    def _on_accept(self, event) :
        position = self.combo.GetSelection()
        deck_id = self.combo.GetClientData(position)

        model = Model()
        response = model.delete_deck(deck_id)
        if response :
            wx.MessageBox("Mazo borrado con éxito", "Borrado", wx.OK)
            self.Layout()
            self.Refresh()
        else :
            wx.MessageBox("No se pudo borrar el mazo", "Error", wx.OK | wx.ICON_ERROR)
            return

        event.Skip()
