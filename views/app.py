import tkinter as tk
from screeninfo import get_monitors

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title = "Lura"

        # Ezequiel tiene dos monitores, por lo que hay que obtener por lo menos el monitor principal.
        monitor = get_monitors()[0]

        # obtenemos la longitud y la altura del monitor principal, luego, obtenemos la posición en la que deberá aparecer la ventana (idealmente es en el centro, por algo se divide)
        self.width = int(monitor.width * 0.6)
        self.height = int(monitor.height * 0.6)
        self.position_x = monitor.x + (monitor.width - self.width) // 2
        self.position_y = monitor.y + (monitor.height - self.height) // 2

        tk.Label(self, text="Bienvenido a Lura", font=("Arial", 18)).pack(pady=20)

        self.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")

    def show_frame(self, frame_class, **kwargs):
        """ Básicamente remplaza el frame actual por uno nuevo. """
        if (self._current_frame is not None):
            self._current_frame.destroy()
        self._current_frame = frame_class(self, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

