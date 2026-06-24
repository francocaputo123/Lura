import wx

class My_panel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)


        self.text = wx.StaticText(self, label=
        "Colores del theme,\n"
        "porque ezequiel es un hdp,\n" \
        "que piensa que todos sabemos lo que quizo poner\n" \
        "en sus nombres de variables:")

        # --- Paleta... ---
        """
        BG_DARK = wx.Colour(30, 60, 45)
        BG_CARD = wx.Colour(103, 160, 59)
        BG_CARD_HOVER = wx.Colour(45, 90, 65)
        BG_CATEGORY = wx.Colour(38, 75, 55)
        BG_NAVBAR = wx.Colour(25, 50, 38)

        FG_PRIMARY = wx.Colour(230, 240, 235)
        FG_SECONDARY = wx.Colour(160, 190, 170)
        FG_CATEGORY = wx.Colour(200, 220, 210)

        CLR_NEW = wx.Colour(100, 180, 255)
        CLR_LEARNING = wx.Colour(255, 165, 80)
        CLR_REVIEW = wx.Colour(100, 215, 130)
        CLR_ACCENT = wx.Colour(80, 160, 120)
        CLR_DANGER = wx.Colour(220, 80, 80)
        """

        button_BG_DARK = wx.Button(self, label="BG_DARK")
        button_BG_CARD = wx.Button(self, label="BG_CARD")
        button_BG_CARD_HOVER = wx.Button(self, label="BG_CARD_HOVER")
        button_BG_CATEGORY = wx.Button(self, label="BG_CATEGORY")
        button_BG_NAVBAR = wx.Button(self, label="BG_NAVBAR")
        button_FG_PRIMARY = wx.Button(self, label="FG_PRIMARY")
        button_FG_SECONDARY = wx.Button(self, label="FG_SECONDARY")
        button_FG_CATEGORY = wx.Button(self, label="FG_CATEGORY")
        button_CLR_NEW = wx.Button(self, label="CLR_NEW")
        button_CLR_LEARNING = wx.Button(self, label="CLR_LEARNING")
        button_CLR_REVIEW = wx.Button(self, label="CLR_REVIEW")
        button_CLR_ACCENT = wx.Button(self, label="CLR_ACCENT")
        button_CLR_DANGER = wx.Button(self, label="CLR_DANGER")

        button_BG_DARK.SetBackgroundColour(wx.Colour(30, 60, 45))
        button_BG_CARD.SetBackgroundColour(wx.Colour(34, 68, 50))
        button_BG_CARD_HOVER.SetBackgroundColour(wx.Colour(45, 90, 65))
        button_BG_CATEGORY.SetBackgroundColour(wx.Colour(38, 75, 55))
        button_BG_NAVBAR.SetBackgroundColour(wx.Colour(25, 50, 38))
        button_FG_PRIMARY.SetBackgroundColour(wx.Colour(230, 240, 235))
        button_FG_SECONDARY.SetBackgroundColour(wx.Colour(160, 190, 170))
        button_FG_CATEGORY.SetBackgroundColour(wx.Colour(200, 220, 210))
        button_CLR_NEW.SetBackgroundColour(wx.Colour(100, 180, 255))
        button_CLR_LEARNING.SetBackgroundColour(wx.Colour(255, 165, 80))
        button_CLR_REVIEW.SetBackgroundColour(wx.Colour(100, 215, 130))
        button_CLR_ACCENT.SetBackgroundColour(wx.Colour(80, 160, 120))
        button_CLR_DANGER.SetBackgroundColour(wx.Colour(220, 80, 80))




        sizer_ppad = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_ppad_verticar = wx.BoxSizer(wx.VERTICAL)
        
        sizer_ppad_verticar_dos = wx.BoxSizer(wx.VERTICAL)
        sizer_ppad_verticar_dos.Add(self.text, 0, wx.ALL, 5)

        sizer_ppad_verticar.Add(button_BG_DARK, 0, wx.ALL, 10) 
        sizer_ppad_verticar.Add(button_BG_CARD, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_BG_CARD_HOVER, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_BG_CATEGORY, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_BG_NAVBAR, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_FG_PRIMARY, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_FG_SECONDARY, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_FG_CATEGORY, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_CLR_NEW, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_CLR_LEARNING, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_CLR_REVIEW, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_CLR_ACCENT, 0, wx.ALL, 10)
        sizer_ppad_verticar.Add(button_CLR_DANGER, 0, wx.ALL, 10)



        sizer_ppad.Add(sizer_ppad_verticar)
        sizer_ppad.Add(sizer_ppad_verticar_dos)

        self.SetSizer(sizer_ppad)
        sizer_ppad.Fit(parent)#Reduce los espacios entre los widgets.
        self.Layout()#Fuerza a todos los widgets de un panel a ordenarse. Se usa cuando las interfaces van cambiando.


class My_frame(wx.Frame):

    def __init__(self):
        super().__init__(None, title = "Visualizador de colores")
        panel = My_panel(self)
        self.Center()
        self.Show()



if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = My_frame()
    app.MainLoop()