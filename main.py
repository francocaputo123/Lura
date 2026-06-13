import wx

from db.connection import Database
from views.app import App


def main():
    db = Database()
    db.connect()

    app = wx.App(False)
    frame = App()
    frame.Show()
    app.MainLoop()

    db.close()


if __name__ == "__main__":
    main()
