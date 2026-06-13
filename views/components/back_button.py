import wx

from views import themes
from views.navigator import show_frame


class BackButton(wx.Button):
    def __init__(self, parent, target=None):
        super().__init__(parent, label="<- Volver al inicio")
        self._target = target
        self.SetFont(themes.font(10))
        self.Bind(wx.EVT_BUTTON, self._on_click)

    def _on_click(self, _):
        if self._target is None:
            from views.frames.main_frame import MainFrame

            self._target = MainFrame
        show_frame(self._target)
