from generated_gui import *

class Viewer(ViewerFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._init_buffer()
    
    def quit_viewer( self, event ):
        self.Close()

    def draw_btn_clicked( self, event ):
        src = self.sourceCodeTextBox.GetValue()
        header = "import python3d as pd\n"
        header += "def addpart(part):\n\tparts.append(part)\n"
        self._execute_drawing(header + src)

    def _execute_drawing(self, code):
        parts = []
        res = exec(code, {"parts":parts})
        self._draw_drawing(parts)

    def _init_buffer(self):
        size = self.canvasScrolledWindow.Size
        #self._buffer = wx.Bitmap(size.width, size.height)
        self._buffer = wx.Bitmap(5000, 5000)

    def _draw_drawing(self, parts):
        dc = wx.BufferedDC(wx.ClientDC(self.canvasScrolledWindow), self._buffer)
        pen   = wx.Pen("black", 2, wx.SOLID)
        brush = wx.Brush("white", wx.SOLID)  # (for filling in areas)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.SetBackground(brush)
        dc.Clear()
        dc.DrawRectangle(10, 10, 100, 50)
        
    def paint_canvas( self, event ):
        dc = wx.BufferedPaintDC(self.canvasScrolledWindow, self._buffer)
    
    def resize_canvas( self, event ):
        event.Skip()

if __name__ == "__main__":
    app = wx.App()
    viewer = Viewer(None)
    viewer.Show()
    app.MainLoop()
