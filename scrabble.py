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

import os
import threading
from tkinter import *

from lettre import Lettre
from scra_client import Client
from winscore import Winscore
from calculator import calculer_score
from dictionary import Dictionary

from common import *
from utils import *

if screen_size()[0] < 1300:
	from data.dim_min import *
else:
	from data.dim_max import *

##########################
## Class of Application ##
##########################

class Scrabble(Tk):

	plateau = None  # Matrix [0..14][0..14] of letters
	stand = None    # List of letters
	bag = None      # Character deck
	mot = None      # Letters of the last word
	dico = None     # Lexicographic dictionary
	login = None    # Player Login
	passwd = None   # Player Password
	locked = True   # Player lock

	def __init__(self, version, addr, port, login, dico, serverflag):

		Tk.__init__(self)

		self.login = login
		self.title('C O V I   S C R A B B L E  %d.%d  –  %s' % (version[0], version[1], login))
		self.resizable(False, False)

		if MAXI_SCREEN:
			self.fond = PhotoImage(file='data/scrabble_max.png')
			self.canvas = Canvas(self, width=800, height=950)
			self.canvas.create_image(405, 410, image=self.fond)
			self.canvas.create_rectangle(0, 820, 805, 955, fill='green', width=0)
			self.canvas.pack(side=TOP)
		else:
			self.fond = PhotoImage(file='data/scrabble_min.png')
			self.canvas = Canvas(self, width=600, height=710)
			self.canvas.create_image(303, 306, image=self.fond)
			self.canvas.create_rectangle(0, 610, 603, 720, fill='green', width=0)
			self.canvas.pack(side=TOP)

		if serverflag: Button(self, text='  Start Game  ', command=self.restart).pack(side=LEFT)
#		Button(self, text='Nouvelle distribution', command=self.newdeal).pack(side=LEFT)
		Button(self, text='  Exit Game  ', command=quit).pack(side=RIGHT)

		self.btn_valider = Button(self, text='  Validate  ', state=DISABLED, command=self.valider)
		self.btn_valider.pack(side=BOTTOM)
		center(self)

		# Create the score window
		self.winscore = Winscore(self)
		self.update_winscore_position()
		self.bind('<Configure>', self.dragging)

		# Initialize game board and stand
		self.plateau = [[None] * 15 for _ in range(15)]
		self.stand = []
		self.mot = []

		# Load the dictionary
		self.dico = Dictionary(dico)

		# Launch the client
		self.client = Client(version, addr, port, self.login)
		client_thread = threading.Thread(target=self.client.run)
		client_thread.daemon = True
		client_thread.start()

	def dragging(self, event):
		# https://stackoverflow.com/questions/45183914/tkinter-detecting-a-window-drag-event
		if event.widget is self: self.update_winscore_position()

	def update_winscore_position(self):
		self.update() # Before getting winfo values
		x = self.winfo_x() + self.winfo_width() + 10
		y = self.winfo_y()
		self.winscore.geometry('+%d+%d' % (x,y))
		self.winscore.lift() # In the foreground

	########################
	## Méthodes du modèle ##
	########################

	def libre(self, ligne, colonne):
	 	return self.plateau[ligne][colonne] is None

	def deposer(self, lettre, ligne, colonne):
		self.plateau[ligne][colonne] = lettre # Add to the board
		self.stand.remove(lettre) # Remove from the stand
		self.mot.append(lettre) # To count the points
		self.client.put(lettre.key, ligne, colonne, lettre.jocker)

	def reprendre(self, lettre):
		self.plateau[lettre.ligne][lettre.colonne] = None # Remove from the board
		self.stand.append(lettre) # Add to the stand
		self.mot.remove(lettre) # To count the points
		self.client.get(lettre.ligne, lettre.colonne)

	def calculer_score(self):
		return calculer_score(self.plateau, self.mot, self.dico)

	def valider(self):
		self.btn_valider.configure(state=DISABLED)
		mot,score = self.calculer_score()
		if score:
			self.lock_all_letters()
			nblettres = 7-len(self.stand) # Number of letters to pick
			self.client.valider(mot, score, nblettres)
		else:
			self.btn_valider.configure(state=NORMAL)

	def restart(self):
		self.client.restart()

	def clear_canvas(self):
		# Delete letters from the stand
		for lettre in self.stand: lettre.delete()
		# Delete letters from the board
		for ligne in range(15):
			for colonne in range(15):
				lettre = self.plateau[ligne][colonne]
				if lettre: lettre.delete()

	def lock_all_letters(self):
		for ligne in range(15):
			for colonne in range(15):
				lettre = self.plateau[ligne][colonne]
				if lettre: lettre.lock()

	#############################
	## Methods from the server ##
	#############################

	def pool(self):
		# To consult the client every 500 ms
		self.client.process_messages(self)
		self.after(500, self.pool)

	def async_put(self, key, li, co, jocker):
		if jocker:
			lettre = Lettre(self, self.canvas, ' ').setKey(key)
		else:
			lettre = Lettre(self, self.canvas, key)
		self.plateau[li][co] = lettre
		# The position on the board
		x = co * L0 + L0 // 2 + X0
		y = li * H0 + H0 // 2 + Y0
		lettre.replace(x, y)
		lettre.redraw()
		lettre.lock()

	def async_get(self, li, co):
		lettre = self.plateau[li][co]
		self.plateau[li][co] = None
		lettre.delete()

	def async_score(self, login, mot, score):
		#print('Score of %s for %s = %d' % (login, mot, score))
		self.winscore.newscore(login, mot, score)

	def async_addstand(self, liste):
		for key in liste:
			self.stand.append(Lettre(self, self.canvas, key))
		# Reposition the letters on the stand
		for i,lettre in enumerate(self.stand):
			lettre.replace((L0 + 10) * i + X0, STAND_Y + 10)
			lettre.redraw()

	def async_player(self, login):
		if login == self.login:
			self.btn_valider.configure(state=NORMAL)
			self.locked = False
			self.mot = []
		else:
			self.btn_valider.configure(state=DISABLED)
			self.locked = True

	def async_restart(self):
		self.clear_canvas()
		self.winscore.reset()
		self.plateau = [[None] * 15 for _ in range(15)]
		self.stand = []
		self.mot = []

	def async_gameover(self, login):
		print('GAME OVER')
		# Redistribute stand points
		somme = sum(lettre.value for lettre in self.stand)
		self.client.redonner(somme, login)

	def async_transfer(self, expediteur, destinataire, somme):
		self.winscore.newscore(expediteur, '', -somme)
		self.winscore.newscore(destinataire, '', somme)
		# Game over popup window
		title = 'The player %s put down the last letter' % destinataire
		Splashwin(self, title, 'data/gameover.png', False)
