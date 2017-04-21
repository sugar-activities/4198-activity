# Currently * Displaying Categories in set language, * Pick English Questions
# To Do
# change to update Leitner info
# display questions based on box

# structure
# class CurrentQuestion
# class Answer
# class Questions

# functions

#     show_answer
#     finished
#     startgame
#     ask_subcat
#     ask_category
#     display_points
#     click_on_
#     next_question
#     next_question
#     spot_found
#     spot_not_found
#     load

import pygame
from pygame import *
from sugar.activity import activity
import os, sys

import random
from layout import *
from frontend import hex2rgb
import time
import threading
from pageview import Pageview

__PLUGIN_NAME__   = 'player'

#set up paths to for adding images and sounds
DATAPATH = os.path.join(activity.get_activity_root(), "data")
ACTIVITYPATH = activity.get_bundle_path()
IMAGEPATH = os.path.join(DATAPATH, 'image')
SOUNDPATH = os.path.join(DATAPATH, 'sound')
ICONPATH = os.path.join(ACTIVITYPATH, 'images')
CORRECT_SOUNDS = ['i-like-it.wav', 'ooh-yeah.wav', 'impressive.wav',
                  'dramatic_chord.wav', 'sweet.wav',
                  'brain-yes.wav', 'mk-excellent.wav', 'that-was-cool.wav',
                  'bt-excellent.wav', 'groovy.wav',
                  'yes-i-like-it.wav', 'burns-excellent.wav', 'oh-yeah.wav']
WRONG_SOUNDS  = ['db_forgetaboutit.wav', 'alf_wrong.wav', 'doh.wav', 'sorry.wav',
                 'awh_man.wav', 'metal_clang_2.wav',
                 'excuse_me.wav', 'negative.wav', 'bunny_awful.wav', 'gwarsh.wav',
                 'not.wav', 'haha.wav', 'oh_no.wav', 'compute.wav', 'hoo-ah.wav']

clock = pygame.time.Clock()

class CurrentQuestion:
    id = 0
    prompt = u''
    response = u''
    imgfn = u''
    sndfn = u''
    map = u''
    answer_link = u''

class Imagequiz_question:
    id = 0
    map = u''
    cat = 0
    subcat = 0
    text = u''
    answer = u''
    answer_link = u''

class Answer:
    display = True
    display_line = True
    sound_enabled = True

    link = u''
    text = u''

    img_found_count = 0
    img_notfound_count = 0
    imgfn_found = ["Emotes/face-grin.png"]
    imgfn_notfound = ["Emotes/face-devil-grin.png"]

    found_straight = 0
    straight_count = 0
    icon_left = 0
    bg_icons = pygame.Surface((500, 32))
    bg_icons_straight = pygame.Surface((500, 32))

    def __init__(self):
        self.sound_found = sf.sound_load("accessed.wav")
        self.sound_notfound = sf.sound_load("sorry.wav")

    def reset_points(self):
        self.found_straight = 0
        self.straight_count = 0
        self.icon_left = 0

        self.bg_icons.fill(hex2rgb(Layout().Toolbar.background))
        self.bg_icons_straight.fill(hex2rgb(Layout().Toolbar.background))

        sf.display_surface(self.bg_icons, (540, 10), "toolbar")
        sf.display_surface(self.bg_icons_straight, (538, 50), "toolbar")
        sf.refresh()

    def add_straight(self):
        # 5 in a row -> special reward
        self.straight_count += 1
        im, im_rect = sf.image_load("images/%s" % "Icons/bulb.png")
        self.bg_icons_straight.blit(im, ((self.straight_count-1) * (im_rect[2] + 4), 0))
        sf.display_surface(self.bg_icons_straight, (538, 50), "toolbar")
        sf.refresh()

    def display_icon(self, icon_name):
        if icon_name == "found":
            self.found_straight += 1
            if self.found_straight == 5:
                # Found Straight 5!
                self.bg_icons.fill(hex2rgb(Layout().Toolbar.background))
                sf.display_surface(self.bg_icons, (540, 10), "toolbar")
                self.add_straight()
                self.icon_left = 0
                self.found_straight = 1

            fn = self.imgfn_found[self.img_found_count %  len(self.imgfn_found)]
            self.img_found_count += 1

        elif icon_name == "not-found":
            self.found_straight = 0
            fn = self.imgfn_notfound[self.img_notfound_count % len(self.imgfn_notfound)]
            self.img_notfound_count  += 1

        img, img_rect = sf.image_load("images/%s" % fn)
        self.bg_icons.blit(img, (self.icon_left, 0))

        sf.display_surface(self.bg_icons, (540, 10), "toolbar")
        sf.refresh()

        self.icon_left += img_rect[2] + 4

    class PlaySoundThread (threading.Thread):
        def set(self, sound, interval):
            self.sound = sound
            self.i = interval

        def run(self):
            time.sleep(self.i)
            self.sound.play()

    def play_sound(self, i):
        if self.sound_enabled:
            t = self.PlaySoundThread()
            if i == 1: t.set(self.sound_found, 0)
            else: t.set(self.sound_notfound, 0.5)
            t.start()

    def display_answer(self):
        if self.display_line: sf.draw_lines()
        if self.display == False: return False

        # Get Top Right Spot of list
        map_arr = Q.question.map.split(", ")

        # Widths & Heights
        bubble_width = 400
        bubble_height = 300
        textfield_width = 270
        textfield_height = 200

        # Extremas of the Polygone will be saved in here:
        x_max = 0
        y_max = 0
        x_min = 1000
        y_min = 1000

        # Extract Extremas from the polygon
        o = []
        a = "x"
        for s in map_arr:
            if a == "x": a = s
            else:
                # Take care of border pixels
                if int(a) > x_max: x_max = int(a)
                if int(s) > y_max: y_max = int(s)
                if int(a) < x_min: x_min = int(a)
                if int(s) < y_min: y_min = int(s)
                a = "x"

        # Set x and y for the Answer Bubble
        y_med = (y_min + y_max) / 2
        x_max -= 5

        x_max += Layout().Question.x + Layout().Question.Image.x + 2
        y_med += Layout().Question.y + Layout().Question.Image.y + 2

#       sf.draw_polygon()

        # Draw Answer Bubble Image & Text
        im, im_rect = sf.image_load('images/bubble.gif')

        text_arr = self.text.split(' ')
        cur_line = ''

        cur_x = 0
        cur_y = 0

        # 'textfield' contains the answer text
        textfield = pygame.Surface((textfield_width, textfield_height))
        textfield.fill((255, 255, 255))

        # Make line breaks after reaching width of 'textfield'
        for t in text_arr:
            cur_line = "%s %s" % (cur_line, t)

            font = pygame.font.Font(None, 38)
            n_text = font.render(cur_line, 1, (0,0,0))
            textpos = n_text.get_rect()
            x,y,w,h = list(textpos)
            if w > (textfield_width):
                textfield.blit(text, (cur_x, cur_y))
                cur_line = t
                cur_y += 30
                written = 1
            else:
                written = 0
                text = n_text

#           print textpos

        # Draw leftovers on textfield
        if written == 0:
            textfield.blit(n_text, (cur_x, cur_y))
        else:
            font = pygame.font.Font(None, 38)
            n_text = font.render(cur_line, 1, (0,0,0))
            textfield.blit(n_text, (cur_x, cur_y))

#       print "draw"

        # Draw on Screen
        sf.display_surface(im, (x_max, y_med))
        sf.display_surface(textfield, (x_max+25, y_med+20))

        pygame.display.update()

class Questions:

    def __init__(self):
        self.in_question = False

        played = 0
        count_won = 0
        count_lost = 0
        id = u''
        questions = []
        question = CurrentQuestion()

    def question_pick(self):
        # Check is Quiz Taker
        if __SERVICES__.frontend.get_isGiver():
            print 'we are giving the quiz'
        elif __SERVICES__.frontend.get_isTaker():
            print 'we are taking the quiz'
        # Check if Questions are left to play
        elif self.played >= len(self.questions):
            # Game / Cat Finished!
            print 'game finished', len(self.questions), self.played
            return False

        # Okay, Next One!
        if __SERVICES__.frontend.get_isTaker():
            print 'player requests next question'
            q  = __SERVICES__.frontend.get_next()
            print 'player received next question', q
            if q['id'] == 'gameover':
                return False
            self.question = CurrentQuestion()
            try:
                self.question.id = q['id']
                self.question.prompt = q['prompt']
                self.question.imgfn = q['imgfn']
                self.question.sndfn = q['sndfn']
                self.question.map = q['map']
            except:
                print 'processing question failed', sys.exc_info()[:2]
            return True
        else:
            print 'we are not taking a quiz'
        notfound = True
        while notfound:
            self.question = self.questions[self.played]
            self.id = self.question.id
            q = "SELECT box, day FROM leitner WHERE question_id = '%i'" % (self.id)
            res = __SERVICES__.db.query(q)
            box = res[0][0]
            day = res[0][1]
            if int(time.time()) - day > 600000:
                box -= 1
                if box < 0:
                    box = 0
            if box < 4:
                notfound = False
            else:
                self.played += 1
                if self.played >= len(self.questions):
                    return False
        A.text = self.question.response
        A.link = self.question.answer_link

        if __SERVICES__.frontend.get_isGiver():
            #send question to quiz takers
            q = {'id':self.question.id,
                 'prompt':self.question.prompt,
                 'imgfn':self.question.imgfn,
                 'sndfn':self.question.sndfn,
                 'map':self.question.map
                }
            __SERVICES__.frontend.send_next(str(q))
        self.played += 1
        print 'question_pick returned True', self.played
        return True

    def load_questions(self, cat_id):
        self._cat_id = cat_id

        self.played = 0
        self.count_won = 0
        self.count_lost = 0
        self.count_found = 0
        self.count_notfound = 0
        self.box = 0
        self.time = 0
        self.day = 0

        q = 'SELECT text FROM categories WHERE id = %i' % cat_id
        print q
        res = __SERVICES__.db.query(q)
        Q.id = res[0][0]

        #get list of questions (by question_id)
        try:
            q = "SELECT question_id FROM quizlink WHERE quiz_id = %i" % cat_id
            questionlist = __SERVICES__.db.query(q)
        except:
            questionlist = []

        #get actual questions
        self.questions = []
        self.boxes = [0,0,0,0,0]
        for questionid in questionlist:
            q = "SELECT * from questions WHERE id = '%i'" % questionid[0]
            res = __SERVICES__.db.query(q)
            question = CurrentQuestion()
            question.id = res[0][0]
            question.prompt = res[0][1].strip()
            question.response = res[0][2].strip()
            question.imgfn = res[0][3].strip()
            question.sndfn = res[0][4].strip()
            question.map = res[0][5].strip()
            if question.map[-1:] == ',':
                question.map = question.map[:-1]
            question.answer_link=res[0][6].strip()
            print question.id, question.prompt, question.imgfn, question.sndfn
            q = "SELECT box from leitner WHERE question_id = '%i'" % question.id
            print q
            res = __SERVICES__.db.query(q)
            if len(res[0]) < 1:
                #leitner not intialized
                q = "INSERT INTO leitner(question_id, count_found, count_notfound, box, time, day) VALUES ('%i', '%i', '%i', '%i', '%i', '%i')" % (question_id, 0, 0, 0, 0, 0)
                print q
                try:
                    __SERVICES__.db.commit(q)
                except:
                    print 'leitner insert failed', sys.exc_info()[0]
                box = 0
            else:
                box = res[0][0]
            print 'box', box
            boxi = int(box)
            if boxi > 4:
                boxi = 4
            self.boxes[boxi] += 1
            print 'self.boxes', boxi, self.boxes[boxi]
            self.questions.append(question)
            print 'question appended', question.id

        #present questions randomly
        random.shuffle(self.questions)

def show_answer():
    A.display_answer()
    Q.in_question = True
    next_question()

def finished():
    sf.clear_text_items()
    sf.clear_question_frame(True)
    sf.refresh()
    sf.add_text_item("You have finished this category!", (180, 80))
    sf.add_text_item("Won: %i" % Q.count_won, (220, 120))
    sf.add_text_item("Lost: %i" % Q.count_lost, (220, 160))
    pygame.display.update()
#   ask_category(130)

def display_points():
    global think
    format = TextFormat(None, 30)
    max_q = len(Q.questions)

#   sf.display_tooltip("%i" % (Q.count_won), (480, 14), format)
#   sf.display_tooltip("%i" % Q.count_lost, (480, 42), format)

    if max_q == 0:
        sf.display_line(0, True)
        sf.display_line(0, False)
    else:
        sf.display_line(100 * Q.count_won / max_q, True)
        sf.display_line(100 * Q.count_lost / max_q, False)
        score = 'score:' + str(Q.count_won*10) + ' boxes: '
        score = score + str(Q.boxes[0]) + '-'
        score = score + str(Q.boxes[1]) + '-'
        score = score + str(Q.boxes[2]) + '-'
        score = score + str(Q.boxes[3]) + '-'
        score = score + str(Q.boxes[4])
        score = score + ' speed: ' + think
        sf.add_text_item(score, (600,20))
    pygame.display.update()

def self_test():
    #show_answer()
    #show two clickable items: smiley face, sad face
    image_right, xy = sf.image_load("images/Emotes/face-grin.png")
    sf.display_surface(image_right, (750,100))
    image_wrong, xy = sf.image_load("images/Emotes/face-devil-grin.png")
    sf.display_surface(image_wrong, (750,100))
    pygame.display.update()
    #this should provide for click on image_right or image_wrong
    response = True
    return response

def display_images():
    global images
    candidate_images = []
    for question in Q.questions:
        candidate_images.append(question.imgfn)
    random.shuffle(candidate_images)
    if Q.question.imgfn in candidate_images[:4]:
        images = candidate_images[:4]
    else:
        images = candidate_images[:3]
        images.append(Q.question.imgfn)
    random.shuffle(images)
    image_tl, xy = sf.image_load(images[0], path = IMAGEPATH)
    image_tr, xy = sf.image_load(images[1], path = IMAGEPATH)
    image_ll, xy = sf.image_load(images[2], path = IMAGEPATH)
    image_lr, xy = sf.image_load(images[3], path = IMAGEPATH)
    sf.display_surface(pygame.transform.scale(image_tl, (320,240)), (250, 150))
    sf.display_surface(pygame.transform.scale(image_tr, (320,240)), (520, 150))
    sf.display_surface(pygame.transform.scale(image_ll, (320,240)), (250, 420))
    sf.display_surface(pygame.transform.scale(image_lr, (320,240)), (520, 420))
    pygame.display.update

def play_query_again():
    global query
    if Q.in_question:
        #print 'play_query'
        query.play()
        while pygame.mixer.get_busy():
            clock.tick(30)

def play_sound(fn):
    global query
    query = sf.sound_load(Q.question.sndfn, path=SOUNDPATH)
    image_play, xy = sf.image_load("play_button.png", path = ICONPATH)
    sf.display_surface(image_play, (300,30))
    pygame.display.update()
    query.play()
    while pygame.mixer.get_busy():
        clock.tick(30)

def picture_tl():
    global images
    if Q.in_question:
        if images[0] == Q.question.imgfn:
            response = True
        else:
            response = False
        delete_reacts(response)

def picture_tr():
    global images
    if Q.in_question:
        if images[1] == Q.question.imgfn:
            response = True
        else:
            response = False
        delete_reacts(response)

def picture_ll():
    global images
    if Q.in_question:
        if images[2] == Q.question.imgfn:
            response = True
        else:
            response = False
        delete_reacts(response)

def picture_lr():
    global images
    if Q.in_question:
        if images[3] == Q.question.imgfn:
            response = True
        else:
            response = False
        delete_reacts(response)

def delete_reacts(response):
    if response:
        correct_answer()
    else:
        wrong_answer()
    return True

def play_correct_response_sound():
    good = sf.sound_load(random.choice(CORRECT_SOUNDS))
    good.play()
    while pygame.mixer.get_busy():
        pygame.time.wait(30)

def play_wrong_response_sound():
    good = sf.sound_load(random.choice(WRONG_SOUNDS))
    good.play()
    while pygame.mixer.get_busy():
        pygame.time.wait(30)

def update_leitner_attributes(response):
    global think
    #finally display 'boxes' and 'points'
    think = '%0.2f' % float( time.time() - Q.starttime)
    Q.time = 0
    if response:
        Q.count_found += 1
        if Q.box < 4:
            Q.boxes[Q.box] -= 1
            Q.box += 1
            Q.boxes[Q.box] += 1
    else:
        Q.count_found += 1
        Q.boxes[Q.box] -= 1
        Q.box = 0
        Q.boxes[0] += 1
    Q.day = int(time.time())
    q = "UPDATE leitner SET count_found = '%i' WHERE question_id = '%i'" % (Q.count_found, Q.question.id)
    __SERVICES__.db.commit(q)
    q = "UPDATE leitner SET count_notfound = '%i' WHERE question_id = '%i'" % (Q.count_notfound, Q.question.id)
    __SERVICES__.db.commit(q)
    q = "UPDATE leitner SET box = '%i' WHERE question_id = '%i'" % (Q.box, Q.question.id)
    __SERVICES__.db.commit(q)
    q = "UPDATE leitner SET time = '%i' WHERE question_id = '%i'" % (Q.time, Q.question.id)
    __SERVICES__.db.commit(q)
    q = "UPDATE leitner SET day = '%i' WHERE question_id = '%i'" % (Q.day, Q.question.id)
    print 'update_leitner_attributes', q
    __SERVICES__.db.commit(q)

def correct_answer(next=True):
    if Q.in_question:
        update_leitner_attributes(True)
        A.display_icon("found")
        #A.play_sound(1)
        Q.in_question = False
        Q.count_won += 1
        display_points()
        try:
            play_correct_response_sound()
        except:
            print 'play_correct_response_sound failed'
        if next:
            next_question()
        else:
            show_answer()

def wrong_answer(next=True):
    if Q.in_question:
        update_leitner_attributes(False)
        A.display_icon("not-found")
        Q.in_question = False
        Q.count_lost += 1
        display_points()
        play_wrong_response_sound()
    if next:
        next_question()
    else:
        show_answer()

def getpossibles(teststr):
        #there may be multiple correct answers separated by a '/'
        lst = []
        test = ''
        for i in range(len(teststr)):
            if teststr[i] != '/':
                test = test + teststr[i]
            else:
                lst.append(test)
                test = ''
        if len(test) > 0:
                lst.append(test)
        return lst

def checkanswer(response):
        possibles = getpossibles(Q.question.response)
        return response.strip() in possibles

def startgame(db_cat_id):

    print 'startgame'
    Q.count_won = 0
    A.reset_points()

    if not __SERVICES__.frontend.get_isTaker():
        Q.load_questions(db_cat_id)
        print 'startgame: questions loaded'
        display_points()

    sf.clear_text_items()
    next_question()

def next_question():
    #Q._cat_id
    #Q.questions
    global reacts
    print 'next_question calls question_pick'
    if Q.question_pick():
        clear_reacts()
        Q.in_question = True
        if not sf.get_isTaker():
            #get leitner attributes from db
            q = "SELECT * FROM leitner WHERE question_id = '%i'" % Q.question.id
            res = __SERVICES__.db.query(q)
            if len(res) > 0:
                Q.count_found = res[0][2]
                Q.count_notfound = res[0][3]
                Q.box = res[0][4]
                Q.time = res[0][5]
                Q.day = res[0][6]
            else:
                Q.count_found = 0
                Q.count_notfound = 0
                Q.box = 0
                Q.time = 0
                Q.day = 0
        if len(Q.question.map) > 0:  #this is an imagequiz question
            iq = Imagequiz_question()
            iq.id = Q.question.id
            iq.imgfn = Q.question.imgfn
            iq.map = Q.question.map
            iq.cat = 0
            iq.subcat = 0
            iq.text = Q.question.prompt
            iq.answer = Q.question.response
            iq.answer_link = Q.question.answer_link
            Q.starttime = time.time()
            __SERVICES__.frontend.question_display(iq)
            print 'imagequiz question displayed'
        elif len(Q.question.imgfn) > 0 and len(Q.question.sndfn) > 0: #this is Renyi
            print 'Renyi', Q.question.imgfn, Q.question.sndfn
            #get four images (one is correct), shuffle them, put them in 'react' squares
            set_reacts()
            print 'display_images'
            display_images()
            print 'update pygame display'
            pygame.display.update()
            #load and play sound
            play_sound(Q.question.sndfn)
            Q.starttime = time.time()
        elif len(Q.question.sndfn) > 0: #this in 'phrase' question
            #load and play sound
            print 'phrase question'
            play_sound(Q.question.sndfn)
            Q.starttime = time.time()
            response = __SERVICES__.frontend.ask("")
            if __SERVICES__.frontend.get_menuflag:
                print 'phrases finished'
                Q.in_question = False
                Q.cat_id = -1
                return
            if len(response) == 0 or len(Q.question.response) == 0:
                correct = self_test()
            else:
                correct = checkanswer(response)
            print 'next_question: delete_reacts'
            delete_reacts(correct)
            next_question()
        else: # this is flashcard
            Q.starttime = time.time()
            response = __SERVICES__.frontend.ask(Q.question.prompt)
            try:
               if __SERVICES__.frontend.get_menuflag():
                   print 'flashcard finished'
                   Q.in_question = False
                   Q._cat_id = -1
                   return
            except:
               print 'get_menuflag failed', sys.exc_info()[0]
            if len(response) == 0 or len(Q.question.response) == 0:
                correct = self_test()
            else:
                correct = checkanswer(response)
            delete_reacts(correct)
            next_question()
    else:
        # game / cat finished
        Q.in_question = False
        print "finished"
        Q._cat_id = -1
        finished()

def spot_found():
    print 'spot_found'
    if Q.in_question:
        if not sf.get_isTaker():
            update_leitner_attributes(True)
        A.display_icon("found")
        play_correct_response_sound()
        #A.play_sound(1)
        Q.in_question = False
        Q.count_won += 1
        display_points()
        show_answer()

def spot_not_found():
    print 'spot not found'
    if Q.in_question:
        if not sf.get_isTaker():
            update_leitner_attributes(False)
        A.display_icon("not-found")
        play_wrong_response_sound()
        #A.play_sound(0)
        Q.in_question = False
        Q.count_lost += 1
        display_points()
        show_answer()

def set_reacts():
    global reacts
    reacts = []
    reacts.append(sf.add_react(250, 150, 320, 240, picture_tl, stopsearch = True))
    reacts.append(sf.add_react(520, 150, 320, 240, picture_tr, stopsearch = True))
    reacts.append(sf.add_react(250, 420, 320, 240, picture_ll, stopsearch = True))
    reacts.append(sf.add_react(520, 420, 320, 240, picture_lr, stopsearch = True))
    reacts.append(sf.add_react(750,100,50,50, correct_answer, stopsearch = True))
    reacts.append(sf.add_react(750,150,50,50, wrong_answer, stopsearch = True))
    reacts.append(sf.add_react(300,30,100,100, play_query_again, stopsearch = True))

def clear_reacts():
    global reacts
    for react in reacts:
        sf.del_react(react)

def click_on_pick_category():
        # Select Category
        print 'click_on_pick_category'
        # This is hokey - client must click on Pick_Quiz to start
        if sf.get_isTaker():
            startgame(0)
        else:
            print 'normal game', sf.get_isTaker()
            cat_id = -1
            if Q.in_question:
                sf.clear_text_items()
                sf.clear_question_frame(True)
                Q.in_question = False
            ask_category(cat_id)

def ask_category(cat_id, offset_y = 0):

    q = 'SELECT id, text FROM categories'
    res = __SERVICES__.db.query(q)
    print 'ask_category', len(res), q
    categories = []
    for cat in res:
        cat_id = cat[0]
        category = cat[1]
        q = 'SELECT count(*) FROM quizlink WHERE quiz_id=%i' % cat_id
        res1 = __SERVICES__.db.query(q)
        count = res1[0][0]
        st = category + '(' + str(count) + ')'
        categories.append((st, cat_id))
    title = 'category(' + str(len(categories)) + ')'
    print 'ask_category', title
    pv.pageview(categories, startgame, title)

#initialization called by quiz.py
def load():
    global sf
    sf = __SERVICES__.frontend;
    global pv
    svcs = __SERVICES__
    pv = Pageview(svcs)

    global think
    think = '0.0'

    global Q
    Q = Questions()

    global A
    A = Answer()

    global button1
    global button2
    global button3

    global reacts
    reacts = []

    sf.add_menu_item('/', '_Pick Quiz', click_on_pick_category, 0)

    sf.add_menu_dir('/options', "Options")
    button1 = sf.add_menu_item('/options', 'Display Answer [ On ]', click_options_answer)
    button2 = sf.add_menu_item('/options', 'Play Sound [ On ]', click_options_sound)
    button3 = sf.add_menu_item('/options', 'Draw Line [ On ]', click_options_line)

    __SERVICES__.add_service("next_question", next_question)
    __SERVICES__.add_service("spot_found", spot_found)
    __SERVICES__.add_service("spot_not_found", spot_not_found)

#clean close
def close():
    print 'quiz close'

# handle options tab on main menu
def click_options_answer():
    if A.display:
        A.display = False
        sf.change_menu_item("change_caption", button1, "Display Answer [ Off ]")
    else:
        A.display = True
        sf.change_menu_item("change_caption", button1, "Display Answer [ On ]")

def click_options_line():
    if A.display_line:
        A.display_line = False
        sf.change_menu_item("change_caption", button3, "Draw Line [ Off ]")
    else:
        A.display_line = True
        sf.change_menu_item("change_caption", button3, "Draw Line [ On ]")

def click_options_sound():
    if A.sound_enabled:
        A.sound_enabled = False
        sf.change_menu_item("change_caption", button2, "Play Sound [ Off ]")
    else:
        A.sound_enabled = True
        sf.change_menu_item("change_caption", button2, "Play Sound [ On ]")
