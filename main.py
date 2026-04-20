import tkinter as tk
from db.connection import Database
from views.app import App

def main():
    db = Database()
    db.connect()

    app = App()
    app.mainloop()

    db.close()
if __name__ == "__main__":
    main()
