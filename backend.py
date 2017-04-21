#!/usr/bin/python
# -*- coding: latin-1 -*-

import os
import sqlite3
import random
import sys
from sugar.activity import activity
from path import path
import subprocess

import traceback

random.seed()

global debug_info
debug_info = True

'''
Handles pysqlite Interaction: query("SELECT..."), commit("UPDATE...")
'''
class Question:
    imgfn = u''
    sndfn = u''
    map = u''
    cat = 0
    subcat = 0
    lang = 1    # 1 = English
    text = u''
    answer = u''
    answer_link = ''

class Database:

    db_filename = "main.db"
    cur = '';
    con = '';

    def __init__(self):
        pass

    def query(self, q):
        dataList = []
        try:
            self.cur.execute(q)
        except:
            # If DB connection get's lost on Activity-Startup, then Reset
            print 'query reset=', q
            self.con = sqlite3.connect(self.db_fn)
            self.cur = self.con.cursor()
            self.cur.execute("-- types unicode")
            try:
                self.cur.execute(q)
            except:
                print 'execute failed', q

        data = self.cur.fetchall()
        #if data:
            #print 'data', len(data)
        #else:
            #print 'data = None'
        if data: dataList = [list(row) for row in data]
        #print 'dbmgr return dataList', len(dataList)
        return dataList

    def commit(self, q):
        try:
            self.cur.execute(q)
        except:
            # If DB connection get's lost on Activity-Startup, then Reset
            print 'execute reset=', q
            self.con = sqlite3.connect(self.db_fn)
            self.cur = self.con.cursor()
            self.cur.execute("-- types unicode")
            self.cur.execute(q)

        try:
            self.con.commit()
        except:
            print 'failure on commit'

    def lastrowid(self):
        return self.cur.lastrowid

    def load(self, services):
        # Init DB
        db = os.path.join(activity.get_activity_root(), "data")
        fullname = os.path.join(db, self.db_filename)
        self.db_fn = fullname
        #for testing, remove db
        #subprocess.call("rm -rf " + fullname, shell=True)
        if os.path.isfile(fullname):
            self.con = sqlite3.connect(fullname)
            self.cur = self.con.cursor()
            self.cur.execute("-- types unicode")
        else:
            # Check for Database Setup
            self.con = sqlite3.connect(fullname)
            self.cur = self.con.cursor()
            self.cur.execute("-- types unicode")
            # Create image, sound folders
            self.imagepath = os.path.join(db,'image')
            subprocess.call("mkdir -p " + self.imagepath, shell=True)
            self.soundpath = os.path.join(db,'sound')
            subprocess.call("mkdir -p " + self.soundpath, shell=True)
            # Setup New Database
            self.cur.execute("CREATE TABLE 'categories' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'text' TEXT);")
            self.cur.execute("CREATE TABLE 'questions' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'prompt' TEXT, 'response' TEXT, 'image_fn' TEXT, 'sound_fn' TEXT, 'map' TEXT, 'answer_link' VARCHAR ( 1024 ));")
            self.cur.execute("CREATE TABLE 'leitner' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'question_id' INT, 'count_found' INT, 'count_notfound' INT, 'box' INT, 'time' INT, 'day' INT);")
            self.cur.execute("CREATE TABLE 'catlink' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'parent_id' INT, 'child_id' INT);")
            self.cur.execute("CREATE TABLE 'quizlink' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'quiz_id' INT, 'question_id' INT);")

            self.con.commit()

            print "* database created"

        if debug_info: print "- database loaded"
        return True

'''
Main Game Backend (Kernel)
'''

class Kernel:
    services = []
    def __init__(self):
                pass

    def load(self, s):
        pass

    def add_service(self, descriptor, function):
        print "* registering service:",descriptor,
        self.services.append([descriptor, function])
        print "... ok"

    def start_service(self, descriptor, params=False):
        for s in self.services:
            if s[0] == descriptor:
                print "* starting service:",s[0],"(",params,")"

                try:
                    print s[1](params)
                except:
                    try:
                        print s[1]()
                    except:
                        print "! starting service %s failed" % s[0]
                        traceback.print_exc()
    def hex2rgb(hex):
        if hex[0:1] == '#': hex = hex[1:];
        return (hex2dec(hex[:2]), hex2dec(hex[2:4]), hex2dec(hex[4:6]))

'''
 Class PluginManager:
 ====================
 Note: Python 2.6 does not support this. An explicit import is required for each plugin
 This class loads the plugins and hooks in the services
 (Loads all .py files from plugin_dir/ not starting with _)
    - plugin1.py will be loaded
    - _plugin1.py will not be loaded
 Usage:
    plugger = PluginManager()
    plugger.load_plugins()
    plugger.debug()
'''
def empty(): pass

class PluginManager:
    plugins = []
    plugin_dir = 'plugins'

    services = ''

    def __init__(self):
        pass

    def load(self, services):
        self.services = services
        if debug_info: print "- plugger loaded"

    def load_plugins(self,plugins):
        log = open('/tmp/logQuiz','w')
        '''
        filenames = os.listdir(self.plugin_dir)
        for fn in filenames:
            # All .py files not starting with _
            if fn[-3:] == '.py' and fn[:1] != '_':
                # Extract File without Extension
                plugin_fn = os.path.splitext(fn)[0]

                # Import
                try:
                    p = __import__('.'.join([self.plugin_dir, plugin_fn]))
                except:
                    print >> log, 'import failed', sys.exc_info()[:2]            

		self.plugins.append(p)

                if debug_info:
                    try:
                        print >> log, "- plugin import:", p.__PLUGIN_NAME__
                    except:
                        print >> log, "no plugin name for ", plugin_fn
        '''
        self.plugins = []
        for p in plugins:
            self.plugins.append(p)
            p.__SERVICES__ = self.services

            try: p.load()
            except: traceback.print_exc()
        log.close()

    def close_plugins(self):
        for p in self.plugins:
            try: p.close()
            except: traceback.print_exc()

    def debug(self):
        print "Activated Plugins:"
        for p in self.plugins:
            print "-", p.__PLUGIN_NAME__
