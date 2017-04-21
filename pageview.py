import sys

class Pageview():
    def __init__(self, svcs):
        self.sf = svcs.frontend
        self.itemsperpage = 10

    def pageview(self, items, action, title):
        #list of items, each item is tuple (name, id) where name is displayed on the page and id is returned to the action
        self.items = items
        #procedure to be called for selected item with parameter 'id'
        self.action = action
        #page title
        self.title = title
        self.display_page(0)

    def display_page(self, direction):
        if direction == 0:
            self.line = 0
        elif direction < 0:
            self.line -= self.itemsperpage
            if self.line < 0:
                self.line = 0
        elif direction > 0:
            self.line += self.itemsperpage
            if self.line > len(self.items):
                self.line -= self.itemsperpage
        else:
            return -1
        self.sf.clear_text_items()
        y = 55
        self.sf.add_text_item(self.title, (280,y))
        if self.line + self.itemsperpage < len(self.items):
            lines = self.line + self.itemsperpage
            moreflag = True
        else:
            lines = len(self.items)
            moreflag = False
        if self.line >0:
            y += 50
            self.sf.add_text_item("<back>", (300,y), self.navigate_cb, -1)
        for item in self.items[self.line:lines]:
            y += 50
            self.sf.add_text_item(item[0], (300,y), self.action, item[1])
        if moreflag:
            y += 50
            self.sf.add_text_item("<more>", (300,y), self.navigate_cb, 1)

    def navigate_cb(self, direction):
        self.display_page(direction)
