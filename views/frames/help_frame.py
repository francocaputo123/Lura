import wx
from views import themes as theme

data_help = DATA_HELP = [
    {
        "title" : "Guía de Inicio Rápido",
        "description" : "Para empezar la aplicación, es tan sensillo como crear(o importar) un mazo de tarjetas. Luego, puedes añadir tarjetas a ese mazo y empezar a estudiar. Durante el estudio, se te presentarán las tarjetas y deberás calificar tu respuesta como 'Mal', 'Bien' o 'Hola'."
    },
    {
        "title" : "Como Funciona el Algoritmo",
        "description" : "Mostramos las tarjetas justo cuando estás a punto de olvidarlas. Si aciertas, tardarán más en volver a aparecer; si fallas, las verás más seguido."
    },
    {
        "title" : "Leyenda de Botones de Calificación",
        "description" : "Otra vez: Se repetira la tarjeta(bajando la dificultad).\n"
                        "Difícil: Se repetira la tarjeta(bajando un poco la dificultad).\n"
                        "Bien: Tardará un poco en volver a aparecer(aumentará un poco la dificultad).\n"
                        "Fácil: Tardará en volver a aparecer(aumentará la dificultad).\n"    },
    {
        "title" : "Gestión de Datos y Privacidad",
        "description" : "La aplicación almacena todos los datos localmente en tu dispositivo, sin enviar información a servidores externos. Esto garantiza que tus tarjetas y progreso de estudio permanezcan privados y seguros.s"
    }
]

class AccordionItem(wx.Panel):
    def __init__(self, parent, title_text, description_text):
        super().__init__(parent)
        
        self.is_expanded = False
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        #Sizer para el Título y el Icono 
        self.title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #Icono del triángulo
        self.icon = wx.StaticText(self, label="► ")
        self.icon.SetForegroundColour(theme.PALET["FG_PRIMARY"]) 
        self.icon.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        #Texto del título
        self.title = wx.StaticText(self, label=title_text)
        self.title.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        self.title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        self.title_sizer.Add(self.icon, 0, wx.ALIGN_CENTER_VERTICAL)
        self.title_sizer.Add(self.title, 1, wx.ALIGN_CENTER_VERTICAL)
        
        #Texto de la descripción  
        self.description = wx.StaticText(self, label=description_text)
        self.description.SetForegroundColour(theme.PALET["FG_PRIMARY"]) 
        self.description.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.description.Wrap(450) #Salto de linea
        self.description.Hide()    #Oculta inicialmente
        
        #Ensambla todo 
        self.main_sizer.Add(self.title_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        self.main_sizer.Add(self.description, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 20) 
        
        self.SetSizer(self.main_sizer)
        
        #Si hacen clic en el icono o en el título, se activa la función
        self.icon.Bind(wx.EVT_LEFT_DOWN, self.on_toggle)
        self.title.Bind(wx.EVT_LEFT_DOWN, self.on_toggle)

    def on_toggle(self, event):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.icon.SetLabel("▼ ")
            self.description.Show()
        else:
            self.icon.SetLabel("► ")
            self.description.Hide()
            
        #Le decimos al panel padre que recalcule los tamaños para hacer espacio al texto nuevo
        self.GetParent().Layout()

class HelpFrame(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        #Sizers de la ventana
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        
        #Panel principal que contendra todo
        panel_content = wx.Panel(self)
        panel_content.SetBackgroundColour(theme.PALET["BG_CARD_PRIMARY"])
        
        
        #Título de la ventana 
        title = wx.StaticText(panel_content, label="Ayuda")
        title.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        title_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT )
        panel_content_sizer.Add(title_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        #Añadir los elementos del acordeón, con el título y el texto de la descripción(en ese orden)
        data_help = DATA_HELP
        
        item1 = AccordionItem(panel_content, data_help[0]["title"], data_help[0]["description"])
        item2 = AccordionItem(panel_content, data_help[1]["title"], data_help[1]["description"])
        item3 = AccordionItem(panel_content, data_help[2]["title"], data_help[2]["description"])
        item4 = AccordionItem(panel_content, data_help[3]["title"], data_help[3]["description"])

        
        #Añadimos los elementos al sizer
        panel_content_sizer.Add(item1, 0, wx.EXPAND | wx.ALL, 5)
        panel_content_sizer.Add(item2, 0, wx.EXPAND | wx.ALL, 5)
        panel_content_sizer.Add(item3, 0, wx.EXPAND | wx.ALL, 5)
        panel_content_sizer.Add(item4, 0, wx.EXPAND | wx.ALL, 5)

        
        panel_content.SetSizer(panel_content_sizer)
        main_sizer.Add(panel_content, 1, wx.EXPAND | wx.ALL, 30)
        self.SetSizer(main_sizer)