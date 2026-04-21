import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title = "Lura"

        # obtenemos la longitud y la altura del monitor principal, (la longitud es una proporción de la altura total)
        self.width = int(self.winfo_screenheight() * 0.9)
        self.height = int(self.winfo_screenheight() * 0.6)

        tk.Label(self, text="Bienvenido a Lura", font=("Arial", 18)).pack(pady=20)

        self.geometry(f"{self.width}x{self.height}")

    def show_frame(self, frame_class, **kwargs):
        """ Básicamente remplaza el frame actual por uno nuevo. """
        if (self._current_frame is not None):
            self._current_frame.destroy()
        self._current_frame = frame_class(self, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

