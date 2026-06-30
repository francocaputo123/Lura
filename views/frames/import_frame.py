import wx

from controllers.import_controller import DeckCollisionError
from controllers.import_controller import ImportError as ControllerImportError
from views import themes as theme
from views.components.back_button import BackButton


class ImportFrame(wx.Panel):
    """Pantalla de importacion de mazos desde archivos .apkg de Anki."""

    def __init__(self, parent, selected_path=None):
        super().__init__(parent)
        self.selected_path = selected_path
        self._build()

    def _build(self):
        self.SetBackgroundColour(theme.PALET["BG_DARK"])
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        title = wx.StaticText(self, label="Importar mazo de Anki")
        title.SetForegroundColour(theme.PALET["FG_PRIMARY"])
        title.SetFont(theme.font(18, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)

        if self.selected_path:
            file_label = f"Archivo seleccionado:\n{self.selected_path}"
        else:
            file_label = "No se seleccionó ningún archivo."
        self.file_lbl = wx.StaticText(
            self,
            label=file_label,
            style=wx.ALIGN_CENTER_HORIZONTAL,
        )
        self.file_lbl.SetForegroundColour(theme.PALET["FG_SECONDARY"])
        self.file_lbl.SetFont(theme.font(10))
        sizer.Add(self.file_lbl, 0, wx.ALL | wx.CENTER, 10)

        self.import_btn = wx.Button(self, label="Importar")
        self.import_btn.SetFont(theme.font(10))
        self.import_btn.Enable(bool(self.selected_path))
        self.import_btn.Bind(wx.EVT_BUTTON, self._on_import)
        sizer.Add(self.import_btn, 0, wx.ALL | wx.CENTER, 10)

        self.status_lbl = wx.StaticText(self, label="")
        self.status_lbl.SetForegroundColour(theme.PALET["FG_SECONDARY"])
        self.status_lbl.SetFont(theme.font(10))
        sizer.Add(self.status_lbl, 0, wx.ALL | wx.CENTER, 10)

        sizer.AddStretchSpacer(1)
        sizer.Add(BackButton(self), 0, wx.ALL | wx.CENTER, 10)

    def _on_import(self, _):
        """Ejecuta la importacion del archivo seleccionado."""
        if not self.selected_path:
            return

        self.status_lbl.SetLabel("Importando...")
        self.import_btn.Disable()
        busy = wx.BusyInfo("Importando mazo, aguardá un momento...")

        try:
            from controllers.import_controller import import_apkg

            result = import_apkg(self.selected_path)
            msg = (
                f"Importación exitosa.\n"
                f"Mazos: {result['decks_imported']}\n"
                f"Cartas: {result['cards_imported']}\n"
                f"Omitidas: {result['skipped']}"
            )
            self.status_lbl.SetLabel(msg.replace("\n", " | "))
            wx.MessageBox(
                msg,
                "Importación completada",
                wx.OK | wx.ICON_INFORMATION,
            )
        except DeckCollisionError as exc:
            self.status_lbl.SetLabel(f"Error: {exc}")
            wx.MessageBox(
                str(exc),
                "Error de importación",
                wx.OK | wx.ICON_ERROR,
            )
        except ControllerImportError as exc:
            self.status_lbl.SetLabel(f"Error: {exc}")
            wx.MessageBox(
                str(exc),
                "Error de importación",
                wx.OK | wx.ICON_ERROR,
            )
        finally:
            del busy
            self.import_btn.Enable()
