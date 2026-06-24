"""Algoritmo de spaced repetition SM-2 con olor a Lura

Esta NO es la versión original de SM-2. Es una variante ajustada, ()claramente)
para funcionar con una escala de calificación de 1 a 4 (en lugar de la escala clásica 0-5).
El umbral tradicional se mantiene:
Una respuesta menor a 3 reinicia la carta y la vuelve a mostrar a los 15 minutos,
Una respuesta mayor o igual a 3 hace crecer el intervalo.

Cada carta guarda tres valores:
- El intervalo: Días hasta la próxima revisión.
- Las repeticiones: Veces respondida correctamente seguidas.
- El "Ease Factor" (EF): Multiplicador de dificultad. Arranca en 2.5
  y nunca baja de 1.3.

La fórmula original del EF usa `(5 - q)` porque la escala va de 0 a 5.
Acá se usa `(4 - q)` para adaptarla a 1-4, de modo que el
mejor rating (4) incremente el EF, el rating débil (3) lo mantenga
plano, y los fallos `(1 y 2)` lo bajen.
"""

MAX_QUALITY = 4


def sm2(quality, interval=0, repetitions=0, ease_factor=2.5):
    """Aplica el algoritmo SM-2 a una carta y devuelve su nuevo estado como un objeto

    Args:
        quality: Calificación del 1 al 4 dada por el usuario, donde 1 es un fallo total y 4 es una respuesta fácil.
        interval: Intervalo actual en días hasta la próxima revisión.
        repetitions: Cantidad de respuestas correctas seguidas.
        ease_factor: Multiplicador de dificultad actual de la carta.

    Returns:
        Un diccionario con el nuevo `interval` (en días, como float),
        `repetitions` (int) y `ease_factor` (float) de la carta.

    Raises:
        ValueError: Si `quality` está fuera del rango 1 a 4. (teóricamente, TEÓRICAMENTE no debería pasar)
    """

    if not 1 <= quality <= 4:
        """ Teóricamente esto no debería pasar... sos alto gil si provocaste esto. """
        raise ValueError("quality debe estar entre 1 y 4, gil")

    if quality < 3:
        interval = 15 / (24 * 60)
        repetitions = 0
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1

    delta = 0.1 - (MAX_QUALITY - quality) * (0.08 + (MAX_QUALITY - quality) * 0.02)
    ease_factor = max(1.3, round(ease_factor + delta, 4))

    return {
        "interval": interval,
        "repetitions": repetitions,
        "ease_factor": ease_factor,
    }

