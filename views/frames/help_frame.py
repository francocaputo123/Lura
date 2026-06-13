import wx

from views.components.back_button import BackButton


class HelpFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        title = wx.StaticText(self, label="Ayuda")
        title.SetForegroundColour(wx.Colour(230, 240, 235))
        font = wx.Font(
            18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )
        title.SetFont(font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        subtitle = wx.StaticText(
            self,
            label=(
                "Esto está en desarrollo\n"
                "(como todo el resto de esta app verga\n"
                "(La ayuda la vamos a necesitar nosotros\n"
                "con esta app de mierda))"
            ),
            size=(400, -1),
            style=wx.ALIGN_CENTER_HORIZONTAL,
        )
        sizer.Add(subtitle, 0, wx.ALL | wx.CENTER, 10)

        sizer.Add(BackButton(self), 0, wx.ALL | wx.CENTER, 10)
