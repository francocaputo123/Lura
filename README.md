# LURA
> Alternativa a Anki construida con Python, tkinter y SQLite. Spaced repetition con el algoritmo SM-2 sin depender de servidores externos para funcionar

## ¿Qué Es?
Lura es una aplicación de escritorio para estudiar con cartas (flashcards) usando el algoritmo de *spaced repetition SM-2*. Las cartas que te cuestan aparecen seguido, mientras que las que más dominas aparecen cada vez menos.

## Stack
| Capa | Tecnología |
|------|-----------|
| UI | tkinter |
| Lógica | Python 3.14 |
| Base de datos | SQLite 3 |
| Algoritmo | SM-2 |

## Estándares
### Código
- PEP8, o sea:
- Cómo definir variables, funciones, clases, módulos, etc. Escribir código overall
```
user_name = "Ezequiel"
def get_cards(): ...

# PascalCase para clases
class deck_frame: ...

# Espacios alrededor de operadores
resultado = x + y
```

- PEP 257, o sea:
- Cómo documentar clases, funciones, módulos... etc. Ejemplo:
```
def sum(a, b):
    """Aplica una suma de dos números

    Args:
        a: El primer número
        quality: El segúndo número

    Returns:
        la suma del número a y el número b
    """
```

### Git
- Conventional Commits - formato de mensajes: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Una rama por feature (`feat:`), merge a `main` cuando esté listo.

###  DB
- Nombres de tablas y columnas en `snake_case`
- Toda modificación al schema va en un archivo de migración en `db/migrations/`

### Arquitectura
- Sin lógica de negocio en los frames.

## Features
### Gestión de mazos (decks)
 
| Feature | Estado |
|---------|--------|
| Crear, editar y eliminar decks | [] |
| Ver cuántas cartas tiene cada deck | [] |
| Ver cuántas cartas están pendientes para hoy por deck | [] |

### Gestión de Cartas
 
| Feature | Estado |
|---------|--------|
| Crear cartas (frente / dorso) | [] |
| Editar cartas existentes | [] |
| Eliminar cartas | [] |
| Buscar por texto dentro de un deck | [] |
| Buscar globalmente en todos los decks disponibles | [] |
 
---
 
### Sesión de Estudio
 
| Feature | Estado |
|---------|--------|
| Mostrar cartas pendientes de hoy | [] |
| "Jugar" (frente -> botón "ver respuesta" -> calificar dificultad del 1 al 4) | [] |
| Aplicar algoritmo SM-2 al calificar la dificultad de la carta | [] |
| Barra de progreso durante la sesión de estudio (o simplemente mostrar n/t donde n es las cartas jugadas mientras que t es el total de cartas por jugar) | [] |
| Pantalla de resumen al terminar | [] |
| Guardar historial de cada revisión de cartas | [] |
 
---
 
### Estadísticas
 
| Feature | Estado |
|---------|--------|
| cartas estudiadas por día (mes actual) | [] |
| Distribución de calificaciones (1 al 4) | [] |
| Racha actual de días estudiando | [] |
| Total de cartas por estado (nueva / aprendiendo / madura) | [] |
| Tiempo promedio para dominar una carta | [] |
 
---
 
### Import / Export
 
| Feature | Estado |
|---------|--------|
| Importar cartas leyendo un .apkg de Anki | [] |
| Exportar deck a .csv | [] |
| Formato .csv compatible con Anki | [] |
 
---
 
### UI / UX
 
| Feature | Estado |
|---------|--------|
| Navegación entre pantallas sin reiniciar la app | [] |
| Atajos de teclado en la sesión de estudio (Para los gordos Arch como yo, atte: Ezequiel)| [] |
 
---

## Sobre el Algoritmo SM-2
El core de la app, Básicamente cada carta guarda tres valores:
- Un **intervalo*+: Días hasta la próxima revisión.
- Cantidad de **Repeticiones**: Veces respondida correctamente seguidas.
- **Ease Factor (EF)**: Multiplicador de dificultad, siempre arranca en un 2.5

Un sm-2 normalmente tiene calificaciones del 0 al 5. Sin embargo, como cualquier número menor que 3 es básicamente fallar, vamos a manejar esta lógica:

- '< 3' => La carta se resetea, se vuelve a ver a los 15 minutos.
- '>= 3' => El intervalo crece
- El EF se ajusta con cada respuesta, nunca baja del 1.3

## Estructura General del Proyecto
```
lura/
├── main.py # Centro del proyecto
├── db/ # conexión a la DB
├── models/ # llamadas a la base de datos
├── controllers/ # lógica interna de la app
└── views/ # vistas
    ├── frames/ # pantallas 
    └── components/ # componentes reutilizables, onda React
```

## Cómo Correr el Proyecto
```
git clone https://github.com/francocaputo123/Lura.git
cd Lura
./setup.sh        # En Linux/Mac
.\setup.ps1       # En Windows (Trashdown)
```

## Autores
Proyecto Universitario Desarrollado por **Ezequiel Monzón** y **Gian Franco Caputo**

### Distribución de tareas
TODO
