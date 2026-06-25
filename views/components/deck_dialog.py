import wx
from views import themes as theme

from models.decks import Model 

class DeckDialog(wx.Dialog) :
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(500, 250))

        self._build()

    def _build(self) :
        self.main_panel = wx.Panel(self)
        self.dialog = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.main_panel.SetBackgroundColour(theme.PALET["BG_DARK"])

        self.vbox.AddStretchSpacer(1)

        #titulo e input para obtener el nombre
        self.label = wx.StaticText(self.main_panel, label="Dale un nombre a tu mazo")
        self.label.SetFont(theme.font(20))
        self.ipt = wx.TextCtrl(self.main_panel, size=(200,-1))
        self.ipt.SetValue("Escribe un nombre...")
        self.vbox.Add(self.label, 0, wx.ALIGN_CENTER | wx.TOP, border=10)
        self.vbox.Add(self.ipt, 0, wx.ALIGN_CENTER | wx.TOP, border=10)

        #botones
        self.confirm_btn = wx.Button(self.main_panel,wx.ID_OK, label="Crear mazo")        
        self.close_btn = wx.Button(self.main_panel,wx.ID_CANCEL, label="Cancelar")

        self.confirm_btn.SetBackgroundColour(theme.PALET["CLR_NEW"])
        self.close_btn.SetBackgroundColour(theme.PALET["CLR_DANGER"])

        self.confirm_btn.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        self.close_btn.SetForegroundColour(theme.PALET["FG_PRIMARY"])


        #se utiliza un sizer horixontal para color los botones
        self.hbox.Add(self.confirm_btn, 0, wx.RIGHT, border=10)
        self.hbox.Add(self.close_btn, 0)

        self.vbox.Add(self.hbox, 0, wx.ALIGN_CENTER | wx.TOP, border=10)
        self.vbox.AddStretchSpacer(1)
        self.main_panel.SetSizer(self.vbox)

        #bindeo de eventos
        self.confirm_btn.Bind(wx.EVT_BUTTON, self._on_accept)

        self.dialog.Add(self.main_panel, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(self.dialog)

    def _on_accept(self, event) :
        deck_name = self.ipt.GetValue()
        
        if not deck_name or deck_name == "Escribe un nombre...":
            wx.MessageBox("El nombre del mazo no puede estar vacío.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        #llamamos al modelo, caso de que existe el nombre, devolvera false, sino true
        model = Model()
        response = model.create_deck(deck_name)
        if response :
            wx.MessageBox("Mazo creado con éxito", "Mazo creado", wx.OK)
        else :
            wx.MessageBox("Ya existe un mazo con ese nombre", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        event.Skip()