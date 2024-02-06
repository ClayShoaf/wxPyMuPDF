import wx, fitz
from classes import *

zoom_factor = 1

def keyHandler(key, scrolly: Scrolly, root, vbox):
    global zoom_factor
    #print(f'key.GetEventType() = {key.GetKeyCode()}')
    #print(f'wx.KeyEvent(keyEventType=wx.WXK_ESCAPE) = {wx.KeyEvent(keyEventType=wx.WXK_ESCAPE).GetKeyCode()}')
    #print(f'key = {key}')
    #print(f'Keycode = {key.KeyCode}')
    #print(f'Keycode = {key.GetKeyCode()}')
    #print(f'UnicodeKey= {chr(key.UnicodeKey)}')
    #print(f'RawKeyCode= {key.RawKeyCode}')
    #print(f'= {key.GetModifiers()}')
    
    
    # Leaving this here so I don't have to look it up again when I want to match other keys
    #if key.GetKeyCode() == wx.WXK_ESCAPE:
    #    scrolly.SetFocus()

    if chr(key.UnicodeKey) == "T" and not key.HasAnyModifiers():
        scrolly.rotate_page(2, zoom_factor)

    elif chr(key.UnicodeKey) == "S" and key.ShiftDown():
        scrolly.is_onpage()
        
    elif chr(key.UnicodeKey) == "P" and not key.HasAnyModifiers():
        scrolly.print_data()
        
    elif chr(key.UnicodeKey) == "P" and key.ShiftDown():
        scrolly.show_sizer()
        
    elif chr(key.UnicodeKey) == "S" and not key.HasAnyModifiers():
        scrolly.set_layout()
        
    elif chr(key.UnicodeKey) == "J" and not key.HasAnyModifiers():
        scrolly.ScrollLines(10)
        scrolly.SetupScrolling(scrollToTop=False)
    
    elif chr(key.UnicodeKey) == "K" and not key.HasAnyModifiers():
        scrolly.ScrollLines(-10)
        scrolly.SetupScrolling(scrollToTop=False)
    
    elif chr(key.UnicodeKey) == "D" and not key.HasAnyModifiers():
        scrolly.ScrollLines(30)
        scrolly.SetupScrolling(scrollToTop=False)
    
    elif chr(key.UnicodeKey) == "U" and not key.HasAnyModifiers():
        scrolly.ScrollLines(-30)
        scrolly.SetupScrolling(scrollToTop=False)
    
    elif chr(key.UnicodeKey) == "H" and not key.HasAnyModifiers():
        view_start_x, view_start_y = scrolly.GetViewStart()
        if view_start_x > 0:
            scrolly.Scroll(view_start_x - 10, view_start_y)
    
    elif chr(key.UnicodeKey) == "L" and not key.HasAnyModifiers():
        sppu_x, sppu_y = scrolly.GetScrollPixelsPerUnit()
        view_start_x, view_start_y = scrolly.GetViewStart()
        scroll_range_x = scrolly.GetScrollRange(wx.HORIZONTAL)
        ps_x = scrolly.GetScrollPageSize(wx.HORIZONTAL)
        if view_start_x < scroll_range_x - ps_x:
            scrolly.Scroll(view_start_x + 10, view_start_y)
    
    elif chr(key.UnicodeKey) == "O" and not key.HasAnyModifiers():
        if .3 < zoom_factor <= 1:
            zoom_factor = round(zoom_factor - .1, 1)
        elif 1 < zoom_factor <= 2:
            zoom_factor = round(zoom_factor - .25, 2)
        elif 2 < zoom_factor <= 3:
            zoom_factor = round(zoom_factor - .5, 1)
        elif 3 < zoom_factor <= 6:
            zoom_factor = int(zoom_factor - 1)
        else:
            return
        scrolly.zoom(zoom_factor)

    elif chr(key.UnicodeKey) == "I" and not key.HasAnyModifiers():
        if .3 <= zoom_factor < 1:
            zoom_factor = round(zoom_factor + .1, 1)
        elif 1 <= zoom_factor < 2:
            zoom_factor = round(zoom_factor + .25, 2)
        elif 2 <= zoom_factor < 3:
            zoom_factor = round(zoom_factor + .5, 1)
        elif 3 <= zoom_factor < 6:
            zoom_factor = int(zoom_factor + 1)
        else:
            return
        scrolly.zoom(zoom_factor)
