#coding:utf-8

#######################################
## --- C O V I - S C R A B B L E --- ##
## Copyright (c) Jérôme Lehuen 2020  ##
#######################################

#########################################################################
##                                                                     ##
##   This file is part of COVI-SCRABBLE.                               ##
##                                                                     ##
##   COVI-SCRABBLE is free software: you can redistribute it and/or    ##
##   modify it under the terms of the GNU General Public License as    ##
##   published by the Free Software Foundation, either version 3 of    ##
##   the License, or (at your option) any later version.               ##
##                                                                     ##
##   COVI-SCRABBLE is distributed in the hope that it will be useful   ##
##   but WITHOUT ANY WARRANTY - without even the implied warranty of   ##
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.              ##
##                                                                     ##
##   See the GNU General Public License for more details. You should   ##
##   have a copy of the GNU GPLv3 along with COVI-SCRABBLE.            ##
##   If not, see https://www.gnu.org/licenses/                         ##
##                                                                     ##
#########################################################################

import socket
import time
import re
from abc import *
from threading import Thread

EOD = '$$' # End of data

def getmyip(): return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.')][0]

def get_data(expression, message): return re.findall(expression, message)[0]

####################
## Client facades ##
####################

class Client:

	sock = None   # The client socket
	addr = None   # The client's IP address
	login = None  # The client's login

	def __init__(self, sock, addr, login):
		self.sock = sock
		self.addr = addr
		self.login = login
		self.sock.settimeout(None) # No timeout

	def send(self, data):
		print('[server] --> [%s] %s' % (self.login, data))
		data += EOD # End of data
		self.sock.send(data.encode())

	def close(self):
		self.sock.close()

############################
## Class Abstract_serveur ##
############################

class Abstract_serveur(ABC):

	sock = None  # The server socket
	clients = [] # The connected clients

	@abstractmethod
	def __init__(self, version, port):
		self.version = version
		self.port = port
		self.host = getmyip()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', port))
		self.sock.listen(3)

	#####################################
	## Waiting for connection requests ##
	#####################################

	def run(self):
		print('[server] %s is listening on port %s' % (self.host, self.port))
		while True:
			sock, addr = self.sock.accept()
			print('[server] connection request from %s' % addr[0])
			login = self.handcheck(sock, addr)
			if login:
				client = Client(sock, addr[0], login)
				self.clients.append(client)
				print('[server] %s is registered' % login)
				Thread(target=self.client_thread, args=(client,)).start()

	##############################
	## Identification procedure ##
	##############################

	def exchange(self, sock, addr, message):
		print('[server] --> [%s] %s' % (addr[0], message))
		sock.send(message.encode())
		reponse = sock.recv(2048).decode('utf-8')
		print('[server] <-- [%s] %s' % (addr[0], reponse))
		return reponse

	def erreur(self, sock, message):
		print('[server] ERROR: %s' % message)
		msg = 'ERROR: %s' % message
		sock.send(msg.encode())

	def check_version(self, version):
		return version == self.version

	def identification(self, login, password):
		# TODO
		return login == password

	def handcheck(self, sock, addr):
		sock.settimeout(5) # 5 seconds to answer
		try:

			# Client version request
			reponse = self.exchange(sock, addr, 'version')
			if not reponse.startswith('version:'):
				self.erreur(sock, 'bad handcheck protocol')
				return False

			data = get_data('^version:(\S+):(\S+)$', reponse)
			maj,min = int(data[0]),int(data[1])

			# Check the client's version
			if not self.check_version((maj, min)):
				self.erreur(sock, 'version %d.%d required' % self.version)
				return False

			# Client login request
			reponse = self.exchange(sock, addr, 'whoareyou')
			if not reponse.startswith('mynameis:'):
				self.erreur(sock, 'bad handcheck protocol')
				return False

			login = get_data('^mynameis:(\S+)$', reponse)

			# Client password request
			reponse = self.exchange(sock, addr,'password')
			if not reponse.startswith('password:'):
				self.erreur(sock, 'bad handcheck protocol')
				return False

			password = get_data('^password:(\S+)$', reponse)

			# Check the login and the password
			if not self.identification(login, password):
				self.erreur(sock, 'bad login or password')
				return False

			# Welcome Message
			print('[server] --> [%s] %s' % (addr[0], 'welcome'))
			sock.send('welcome'.encode())
			return login

		except socket.timeout:
			self.erreur(sock, 'timeout during handcheck')
			return False

	###########################
	## One thread per client ##
	###########################

	def client_thread(self, client):
		while True:
			message = client.sock.recv(2048).decode('utf-8')
			print('[server] <-- [%s] %s' % (client.login, message))

			if not message:
				print('[server] %s has deconnected' % client.login)
				self.remove(client)
				break

			else: self.message_handler(message, client)

	############################
	## To broadcast a message ##
	############################

	def broadcast(self, message, login):
		# A client can be excluded from the broadcast
		for c in self.clients:
			if c.login == login: continue
			c.send(message)

	########################
	## To delete a client ##
	########################

	def remove(self, client):
		if client in self.clients:
			client.close()
			self.clients.remove(client)
			print('[server] %s is unregistered' % client.login)



