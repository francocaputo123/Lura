"""
Módulo de navegación universal.

Cualquier frame puede importar `show_frame` y llamarlo con la clase del panel que quiera renderizar.
"""

_app = None


def register_app(app):
    """Registra la instancia de App para que el navigator pueda operar sobre ella, basically."""
    global _app
    _app = app


def show_frame(frame_class, *args, **kwargs):
    """Navega a un panel de forma universal, es simplemente una instancia de lo que definimos en app
    Args:
        frame_class: Clase del panel (wx.Panel) a mostrar.
        *args, **kwargs: Argumentos adicionales que se pasan al constructor del panel.

    Raises:
        RuntimeError: Si no se ha registrado una App antes de llamar a esta función.
    """
    if _app is None:
        raise RuntimeError(
            "App not registered with navigator. Llamá a register_app() primero."
        )
    _app.show_frame(frame_class, *args, **kwargs)
