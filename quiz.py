#! /usr/bin/env python
# -*- coding: latin-1 -*-

import os
import sys
import sqlite3
import time

import pygame
from pygame.locals import *

import olpcgames

from layout import *

import backend
import frontend

#import plugins (no longer possible to import by filename)
from plugins import demoplugin
from plugins import single_player
from plugins import multi_player
from plugins import make
from plugins import tools
from plugins import utility
plugins = [demoplugin,single_player,multi_player,make,tools,utility]
''' Definitions '''
show_infos_pygame_events = False

'''This class provides functions to the Plugins'''
class Services:
    class locale:
        lang_id = 1
        lang_name = "English"
    class db:
        query = ''
        commit = ''
    class brain:
        question_pick = ''
    class frontend:
        add_menu_item = ''
        change_dir = ''
    class plugins:
        services = []

services = Services()

''' INIT Part '''
# Init All Modules
db = backend.Database()
brain = backend.Kernel()
plugger = backend.PluginManager()
display = frontend.Kernel()

''' Hook-In Services for the Plugins '''
services.Layout = Layout()
services.Question = backend.Question

services.add_service = brain.add_service
services.start_service = brain.start_service
services.hex2rgb = brain.hex2rgb

services.db.query = db.query
services.db.commit = db.commit
services.db.lastrowid = db.lastrowid

services.frontend.add_menu_dir = display.add_menu_dir
services.frontend.add_menu_item = display.add_menu_item
services.frontend.change_menu_item = display.change_menu_item
services.frontend.change_dir = display.change_dir

services.frontend.image_load = display.image_load
services.frontend.sound_load = display.sound_load
services.frontend.point_inside_polygon = display.point_inside_polygon

services.frontend.draw_polygon = display.draw_polygon
services.frontend.draw_lines = display.draw_lines

services.frontend.display_line = display.display_line

#services.frontend.show_image = display.show_image
#services.frontend.show_surface = display.show_surface

services.frontend.question_display = display.question_display
services.frontend.clear_question_frame = display.clear_question_frame

services.frontend.add_react = display.add_react
services.frontend.del_react = display.del_react

services.frontend.current_caption = display.current_caption
services.frontend.add_event_hook = display.add_event_hook
services.frontend.del_event_hook = display.del_event_hook
services.frontend.list_event_hooks = display.list_event_hooks

services.frontend.refresh = display.refresh
services.frontend.display_surface = display.display_surface
services.frontend.get_screen = display.get_screen

services.frontend.ask = display.ask
services.frontend.display_tooltip = display.display_tooltip

services.frontend.add_text_item = display.add_text_item
services.frontend.del_text_item = display.del_text_item
services.frontend.clear_text_items = display.clear_text_items

''' Load all Modules '''
db.load (services)
brain.load (services)

plugger.load (services)
plugger.load_plugins(plugins)

display.load (services)

''' Game Control Start '''
print 'game control start'

class QuizActivity:
    user_name = u"chris"

    def game(self):
        clock = pygame.time.Clock()
        screen = display.get_screen()

        # Pygame event loop.
        while True:
            clock.tick(20)
            pygame.display.update()

            for event in [ pygame.event.wait() ] + pygame.event.get( ):
                self.input(event)

    # Handle a pygame event
    def exit_all(self):
        plugger.close_plugins()
#       time.sleep(3)
        sys.exit(0)

    def input(self, event):
        if show_infos_pygame_events: print event
        if event.type == QUIT:
            self.exit_all()

        elif event.type == MOUSEBUTTONUP:
            display.check_click(event.pos)

        elif event.type == KEYUP:
            if event.key == 113:    # 'q'
                self.exit_all()
            elif event.key == 102:  # 'f'
                pygame.display.toggle_fullscreen()

#       elif event.type == MOUSEMOTION:
#           pass

#           else:
#               x = event.type
#               display.show_tool_tip((200, 10), "%i" % int(x))
#               pygame.display.update()

    def __init__(self):
            self.game()

def main():
    Quiz = QuizActivity()

if __name__ == "__main__" or __name__ == "Quiz":
    main()
