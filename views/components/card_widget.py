import wx

from views import themes


CARD_CONTENT = [
    {
        "question" : "En una lista enlazada tenemos dos tipos importantes de variables, mencione cuales son."
    },
    {
        "answer" : "Son head y tail"
    }
]

class CardWidget(wx.Panel):
    def __init__(self, parent, size, data_buttons, content, **kwargs):
        self.card_position = kwargs.pop("position", 0)
        self.content_position = kwargs.pop("c_position", 0)
        super().__init__(parent, size=size,**kwargs)

        self.base_width = size[0]
        self.base_height = size[1]

        self.SetMinSize((self.base_width, self.base_height))

        self._build(data_buttons, content)

    def _build(self, data_buttons, content) :

        self.SetBackgroundColour(themes.PALET["BG_CARD"])
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.content_layout = self._content(content)
        self.main_sizer.Add(self.content_layout, 1, wx.ALL, 15)

        self.buttons= self._buttons_content(data_buttons)
        self.main_sizer.Add(self.buttons, 0, wx.EXPAND , 0)

        self.Fit()
    def _content(self, content) :
        content_panel = wx.Panel(self)

        content_panel.SetBackgroundColour(themes.PALET["BG_CARD_HOVER"])

        inside_sizer = wx.BoxSizer(wx.VERTICAL)

        for data in content[self.content_position] :
            text = wx.StaticText(content_panel, label=data["label"])
            text.SetForegroundColour(data["color"])
            font = wx.Font(*data["font"])
            text.SetFont(font)

            inside_sizer.Add(text, 1, wx.ALL  , 15)

        content_panel.SetSizer(inside_sizer)
        return content_panel

    def _buttons_content(self, data_buttons) :
        content_buttons = wx.Panel(self)

        content_buttons.SetBackgroundColour(themes.PALET["BG_CATEGORY"])

        inside_buttons = wx.BoxSizer(wx.HORIZONTAL)

        #esta iteracion nos ayuda a crear los botones que necesitemos con data_buttons
        for data in data_buttons[self.card_position] :
            #se crea el boton contenedor y se le asigna a la clase con setattr
            btn = wx.Button(content_buttons, label=data["label"], size=wx.DefaultSize)

            setattr(self, f"btn_{data['name']}", btn)
            if "func" in data :
                for f_data in data["func"] :
                    #guardamos la funcion
                    action = f_data["action"]
                    setattr(self, f_data["name"], f_data["action"])
                    btn.Bind(
                        wx.EVT_BUTTON,
                        lambda event, action=action : action(event)
                        )

            inside_buttons.Add(btn, data["proportion"], data["flag"], data["margin"])

        content_buttons.SetSizer(inside_buttons)

        return content_buttons

    #esta funcion sirvepara actualizar la posicion del array
    def update_position(self, new_card_position, new_content_position , data_buttons, content):
        self.card_position = new_card_position
        self.content_position = new_content_position

        #limpiamos los contenedores internos
        self.content_layout.Destroy()
        self.buttons.Destroy()

        #los volvemos a reconstruir
        self.content_layout = self._content(content)
        self.buttons = self._buttons_content(data_buttons)

        #los añadimos al principal
        self.main_sizer.Add(self.content_layout, 1, wx.ALL | wx.EXPAND, 15)
        self.main_sizer.Add(self.buttons, 0, wx.EXPAND, 0)

        self.Refresh()
        self.Layout()

