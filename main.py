import wx, sys
from classes import *
from functions import keyHandler
import wx.lib.mixins.inspection

#app = wx.App()
app = wx.lib.mixins.inspection.InspectableApp()
root = wx.Frame(None, -1, "SIGMA CHUDETTE", size=(800,600))
#root.ShowFullScreen(True)
root.Maximize(True)
vbox = wx.BoxSizer(wx.VERTICAL)
root.SetSizer(vbox)
root.SetAutoLayout(1)

# The main ScrolledPanel found in classes.py
scrolly = Scrolly(root, Doccy(sys.argv[1]))

vbox.Add(scrolly, 0, wx.ALIGN_CENTER)

def on_resize(e):
    scrolly.SetSize(root.GetVirtualSize())
    scrolly.update_pages()
    scrolly.SetupScrolling(scrollToTop=False)

root.Bind(wx.EVT_SIZE, on_resize)
root.Bind(wx.EVT_CHAR_HOOK, lambda e: keyHandler(e, scrolly, root, vbox))

root.Show()
app.MainLoop()
