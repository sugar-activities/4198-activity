__PLUGIN_NAME__   = 'utilities'

'''
 List of Services:
 - ImageQuiz.py, Line 37: "Hook-In Services"
 - http://wiki.laptop.org/index.php?title=XO_ImageQuiz/Plugins#Overview
'''

import os, sys
from pageview import Pageview
from question import Question
from sugar.activity import activity
from sugar.datastore import datastore
from path import path
import subprocess
import zipfile
import xml.dom.minidom

#set up paths to for adding images and sounds
DATAPATH = path(activity.get_activity_root()) / "data"
ACTIVITYPATH = path(activity.get_bundle_path())
ICONPATH = ACTIVITYPATH / 'images'
IMAGEPATH = DATAPATH / 'image'
SOUNDPATH = DATAPATH / 'sound'
BUNDLEPATH = DATAPATH / 'bundle'

def clickOnImport():
    global uglyflag
    uglyflag = False
    #get list of available bundles from journal
    items = []
    print 'import'
    #get mount points
    ds_mounts = datastore.mounts()
    for i in range(0, len(ds_mounts), 1):
        if ds_mounts[i]['uri'].find('datastore') > 0:
            mountpoint = ds_mounts[i]['id']

    #get objects from the local datastore
    ds_objects, num_objects = datastore.find({'mountpoints':[mountpoint], 'mime_type': ['application/x-imagequiz', 'application/zip']})
    print 'import: num_objects', num_objects
    for i in xrange(0, num_objects, 1):
        ds_objects[i].destroy()
        obj = ds_objects[i].object_id
        title = ds_objects[i].metadata['title']
        mime_type = ds_objects[i].metadata['mime_type']
        activity = ds_objects[i].metadata['activity']
        if mime_type == 'application/x-imagequiz':
            pth1 = path(ds_objects[i].get_file_path())
            pos = pth1.find('(')
            if pos >= 0:
                pos1 = pth1[pos:].find(')')
                pth = pth1[:pos] + pth1[pos+pos1+1:].replace('..','.')
            else:
                pth = pth1
            print 'import:', pth1, pth
            items.append((title, pth))
    pv.pageview(items, getbundle, 'Quiz')

def clickOnExport():
    #get list of quizzes
    q = 'SELECT text, id FROM categories'
    categories = __SERVICES__.db.query(q)
    pv.pageview(categories, makebundle, 'Quiz')

def clickOnDelete():
    #get list of quizzes
    q = 'SELECT text, id FROM categories'
    categories = __SERVICES__.db.query(q)
    pv.pageview(categories, deletequiz, 'Quiz')

def clickOnReset():
    path = DATAPATH + '/*'
    subprocess.call("rm -rf " + path, shell = True)
    sf.ask("restart activity")

def deletequiz(quiz_id):
    #first delete quiz from categories, quizlink
    q = "DELETE FROM quizlink WHERE quiz_id = '%i'" % quiz_id
    __SERVICES__.db.commit(q)
    q = "DELETE FROM categories WHERE id = '%i'" % quiz_id
    __SERVICES__.db.commit(q)
    #next cleanup db (remove unused questions, images, sounds)
    q = "SELECT id FROM questions"
    res = __SERVICES__.db.query(q)
    for item in res:
        q = "SELECT id FROM quizlink WHERE question_id = '%i'" % item[0]
        rslt = __SERVICES__.db.query(q)
        if len(rslt) == 0:
            q = "DELETE FROM questions WHERE id = '%i'" % item[0]
            __SERVICES__.db.commit(q)
    q = "SELECT image_fn FROM questions"
    res = __SERVICES__.db.query(q)
    images = []
    for item in res:
        images.append(str(item[0]))
    for f in IMAGEPATH.files():
        if f.name not in images:
            f.remove()
    q = "SELECT sound_fn FROM questions"
    res = __SERVICES__.db.query(q)
    sounds = []
    for item in res:
        sounds.append(str(item[0]))
    for f in SOUNDPATH.files():
        if f.name not in sounds:
            f.remove()
    sf.clear_text_items()

def makebundle(quiz_id):
    q = "SELECT text FROM categories WHERE id = '%i'" % quiz_id
    res = __SERVICES__.db.query(q)
    quizname = res[0][0]
    create_empty_folder(BUNDLEPATH)
    #get list of questions (by question_id)
    q = "SELECT question_id FROM quizlink WHERE quiz_id = '%i'" % quiz_id
    questionlist = __SERVICES__.db.query(q)
    #get actual questions
    questions = []
    for questionid in questionlist:
        q = "SELECT * from questions WHERE id = '%i'" % questionid[0]
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
    #copy images and sounds to BUNDLEPATH
    for question in questions:
        if len(question.imgfn) > 0:
            src = IMAGEPATH / question.imgfn
            path.copy(src, BUNDLEPATH)
        if len(question.sndfn) > 0:
            src = SOUNDPATH / question.sndfn
            path.copy(src,BUNDLEPATH)
    questions_to_xml(questions, quizname, BUNDLEPATH)
    fn = quizname + '.iqxo'
    pth = BUNDLEPATH / fn
    print 'makebundle: zip_folder', pth
    zip_folder(BUNDLEPATH, pth)
    print 'makebundle: write bundle to datastore'
    dsobject = datastore.create()
    dsobject.metadata['title'] = quizname
    dsobject.metadata['mime_type'] = 'application/x-imagequiz'
    dsobject.set_file_path(pth)
    datastore.write(dsobject)
    sf.clear_text_items()

def getbundle(pth):
    global uglyflag
    quizname = path(pth).namebase
    create_empty_folder(BUNDLEPATH)
    unzip_bundle(pth, BUNDLEPATH)
    #copy images and sounds to IMAGEPATH, SOUNDPATH
    for f in BUNDLEPATH.files():
        if f.ext in ['.jpg', '.svg', '.png', '.gif']:
            path.copy(f, IMAGEPATH)
        if f.ext in ['.ogg', '.mp3', '.wav']:
            path.copy(f, SOUNDPATH)
        if f.ext == '.xml':
            xmlpth = f
    print 'convert xml to questions', xmlpth
    questions = xml_to_questions(xmlpth)
    print 'add quiz to categories'
    #add quiz to categories
    q = "INSERT INTO categories (text) VALUES ('%s')" % quizname
    __SERVICES__.db.commit(q)
    q = "SELECT id FROM categories WHERE text = '%s'" % quizname
    res = __SERVICES__.db.query(q)
    quiz_id = res[0][0]
    #add questions to db
    for question in questions:
        q = u'INSERT INTO questions (prompt, response, image_fn, sound_fn, map, answer_link)VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (question.prompt, question.response, question.imgfn, question.sndfn,  question.map, "")
        __SERVICES__.db.commit(q)
        question_id = __SERVICES__.db.lastrowid()
        q = "INSERT INTO quizlink (quiz_id, question_id) VALUES ('%i', '%i')" % (quiz_id, question_id)
        __SERVICES__.db.commit(q)
        q = "INSERT INTO leitner (question_id, count_found, count_notfound, box, time, day) VALUES ('%i', '%i', '%i', '%i', '%i', '%i')" % (question_id, 0, 0, 0, 0, 0)
        __SERVICES__.db.commit(q)
    if not uglyflag:
        sf.clear_text_items()

def create_empty_folder(path):
    subprocess.call("mkdir -p " + path, shell = True)
    subprocess.call("rm -rf " + path + '/*', shell = True)

def questions_to_xml(questions, name, pth):
    #create dom document
    dom = xml.dom.minidom.Document()
    #create quiz element
    quiz = dom.createElement('quiz')
    for question in questions:
        card = dom.createElement('card')
        prompt = dom.createElement('prompt')
        prompt.appendChild(dom.createTextNode(question.prompt))
        if len(question.sndfn) > 0:
            sound = dom.createElement('sound')
            sound.appendChild(dom.createTextNode(question.sndfn))
            prompt.appendChild(sound)
        card.appendChild(prompt)
        response = dom.createElement('response')
        response.appendChild(dom.createTextNode(question.response))
        if len(question.imgfn) > 0:
             image = dom.createElement('image')
             image.appendChild(dom.createTextNode(question.imgfn))
             if len(question.map) > 0:
                 map = dom.createElement('map')
                 map.appendChild(dom.createTextNode(question.map))
                 image.appendChild(map)
             response.appendChild(image)
        card.appendChild(response)
        quiz.appendChild(card)
    #dom to xml str
    str = quiz.toprettyxml()
    #write str to name + .xml in path (e.g. BUNDLEPATH)
    fn = name + '.xml'
    xmlpth = pth / fn
    fout = open(xmlpth, 'w')
    fout.write(str)
    fout.close()

def xml_to_questions(pth):
    dom = xml.dom.minidom.parse(pth)
    quiz = dom.getElementsByTagName('quiz')
    cards = dom.getElementsByTagName('card')
    if len(cards) < 1:
        cards = dom.getElementsByTagName('question')
    questions= []
    for card in cards:
        q = Question()
        print card.toprettyxml()
        prompt = card.getElementsByTagName('prompt') [0]
        q.prompt = prompt.firstChild.data.strip()
        print 'prompt', q.prompt
        response = card.getElementsByTagName('response') [0]
        q.response = response.firstChild.data.strip()
        print 'response', q.response
        nodes = card.getElementsByTagName('sound')
        if len(nodes) > 0:
            q.sndfn = nodes[0].firstChild.data.strip()
        else:
            q.sndfn = ""
        print 'sound' , q.sndfn
        nodes = card.getElementsByTagName('image')
        if len(nodes) > 0:
            q.imgfn = nodes[0].firstChild.data.strip()
        else:
            q.imgfn = ""
        print 'image', q.imgfn
        nodes = card.getElementsByTagName('map')
        if len(nodes) > 0:
            q.map = nodes[0].firstChild.data.strip()
        else:
            q.map = ""
        q.answerlink = ""
        questions.append(q)
        print 'question', q
    print 'return questions', len(questions)
    return questions

def zip_folder(src, dst):
    z = zipfile.ZipFile(dst, "w")
    root, dirs, files = os.walk(src).next()
    for f in files:
        if not path(f).ext == '.iqxo':
            z.write(os.path.join(root, f), f)
    z.close()
    print 'zip_folder:done'

def unzip_bundle(file_path, pth):
    fpth = path(file_path)
    if not fpth.exists():
        print 'unzip_bundle no file', fpth
        return
    z = zipfile.ZipFile(fpth, "r")
    for i in z.infolist():
        f = open(os.path.join(pth, i.filename), "wb")
        f.write(z.read(i.filename))
        f.close()
    z.close()

def debug():
	pass

def load():
    global sf, pv
    global uglyflag
    uglyflag = True
    sf = __SERVICES__.frontend
    global pv
    svcs = __SERVICES__
    pv = Pageview(svcs)

    sf.add_menu_dir('/utility', 'Utilities')
    sf.add_menu_item('/utility', 'import', clickOnImport)
    sf.add_menu_item('/utility', 'export', clickOnExport)
    sf.add_menu_item('/utility', 'delete', clickOnDelete)
    sf.add_menu_item('/utility', 'reset', clickOnReset)
    lib = ACTIVITYPATH / 'quiz_library'
    #now import any bundle in quiz_library not in categories
    #make list of categories in db
    q = 'SELECT text FROM categories'
    res = __SERVICES__.db.query(q)
    categories = []
    for item in res:
        categories.append(item[0])
    for f in lib.files():
        if f.namebase not in categories:
            getbundle(f)

def close():
	pass
