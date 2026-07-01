import wx


class AnimatedSplash(wx.Frame):
    def __init__(self, bitmap, duration):
        super().__init__(None, style=wx.STAY_ON_TOP | wx.NO_BORDER | wx.FRAME_NO_TASKBAR)
        screen_width, screen_height = wx.DisplaySize()
        self.w = int(screen_height * 0.9)
        self.h = int(screen_height * 0.6)


        self.bitmap = bitmap
        self.SetSize(self.w, self.h)
        self.Centre()

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.hold_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.start_collapse, self.hold_timer)
        self.hold_timer.Start(duration, oneShot=True)

        self.animate_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.animate_close, self.animate_timer)

        self.current_height = self.h

    def on_paint(self, event) :
        dc = wx.PaintDC(self)

        image = self.bitmap.ConvertToImage()

        image = image.Rescale(self.w, self.h, wx.IMAGE_QUALITY_HIGH)

        btm = wx.Bitmap(image)

        dc.DrawBitmap(btm, 0, 0, True)

    def start_collapse(self, event) :

        self.animate_timer.Start(15)

    def animate_close(self, event) :

        close_y = 30

        self.current_height -= close_y

        if self.current_height <= 10 :
            self.animate_timer.Stop()
            self.Destroy()
            return

        self.SetSize((self.w, self.current_height))
        self.Centre()
        self.Refresh()