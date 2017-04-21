__PLUGIN_NAME__   = 'make'

'''
 List of Services:
 - ImageQuiz.py, Line 37: "Hook-In Services"
 - http://wiki.laptop.org/index.php?title=XO_ImageQuiz/Plugins#Overview
'''

import os, sys

import pygame
from pygame.locals import *

from sugar.activity import activity
from sugar.datastore import datastore

import pygst
#pygst.require("0.10")
import gst

from path import path
from pageview import Pageview
from question import Question

from layout import *
from frontend import hex2rgb

import subprocess

#set up paths to for adding images and sounds
DATAPATH = path(activity.get_activity_root()) / "data"
ACTIVITYPATH = path(activity.get_bundle_path())
ICONPATH = ACTIVITYPATH / 'images'
IMAGEPATH = DATAPATH / 'image'
SOUNDPATH = DATAPATH / 'sound'

clock = pygame.time.Clock()

def clickOnMake():
    global sf
    sf.display_line(0, True)
    sf.display_line(0, False)
    bg_icons = pygame.Surface((500, 32))
    bg_icons.fill(hex2rgb(Layout().Toolbar.background))
    sf.display_surface(bg_icons, (540, 10), "toolbar")
    sf.display_surface(bg_icons, (538, 50), "toolbar")
    sf.clear_text_items()
    # Select Quiz
    cat_id = -1
    print 'ask_category', cat_id
    ask_category(cat_id)

def ask_category(cat_id, offset_y = 0):
    global pv
    if cat_id == -1:
        #first we need to query for categories
        cats = __SERVICES__.db.query("SELECT id, text FROM categories;")
        nlines = 0
        print 'cats', len(cats), cats
        itemlist = []
        for cat in cats:
            print 'cat', cat[0], cat[1]
            cat_id = cat[0]
            category = cat[1]
            try:
                q = 'SELECT count(*) FROM quizlink WHERE quiz_id=%i' % cat_id
                res1 = __SERVICES__.db.query(q)
                count = res1[0][0]
            except:
                print 'query error', q
            print 'count', category, count
            if count > 0:
                print 'string', category, count
                itm = (category + '(' + str(count) + ')', cat_id)
                print 'itm', itm[0],[1]
                itemlist.append(itm)
        print 'call pv.pageview', len(itemlist), 'quiz'
        pv.pageview(itemlist, ask_quiz, 'quiz')

def ask_quiz(cat_id):
    print 'ask_quiz', cat_id
    #get list of questions (by question_id)
    q = "SELECT question_id FROM quizlink WHERE quiz_id = %i" % cat_id
    questionlist = __SERVICES__.db.query(q)
    #get actual questions
    questions = []
    for questionid in questionlist:
        q = 'SELECT * from questions WHERE id = %i' % questionid[0]
        res = __SERVICES__.db.query(q)
        question = Question()
        question.id = res[0][0]
        question.prompt = res[0][1]
        question.response = res[0][2]
        question.imgfn = res[0][3]
        question.sndfn = res[0][4]
        question.map = res[0][5]
        question.answer_link=res[0][6]
        questions.append(question)
    questionview(questions, cat_id)

def questionview(quiz, cat_id, navigation = None):
    #provide navigation: 0 = escape, 1 = next question, -1 = previous question, None = first call
    #if escape, redisplay current question
    #if None, display question 0
    #if previous question and current question is 0, ignore
    #if next question and current question is the last one, ignore
    global next
    global quizid
    global quizname
    quizid = cat_id
    if navigation == None:
        print 'questionview: first call'
        navigation = 0
        next = 0
    currentnext = next
    if navigation > 0 and next < len(quiz):
        next += 1
    elif navigation < 0and next > 0:
        next -= 1
    q = "SELECT text FROM categories WHERE id = %i" % cat_id
    rslt = __SERVICES__.db.query(q)
    quizname = rslt[0][0]
    print 'call display-question', navigation, next, quizname
    display_question(quiz, next)

def display_question(quiz, next):
    global quizname
    #display question
    #id = 0
    #prompt = u''
    #response = u''
    #imgfn = u''
    #sndfn = u''
    #map = u''

    global dquiz, dnext
    global prompt_id
    global response_id
    global work
    global q
    dquiz = quiz
    dnext = next
    print 'display_question', quizname, len(quiz), next
    if next < len(quiz):
        q = quiz[next]
    else:
        q = Question()
        q.id = -1 #don't add question to db before needed
        q.prompt = ''
        q.response = ''
        q.imgfn = ''
        q.sndfn = ''
        q.map = ''
        q.answer_link = ''
    print 'q is', q.id,':', q.prompt,':', q.response,':', q.imgfn,':', q.sndfn,':', q.map
    #we need a working copy of the question to support undo
    work = Question()
    work.prompt = q.prompt
    work.response = q.response
    work.id = q.id
    work.imgfn = q.imgfn
    work.sndfn = q.sndfn
    work.map = q.map
    display_page()

def display_page():
    #display page
    global quizname
    global work
    global img
    global prompt_id
    global response_id
    sf.clear_text_items()
    y = 55
    #first show quiz name
    print 'display quiz name', quizname
    sf.add_text_item(quizname, (20, 0))
    #show prompt and response at bottom of screen
    sf.add_text_item('prompt:', (20,700))
    print 'display prompt'

    if len(work.imgfn) > 0:
        print 'load', work.imgfn
        img, rect = sf.image_load(work.imgfn, path = IMAGEPATH)
        if len(work.map) > 0:
            print 'map', len(work.map)
            draw_map(img, work.map)
        sf.display_surface(img, (40,40))

    # new plan - when user clicks on 'editable' item, use ask to get value
    y += 50
    if len(work.prompt) > 0:
        t = work.prompt
    else:
        t = "________________________________________"
    prompt_id = sf.add_text_item(t, (150,700), edit_prompt, work)
    print 'display sndfn'
    if len(work.sndfn) > 0:
        t = work.sndfn
    else:
        t = 'audio'
    sf.add_text_item(t, (700, 650))
    clip = SOUNDPATH / work.sndfn
    #now show response
    y += 50
    sf.add_text_item('response:', (20,750))
    print 'display response'
    y += 50
    if len(work.response) > 0:
        t = work.response
    else:
        t = "________________________________________"
    response_id = sf.add_text_item(t, (150,750), edit_response, work)
    print 'display imgfn'
    if len(work.imgfn) > 0:
        t = work.imgfn
    else:
        t = 'image'
    sf.add_text_item(t, (100,650)) # as caption under image
    image = IMAGEPATH / work.imgfn
    show_buttons()

def show_buttons():
    sound_play, xy = sf.image_load("gtk-media-play-ltr.png", path = ICONPATH)
    sf.display_surface(sound_play, (500,650))
    sound_record, xy = sf.image_load("gtk-media-record.png", path = ICONPATH)
    sf.display_surface(sound_record, (550, 650))
    sound_browse, xy = sf.image_load("btnsearch.png", path = ICONPATH)
    sf.display_surface(sound_browse, (600,650))
    button_draw, xy = sf.image_load("pencil.png", path = ICONPATH)
    sf.display_surface(button_draw, (900,500))
    image_browse, xy = sf.image_load("btnsearch.png", path = ICONPATH)
    sf.display_surface(image_browse, (20,650))
    button_next, xy = sf.image_load("btnnext.png", path = ICONPATH)
    sf.display_surface(button_next, (900,600))
    button_back, xy = sf.image_load("btnprev.png", path = ICONPATH)
    sf.display_surface(button_back, (900,550))
    button_undo, xy = sf.image_load("stock_undo.png", path = ICONPATH)
    sf.display_surface(button_undo, (900,500))

def svg_image_load(src, pth = None):
    svgsrf = pygame.surface(64, 64)
    ctx = cairo.Context(svgsrf)
    fn = pth / src
    svgsrc = open(fn, 'r')
    svg = svgsrc.read()
    svgsrc.close()
    handle = rsvg.Handle(svg)
    handle.render(ctx)
    return ctx

def draw_map(img, map):
    color = (100,0,0)
    pen = 4
    pts = []
    coords = []
    maplst = map.split(',')
    for pt in maplst:
        try:
            coords.append(int(pt))
        except:
            pass
    i = 0
    while i < len(coords):
        pts.append((coords[i],coords[i+1]))
        i += 2
    print 'draw lines'
    pygame.draw.lines(img, color, True, pts, pen)

def drawmap():
    global work
    global drawing
    global img
    global map
    if drawing:
        drawing = False
        map.append(map[0])
        print 'drawmap:', len(map), map
        work.map = ""
        for pos in map:
            if len(work.map) > 0:
                work.map = work.map + ',' + str(pos[0] - 40) + ',' + str(pos[1] - 40)
            else:
                work.map = str(pos[0] - 40) + ',' + str(pos[1] - 40)
        print 'drawmap: new work.map', work.map
        display_page()
    else:
        #draw new map on image
        drawing = True
        work.map = ""
        print "drawmap: display_page"
        display_page()
        pygame.display.update()
        print "drawmap: draw map"
        map = []
        #user draws new map
        firsttime = True
        while drawing:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    startpos = pygame.mouse.get_pos()
                    print 'drawmap startpos:', startpos
                    if startpos[0] > 900:
                        print 'drawmap: done', len(map)
                        return
                    if firsttime:
                        map.append(startpos)
                        firsttime = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    endpos = pygame.mouse.get_pos()
                    print 'drawmap endpos:', endpos
                    startpos = map[len(map) - 1]
                    map.append(endpos)
                    pygame.draw.line(img, (100,0,0), startpos, endpos, 3)
                    sf.display_surface(img, (40,40))
                    pygame.display.update()

def play():
    global work
    sound = sf.sound_load(SOUNDPATH / work.sndfn)
    sound.play()
    while pygame.mixer.get_busy():
        clock.tick(30)

def record():
    global recording
    global pipe
    if recording:
        recording = False
        subprocess.call("killall -q arecord", shell=True)
        clipname = sf.ask("name?")
        work.sndfn = clipname + '.ogg'
        #convert to ogg file
        pth = SOUNDPATH / work.sndfn
        pipeline = pipe + pth
        subprocess.call("gst-launch-0.10 " + pipeline, shell=True)
        #reset mic boost
        subprocess.call("amixer cset numid=11 off", shell = True)
        display_page()
    else:
        recording = True
        #turn on mic boost (xo)
        print 'turn on mic boost'
        subprocess.call("amixer cset numid=11 on", shell=True)
        subprocess.Popen("arecord -d 20 -f cd /tmp/temp.wav", shell=True)

def clipbrowse():
    global clips
    #set up pageview to show audio clips in sound (and later the journal)
    #clips is a list of tuples: (src, fn)
    clips = []
    #get paths to sound clips in sound folder
    d = SOUNDPATH
    print 'clipbrowse: ', len(d.files()), len(d.files('*.ogg'))
    for f in d.files('*.ogg'):
        clips.append((f.name, f, 's'))
        print 'clipbrowse: ', f.name
    #get objects from the local datastore
    print 'clipbrowse: get objects from the local datastore'
    ds_objects, num_objects = datastore.find({'mime_type':['application/ogg', 'audio/ogg', 'audio/mp3']})
    print 'clipbrowse: ', num_objects
    for f in ds_objects:
        obj = datastore.get(f.object_id)
        pth = path(obj.get_file_path())
        if len(pth) > 0:
            clips.append((pth.name, obj, 'd'))
            print 'clipbrowse:', pth.name
        f.destroy()
    print 'clipbrowse: call pageview'
    pv.pageview(clips, setnewclip, "audio clips")

def setnewclip(clip_id):
    global work
    global dquiz, quizid
    print 'setnewclip', clip_id
    work.sndfn = path(clip_id).name
    if SOUNDPATH in clip_id:
        print 'clip from activity'
    else:
        print 'clip from datastore'
        #copy image to activity
        srcpath = clip_id
        dstpath = SOUNDPATH / work.sndfn
        path.copy(srcpath, dstpath)
    print 'setnewclip', work.sndfn
    display_page()

def imgbrowse():
    global imgs
    #set up pageview to show images in image
    #imgs is a list of tuples: (fn, src))
    imgs = []
    #get paths to images in image folder
    d = IMAGEPATH
    print 'imgbrowse: ', len(d.files()), len(d.files('*.png'))
    for f in d.files('*.png'):
        imgs.append((f.name, f, 's'))
    for f in d.files('*.jpg'):
        imgs.append((f.name, f, 's'))
    #get objects from the local datastore
    print 'imgbrowse: get objects from the local datastore'
    ds_objects, num_objects = datastore.find({'mime_type':['image/png', 'image/jpeg','image/svg']})
    print 'imgbrowse: ', num_objects
    for f in ds_objects:
        obj = datastore.get(f.object_id)
        pth = path(obj.get_file_path())
        print 'imgbrowse: ', obj.get_file_path()
        imgs.append((pth.name, obj, 'd'))
        f.destroy()
    print 'imgbrowse: call pageview'
    vw.pageview(imgs, setnewimg, "images")

def setnewimg(image_id):
    global work
    global dquiz, quizid
    #image_id is absolute path name
    work.imgfn = path(work.imgfn).name
    print 'setnewimg', image_id
    if IMAGEPATH in image_id:
        print 'image from activity'
    else:
        print 'image from datastore'
        #copy image to activity
        srcpath = image_id
        dstpath = IMAGEPATH / work.imgfn
        path.copy(srcpath, dstpath)
    print 'setnewimg', work.imgfn
    display_page()

def escape_cb():
    global dquiz, quizid
    global q, work
    print 'enter escape_cb'
    work.id = q.id
    work.prompt = q.prompt
    work.response = q.response
    work.imgfn = q.imgfn
    work.sndfn = q.sndfn
    work.map = q.map
    print 'escape_cb: call questionview'
    display_page()

def next_cb():
    global quizid
    global dquiz, work
    print 'next_cb', work.prompt, work.response
    update_db(work)
    print 'next_cb: advance to next question'
    questionview(dquiz, quizid, 1)

def back_cb():
    global quizid
    global dquiz, work
    update_db(work)
    questionview(dquiz, quizid, -1)

def update_db(work):
    #if work.id < 0, it is a new question to be added to the db and linked to the quiz
    print 'update_db:', work.id
    if work.id < 0:
        #add new question to db and link to quiz
        print 'update_db: enter add_question'
        add_question(work)
        work.imgfn = path(work.imgfn).name
    else:
        q = "UPDATE questions SET prompt = '%s' WHERE id = '%i'" % (work.prompt, work.id)
        print 'update_db', q
        __SERVICES__.db.commit(q)
        q =	"UPDATE	questions SET response = '%s' WHERE id = '%i'" %(work.response,  work.id)
        print 'update_db', q
        __SERVICES__.db.commit(q)
        q =	"UPDATE	questions SET image_fn = '%s' WHERE id = '%i'" %(work.imgfn, work.id)
        print 'update_db', q
        __SERVICES__.db.commit(q)
        q =	"UPDATE	questions SET sound_fn = '%s' WHERE id = '%i'" %(work.sndfn, work.id)
        print 'update_db', q
        __SERVICES__.db.commit(q)
        q =	"UPDATE	questions SET map = '%s' WHERE id = '%i'" %(work.map, work.id)
        print 'update_db', q
        __SERVICES__.db.commit(q)

def add_question(work):
        global dquiz, quizid, next
        # Insert Question
        q = u'INSERT INTO questions (prompt, response, image_fn, sound_fn, map, answer_link) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (work.prompt, work.response, work.imgfn, work.sndfn,  work.map, "")
        print 'add_question:', q
        __SERVICES__.db.commit(q)
        dquiz.append(work)
        print 'add_question: next, len(quiz):', next, len(dquiz)

        # Get Question_ID of last question inserted
        print 'add_question: get question_id'
        question_id = __SERVICES__.db.lastrowid()
        print 'add_question:', question_id
        work_id = question_id

        # Link question to quiz
        q = u"INSERT INTO quizlink (quiz_id, question_id) VALUES (%i, %i)" % (quizid, question_id)
        print 'add_question:', q
        try:
            __SERVICES__.db.commit(q)
        except:
            print 'insert into quizlink failed', os.exc_info()[0]
        finally:
            print 'insert into quizlink finally done'
        print 'leaving add_question'

def edit_prompt(work):
    global prompt_id
    print 'enter edit_prompt'
    t = sf.ask("")
    print 'new prompt', t
    work.prompt = t
    print 'del old text_item'
    sf.del_text_item(prompt_id)
    print 'add new one'
    prompt_id=sf.add_text_item(work.prompt, (150,700), edit_prompt, work)
    print 'show buttons ?'
    show_buttons()

def edit_response(work):
    global response_id
    print 'enter edit response'
    t = sf.ask("")
    print 'new response', t
    work.response = t
    print 'del old text_item'
    sf.del_text_item(response_id)
    print 'add new one'
    response_id = sf.add_text_item(work.response, (150, 750), edit_response, work)
    print 'show buttons?'
    show_buttons()

def clickOnDone():
    #user is done with edit
    #we need to clear the page and continue from the menu
    clear_reacts()

def clickOnNew():
    #user wants to create new quiz
    #add quiz to db
    #proceed to ask_question?
    #display page
    sf.clear_text_items()
    quizname = sf.ask('name?')
    id = add_cat(quizname)
    while id < 0:
        st = quizname + ' in use, try another'
        quizname = sf.ask(st)
        id = add_cat(quizname)
    quiz = []
    questionview(quiz, id)

def add_cat(quizname):
    # Category exists?
    q = u"SELECT count(*) FROM categories WHERE text='%s'" % (quizname)
    res = __SERVICES__.db.query(q)
    print 'add_cat:', res[0][0], q
    if res[0][0] > 0:
        # Yes, error
        return -1
    q = u"INSERT INTO categories (text) VALUES ('%s')" % (quizname)
    print 'add_cat:', q
    __SERVICES__.db.commit(q)
    q = u"SELECT id FROM categories WHERE text='%s'" % (quizname)
    res = __SERVICES__.db.query(q)
    id = res[0][0]
    print 'add_cat:', id, q
    return id

def set_reacts():
    global reacts
    reacts = []
    #undo
    reacts.append(sf.add_react(900, 500, 32, 32, escape_cb, stopsearch = True))
    #back
    reacts.append(sf.add_react(900, 550, 32, 32, back_cb, stopsearch = True))
    #next
    reacts.append(sf.add_react(900, 600, 32, 32, next_cb, stopsearch = True))
    #image browse
    reacts.append(sf.add_react(20, 650, 64, 32, imgbrowse, stopsearch = True))
    #draw
    reacts.append(sf.add_react(900, 500, 187, 187, drawmap, stopsearch = True))
    #audio browse
    reacts.append(sf.add_react(600, 650, 64, 32, clipbrowse, stopsearch = True))
    #play
    reacts.append(sf.add_react(500, 650, 32, 32, play, stopsearch = True))
    #record
    reacts.append(sf.add_react(550, 650, 32, 32, record, stopsearch = True))

def clear_reacts():
    global reacts
    for react in reacts:
        sf.del_react(react)

def load():
    global sf
    sf = __SERVICES__.frontend
    global pv
    global recording
    global drawing
    global pipe
    svcs = __SERVICES__
    pv = Pageview(svcs)
    recording = False
    drawing = False
    # Menu
    sf.add_menu_dir('/make', 'Make')
    sf.add_menu_item('/make', 'New Quiz', clickOnNew, 0)
    sf.add_menu_item('/make', 'Select Quiz', clickOnMake, 1)
    sf.add_menu_item('/make', 'Done', clickOnDone, 2)

    #initialize convert pipeline
    p = "filesrc location=/tmp/temp.wav ! wavparse "
    p = p + "! audioconvert ! vorbisenc ! oggmux "
    p = p + "! filesink location="
    pipe = p

    set_reacts()

def close():
    print 'make closed'

    clear_reacts()
