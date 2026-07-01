import wx
from views import themes as theme

class StatsFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        panel_content = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        selector_sizer = wx.BoxSizer(wx.HORIZONTAL)

        panel_content.SetBackgroundColour(theme.PALET["BG_CARD_PRIMARY"])


        #Selección de mazo
        title = wx.StaticText(panel_content, label="Mazo seleccionado: ")
        title.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        title.SetFont(theme.font(18, wx.FONTWEIGHT_BOLD))
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title.SetFont(font)

        opciones = ["Mazo 1", "Mazo 2", "Mazo 3"]
        self.combo = wx.ComboBox(panel_content, choices=opciones, pos=(20, 20), style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, on_seleccionar)

        def on_seleccionar(self, event):
            self.seleccion = self.combo.GetValue()
            print(f'Elegiste: {self.seleccion}')







        selector_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        selector_sizer.Add(self.combo, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        panel_content.SetSizer(panel_content_sizer)


        main_sizer.Add(panel_content, 1, wx.ALL | wx.EXPAND, 30)
        self.SetSizer(main_sizer)
