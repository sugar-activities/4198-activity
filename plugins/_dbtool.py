'''
 List of Services:
 - ImageQuiz.py, Line 37: "Hook-In Services"
 - http://wiki.laptop.org/index.php?title=XO_ImageQuiz/Plugins#Overview
'''
import subprocess
from path import path
from sugar.activity import activity

__PLUGIN_NAME__   = 'dbtool'

DATADIR = path(activity.get_activity_root()) / 'data'
ACTIVITYDIR = path(activity.get_bundle_path())
print 'directories', DATADIR, ACTIVITYDIR

def dbdelete():
    sf.clear_text_items()
    sf.add_text_item("Clear database", (280,110))
    cmd = "rm -rf *"
    #cmd = "ls -l > " + DATADIR + "/iq.log"
    subprocess.call(cmd, shell=True, cwd=DATADIR)
    print "Clear database"


#TABLE 'categories' ('id','cat_id', 'lang_id', 'text', 'parent_id', 'base_parent_id')
#TABLE 'questions' ('id', 'image_id', 'sound_id', 'map', 'cat', 'subcat', 'answer_link', 'count_found', 'count notfound', 'box', 'time', 'day')
#TABLE 'quizlinks' ('id', 'quiz_id', 'question_id')
#TABLE 'catlinks' ('id', 'parent_id', 'child_id')
#TABLE 'Leitner' ('id', 'question_id', etc )

def dbcategories():
    sf.clear_text_items()
    sf.add_text_item("Show categories", (280,110))
    cats = __SERVICES__.db.query("SELECT id, text FROM categories;")
    count = 0
    for cat in cats:
        count += 1
        catstr = str(cat[0]) + ' category: ' + str(cat[1])
        sf.add_text_item(catstr, (180 + 50, 110 +count * 50))
    print "Show categories"

def dbquestions(count):
    sf.clear_text_items()
    sf.add_text_item("Show questions", (280,110))
        #allow user to go to next page
    sf.add_text_item("next page", (400,110), dbquestions, count + 12, True)
    q = "SELECT id, prompt, response, image_fn, sound_fn, map, answer_link  FROM questions;"
    questions = __SERVICES__.db.query(q)
    if count < len(questions):
        showpage(questions, count)
    
def showpage(questions, count):
    line = 0
    for i in range(12):
        if count < len(questions):
            question = questions[count]
            qstr = str(question[0]) + ' prompt:' + question[1] 
            qstr = qstr + ' response:' + question[2] 
            qstr = qstr + ' img: ' + question[3] 
            qstr = qstr + ' snd: ' + question[4] + ' map ' + question[5]
            qstr = qstr + ' answer_link: ' + question[6]
            sf.add_text_item(qstr, (180 + 50, 160 + line * 25))
        else:
            return True
        count += 1
        line += 1
    return False
        
def dbquizlinks():
    sf.clear_text_items()
    sf.add_text_item("Show questions in quiz", (280,110))
    q = "SELECT id, quiz_id, question_id FROM quizlink;"
    links = __SERVICES__.db.query(q)
    count = 0
    for link in links:
        count += 1
        qstr = str(link[0]) + ' quiz: ' + str(link[1]) + ' question ' + str(link[2]) + ');'
        sf.add_text_item(qstr, (180 + 50, 110 + count * 25))
    

def debug():
    pass

def dbquestions1():
    dbquestions(0)
    
def load():
    global sf
    sf = __SERVICES__.frontend;
    sf.add_menu_dir('/dbtool', 'DB Tool')
    sf.add_menu_item('/dbtool', 'show categories', dbcategories)
    sf.add_menu_item('/dbtool', 'show questions', dbquestions1)
    sf.add_menu_item('/dbtool', 'show quizlinks', dbquizlinks)
    #sf.add_menu_item('/dbtool', 'clear database', dbdelete)

    pass

def close():
    pass
