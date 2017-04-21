import sys
import pygame

__PLUGIN_NAME__ = 'db tools'

''' Mixed Functions '''
def clickOnDBSave():
	pass

def clickOnDBRevert():
	pass

def clickOnDBWipe():
	pass	
	
def clickOnQuitYes():
	sys.exit(0)

def clickOnToggleFS():
	pygame.display.toggle_fullscreen()
		
def clickOnOptions_Exchange():
	print "Click on Options - Exchange"

def event1(params):
	print "Event 1 Started :-) params:", params

def React1():
	print "React 1"

def clickOnQuestionItem(params):
	print params
	

# Click on Test()
def clickOnTest():
	print "Start Test"
	sf.clear_question_items()
	
	# Clear the Frame and display Stuff
	sf.question_frame_clear()
	sf.question_frame_show_text('images/europe.gif',0,0)
	sf.question_frame_show_image('images/europe.gif',0,50)
	pygame.display.update()
	
	# Add Hook to onclick
	# 	hook_id = sf.add_event_hook('onclick', event1)
	# 	print "- added hook", hook_id
	
	
''' Click on Test2() '''
def clickOnTest2():
	# Show last Question
	#	sf.question_display()

	# Add Reacts
	#	a = sf.add_react(0, 0, 100, 100, React1, False, True)
	#	b = sf.add_react(50, 50, 100, 100, React1, False, True)
	
	# Remove React a
	#	sf.del_react(a)

	x = sf.ask("Your name:")
	print ">", x
	
	sf.add_question_item(x, (100, 100), clickOnQuestionItem, 0)
	sf.add_question_item(x*2, (100, 150), clickOnQuestionItem, 1)
	
	sf.draw_question_items()
	pygame.display.update()

''' Init Part '''	
def load():
	global sf
	sf = __SERVICES__.frontend;
	
	# Use DB like that:
	# print __SERVICES__.db.query("SELECT * FROM xoquiz WHERE 1")

	# Menu /test
#	sf.add_menu_dir('/test', 'Test')
#	sf.add_menu_item('/test', 'Test()', clickOnTest,3)
#	sf.add_menu_item('/test', 'Test2()', clickOnTest2,3)

	# Menu /options
	sf.add_menu_dir('/options', 'Options')
	sf.add_menu_item('/options', 'Toggle Fullscreen', clickOnToggleFS, 0)

	# Menu /options/database
#	sf.add_menu_dir('/options/database', 'Database')
#	sf.add_menu_item('/options/database', 'Save', clickOnDBSave, 0)
#	sf.add_menu_item('/options/database', 'Revert', clickOnDBRevert, 1)
#	sf.add_menu_item('/options/database', 'Wipe All', clickOnDBWipe, 2)
	
	# Menu /quit
	sf.add_menu_dir('/quit', 'Quit', 5)
	sf.add_menu_item('/quit', 'Yes, really Quit', clickOnQuitYes, 3)

def close():
	pass