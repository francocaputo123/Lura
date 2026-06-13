"""
Estilos genrales de la app.
Importarlos desde acá en lugar de hardcodearlos en cada frame.
"""

import wx

# --- Paleta... ---
BG_DARK = wx.Colour(30, 60, 45)
BG_CARD = wx.Colour(34, 68, 50)
BG_CARD_HOVER = wx.Colour(45, 90, 65)
BG_CATEGORY = wx.Colour(38, 75, 55)
BG_NAVBAR = wx.Colour(25, 50, 38)

FG_PRIMARY = wx.Colour(230, 240, 235)
FG_SECONDARY = wx.Colour(160, 190, 170)
FG_CATEGORY = wx.Colour(200, 220, 210)

CLR_NEW = wx.Colour(100, 180, 255)
CLR_LEARNING = wx.Colour(255, 165, 80)
CLR_REVIEW = wx.Colour(100, 215, 130)
CLR_ACCENT = wx.Colour(80, 160, 120)
CLR_DANGER = wx.Colour(220, 80, 80)


# --- Tipografía... ---
def font(size=10, weight=wx.FONTWEIGHT_NORMAL, italic=False):
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    return wx.Font(size, wx.FONTFAMILY_DEFAULT, style, weight)


# --- Espaciado... ---
PAD_SM = 6
PAD_MD = 12
PAD_LG = 20
