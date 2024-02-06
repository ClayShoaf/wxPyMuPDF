import wx
import wx.lib.scrolledpanel as scrolled
import fitz

# The main scrollable window that contains all of the widgets
class Scrolly(scrolled.ScrolledPanel):
    def __init__(self, parent, doccy):
        scrolled.ScrolledPanel.__init__(self, parent, -1, size=parent.GetSize())
        self.SetAutoLayout(0)
        self.Bind(wx.EVT_SCROLLWIN, self.onScroll)

        self.zoom_factor = 1
        self.gap = 10
        self.layout = 1
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.fgs = wx.FlexGridSizer(cols=1, vgap=10, hgap=10)
        self.gbs = wx.GridBagSizer(self.gap, self.gap)
        self.gbs.SetEmptyCellSize((-self.gap,-self.gap))

        self.doccy = doccy
        self.pages = []
        self.drawn_pages = set()

        for i,dl in enumerate(self.doccy.dls):
            self.pages.append(Page(self, i+1, dl))
            self.gbs.Add(self.pages[i], (i,0), flag=wx.ALIGN_CENTER_HORIZONTAL)

        self.hbox.AddStretchSpacer(1)
        self.hbox.Add(self.gbs)
        self.hbox.AddStretchSpacer(1)
        self.SetSizer(self.hbox)
        self.SetupScrolling()

    def onScroll(self,evt: wx.ScrollWinEvent):
        self.is_onpage()
        evt.Skip()
        
    def OnChildFocus(self, evt):
        pass

    def set_layout(self):
        if self.layout == 1:
            for i,item in enumerate(self.gbs.GetChildren()):
                pos = item.GetPos()
                if i%2:
                    w,h = item.GetSize()
                    prev = self.gbs.GetChildren()[i-1]
                    prev_w,prev_h = prev.GetSize()
                    if w-h < 0:
                        if prev_w - prev_h > 0:
                            self.gbs.SetItemPosition(item.GetWindow(), (pos[0], pos[1]+1))
                        else:
                            self.gbs.SetItemPosition(item.GetWindow(), (pos[0]-1, pos[1]+1))
            self.layout = 2
        elif self.layout == 2:
            for i,item in enumerate(self.gbs.GetChildren()):
                pos = item.GetPos()
                if i%2:
                    w,h = item.GetSize()
                    prev = self.gbs.GetChildren()[i-1]
                    prev_w,prev_h = prev.GetSize()
                    if w-h < 0:
                        if prev_w - prev_h > 0:
                            self.gbs.SetItemPosition(item.GetWindow(), (pos[0], pos[1]-1))
                        else:
                            self.gbs.SetItemPosition(item.GetWindow(), (pos[0]+1, pos[1]-1))
            self.layout = 1
        self.gbs.Layout()
        self.SetupScrolling(scrollToTop=False)
        self.is_onpage()
    
    def zoom(self, zoom_factor=1, x=None, y=None):
        self.zoom_factor = zoom_factor
        scroll_size_y = self.GetScrollPageSize(wx.VERTICAL)
        scroll_pos_y = self.GetScrollPos(wx.VERTICAL)
        scroll_range_x = self.GetScrollRange(wx.HORIZONTAL)
        scroll_range_x = self.GetScrollRange(wx.VERTICAL)
        ratio = (scroll_pos_y + (scroll_size_y/2)) / scroll_range_x

        for page in self.pages:
            page.zoom(zoom_factor)
            
        self.gbs.Layout()
        self.SetupScrolling(scrollToTop=False)
        
        n_scroll_size_x = self.GetScrollPageSize(wx.HORIZONTAL)
        n_scroll_size_y = self.GetScrollPageSize(wx.VERTICAL)
        n_scroll_range_x = self.GetScrollRange(wx.HORIZONTAL)
        n_scroll_range_y = self.GetScrollRange(wx.VERTICAL)
        n_view_start_x = n_scroll_range_x * ratio - n_scroll_size_x/2
        n_view_start_y = n_scroll_range_y * ratio - n_scroll_size_y/2

        self.Scroll(int(n_view_start_x),int(n_view_start_y))
        self.drawn_pages.clear()
        self.is_onpage()

    # We have to use 1-indexed pages because wxPython objects can't have ID "0".
    # See the `for` loop in the __init__
    def rotate_page(self, page, zoom_factor=False):
        idx = page-1
        if zoom_factor:
            self.zoom_factor = zoom_factor
        else:
            zoom_factor = self.zoom_factor

        if self.pages[idx] is not self.pages[-1]:
            next = idx+1
            next_pos = self.gbs.GetItemPosition(self.pages[next])
        else:
            next = None
            next_pos = None
        if idx != 0:
            prev = idx-1
        else:
            prev = None

        pos = self.gbs.GetItemPosition(self.pages[idx])
        is_portrait = self.pages[idx].img.Width - self.pages[idx].img.Height < 0

        if self.layout == 1:
            if is_portrait:
                self.gbs.SetItemSpan(self.pages[idx], (1,2))
            else:
                self.gbs.SetItemSpan(self.pages[idx], (1,1))
        if self.layout == 2:
            if idx%2:
                prev_is_portrait = self.pages[prev].img.Width - self.pages[prev].img.Height < 0
                if prev_is_portrait:
                    if is_portrait:
                        self.gbs.SetItemPosition(self.pages[idx],(pos[0]+1,0))
                        self.gbs.SetItemSpan(self.pages[idx], (1,2))
                    else:
                        self.gbs.SetItemSpan(self.pages[idx], (1,1))
                        self.gbs.SetItemPosition(self.pages[idx],(pos[0]-1,1))
                else:
                    if is_portrait:
                        self.gbs.SetItemSpan(self.pages[idx], (1,2))
                        self.gbs.SetItemPosition(self.pages[idx],(pos[0],0))
                    else:
                        self.gbs.SetItemSpan(self.pages[idx], (1,1))
                        self.gbs.SetItemPosition(self.pages[idx],(pos[0],1))
            elif not next:
                pass
            else:
                next_is_portrait = self.pages[next].img.Width - self.pages[next].img.Height < 0
                if next_is_portrait:
                    if is_portrait:
                        self.gbs.SetItemPosition(self.pages[next],(next_pos[0]+1,1))
                        self.gbs.SetItemSpan(self.pages[idx], (1,2))
                    else:
                        self.gbs.SetItemSpan(self.pages[idx], (1,1))
                        self.gbs.SetItemPosition(self.pages[next],(next_pos[0]-1,1))
                else:
                    if is_portrait:
                        self.gbs.SetItemSpan(self.pages[idx], (1,2))
                    else:
                        self.gbs.SetItemSpan(self.pages[idx], (1,1))

        self.gbs.Layout()
        self.SetupScrolling(scrollToTop=False)
        self.Update()

    def update_pages(self, idx=None):
        if idx is None:
            for page in self.pages:
                page.OnSize()
        else:
            self.pages[idx].OnSize()
        
    def print_data(self):
        for item in self.pages:
            print(f'item.GetId(): {item.GetId()}')
        print(f'gbs size: {self.gbs.GetSize()}')
        print(f'gbs position: {self.gbs.GetPosition()}')
        print(f'doccy ClientSize: {self.GetClientSize()}')
        print(f'doccy Size: {self.GetSize()}')
        print(f'doccy ScreenRect: {self.GetScreenRect()}')
        print(f'doccy ClientRect: {self.GetClientRect()}')
        print(f'doccy TargetRect: {self.GetTargetRect()}')
        print(f'doccy ViewStart: {self.GetViewStart()}')
        print(f'doccy ScrollPageSize v: {self.GetScrollPageSize(wx.VERTICAL)}')
        print(f'doccy ScrollPageSize h: {self.GetScrollPageSize(wx.HORIZONTAL)}')
        print(f'doccy ScrollRange v: {self.GetScrollRange(wx.VERTICAL)}')
        print(f'doccy ScrollRange h: {self.GetScrollRange(wx.HORIZONTAL)}')
        print(f'doccy ScrollPixelsPerUnit: {self.GetScrollPixelsPerUnit()}')
        print(f'doccy Position: {self.GetPosition()}')
        print(f'doccy VirtualSize: {self.GetVirtualSize()}')
        print(f'#########################\n')

    def show_sizer(self):
        for i,item in enumerate(self.gbs.GetChildren()):
            print(f'###\nPAGE {i+1}')
            print(f'item.Position(): {item.GetPosition()}')
            print(f'item.Rect(): {item.GetRect()}')
            print(f'item.Position(): {item.GetPosition()}')
            print(f'item.Id(): {item.GetId()}')
            print(f'item.Proportion(): {item.GetProportion()}')

    def is_onpage(self):
        pixels_h,pixels_v = self.GetSize()
        for i,page in enumerate(self.pages):
            x,y,w,h = page.GetRect()
            if y < 0 and y+h > 0 and i not in self.drawn_pages:
                self.drawn_pages.add(i)
                page.draw()
            elif y >= 0 and y <= pixels_v and i not in self.drawn_pages:
                self.drawn_pages.add(i)
                page.draw()
            elif i in self.drawn_pages:
                self.drawn_pages.remove(i)

    # TODO
    def blit(self, zoom_factor=1, x=None, y=None):
        #What's here now was just copied and pasted from some other part, for reference
        view_start_x, view_start_y = self.GetViewStart()
        for i,dl in enumerate(self.doccy.dls):
            #pic = dl.get_pixmap(matrix=fitz.Matrix(zoom_factor,zoom_factor), clip=(10,10,100,100))
            pic = dl.get_pixmap(matrix=fitz.Matrix(zoom_factor,zoom_factor))
            static_bmps[i].SetBitmap(wx.Bitmap(wx.Image(pic.w,pic.h,pic.samples_mv)))

# Our document
class Doccy():
    def __init__(self, document, mat=6):
        self.doc = fitz.Document(document)
        self.mat = fitz.Matrix(mat,mat)
        self.dls = []
        
        for page in self.doc:
            self.dls.append(page.get_displaylist())

# Dynamic pages
class Page(wx.Window):
    def __init__(self, parent: Scrolly, id, dl: fitz.DisplayList):
        wx.Window.__init__(self, parent, id, style=wx.BORDER_DOUBLE)
        self.parent = parent
        self.dl = dl
        self.matrix = fitz.Matrix(1,1)
        self.pixmap = self.dl.get_pixmap(self.matrix)

        self.degrees = {0: 0.0, 1: 90.0, 2: 180.0, 3: 270.0}
        self.rotation = 0
        self.zoom_factor = 1

        self.img = wx.Image(self.pixmap.w,self.pixmap.h,self.pixmap.samples_mv)
        self.static = wx.StaticBitmap(self, id, wx.Bitmap(self.img))
        self.SetSize(self.img.GetSize())

        self.rot_btn_size = 35
        self.rot_l = wx.Button(self, -1, '↶', (0,0), (self.rot_btn_size,self.rot_btn_size), name='rot_l')
        self.rot_l.Hide()
        self.rot_r = wx.Button(self, -1, '↷', (0,0), (self.rot_btn_size,self.rot_btn_size), name='rot_r')
        self.rot_r.Hide()

        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_ENTER_WINDOW, self.showButtons)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.showButtons)

    def draw(self):
        self.matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        self.matrix.prerotate(self.degrees[self.rotation%4])
        self.pixmap = self.dl.get_pixmap(self.matrix)
        pic = wx.Image(self.pixmap.w, self.pixmap.h, self.pixmap.samples_mv)
        self.static.SetBitmap(wx.Bitmap(pic))
        self.OnSize()

    def zoom(self, zoom_factor):
        self.zoom_factor = zoom_factor
        x,y = self.img.GetSize()
        #pic = self.img.Size(self.img.GetSize()*zoom_factor, (0,0))
        pic = self.img.Scale(int(x * zoom_factor), int(y * zoom_factor), wx.IMAGE_QUALITY_NEAREST)
        self.static.SetBitmap(wx.Bitmap(pic))
        self.parent.drawn_pages.clear()
        self.parent.is_onpage()
        self.OnSize()

    def OnSize(self):
        size = self.static.GetSize()
        self.rot_l.SetPosition((0,size[1]-self.rot_btn_size))
        self.rot_r.SetPosition((size[0]-self.rot_btn_size,size[1]-self.rot_btn_size))
        self.Update()

    def showButtons(self, event):
        if event.GetEventType() == wx.wxEVT_ENTER_WINDOW:
            self.rot_l.Show()
            self.rot_r.Show()
        elif event.GetEventType() == wx.wxEVT_LEAVE_WINDOW:
            pos = event.GetPosition()
            rect_l = self.rot_l.GetRect()
            rect_r = self.rot_r.GetRect()
            good = True
            if rect_r.Contains(pos):
                good = False
            if rect_l.Contains(pos):
                good = False
            if good:
                self.rot_l.Hide()
                self.rot_r.Hide()
                self.parent.SetFocus()

    def OnButton(self, event):
        if event.GetEventObject().Name == 'rot_r':
            self.rotate(clockwise=True)

        elif event.GetEventObject().Name == 'rot_l':
            self.rotate(clockwise=False)

    def rotate(self, clockwise=True):
        self.parent.rotate_page(self.GetId())
        if clockwise:
            self.rotation += 1
        else:
            self.rotation -= 1
        self.img = self.img.Rotate90(clockwise)
        self.static.SetBitmap(wx.Bitmap(self.img))
        self.zoom(self.zoom_factor)
        self.OnSize()









