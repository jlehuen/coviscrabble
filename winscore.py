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

from tkinter import *
from tkinter.font import Font

########################
## Score window class ##
########################

class Winscore(Toplevel):

	players = {}

	def __init__(self, root):

		Toplevel.__init__(self, root)

		self.title('Scores')
		self.resizable(False, False)
		self.protocol("WM_DELETE_WINDOW", self.close_window)
		self.font = Font(family='Verdana', size=12)

		self.canvas = Canvas(self, width=200, height=400, bg="floral white", scrollregion=(0,0,500,500))
		self.canvas.config(width=200, height=200)
		self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

	def close_window(self): pass

	def reset(self):
		self.players = {}
		self.redraw()

	def newscore(self, login, mot, score):
		if login in self.players.keys():
			self.players[login].append((mot,score))
		else:
			self.players[login] = [(mot,score)]
		self.redraw()

	########################
	## Redraw the content ##
	########################

	def redraw(self):
		self.canvas.delete(ALL)
		for i,login in enumerate(self.players):
			x = 140 * i
			self.canvas.create_text(x+70, 10, text=login, font=self.font)
			self.canvas.create_line(x+140, 0, x+140, 400, width=1)
			total = 0

			# Display words and scores for the player login
			for j,(mot,score) in enumerate(self.players[login]):
				y = 15 * j + 40
				self.canvas.create_text(x+10, y, text=mot, font=self.font, anchor=W)
				self.canvas.create_text(x+130, y, text=score, font=self.font, anchor=E)
				total += score

			# Display total score for the player login
			self.canvas.create_line(x, y+15, x+140, y+15, width=1)
			self.canvas.create_text(x+130, y+30, text=total, font=self.font, anchor=E)
			self.canvas.config(width=x+150, height=y+60) # Resize the window


