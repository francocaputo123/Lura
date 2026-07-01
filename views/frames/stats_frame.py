import wx
from views import themes as theme

class StatsFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        panel_content = wx.Panel(self)
        selector_panel = wx.Panel(panel_content)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        selector_sizer = wx.BoxSizer(wx.VERTICAL)
        

        panel_content.SetBackgroundColour(theme.PALET["BG_CARD_PRIMARY"])
        selector_panel.SetBackgroundColour(theme.PALET["FG_PRIMARY"])


        selector = wx.StaticText(selector_panel, label="Seleccionar mazo: ")
        selector.SetForegroundColour(theme.PALET["BG_DARK"])
        selector.SetFont(theme.font(18, wx.FONTWEIGHT_BOLD))
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        selector.SetFont(font)








        panel_content.SetSizer(panel_content_sizer)
        selector_panel.SetSizer(selector_sizer)

        panel_content_sizer.Add(selector_panel, 0, wx.EXPAND | wx.ALL, 10)
        selector_sizer.Add(selector, 1, wx.CENTER | wx.ALL, 10)
        main_sizer.Add(panel_content, 1, wx.ALL | wx.EXPAND, 30)
        self.SetSizer(main_sizer)