import wx

from views.frames.study_frame import StudyFrame

class main(wx.Frame):
    def __init__(self, *args, **kw):
        super(main, self).__init__(*args, **kw)

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = StudyFrame(self)

        self.main_sizer.Add(self.panel, 1, wx.EXPAND, 0)

        self.SetSize(1000,1000)
        self.Show()


app = wx.App()

frame = main(None)

app.MainLoop()