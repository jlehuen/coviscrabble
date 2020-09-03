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
import queue
from abc import *

EOD = '$$' # End of data

class Abstract_client(ABC):

	login = None
	serveur = None # Le socket du serveur
	queue = queue.Queue() # File d'attente des messages

	#################
	## Constructor ##
	#################

	@abstractmethod
	def __init__(self, version, hote, port, login):
		self.login = login
		self.version = version
		self.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.serveur.connect((hote, port))
			print('[client] connection with server OK')
		except:
			print('[client] no server available')
			exit()

	def send(self, data):
		print('[client] --> %s' % data)
		self.serveur.send(data.encode())

	####################################
	## Processing of waiting messages ##
	####################################

	def process_messages(self, game):
		# Periodic process requested by Tkinter
		while self.queue.qsize():
			message = self.queue.get(0)
			self.message_handler(message, game)

	########################
	## Client thread loop ##
	########################

	def run(self):

		# Handcheck procedure

		while True:
			message = self.serveur.recv(2048).decode('utf-8')
			print('[client] <-- %s' % message)

			if not message:
				print('[client] connection with server lost')
				self.serveur.close()
				exit()

			elif message.startswith('ERROR'): # Unvalid handcheck
				self.serveur.close()
				exit()

			elif message == 'version':
				reponse = 'version:%d:%d' % (self.version[0], self.version[1])
				self.send(reponse)

			elif message == 'whoareyou':
				reponse = 'mynameis:%s' % self.login
				self.send(reponse)

			elif message == 'password':
				reponse = 'password:%s' % self.login
				self.send(reponse)

			elif message == 'welcome': break # Valid handcheck

			else: print('[client] unrecognized message: %s' % message)

		# Asynchronous message processing

		accumulateur = ''
		while True:
			data = self.serveur.recv(2048).decode('utf-8')
			if not data:
				print('[client] connection with server lost')
				self.serveur.close()
				exit()
			accumulateur += data
			while EOD in accumulateur:
				message = accumulateur[:accumulateur.find(EOD)]
				accumulateur = accumulateur[accumulateur.find(EOD)+len(EOD):]
				print('[client] <-- %s' % message)
				self.queue.put(message)

		self.serveur.close()

