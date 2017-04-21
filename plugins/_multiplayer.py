import pygame
from pygame import *
from layout import *
from frontend import hex2rgb
import threading
import time
import traceback

__PLUGIN_NAME__   = 'multi player'
#import single_player

class Status:
	""" edited by the hosts """

	game_state = '0' # 0=open_before_game, 1=..?
	
	status_line = 'statusline'
	clients = []	

	class Client:
		def __init__(self, name, status=''):
			self.name = name
			self.status = status
		
	def set_status_line(self, s1, s2): 
		return True
		
	def get_status_line(self): 
		self.status_line = "%s;;%s" % (self.game_state, self.get_user_names(";"))
		return self.status_line

	def get_user_names(self, split_str=';;'):
		usernames = []
		for c in self.clients:
			usernames.append(c.name)
		return split_str.join(usernames)

	def add_user(self, user_name): 
		for c in self.clients:
			if c.name.upper() == user_name.upper(): return False
		
		new_client = self.Client(user_name)
		self.clients.append(new_client)
		return True
		
	def del_user(self, user_name): 
		print "deleting user %s" % user_name
		new_clients = []
		for c in self.clients:
			if c.name.upper() != user_name.upper():
				new_clients.append(c)

		self.clients = new_clients
		return True
		
		
def show_answer():
	A.display_answer()
		
def finished():
	sf.refresh()
	sf.add_text_item("You have finished this category!", (180, 80))
	sf.add_text_item("Won: %i" % Q.count_won, (220, 120))
	sf.add_text_item("Lost: %i" % Q.count_lost, (220, 160))
	pygame.display.update()
	ask_category(130)
	
	
def startgame(db_cat_id):
	print "* Starting Game, Category:", db_cat_id
	print "** Loading Questions"

	Q.count_won = 0
	Q.count_won = 0
	A.reset_points()	
	
	Q.load_questions(db_cat_id)
	display_points()

	sf.clear_text_items()
	next_question(0)
	

def ask_category(offset_y = 0, offset_x = 0, cat_id=0):
	Q.load(__SERVICES__.locale.lang_id, __SERVICES__.locale.lang_name)

#	sf.clear_text_items()

	i = 1
	y = 110 + offset_y
	x = 340 + offset_x
	
	sf.add_text_item("Category:", (x,y))
	y += 50
	x += 50
	sf.add_text_item('All', (x,y), game_host.set_category, 0, True)
#	global game_host
	for q in Q.categories:
		y += 50
		sf.add_text_item("%s (%s)" % (q[1], q[2]), (x,y), game_host.set_category, q[0], True)
		i += 1
		
	display_points()
	
def display_points():
	format = TextFormat(None, 30)
	max_q = len(Q.questions)

#	sf.display_tooltip("%i" % (Q.count_won), (480, 14), format)
#	sf.display_tooltip("%i" % Q.count_lost, (480, 42), format)
	
	if max_q == 0:
		sf.display_line(0, True)
		sf.display_line(0, False)
	else:
		sf.display_line(100 * Q.count_won / max_q, True)
		sf.display_line(100 * Q.count_lost / max_q, False)

def click_on_next_question():
	next_question(0)

def next_question(params):
	print "* Next Question"

	# Select Category
	if Q._cat_id == -1:
		ask_category()
		return 1
		
	
	# Pick only locale language's categories
	if Q.question_pick():
		__SERVICES__.frontend.question_display(Q.question)
		Q.in_question = True
		
		pass
	else:
		# game / cat finished!
		in_question = False
		print "finished"
		Q._cat_id = -1
		finished()
		pass
	
def spot_found(params):
	if Q.in_question:
		print "found"
		A.display_icon("found")
		A.play_sound(1)
		Q.in_question = False
		Q.count_won += 1
		display_points()
		show_answer()

def spot_not_found(params):
	print params
	if Q.in_question:
		print "not found"
		A.display_icon("not-found")
		A.play_sound(0)
		Q.in_question = False
		Q.count_lost += 1
		display_points()
		show_answer()
	return "ok"
	



class getStatus(threading.Thread):
	running = True
	
	def set(self, client_talk, status_call_function, abort_function=None):	
		self.talk = client_talk
		self.status_call_function = status_call_function
		self.abort_function = abort_function
		self.running = True

	def run(self):
		while self.running:
			time.sleep(2)
			try: 
				self.status = self.talk('get:status')
				self.status_call_function(self.status)	
			except:
				traceback.print_exc()
				print "getstatus aborted"
				self.running = False
				if self.abort_function != None: self.abort_function()
		

class waitForUsersToJoin(threading.Thread):
	running = True
	last_users = ''
	
	def set(self, talk, waittext_id, textid_connectedto=None):
		self.talk = talk
		self.waittext_id = waittext_id
		self.textid_connectedto = textid_connectedto

	def display_server_quit(self):
		self.running = False
			
	def run(self):
		format = TextFormat()			
		font = pygame.font.Font(None, format.size)		
		bg = pygame.Surface((560, 30))

		while self.running:
			time.sleep(2)

			users = self.talk("get:userlist")
			if users == False: return

			self.users = users.split(";;")
			users = users.replace(";;", ",  ")
			
			print self.users
			print users
					
			text = font.render(">  %s" % users, 1, hex2rgb(format.color))
			textpos = text.get_rect()

			bg.fill(hex2rgb(Layout().background))	
			bg.blit(text, (0,0))
			sf.display_surface(bg, (48, 610))

			pygame.display.update((48, 610, 560, 30))

class DrawTimer:
	def __init__(self):
		self.bg = pygame.Surface((100, 60))
		
	def draw(self, time):
		self.bg.fill(hex2rgb(Layout().Question.background))
		
		format = TextFormat(None, 46, None)
		font = pygame.font.Font(None, format.size)
		text = font.render("%i sec" % time, 1, hex2rgb(format.color))
		
		self.bg.blit(text, (0,0))
		sf.display_surface(self.bg, (150, 440))
		pygame.display.update()

class MultiPlayerHost:
	category = 0
	game_time = 0
	textid_timer = -1
	status = Status()
	
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = __import__("plugins/_quizsocket")

		print "starting server"
		self.server = self.socket.Server('', port, self.status)
		self.server.start()
		
	def close(self):
		self.client.running = False
		self.waituser.running = False
		self.server.quit()
		
	def update_status(self, params):
		print params

	def load(self):
		print "Creating a new game"
		sf.clear_question_frame(True)
		
		# Display some text
		format = TextFormat(None, 40)
		sf.add_text_item("New Multiplayer Game", (340, 45), None, None, False, format)
		waittext_id = sf.add_text_item("Waiting for users to join...", (40, 570))

		# let's spawn our own client now
		self.client = self.socket.Client(self.host, self.port, Layout().user_name)
		self.client.start()

		# Display "Waiting for users to join..."
		self.waituser = waitForUsersToJoin()
		self.waituser.set(self.client.talk, waittext_id, None)
		self.waituser.start()
		
		# Constantly Get Status Updates from the Host
#		self.getstatus = getStatus()
#		self.getstatus.set(self.Spawner.client_talk, self.update_status, self.abort_net)
#		self.getstatus.start()
		
		# Display Start Button
		format = TextFormat(None, None, Colors().green)
		sf.add_text_item("Start", (Layout().Question.x + Layout().Question.width - 150, 570), None, None, True, format)

		# Display Categories		
		ask_category()		
		self.set_category(0)
		pygame.display.update()

		self.hookid_click = sf.add_event_hook("onclick", self.click)


		# Draw Timer Option
		img, rect = sf.image_load("images/xclock.png")
		sf.display_surface(img, (40, 400))
		self.draw_timer = DrawTimer()
		self.click_timer()
				
	
	def click(self, params):
		x, y = list(params)
		if x > 40 and x < (40 + 96) and y > 400 and y < (400 + 96):
			# Click on Clock
			self.click_timer()
		
	def click_timer(self):
		if self.game_time == 30:
			self.game_time = 10
		elif self.game_time == 20:
			self.game_time = 30
		elif self.game_time == 10:
			self.game_time = 20
		elif self.game_time == 0:
			self.game_time = 10
		
#		self.Spawner.master_set_status("time:%i" % self.game_time)
		self.draw_timer.draw(self.game_time)
					
	def set_category(self, param):
		cat_id = int(param)
		self.category = cat_id

		cat_name = 'All'		
		if cat_id > 0:
			q = "SELECT text FROM categories WHERE cat_id=%i AND lang_id=%s" % (cat_id, __SERVICES__.locale.lang_id)
			res = __SERVICES__.db.query(q)
			print res
			cat_name = res[0][0]

#		self.Spawner.master_set_status(u"cat:%s" % cat_name)

		bg = pygame.Surface((360, 30))
		bg.fill(hex2rgb(Layout().background))

		format = TextFormat()			
		font = pygame.font.Font(None, format.size)		

		text = font.render("%s" % cat_name, 1, hex2rgb(format.color))
		bg.blit(text, (0,0))
		sf.display_surface(bg, (480, 115))
		pygame.display.update()

class MultiPlayerClient:
	connected = False
	game_time = 0
	cat_name = u''

	socket = None
	waittext_id = None

	format = TextFormat()			
	font = pygame.font.Font(None, format.size)
	bg = pygame.Surface((560, 30))

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.connected = False
		if self.socket == None: self.socket = __import__("plugins/_quizsocket")

	def close(self):
		self.getstatus.running = False
		self.client.close()
		self.connected = False

	def load(self):
		print "Joining a multiplayer game"

		sf.clear_question_frame(True)

		format = TextFormat(None, 40)
		sf.add_text_item("Joining a Multiplayer Game", (340, 45), None, None, False, format)
		pygame.display.update()

#		print self.connected				
		if self.connected == False:		
			host = sf.ask("host")
			sf.refresh()
			print "host: ", host
			self.host = host
		
			if len(host) == 0:
				return False
			
#			if host == "l": host = "localhost"
			print "starting client"
			textid_connectedto = sf.add_text_item("[connecting to %s]" % host, (340, 80))
			self.textid_connectedto = textid_connectedto

			self.client = self.socket.Client(self.host, self.port, Layout().user_name, self.nonet_function)
			self.client.start()
			
			self.getstatus = getStatus()
			self.getstatus.set(self.client.talk, self.update_status, self.nonet_function)
			self.getstatus.start()
				
	def display_catname(self):
		bg = pygame.Surface((300, 60))
		bg.fill(hex2rgb(Layout().Question.background))
		
		format = TextFormat(None, 40)			
		font = pygame.font.Font(None, format.size)		
		text = font.render("Category: %s" % self.cat_name, 1, hex2rgb(format.color))
		
		bg.blit(text, (0,0))
		sf.display_surface(bg, (350, 190))
		pygame.display.update()		
		
	def update_status(self, params):		
		self.status = params
		print "STATUS UPDATE:",params
		
		if params == False or len(params) == 0 or params == None or params == "None":
			self.close()
			return
			
		if self.connected == False:
			self.connection_ok()
						
		n = params.split(";;")
			
		users = n[1].replace(";", ",  ")					

		text = self.font.render(">  %s" % users, 1, hex2rgb(self.format.color))
		textpos = text.get_rect()

		self.bg.fill(hex2rgb(Layout().background))	
		self.bg.blit(text, (0,0))
		sf.display_surface(self.bg, (48, 610))

		pygame.display.update((48, 610, 560, 30))		
		print params
		
#		for n in params:
#			m = n.split(":")
#			if m[0] == "time":
#				if int(m[1]) != self.game_time:
#					self.game_time = int(m[1])
#					self.draw_timer.draw(self.game_time)
#
#			if m[0] == "cat":
#				if m[1] != self.cat_name:
#					self.cat_name = m[1]
#					self.display_catname()


	def connection_ok(self):
		self.connected = True
		sf.del_text_item(self.textid_connectedto)

		self.textid_connectedto = sf.add_text_item("[connected to %s]" % self.host, (340, 80))
		self.waittext_id = sf.add_text_item("Waiting for users to join...", (40, 570))

		pygame.display.update()

		# Draw Timer Option
		img, rect = sf.image_load("images/xclock.png")
		sf.display_surface(img, (40, 400))
		self.draw_timer = DrawTimer()
	
	def nonet_function(self):
		print "client net aborted, quitting MultiPlayer-Client"

		self.running = False
		
		if self.waittext_id != None: sf.del_text_item(self.waittext_id)		
		if self.textid_connectedto != None: sf.del_text_item(self.textid_connectedto)

		sf.add_text_item("Server quit the game", (340, 84))

		# clear player
		bg = pygame.Surface((560, 30))
		bg.fill(hex2rgb(Layout().background))	
		sf.display_surface(bg, (48, 610))
		pygame.display.update()

		self.close()
		
		global game_client
		game_client = None
		



def click_create():
	global game_client
	global game_host

	if game_client == None and game_host == None:
		game_host = MultiPlayerHost("", Layout().port)
		sf.clear_text_items(False)
		game_host.load()


def click_join():
	global game_client
	global game_host
	
	if game_client == None and game_host == None:
		game_client = ''
		game_client = MultiPlayerClient("localhost", Layout().port)		

		sf.clear_text_items()
		
		res = game_client.load()
		if res  == False:
			game_client = None

def load():
	global sf
	sf = __SERVICES__.frontend;

	sp = __import__("plugins/single_player")
	sp.sf = sf
	
	global Q
	Q = sp.Questions()
	
	global A
	A = sp.Answer()
	
	global game_host
	game_host = None
	
	global game_client
	game_client = None

	sf.add_menu_dir('/multi-player', 'Multiplayer', 1)
	sf.add_menu_item('/multi-player', 'Create Game', click_create, 1)
	sf.add_menu_item('/multi-player', 'Join Game', click_join, 2)

	__SERVICES__.add_service("next_question", next_question)
	__SERVICES__.add_service("spot_found", spot_found)
	__SERVICES__.add_service("spot_not_found", spot_not_found)

def close():
	global game_host
	global game_client
	
	if game_host != None: game_host.close()
	if game_client != None: game_client.close()
	
