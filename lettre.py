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
import string
from tkinter import *
from tkinter.font import Font
from tkinter.simpledialog import askstring

from common import *
from utils import *

if screen_size()[0] < 1300:
	from data.dim_min import *
else:
	from data.dim_max import *

##################
## Class Lettre ##
##################

class Lettre():

	app = None       # Application
	canvas = None    # Graphic canvas
	key = None       # Character to display
	ligne = None     # Line on the board [0..14]
	colonne = None   # Column on the board [0..14]
	locked = False   # Lock of the letter
	jocker = False   # Flag if jocker

	########################
	## Lettre constructor ##
	########################

	def __init__(self, app, canvas, key):

		self.key = key
		self.app = app
		self.value = BAG_FR[key][0]
		self.jocker = key == ' '
		self.canvas = canvas

		font1 = Font(family='Verdana', size=int(L0/1.8)) # Font of the letter
		font2 = Font(family='Verdana', size=int(L0/4)) # Font of the value

		# Instanciation of the 3 displayable items
		self.item1 = canvas.create_rectangle(0, 0, 0, 0, fill='blanchedalmond', width=0)
		self.item2 = canvas.create_text(0, 0, text=key, font=font1)
		self.item3 = canvas.create_text(0, 0, text=self.value, font=font2, anchor=E)

		# Binding one listener per action and per item
		canvas.tag_bind(self.item1, '<Button-1>', self.clic)
		canvas.tag_bind(self.item2, '<Button-1>', self.clic)
		canvas.tag_bind(self.item3, '<Button-1>', self.clic)
		canvas.tag_bind(self.item1, '<Button1-Motion>', self.move)
		canvas.tag_bind(self.item2, '<Button1-Motion>', self.move)
		canvas.tag_bind(self.item3, '<Button1-Motion>', self.move)
		canvas.tag_bind(self.item1, '<ButtonRelease-1>', self.release)
		canvas.tag_bind(self.item2, '<ButtonRelease-1>', self.release)
		canvas.tag_bind(self.item3, '<ButtonRelease-1>', self.release)

	def replace(self, x, y):
		self.x = x
		self.y = y

	def setKey(self, lettre):
		self.canvas.itemconfig(self.item2, text=lettre)
		self.key = lettre
		return self

	def delete(self):
		self.canvas.delete(self.item1)
		self.canvas.delete(self.item2)
		self.canvas.delete(self.item3)

	def lock(self):
		self.locked = True

	def askforletter(self):
		while True:
			lettre = askstring('Jocker Letter', 'Enter a letter :', initialvalue='*', parent=self.app)
			if lettre and len(lettre) == 1 and lettre.upper() in string.ascii_uppercase: break
		return lettre.upper()

	######################
	## Listener methods ##
	######################

	def clic(self, event):
		# Memorization of the position of the initial click
		if not self.locked:
			self.dx = self.x - event.x
			self.dy = self.y - event.y
			self.devant() # Bring to the front
			self.reprendre()

	def move(self, event):
		if not self.locked:
			self.x = event.x + self.dx
			self.y = event.y + self.dy
			# So as not to lose the letters
			if self.x < MIN_X: self.x = MIN_X
			if self.y < MIN_Y: self.y = MIN_Y
			if self.x > MAX_X: self.x = MAX_X
			if self.y > MAX_Y: self.y = MAX_Y
			# To respect the game rounds
			if self.app.locked:
				if self.y < STAND_Y: self.y = STAND_Y
			self.redraw()

	def release(self, event):
		if not self.locked:
			co = (self.x - X0) // L0
			li = (self.y - Y0) // H0
			if co in range(0, 15) and li in range(0, 15):

				# Alignment on the board
				self.x = co * L0 + L0 // 2 + X0
				self.y = li * H0 + H0 // 2 + Y0
				self.redraw()

				if self.app.libre(li, co):
					# Choice of the letter if jocker
					if self.jocker and self.key == ' ':
						self.setKey(self.askforletter())
					self.deposer(li, co)
				else:
					# Offset
					self.x += L0 // 2
					self.y += H0 // 2
					self.redraw()

			elif self.jocker:
				# Delete the letter
				self.setKey(' ')

	###########################################
	## View methods (not a real MVC pattern) ##
	###########################################

	def redraw(self):
		# To redraw the letter
		self.canvas.coords(self.item1, self.x-L0//2, self.y-H0//2, self.x+L0//2+1, self.y+H0//2+1)
		self.canvas.coords(self.item2, self.x, self.y)
		self.canvas.coords(self.item3, self.x+L0//2-2, self.y+H0//2-8)

	def devant(self):
		# To bring the letter to the foreground
		self.canvas.tag_raise(self.item1)
		self.canvas.tag_raise(self.item2)
		self.canvas.tag_raise(self.item3)

	############################################
	## Model methods (not a real MVC pattern) ##
	############################################

	def deposer(self, ligne, colonne):
		# To put the letter on the board
		self.app.deposer(self, ligne, colonne)
		self.ligne = ligne
		self.colonne = colonne

	def reprendre(self):
		# To remove the letter from the board
		if self.ligne is not None:
			self.app.reprendre(self)
			self.ligne = None
			self.colonne = None
