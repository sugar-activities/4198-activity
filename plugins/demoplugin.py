__PLUGIN_NAME__   = 'demo plugin 1'

'''
 List of Services:
 - ImageQuiz.py, Line 37: "Hook-In Services"
 - http://wiki.laptop.org/index.php?title=XO_ImageQuiz/Plugins#Overview
'''

def clickOnItem1():
	print "Demoplugin Menu Item 1"

def debug():
	pass
	
def load():
	global sf
	sf = __SERVICES__.frontend;

#	print __SERVICES__.db.query("SELECT * FROM xoquiz WHERE 1")
#	sf.add_menu_dir('/demodir', 'Demo Directory')
#	sf.add_menu_item('/', 'Demo Item 3', clickOnItem1)
	pass

def close():
	pass