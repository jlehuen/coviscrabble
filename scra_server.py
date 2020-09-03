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

import time
import re

from random import choice
from common import *

from socketlib.abstract_serveur import Abstract_serveur

def get_data(expression, message):
	return re.findall(expression, message)[0]

###################
## Class Serveur ##
###################

class Serveur(Abstract_serveur):

	def __init__(self, version, port):
		Abstract_serveur.__init__(self, version, port)

	#####################################
	## Processing of received messages ##
	#####################################

	def message_handler(self, message, client):

		if message == 'restart':
			self.restart()

		elif message.startswith('valider:'):
			data = get_data('^valider:(.+):(.+):(.+)$', message)
			self.valider(client, data[0], int(data[1]), int(data[2]))

		elif message.startswith('redonner:'):
			data = get_data('^redonner:(.+):(.+)$', message)
			self.redonner(client, int(data[0]), data[1])

		elif message.startswith('put:'):
			self.broadcast(message, client.login)

		elif message.startswith('get:'):
			self.broadcast(message, client.login)

		else: print('[server] unrecognized message: %s' % message)

	###########################
	## Scrabble game methods ##
	###########################

	bag = None       # The bag of letters
	id_player = 0    # Current Player Index
	PIOCHE = BAG_FR  # BAG_FR / BAG_EN

	def init_bag(self):
		self.bag = []
		for key,data in self.PIOCHE.items():
			self.bag.extend([key for _ in range(data[1])])

	def tirage(self, nblettres):
		liste = []
		for _ in range(nblettres):
			if not self.bag: break # The bag is empty
			lettre = choice(self.bag)
			self.bag.remove(lettre)
			liste.append(lettre)
		return liste

	def restart(self):
		# Reset the clients
		self.broadcast('restart', None)

		# Reset the bag
		self.init_bag()

		# Distributing the letters
		time.sleep(0.5)
		for c in self.clients:
			data = ':'.join(self.tirage(7))
			msg = 'addstand:%s' % data
			c.send(msg)

		# Activate the first player
		time.sleep(0.5)
		self.id_player = 0
		player = self.clients[0].login
		msg = 'player:%s' % player
		self.broadcast(msg, None)

	def valider(self, client, mot, score, nblettres):
		# Distribute the player's score
		msg = 'score:%s:%s:%d' % (client.login, mot, score)
		self.broadcast(msg, None)
		time.sleep(0.5)

		# Pick up the missing letters
		data = ':'.join(self.tirage(nblettres))

		game_over = not data and nblettres == 7

		if game_over:
			# Announce the end of the game
			msg = 'gameover:%s' % client.login
			self.broadcast(msg, client.login)

		else:
			if data:
				msg = 'addstand:%s' % data
				client.send(msg)
				time.sleep(0.5)

			# Activate the next player
			player = self.next_player()
			msg = 'player:%s' % player
			self.broadcast(msg, None)

	def next_player(self):
		self.id_player += 1
		if self.id_player == len(self.clients): self.id_player = 0
		return self.clients[self.id_player].login

	def redonner(self, client, somme, destinataire):
		msg = 'transfer:%s:%s:%d' % (client.login, destinataire, somme)
		self.broadcast(msg, None)


