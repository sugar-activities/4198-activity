import os
import sys
import pygame
from pygame.locals import *

from layout import *
from sugar.activity import activity

DATA = os.path.join(activity.get_activity_root(), "data")
IMAGES = os.path.join(DATA, 'image')
SOUNDS = os.path.join(DATA, 'sound')

debug_info = True

''' Utilities '''
def empty(): pass
def hex2dec(hex): return int(hex, 16);
def hex2rgb(hex):
    if hex[0:1] == '#': hex = hex[1:];
    return (hex2dec(hex[:2]), hex2dec(hex[2:4]), hex2dec(hex[4:6]))

def border2px_rgb(border):
    px = 1;
    b = '75b844';
    if border.find('px') > -1:
        if border.find('#') > 1:
            px = border[0:border.find('px')]
            b = border[border.find('#')+1:]
    return int(px), hex2rgb(b)

''' Class Display() handles the drawing/blittins things '''
class Display:
    Layout = Layout()
    Colors = Colors()

    menu_entries = []   # Array with MenuEntry Objects
    text_items = []
    tooltips = []

    window = ''     # pygame window
    screen = ''     # pygame screen

    # Create Surfaces for Layouts
    bg_layout = pygame.Surface((1200, 825), 16)

    bw, bc = border2px_rgb(Layout.MenuMain.border)
    bg_menu = pygame.Surface((Layout.MenuMain.width - (2*bw)+1, Layout.MenuMain.height - (2*bw)+1))

    bw, bc = border2px_rgb(Layout.Question.border)
    bg_question = pygame.Surface((Layout.Question.width - (2*bw)+1, Layout.Question.height - (2*bw)+1))

    bw, bc = border2px_rgb(Layout.Toolbar.border)
    bg_toolbar = pygame.Surface((Layout.Toolbar.width - (2*bw)+1, Layout.Toolbar.height - (2*bw)+1))

    def __init__(self, s):
        self.__SERVICES__ = s

        # Fire Up Display
        self.window = pygame.display.set_mode((1200, 825))
        pygame.display.set_caption('XO Image-Quiz')

        # Init Surface
        self.screen = pygame.display.get_surface()

    def set_cursor(self, name):
        if name == "pointer-big":
            a, b, c, d = pygame.cursors.load_xbm("images/cursor_big.xbm", "images/cursor_big_mask.xbm")
            pygame.mouse.set_cursor(a, b, c, d)

    ''' Create the Backgrounds -> self.bg_layout '''
    def create_bg(self):
        # Fill all Black
        self.bg_layout.fill(hex2rgb(self.Layout.background))
        self.bg_question.fill(hex2rgb(self.Layout.Question.background))
        self.bg_menu.fill(hex2rgb(self.Layout.MenuMain.background))
        self.bg_toolbar.fill(hex2rgb(self.Layout.Toolbar.background))

        # Create bg_Layout and Menu
        self.draw_layout()
        self.draw_menu("/")

        self.add_emblem(self.bg_question)

    def refresh(self):
        self.screen.fill(hex2rgb(self.Layout.background))

        self.display_surface(self.bg_layout)
        self.display_menu()
        self.display_question()
        self.display_toolbar()
        self.display_text_items()

        pygame.display.update()

    ''' Display = Blit Surface on Screen '''
    def display_surface(self, surface, pos=(0,0), to=None):
        if to == None: self.screen.blit(surface, pos)
        elif to == "toolbar":
            self.bg_toolbar.blit(surface, pos)
        elif to == "question":
            self.bg_question.blit(surface, pos)
#       self.snapshot = self.screen
#       pygame.display.update()

    def display_menu(self):
        bw, bc = border2px_rgb(Layout.MenuMain.border)
        self.display_surface(self.bg_menu, (self.Layout.MenuMain.x+bw, self.Layout.MenuMain.y+bw))

    def display_question(self):
        bw, bc = border2px_rgb(Layout.Question.border)
        self.display_surface(self.bg_question, (self.Layout.Question.x+bw, self.Layout.Question.y+bw))

    def display_toolbar(self):
        bw, bc = border2px_rgb(Layout.Toolbar.border)
        self.display_surface(self.bg_toolbar, (self.Layout.Toolbar.x+bw, self.Layout.Toolbar.y+bw))

    def display_text_items(self):
        for i in self.text_items:
            if i != None:
                self.display_surface(i.image, i.pos)

    def display_tooltip(self, text, pos, format=None):
        self.add_text(self.bg_toolbar, text, pos, format)
        self.display_toolbar()

    def display_notfound_line(self, percent):
        pass

    ''' Adds Text / Images / ... to Surfaces '''
    def add_emblem(self, surface):
        # Adding the emblem to any surface
        self.add_image(surface, 'images/logo.jpg', (30, 100))
        textformat = TextFormat(None, 46)
        self.add_text(surface, 'XO Quiz', (30, 20), textformat)

    def add_image(self, surface, imgfn, pos):
        im, im_rect = self.image_load(imgfn)
        surface.blit(im, pos)

    def add_text(self, surface, text, pos, format=None):
        if format == None: format = TextFormat()

        font = pygame.font.Font(None, format.size)
        text = font.render(text, 1, hex2rgb(format.color))
        textpos = text.get_rect()
        x,y,w,h = list(textpos)

        # clear text behind
        bg = pygame.Surface((w,h))
        bg.fill(hex2rgb(self.Layout.Toolbar.background))

        surface.blit(bg, pos)
        surface.blit(text, pos)

    '''
     Drawing Backgrounds
    '''
    def draw_layout(self):
        q = self.Layout.Question;
        m1 = self.Layout.MenuTop;
        m2 = self.Layout.MenuMain;
        t = self.Layout.Toolbar;

        # Clear
        self.bg_layout.fill(hex2rgb(self.Layout.background))

        # Question Part
        bw, bc = border2px_rgb(q.border)
        pygame.draw.rect(self.bg_layout, bc, (q.x, q.y, q.width, q.height), bw)

        # Menu Caption and Menu Field
        bw, bc = border2px_rgb(m1.border)
        pygame.draw.rect(self.bg_layout, bc, (m1.x, m1.y, m1.width, m1.height), bw)

        bw, bc = border2px_rgb(m2.border)
        pygame.draw.rect(self.bg_layout, bc, (m2.x, m2.y, m2.width, m2.height), bw)

        # Toolbar
        bw, bc = border2px_rgb(t.border)
        pygame.draw.rect(self.bg_layout, bc, (t.x, t.y, t.width, t.height), bw)

        # Menu Text
        font = pygame.font.Font(None, m1.Text.size)
        text = font.render(m1.Text.text, 1, hex2rgb(m1.Text.color))
        textpos = text.get_rect()
        self.bg_layout.blit(text, (m1.x + m1.Text.x, m1.y + m1.Text.y))

    def draw_menu(self, menu_path):
        self.bg_menu.fill(hex2rgb(self.Layout.MenuMain.background))

        x = self.Layout.MenuMain.Button.x
        y = self.Layout.MenuMain.Button.y

        for m in self.menu_entries:
            if m.path == menu_path:
                m.pos = (x,y)
                self.bg_menu.blit(m.box.image, (x,y))
                y += 50;

    ''' Display A Question '''
    def clear_question_frame(self, emblem=True):
        self.bg_question.fill(hex2rgb(self.Layout.Question.background))
        if emblem: self.add_emblem(self.bg_question)

        self.display_question()
        pygame.display.update()

    def question_display(self, q):
        ''' class q (CurrentQuestion):
            id = 0
            imgfn = u''
            map = u''
            cat = 0
            subcat = 0
            text = u''
            answer = u''
            answer_link = ''
        '''
        self.bg_question.fill(hex2rgb(self.Layout.Question.background))

        # Load Image & Render on Background
        im, im_rect = self.image_load(os.path.join(IMAGES, q.imgfn))
        self.bg_question.blit(im, (self.Layout.Question.Image.x, self.Layout.Question.Image.y))

        # Render Question Text on Screen
        font = pygame.font.Font(None, self.Layout.Question.Text.size)
        text = font.render(q.text, 1, hex2rgb(self.Layout.Question.Text.color))
        textpos = text.get_rect()

        self.bg_question.blit(text, (self.Layout.Question.Text.x, self.Layout.Question.Text.y))

        self.refresh()
        return q.map

    def image_load(self, name):
        fullname = name
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print "Cannot load image:", name, 'fullname', fullname
            raise SystemExit, message
        image = image.convert()
        return image, image.get_rect()

    ''' Toolbar Tools '''
    def display_line(self, percent, found=True):
        print "draw line"

        if found: f = Layout.Toolbar.FoundLine
        else: f = Layout.Toolbar.NotFoundLine

        # Very Background Surface
        bbg = pygame.Surface((f.width + f.image_width, f.height))
        self.add_image(bbg, f.image, (f.image_left,0))

        # Draw Outside Rect
        bg = pygame.Surface((f.width, f.height))
        bg.fill(hex2rgb(f.Outside.background))

        bw, bc = border2px_rgb(f.Outside.border)
        if bw > 0: pygame.draw.rect(bg, bc, (0,0, f.width, f.height), bw)

        # Draw Inside Rect - Accorting to %
        new_height = f.height - (2*f.padding)
        max_width = f.width - (2*f.padding)
        new_width = max_width * percent / 100

        bg2 = pygame.Surface((new_width, new_height))
        bg2.fill(hex2rgb(f.Inside.background))

        bw, bc = border2px_rgb(f.Inside.border)
        if bw > 0: pygame.draw.rect(bg2, bc, (0,0,new_width, new_height), bw)

        bg.blit(bg2, (f.padding, f.padding))
        bbg.blit(bg, (f.image_width,0))

        self.bg_toolbar.blit(bbg, (f.x, f.y))
#       self.display_surface(bbg, (Layout.Toolbar.x + f.x, Layout.Toolbar.y + f.y))
        self.refresh()

'''
Overall Game Frontend
  - Needs no services yet
'''
class Kernel:
    Layout = Layout()
    Colors = Colors()

    lang = "English"

    map_list = ((0,0))  # Current Questions Map as List
    image_file_name = u""   # Current Questions Filename

    menu_current = '/'  # Current Directory
    menu_entries = []   # Array with MenuEntry Objects
    menu_raw = []       # [path, caption, onclick, part, is_Directory]

    menu_dirs = []      # Array with menu directories (['/', '/quit', ...])

    question_frame_reacts = []  # Reacts Array [x, y, width, height, onclick, stopsearch]
    text_items = []         # Array containing text item-objects on the question_frame
    hooks = []          # Array [event, function]

    def __init__(self):
        pygame.init()

        if not pygame.font: print 'Warning, fonts disabled'
        if not pygame.mixer: print 'Warning, sound disabled'

    def load(self, s):
        # Setup Menu
        global __SERVICES__
        __SERVICES__ = s

        self.D = Display(s)

        self.menu_setup()

        self.D.set_cursor("pointer-big")
        self.D.create_bg()
        self.D.refresh()

#       self.display_tooltip("Language: %s" % self.lang, (10, 10))
        if debug_info: print "- frontend loaded"

    def start_event_hooks(self, event, params):
        print "- checking event hooks"
        for h in self.hooks:
            # h[0] contains event, h[1] pointer to function
            print "-", event, h[0]
            if event == h[0]:
                try:
                    h[1](params)
                    print "- hook function started"
                except: print "! couldn't start hook", h

    def check_click(self, pos, key = None):
        # Click happened!
        # Could mean: In game, on menu, ...

        x, y = pos
        print 'click', pos

        ''' Start Plugin onclick Events '''
        self.start_event_hooks('onclick', pos);

        ''' Check In Reacts '''
        i = 0
        for m in self.question_frame_reacts:
            if m != None:
                bw, bc = border2px_rgb(self.Layout.Question.border)
                if x >= m[0] and x <= m[0] + m[2] and y >= m[1] and y <= m[1] + m[3]:
                    m[4]()
                    if m[5]: return True
                else:
                    print "* React #", i, ": not found"
            i += 1

        ''' Check in Text-Items '''
        for qi in self.text_items:
            if qi != None:
                if qi.pos_inside((x,y)):
                    if qi.onclick != None:
                        if qi.retvar != None:
                            qi.onclick(qi.retvar)
                            return True
                        else:
                            qi.onclick()

        ''' Check in Polygon '''
        if self.map_list != ((0, 0)):
            if self.point_inside_polygon(x, y, self.map_list):
                __SERVICES__.start_service('spot_found', pos)
                print "Click inside Polygon!"
                return True
            else:
                # If click inside game window, trigger not_found
                q = self.Layout.Question
                if x > q.x and x < (q.x + q.width) and y > q.y and y < (q.y + q.height):
                    __SERVICES__.start_service('spot_not_found', pos)

        ''' Check ON Menu '''
        if (x >= self.Layout.MenuTop.x and x <= self.Layout.MenuTop.x + self.Layout.MenuTop.width) and (y >= self.Layout.MenuTop.y and y <= self.Layout.MenuTop.y + self.Layout.MenuTop.height):
            self.change_dir('/')
            return True

        ''' Check In Menu '''
        x, y = pos
        x -= self.Layout.MenuMain.x
        y -= self.Layout.MenuMain.y
        checkpath = self.menu_current
        for m in self.menu_entries:
            if m.path == checkpath:
                print "- Click on Menu",m.caption,":", m.pos_inside((x,y))
                if m.pos_inside((x,y)):
                    if m.isDirectory == None:
                        # Check for Back Button
                        if m.onclick == None:
                            path = m.path.strip()
                            if len(path) > 1 and path[-1] == '/': path = path[0:-1]
                            path_base = path[:path.rfind('/')]
                            if len(path_base) == 0: path_base = '/'
                            self.change_dir(path_base)
                            return True
                        else:
                            # Action Button
                            self.mycaption = m.caption
                            m.onclick()
                            return True
                    else:
                        # Directory Button
                        self.change_dir(m.isDirectory)
                        return True

    def map_str_to_list(self, map_str):
        # convert 11, 12, 21, 22, 31, 33 in list [(11, 12), (21, 22), (31, 32)]
        print 'map_str', map_str
        map_arr = map_str.split(", ")
        o = []
        a = "x"
        for s in map_arr:
            if a == "x": a = s
            else:
                # Take care of border pixels
                bw, bc = border2px_rgb(self.Layout.Question.border)
                o.append((int(a)+self.Layout.Question.x+self.Layout.Question.Image.x+(bw+1), int(s)+self.Layout.Question.y+self.Layout.Question.Image.y+bw))
                a = "x"

        return o

    def question_set(self, question, image, map):
        self.question = question
        self.image = image
        self.map_list = self.map_str_to_list(map)

    '''
     Menu Functions
     ==============
    '''
    def menu_setup(self):
        # Put Menu items in correct order from self.menu_raw into self.menu_entries
        ms01 = []
        ms23 = []
        ms45 = []

        self.menu_entries = []

        for n in self.menu_raw:
            if n[3] == 0: ms01.insert(0, n)
            elif n[3] == 1: ms01.append(n)
            elif n[3] == 2: ms23.insert(0, n)
            elif n[3] == 3: ms23.append(n)
            elif n[3] == 4: ms45.insert(0, n)
            elif n[3] == 5: ms45.append(n)

        for n in ms01:
            m = MenuEntry(n[0], n[1], n[2], n[3], n[4], n[5])
            self.menu_entries.append(m)

        for n in ms23:
            m = MenuEntry(n[0], n[1], n[2], n[3], n[4], n[5])
            self.menu_entries.append(m)

        for n in ms45:
            m = MenuEntry(n[0], n[1], n[2], n[3], n[4], n[5])
            self.menu_entries.append(m)

        self.D.menu_entries = self.menu_entries

    def change_dir(self, menu_dir):
        print "change dir to", menu_dir
        self.menu_current = menu_dir;
        self.clear_text_items()
        self.refresh()

        self.D.draw_menu(menu_dir)
        self.D.display_menu()

    def add_menu_item(self, path, caption, onclick, part = 3):
        self.menu_raw.append([path, caption, onclick, part, None, len(self.menu_raw)]);
        return len(self.menu_raw)-1

    def change_menu_item(self, change_type, menu_item_id, change_text):
        print change_type, menu_item_id, change_text

        if change_type == "change_caption":
            i = 0
            for n in self.menu_entries:
                if n.id == menu_item_id:
                    self.menu_entries[i] = MenuEntry(n.path, change_text, n.onclick, n.part, n.isDirectory, n.id)
                    self.D.menu_entries = self.menu_entries
                    self.D.draw_menu(self.menu_current)
                    self.D.refresh()
                    return True
                i += 1

    def add_menu_dir(self, path, caption, part = 4):
        path = path.strip()
        if len(path) > 1 and path[-1] == '/': path = path[0:-1]

        # Avoid Duplicates:
        if self.menu_dirs.count(path) == 0:
            path_base = path[:path.rfind('/')]
            if len(path_base) == 0: path_base = '/'

            self.menu_raw.append([path_base, caption, None, part, path, len(self.menu_raw)]);
            self.menu_dirs.append(path)

            self.add_menu_item(path, "Back", None, 5)

        return True

    '''
     Services
     ========
    '''
    def refresh(self):                  self.D.refresh()
    def display_tooltip(self, text, pos, format=None):  self.D.display_tooltip(text, pos, format)
    def display_line(self, percent, found):         self.D.display_line(percent, found)
    def question_display(self, q):              self.map_list = self.map_str_to_list(self.D.question_display(q))
    def display_surface(self, s, pos, to=None):         self.D.display_surface(s, pos, to)
    def clear_question_frame(self, emblem=False):       self.D.clear_question_frame(emblem)
    def get_screen(self): return self.D.screen

    #service added for library
    def current_caption(self):
        return self.mycaption

    def add_event_hook(self, event, function):
        self.hooks.append([event, function])
        return len(self.hooks) - 1

    def del_event_hook(self, id):
        self.hooks[id:id+1] = [None, None]

    def list_event_hooks(self, event = None):
        if event == None:
            print self.hooks
            return True

        for h in self.hooks:
            if h[0] == event: print h

    def add_text_item(self, text, pos, onclick=None, retvar=None, border=False, format=None):
        # adds an clickable text-item to the question frame
        if format == None: format=TextFormat()
        qi = TextItem(text, pos, onclick, retvar, border, format)
        item_count = len(self.text_items)
        self.text_items.append(qi)
        self.D.text_items = self.text_items
        self.D.display_text_items()

#       print self.text_items
        return item_count

    def del_text_item(self, item_id):
#       print self.text_items
        self.text_items[item_id] = None
        self.D.text_items = self.text_items
        self.refresh()
#       print self.text_items

    def clear_text_items(self, refresh=True):
#       print "clearing"
#       print self.text_items
        self.text_items = []
        self.D.text_items = []
#       print self.text_items
        if refresh: self.refresh()

    def add_react(self, x, y, width, height, onclick, stopsearch = False, display = False):
        self.question_frame_reacts.append([x, y, width, height, onclick, stopsearch])

        if display:
            pygame.draw.rect(self.screen, hex2rgb(self.Colors.blue), (x, y, width, height), 3)
            pygame.display.update()

        return len(self.question_frame_reacts)-1

    def del_react(self, id):
        self.question_frame_reacts[id:id+1] = [None, None]
        return True

    ''' Polygon Drawing '''
    def draw_polygon(self):
        # Draw The Polygon on Screen
        pygame.draw.polygon(self.D.screen, hex2rgb(self.Layout.Polygon.color), self.map_list)

    def draw_lines(self):
        last_pos = ()
        for i in self.map_list:
            if len(last_pos) > 0:
                pygame.draw.line(self.D.screen, hex2rgb(self.Layout.Polygon.color), last_pos, i, 5)
            last_pos = i

    '''
     Text Input Tools
    '''
    def display_box(self, message):
        x = self.Layout.TextInput;

        area = Rect(x.Box.x, x.Box.y, x.Box.width, x.Box.height)

        bw, bc = border2px_rgb(x.Box.border)

        pygame.draw.rect(self.D.screen, hex2rgb(x.Box.background), area, 0)
        pygame.draw.rect(self.D.screen, bc, area, bw)

        oldclip = self.D.screen.get_clip()
        self.D.screen.set_clip(area.inflate(-4, -4))

        if len(message):
            text = pygame.font.Font(None, x.Text.size)
            text = text.render(message, 1, hex2rgb(x.Text.color))
            self.D.screen.blit(text, area.move(5, 7))

            self.D.screen.set_clip(oldclip)
            pygame.display.update(area)

    def ask(self, question):
        "ask(screen, question) -> answer"
        current_string = ''
        self.display_box(question + ":")
        while 1:
            event = pygame.event.wait()

            if event.type == QUIT:
                sys.exit(0)

            if event.type == MOUSEBUTTONUP:
                self.check_click(event.pos)

            if event.type != KEYDOWN:
                continue

            if event.key == K_ESCAPE:
                current_string = ""
                break

            elif event.key == 271 or event.key == K_RETURN:
                break

            elif event.key == K_BACKSPACE:
                current_string = current_string[:-1]
                self.display_box(question + ": " + current_string)

            elif event.unicode:
                current_string += chr(event.key)  #should be += event.unicode, workaround for xo bug
                self.display_box(question + ": " + current_string)

#       self.refresh_question_display()
        return current_string

    '''
     Other Tools
     ===========
    '''
    def sound_load(self, name, path = 'sounds'):
        class NoneSound:
            def play(self): pass
        if not pygame.mixer:
            return NoneSound()
        fullname = os.path.join(path, name)
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error, message:
            print "Cannot load sound:", message, name
            sound = NoneSound()
        return sound

    def image_load(self, name, path=''):
        fullname = os.path.join(path, name)
#       fullname = name
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print "Cannot load image:", name, 'fullname', fullname
            #raise SystemExit, message
            return None
        image = image.convert()
        return image, image.get_rect()

    def point_inside_polygon(self, x,y,poly):
        n = len(poly)
        inside =False
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y
        return inside

'''
 Classes for the Menu Structure
 ==============================
'''
class MenuBox(pygame.sprite.Sprite):
    Layout = Layout();
    def __init__(self, caption, isDirectory):
        # Init Sprite
        pygame.sprite.Sprite.__init__(self)

        # Create Button Surface
        self.image = pygame.Surface((self.Layout.MenuMain.Button.width, self.Layout.MenuMain.Button.height))

        # Apply Styles
        if isDirectory:
            bgcolor = self.Layout.MenuMain.Button.Button_Directory.background
            border = self.Layout.MenuMain.Button.Button_Directory.border
            textsize = self.Layout.MenuMain.Button.Button_Directory.Text.size
            textcolor = self.Layout.MenuMain.Button.Button_Directory.Text.color
        else:
            bgcolor = self.Layout.MenuMain.Button.background
            border = self.Layout.MenuMain.Button.border
            textsize = self.Layout.MenuMain.Button.Text.size
            textcolor = self.Layout.MenuMain.Button.Text.color

        # Fill Menu BG
        self.image.fill(hex2rgb(bgcolor))

        # Draw Border of MenuBox
        bw, bc = border2px_rgb(border)
        pygame.draw.rect(self.image, bc, (0, 0, self.Layout.MenuMain.Button.width, self.Layout.MenuMain.Button.height), bw)

        # Render Text
        font = pygame.font.Font(None, textsize)
        text = font.render(caption, 1, hex2rgb(textcolor))

        # Blit on self.image
        self.image.blit(text, (self.Layout.MenuMain.Button.Text.x, self.Layout.MenuMain.Button.Text.y))
        self.rect = self.image.get_rect()

class MenuEntry:
    # Load Layout
    Layout = Layout()

    # 'pos' stores the current Position; draw_menu sets it
    pos = (0, 0)

    def __init__(self, path, caption, onclick, part, isDirectory, id):
        self.isDirectory = isDirectory;
        self.id = id
        self.caption = caption
        self.onclick = onclick
        self.path = path

        if onclick == None:
            self.box = MenuBox(caption, True)
        else:
            self.box = MenuBox(caption, isDirectory)
        self.part = part # part is display-order 0-5

    def pos_inside(self, pos):
        x, y = list(pos)
        self_w = self.Layout.MenuMain.Button.width
        self_h = self.Layout.MenuMain.Button.height
        self_x, self_y = list(self.pos)

        if (x >= self_x and x <= self_x + self_w) and (y >= self_y and y <= self_y + self_h):
            return True
        else:
            return False

class TextItem:
    # Represents a Text Field w/wo border in the Question Frame
    # * Catches Clicks on It

    Layout = Layout()
    pos = (0, 0)
    size = (0, 0)
    text = u''
    textformat = TextFormat()

    def __init__(self, text, pos, onclick, retvar, border, textformat=None):
        self.text = text
        self.pos = pos
        self.onclick = onclick
        self.border = border
        self.retvar = retvar

        if textformat != True and textformat != False and textformat != None:
            self.textformat = textformat

        self.draw()

        x,y,w,h = list(self.textpos)
        x,y = list(pos)
        self.area = ((x,y,w,h))

    def draw(self):
        font = pygame.font.Font(None, self.textformat.size)
        text = font.render(self.text, 1, hex2rgb(self.textformat.color))
        textpos = text.get_rect()
        self.textpos = textpos

        x,y,w,h = list(textpos)
        self.size = (w+16,h+8)

        self.image = pygame.Surface(self.size)
        if self.textformat.background != None:
            self.image.fill(hex2rgb(self.textformat.background))
        self.image.blit(text, (8,4))

        if self.border:
            pygame.draw.rect(self.image, (255, 255, 255), (x,y,w+16,h+8), 2)

    def pos_inside(self, pos):
        x, y = list(pos)
        self_x, self_y = list(self.pos)
        self_w, self_h = list(self.size)

        if (x >= self_x and x <= self_x + self_w) and (y >= self_y and y <= self_y + self_h):
            return True
        else:
            return False

class ToolTip:
    Layout = Layout()

    def __init__(self, pos, text):
        self.pos = pos
        self.display(text)

    def display(self, caption):
        font = pygame.font.Font(None, self.Layout.Toolbar.Text.size)
        text = font.render(caption, 1, hex2rgb(self.Layout.Toolbar.Text.color))
        textpos = text.get_rect()

        x,y,w,h = list(textpos)
        self.size = (w,h)

        self.image = pygame.Surface(self.size)
        self.image.blit(text, (0,0))
