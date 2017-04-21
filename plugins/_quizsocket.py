#! /usr/bin/env python

#!/usr/bin/env python

import select
import socket
import sys
import threading
import time

class Interact:
#	status = Status()
	def __init__(self, status):
		self.status = status
		
	def strip(self, str, what):
		str = str.strip()
		while len(str) > 0 and str[-1:] == what: str = str[:-1]	
		while len(str) > 0 and str[:1] == what:  str = str[1:]
		return str
	
	def process_input(self, s):
		""" input comes as arg:param """
		s = self.strip(s, "'")
		print "processing: %s" % s

		if len(s) == 0: return False
		if ":" not in s: return False
		
		s1 = s[:s.index(":")]
		s2 = s[s.index(":")+1:]
				
		
		if s1 == 'get' and s2 == 'userlist':
			return self.status.get_user_names()
		
		elif s1 == 'get' and s2 == 'status':
			return self.status.get_status_line()

		elif s1 == 'reguser' and len(s2) > 1:
			i = 1
			user_name = s2
			while self.status.add_user(user_name) == False:
				user_name = "%s-%i" % (s2, i)
				i += 1
						
			print "interact: registered user '%s'" % s2
			return user_name

class Server(threading.Thread):	

	def __init__(self, host, port, status):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.backlog = 5
		self.size = 1024
		self.server = None
		self.threads = []
		self.interact = Interact(status)


	def open_socket(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setblocking(0)
			self.server.bind((self.host,self.port))
			self.server.listen(5)
		except socket.error, (value,message):
			if self.server:
				self.server.close()
			print "Could not open socket: " + message
			if message == "Address already in use":
				self.__init__(self.host, self.port + 5)
			else:
				sys.exit(1)

	def run(self):
		self.open_socket()
		input = [self.server]
		self.running = True
		while self.running:
			inputready,outputready,exceptready = select.select(input,[],[],3)

			for s in inputready:

				if self.running and s == self.server:
					# handle the server socket
					print "start new client"
					c = ClientServer(self.server.accept(), self.interact)
					c.start()
					self.threads.append(c)

		# close all threads
		print "closing server.run()"
			
	def quit(self):
		print "server quitting"
		self.running = False
		self.server.close()
		for c in self.threads:		
			c.running = 0
			c.join()
	
class ClientServer(threading.Thread):
	def __init__(self,(client,address), interact):
		threading.Thread.__init__(self)
		self.client = client
		self.client.setblocking(0)
		self.address = address
		self.size = 1024
		self.interact = interact
		
	def run(self):
		self.running = 1
		while self.running:
			try:
				data = self.client.recv(self.size)			
				if self.running and data:
					if self.running:
						if data[:3] == "bye" and ":" in data:
							self.interact.status.del_user(data[4:])
							data_back = "bye"
						else:
							data_back = self.interact.process_input(repr(data))
					else:
						data_back = "bye"
					
					print "sending back:", data_back
					self.client.send("%s" % data_back)
				else:
					self.client.close()
					self.running = 0
					
			except Exception, inst:
				# socket is in non-blocking mode, so it raises a lot of exceptions
				if inst.args[0] == 104:
					# connection reset by peer
					self.interact.status.del_user(data[4:])
					self.running = False
					
				elif inst.args[0] != 11:
					print type(inst)
					print inst.args
					
#				time.sleep(0.3)

class Client(threading.Thread):
	def __init__(self, host, port, username, nonet_function=None):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.username = username
		self.nonet_function = nonet_function
	
	def close(self):
		print "sending bye to server"
		try: 
			self.s.send("bye:%s" % self.username)
			time.sleep(1)
		except: pass
		self.running = False
		
	def run(self):
		host = self.host
		port = self.port
		size = 1024
		self.size = size
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try: s.connect((host,port))
		except:
			if self.nonet_function != None: self.nonet_function()
			return False
		
		s.setblocking(0)

		self.s = s
		
		# Register Username
		cmd = "reguser:%s" % self.username		
		self.username = self.talk(cmd)
		print "received username: %s" % self.username

		self.running = True
		while self.running:
			time.sleep(2)
#			print self.talk("get:userlist")

		s.close()

	def talk(self, s):		
#		cmd = "get:userlist"
		print "< %s" % s
		loop = True
		while loop:
			try:
				self.s.send(s)
				loop = False
			except Exception, inst:
				print type(inst)
				print inst.args

#				errno, errstr = list(inst.args)
				if inst.args[0] == 11: time.sleep(0.5)
				else:
					print "Host has quit"
					self.running = False
					return False

		loop = True
		while loop:
			try:
				data = self.s.recv(self.size)
				loop = False
				return data
			except Exception, inst:
#				print type(inst)
#				print inst.args
				errno, errstr = list(inst.args)
				if errno == 11: time.sleep(0.5)
				else:
					print "Host has quit"
					self.running = False
					return False
			


if __name__ == "__main__":
	host = "localhost"
	port = 50056
	username = "chris"
	
	if len(sys.argv) > 1:
		if sys.argv[1] == "0":
			s = Server('', port)
			s.start()
			
			time.sleep(10)
			s.quit()			
				
			print "ciao ciao"
			
		else:
			c = Client(host, port, username)
			c.start()
