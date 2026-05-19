# -*- coding: utf-8 -*-

import sys

try:
    import gtk.glade
except:
    print 'not installed GTK+ bindings: Glade support'
    print 'ex) sudo apt-get install python-glade2'
    print 'ex) sudo yum install pygtk2-libglade'
    sys.exit(2)


class Position(object):
    def __init__(self, idx):
        if idx == 0:
            self.idx = idx
            self.Caps = 'L'
        elif idx == 1:
            self.idx = idx
            self.Caps = 'R'


class Glade(gtk.glade.XML):
    def addPos(self, wName):
        retNode = self.get_widget(wName)
        if (wName.endswith('L')):
            pos = Position(0)
        elif (wName.endswith('R')):
            pos = Position(1)
        else:
            return retNode
        setattr(retNode, 'posit', pos)
        return retNode
