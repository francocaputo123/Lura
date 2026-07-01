import wx
from views.components.back_button import BackButton
from views.components.card_widget import CardWidget
from views import themes
from controllers.cards_controller import CardController

class StudyFrame(wx.Panel):
    def __init__(self, parent, deck_title=None, deck_id=None):
        super().__init__(parent)
        self.deck_id = deck_id if deck_id else None
        self.deck_title = deck_title if deck_title else "Study Frame"
        self.controller = CardController()
        self.cards = self.controller.new_cards(self.deck_id)
        self._build()


    def _build(self) :
        self.card_pos = 0
        self.content_pos = 0
        self.current_card = 0

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetBackgroundColour(themes.PALET["BG_DARK"])

        title = wx.StaticText(self, label=f"{self.deck_title}")
        title.SetForegroundColour(themes.PALET["CLR_ACCENT"])
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title.SetFont(font)

        #cualquier boton que se quiera agregar
        self.data_buttons = DATA_BUTTONS = [
            [
                {
                    "name" : "show_answer",
                    "label" : "Mostrar respuesta",
                    "proportion" : 2,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "color" : themes.PALET["CLR_LEARNING"],
                    "func" :[
                        {
                            "name" : "show",
                            "action" :
                            lambda event : self.change_card_pos()
                        }
                    ]
                }
            ],
            [
                {
                    "name" : "again",
                    "label" : "Otra vez",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "color" : themes.PALET["CLR_LEARNING"],
                    "func" :[
                        {
                            "name" : "next",
                            "action" :
                            lambda event : self._handle_next_card(1)
                        }
                    ]
                },
                {
                    "name" : "hard",
                    "label" : "Difícil",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "color" : themes.PALET["CLR_LEARNING"],
                    "func" :[
                        {
                            "name" : "next",
                            "action" :
                            lambda event : self._handle_next_card(2)
                        }
                    ]
                },
                {
                    "name" : "good",
                    "label" : "Bien",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "color" : themes.PALET["CLR_LEARNING"],
                    "func" :[
                        {
                            "name" : "next",
                            "action" :
                            lambda event : self._handle_next_card(3)
                        }
                    ]
                },
                {
                    "name" : "easy",
                    "label" : "Fácil",
                    "proportion" : 1,
                    "margin": 10,
                    "flag" : wx.CENTER | wx.ALL,
                    "color" : themes.PALET["CLR_LEARNING"],
                    "func" :[
                        {
                            "name" : "next",
                            "action" :
                            lambda event : self._handle_next_card(4)
                        }
                    ]
                },
            ]
        ]

        self.sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        self.content = None

        if not self.cards :
            self.info_panel = wx.Panel(self)
            self.vinfo_sizer = wx.BoxSizer(wx.VERTICAL)
            self.info_panel.SetBackgroundColour(themes.PALET["BG_CARD_HOVER"])
            end_text = wx.StaticText(self.info_panel, label="¡Felicidades, has terminado este mazo por el momento!")
            end_text_bottom = wx.StaticText(self.info_panel, label="Vuelve mañana para seguir con mas cartas")
            end_text.SetForegroundColour(themes.PALET["FG_PRIMARY"])
            end_text_bottom.SetForegroundColour(themes.PALET["FG_PRIMARY"])
            end_text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            end_text_bottom.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.vinfo_sizer.Add(end_text, 0, wx.ALL, 10)
            self.vinfo_sizer.Add(end_text_bottom, 0, wx.ALL, 10)
            self.info_panel.SetSizer(self.vinfo_sizer)
            self.sizer.Add(self.info_panel, 1 , wx.EXPAND | wx.ALL ,20 )
            self.Layout()
            return

        if self.cards  :
            self.content = self._get_current_card()
            self.card = CardWidget(
                self,
                size=(500,600),
                data_buttons=self.data_buttons,
                position=self.card_pos,
                content=self.content ,
                c_position=self.content_pos
                )
            self.sizer.Add(self.card, 0, wx.CENTER | wx.ALL, border=20)


    def _get_current_card(self) :

        card_data = self.cards[self.current_card]

        front = card_data.get("front", "No hay anverso")
        back = card_data.get("back", "No hay reverso")
        deck_id = card_data.get("deck_id", 1)

        #media
        images = card_data.get("images", [])
        audios = card_data.get("audios", [])

        front_card = [
            {
                "type" : "text",
                "label" : front,
                "color" : themes.PALET["FG_PRIMARY"],
                "font" : (15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            }
        ]

        back_card = [
            {
                    "type" : "text",
                    "label" : back,
                    "color" : themes.PALET["FG_PRIMARY"],
                    "font" : (15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            }
        ]

        for img_data in images:
            front_card.append(img_data)

        for audio_data in audios:
            back_card.append(audio_data)

        return [
            front_card,
            back_card
        ]

    def _handle_next_card(self, quality) :

        current_card = self.cards[self.current_card]
        self.controller.update_next_review(current_card.get("id", -1), current_card.get("deck_id", -1), quality)

        self.current_card += 1

        if self.current_card < len(self.cards):
            self.content = self._get_current_card()
            # Reiniciamos la vista del widget al Frente
            self.card.update_position(
                new_card_position=0,
                new_content_position=0,
                data_buttons=self.data_buttons,
                content=self.content
            )
        else :
            self.card.Hide()
            end_text = wx.StaticText(self, label="¡Has terminado de estudiar este mazo!")
            end_text.SetForegroundColour(themes.PALET["CLR_ACCENT"])
            end_text.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.sizer.Add(end_text, 0, wx.CENTER | wx.ALL, 40)
            self.Layout()

    def change_card_pos(self) :
        if self.card_pos == 0 :
            self.card_pos = 1
            self.content_pos = 1
        else :
            self.card_pos = 0
            self.content_pos = 0


        self.card.update_position(self.card_pos, self.content_pos, self.data_buttons, self.content)
