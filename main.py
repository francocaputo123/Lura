#! /usr/bin/python3
import wx
import wx.adv
from pathlib import Path

from db.connection import Database
from views.app import App
from views.frames.splash_frame import AnimatedSplash


def main():

    db = Database()
    db.connect()

    app = wx.App(False)

    #seccion splash
    abs_path = Path('public/lura_logo.png').resolve()

    splash_bitmap = wx.Bitmap(str(abs_path), wx.BITMAP_TYPE_PNG)

    splash = AnimatedSplash(splash_bitmap, 1000)
    splash.Show()

    frame = App()
    wx.Yield()
    frame.Show()
    app.MainLoop()

    db.close()


if __name__ == "__main__":
    main()


