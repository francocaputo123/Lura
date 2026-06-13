import wx

from views.components.back_button import BackButton


class DeckFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        title = wx.StaticText(self, label="Deck Frame")
        title.SetForegroundColour(wx.Colour(230, 240, 235))
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        sizer.Add(BackButton(self), 0, wx.ALL | wx.CENTER, 10)
