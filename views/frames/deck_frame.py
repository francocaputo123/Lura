import wx

from views.components.back_button import BackButton

from models.decks import Model

from views import themes as theme

class DeckFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self._build()

    def _build(self) :
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="Editar mazo")
        title.SetForegroundColour(wx.Colour(230, 240, 235))
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title.SetFont(font)
        self.main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        #seccion que funciona como formulario
        self.decks_combo()
        self.cards_input()
        self.save_btn = wx.Button(self, label="Guardar carta")
        self.save_btn.SetBackgroundColour(theme.PALET["CLR_NEW"])
        self.sizer.Add(self.save_btn, 0, wx.ALL | wx.CENTER, 10)
        self.sizer.Add(BackButton(self), 0, wx.ALL | wx.CENTER, 10)

        self.main_sizer.Add((0, 0), 1, wx.EXPAND)
        self.main_sizer.Add(self.sizer, 0, wx.CENTER)
        self.main_sizer.Add((0, 0), 1, wx.EXPAND)

        self.SetSizer(self.main_sizer)

        self.Layout()

        #eventos
        self.Bind(wx.EVT_CHOICE, self._on_change, self.combo)
        self.save_btn.Bind(wx.EVT_BUTTON, self._add_card)
        self.ipt_front.Bind(wx.EVT_TEXT, self._expand_input)
        self.ipt_back.Bind(wx.EVT_TEXT, self._expand_input)
        self.Bind(wx.EVT_SIZE, self._on_resize)


    def _on_resize(self, event) :
        w, h = self.GetParent().GetSize()

        if w > 800 and h > 500 :
            self.ipt_front.SetMinSize((600, -1))
            self.ipt_back.SetMinSize((600, -1))
            self.combo.SetMinSize((600, -1))
            for widget in [self.label_combo, self.label_back, self.label_front] :
                widget.SetFont(theme.font(16))
                widget.SetMinSize((120, -1))

        else :
            self.ipt_front.SetMinSize((400, -1))
            self.ipt_back.SetMinSize((400, -1))
            self.combo.SetMinSize((400, -1))
            for widget in [self.label_combo, self.label_back, self.label_front] :
                widget.SetFont(theme.font(12))
                widget.SetMinSize((110, -1))

        self.Layout()
        event.Skip()

    def _get_decks(self) :
        try :
            model = Model()
            #traemos los mazos, si no existe ninguno, devolvera None
            decks = model.get_decks()

            if not decks :
                return []

            return decks
        except Exception as e :
            wx.MessageBox(
                f"No se pudieron obtener los mazos: {e}",
                "Error de Base de Datos",
                wx.OK | wx.ICON_ERROR
            )

    def decks_combo(self) :
        #obtenemos los mazos
        decks = self._get_decks()
        #sizer que sirve para alinear la etiqueta con el combo
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.label_combo = wx.StaticText(self, label="Mis mazos :")
        self.label_combo.SetFont(theme.font(12))
        self.label_combo.SetMinSize((110, -1))
        self.label_combo.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        self.combo = wx.Choice(self, size=(400,-1))
        self.hbox.Add(self.label_combo, 0, wx.ALIGN_CENTER | wx.RIGHT, border=10)
        self.hbox.Add(self.combo, 1, wx.ALIGN_CENTER , 0)

        self.sizer.Add(self.hbox,0, wx.ALIGN_CENTER | wx.ALL, border=10 )

        if not decks :
            self.combo.Append("Aún no has creado ningun mazo.")

        #agregamos con append cada diccionario del mazo, el nombre y su id oculto
        for deck in decks :
            self.combo.Append(deck['name'], deck['id'])

        if decks or not decks:
            self.combo.SetSelection(0)

    def _on_change(self,event) :
        selection = self.combo.GetSelection()
        return selection

    def cards_input(self) :
        #contenedor principal horizontal para contener a los verticales
        self.vbox_cards_container = wx.BoxSizer(wx.VERTICAL)
        self.hbox_front = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_back = wx.BoxSizer(wx.HORIZONTAL)

        #etiquetas
        self.label_front = wx.StaticText(self, label="Anverso: ")
        self.label_front.SetFont(theme.font(12))
        self.label_front.SetMinSize((110, -1))
        self.label_front.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        self.label_back = wx.StaticText(self, label="Reverso: ")
        self.label_back.SetFont(theme.font(12))
        self.label_back.SetMinSize((110, -1))
        self.label_back.SetForegroundColour(theme.PALET["FG_PRIMARY"])

        #inputs
        self.ipt_front = wx.TextCtrl(self, size=(400, -1), style=wx.TE_MULTILINE | wx.HSCROLL)
        self.ipt_back = wx.TextCtrl(self, size=(400, -1), style=wx.TE_MULTILINE | wx.HSCROLL)

        #ANVERSO
        self.hbox_front.Add(self.label_front, 0, wx.ALIGN_TOP | wx.RIGHT, 10)
        self.hbox_front.Add(self.ipt_front, 1, wx.EXPAND)

        #REVERSO
        self.hbox_back.Add(self.label_back, 0, wx.ALIGN_TOP | wx.RIGHT, 10)
        self.hbox_back.Add(self.ipt_back, 1, wx.EXPAND)

        self.vbox_cards_container.Add(self.hbox_front, 0, wx.BOTTOM, 15)
        self.vbox_cards_container.Add(self.hbox_back, 0, wx.BOTTOM, 15)

        self.sizer.Add(self.vbox_cards_container, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

    #metodo para expandir el input automaticamente
    def _expand_input(self, event) :
        ipt = event.GetEventObject()

        '''
        En esta seccion obtenemos la cantidad de saltos de linea totales.
        Si los saltos son 0, significa que el usuario aun sigue escribiendo en la misma linea
        '''
        text = ipt.GetValue()
        lines = len(text.split("\n"))

        if lines == 0 :
            lines = 1

        #tomamos a la fuente para asi saber la nueva altura que tendra el input
        _, height_line = ipt.GetTextExtent("AG")

        padding = 5

        new_height = (lines * height_line) + padding

        if lines == 1 :
            new_height = -1

        #alto maximo posible
        if new_height > 300 :
            new_height = 300

        current_width = ipt.GetSize().width
        ipt.SetMinSize((current_width, new_height))

        self.Layout()

        event.Skip()

    def _add_card(self, event) :
        if not self._validate_fields() :
            return

        front = self.ipt_front.GetValue().strip()
        back = self.ipt_back.GetValue().strip()

        selection = self.combo.GetSelection()
        deck_id = self.combo.GetClientData(selection)

        response = self._insert_card(deck_id, front, back)

        if response :
            wx.MessageBox(
                "Tarjeta añadida con éxito.",
                "Éxito",
                wx.OK | wx.ICON_INFORMATION
            )
            self.ipt_back.Clear()
            self.ipt_front.Clear()

    def _validate_fields(self) :
        decks = self._get_decks()
        '''
        Validamos que existan mazos para elegir y ademas que el usuario ingreso texto en los inputs.
        '''
        if not decks :
            wx.MessageBox(
                "No puedes agregar cartas, aun no has creado nigun mazo.",
                "No hay mazos",
                wx.OK | wx.ICON_ERROR
            )
            return False

        front = self.ipt_front.GetValue().strip()
        back = self.ipt_back.GetValue().strip()

        if front == "" or back == "" :
            wx.MessageBox(
                "Faltan campos.",
                "",
                wx.OK | wx.ICON_ERROR
            )
            return False
        return True

    def _insert_card(self, deck_id, front, back) :
        try :
            model = Model()
            response = model.insert_card(deck_id, front, back)
            return response
        except Exception as e :
            wx.MessageBox(
                f"Hubo un erro al insertar la carta: {e}",
                "Error en la base de datos",
                wx.OK | wx.ICON_ERROR
            )
            return