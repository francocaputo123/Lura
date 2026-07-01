import wx

from views import navigator, themes
from views.components.navbar import Navbar
from views.frames.deck_frame import DeckFrame
from views.frames.help_frame import HelpFrame
from views.frames.main_frame import MainFrame
from views.frames.stats_frame import StatsFrame
from views.frames.study_frame import StudyFrame
from views.navigator import register_app


class App(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Lura")

        # obtenemos la longitud y la altura del monitor principal
        screen_width, screen_height = wx.DisplaySize()
        self.width = int(screen_height * 0.9)
        self.height = int(screen_height * 0.6)

        self.SetSize((self.width, self.height))

        # panel principal con sizer
        self.main_panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_panel.SetSizer(self.sizer)
        self.navbar = Navbar(
            self.main_panel,
            routes=[
                ("Mis Mazos", MainFrame),
                ("Estadísticas", StatsFrame),
                ("Añadir", DeckFrame),
                ("Ayuda", HelpFrame),
            ],
        )
        self.sizer.Add(self.navbar, 0, wx.EXPAND)
        self._current_frame = None

        register_app(self)
        self.show_frame(MainFrame)

        self.Centre()

    def show_frame(self, frame_class, *args, **kwargs):
        """Básicamente remplaza el panel actual por uno nuevo."""
        if self._current_frame is not None:
            self.sizer.Detach(self._current_frame)
            self._current_frame.Destroy()
        self._current_frame = frame_class(self.main_panel, *args, **kwargs)
        self._current_frame.SetBackgroundColour(themes.PALET["BG_DARK"])
        self._current_frame.SetForegroundColour(themes.PALET["FG_PRIMARY"])
        self.sizer.Add(self._current_frame, 1, wx.EXPAND)
        self.navbar.set_active(frame_class)
        self.main_panel.Layout()
