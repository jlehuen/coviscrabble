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

import re
from socketlib.abstract_client import Abstract_client

def get_data(expression, message):
	return re.findall(expression, message)[0]

class Client(Abstract_client):

	def __init__(self, version, hote, port, login):
		Abstract_client.__init__(self, version, hote, port, login)

	####################################
	## Messages to send to the server ##
	####################################

	def put(self, lettre, ligne, colonne, jocker):
		message = 'put:%s:%d:%d:%r' % (lettre, ligne, colonne, jocker)
		self.send(message)

	def get(self, ligne, colonne):
		message = 'get:%s:%s' % (ligne, colonne)
		self.send(message)

	def valider(self, mot, score, nblettres):
		message = 'valider:%s:%d:%d' % (mot, score, nblettres)
		self.send(message)

	def redonner(self, somme, destinataire):
		message = 'redonner:%d:%s' % (somme, destinataire)
		self.send(message)

	def restart(self):
		self.send('restart')

	#####################################
	## Processing of received messages ##
	#####################################

	def message_handler(self, message, game):

		if message.startswith('put:'):
			data = get_data('^put:(.+):(.+):(.+):(.+)$', message)
			game.async_put(data[0], int(data[1]), int(data[2]), eval(data[3]))

		elif message.startswith('get:'):
			data = get_data('^get:(.+):(.+)$', message)
			game.async_get(int(data[0]), int(data[1]))

		elif message.startswith('score:'):
			data = get_data('^score:(.+):(.+):(.+)$', message)
			game.async_score(data[0], data[1], int(data[2]))

		elif message.startswith('addstand:'):
			data = get_data('^addstand:(.+)$', message)
			liste = data.split(':')
			game.async_addstand(liste)

		elif message.startswith('player:'):
			data = get_data('^player:(.+)$', message)
			game.async_player(data)

		elif message.startswith('gameover:'):
			data = get_data('^gameover:(.+)$', message)
			game.async_gameover(data)

		elif message.startswith('transfer:'):
			data = get_data('^transfer:(.+):(.+):(.+)$', message)
			game.async_transfer(data[0], data[1], int(data[2]))

		elif message == 'restart':
			game.async_restart()

		else: print('[client] unrecognized message: %s' % message)
