import wx
from views.components.back_button import BackButton
from views.components.card_widget import CardWidget
from views import themes

class StudyFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()


    def _build(self) :
        self.card_pos = 0
        self.content_pos = 0
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetBackgroundColour(themes.PALET["BG_DARK"])

        title = wx.StaticText(self, label="Study Frame")
        title.SetForegroundColour(themes.PALET["CLR_ACCENT"])
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title.SetFont(font)

        #cualquier boton que se quiera agregar
        self.data_buttons = DATA_BUTTONS = [
            [
                {
                    "name" : "edit",
                    "label" : "Editar",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL
                },
                {
                    "name" : "show_answer",
                    "label" : "Mostrar respuesta",
                    "proportion" : 2,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "func" :[
                        {
                            "name" : "more",
                            "action" :
                            lambda event : self.change_card_pos()
                        }
                    ]
                },
                {
                    "name" : "more",
                    "label" : "Más",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL
                },
                {
                    "name" : "more",
                    "label" : "Hola",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL
                }

            ],
            [
                {
                    "name" : "bad",
                    "label" : "Mal",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL
                },
                {
                    "name" : "good",
                    "label" : "Bien",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL
                },
            ]
        ]
        #contenido
        self.content = DATA_CONTENT = [
            [
                {
                    "label" : "En una lista enlazada tenemos dos tipos importantes de variables, mencione cuales son.",
                    "color" : themes.PALET["FG_PRIMARY"],
                    "font" : (15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                }
            ],
            [
                {
                    "label" : "Son head y tail",
                    "color" : themes.PALET["FG_PRIMARY"],
                    "font" : (15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
                }
            ]
        ]

        self.card = CardWidget(self, size=(500,600), data_buttons=self.data_buttons, position=self.card_pos, content=self.content , c_position=self.content_pos)
        self.sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        self.sizer.Add(self.card, 0, wx.CENTER | wx.ALL, border=20)

    def change_card_pos(self) :
        if self.card_pos == 0 :
            self.card_pos = 1
            self.content_pos = 1
        else :
            self.card_pos = 0
            self.content_pos = 0


        self.card.update_position(self.card_pos, self.content_pos, self.data_buttons, self.content)
