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

import pickle
from pathlib import Path
from tkinter import messagebox

######################
## Class Dictionary ##
######################

class Dictionary:

	rootnode = None
	dico_user = 'dico/dico_user.txt'

	def __init__(self, dico):
		self.filename_txt = 'dico/%s.txt' % dico
		self.filename_dic = 'dico/%s.dic' % dico

		# Search the compiled dictionary
		if Path(self.filename_dic).is_file():
			self.load(self.filename_dic)

		# Search the source dictionary
		elif Path(self.filename_txt).is_file():
			self.rootnode = node()
			self.build(self.filename_txt)

			# Search the user dictionary
			if Path(self.dico_user).is_file():
				self.build(self.dico_user)

			# Save the compiled dictionary
			self.save(self.filename_dic)
		else:
			print('Warning: no dictionnary found')

	def load(self, filename):
		# Load the compiled dictionary (.dic)
		with open(filename, 'rb') as fhand:
			self.rootnode = pickle.load(fhand)

	def save(self, filename):
		# Save the compiled dictionary (.dic)
		with open(filename, 'wb') as fhand:
			pickle.dump(self.rootnode, fhand, pickle.HIGHEST_PROTOCOL)

	def build(self, filename):
		# Added a list of words to the dictionary
		with open(filename) as fhand:
			for line in fhand:
				word = line.rstrip()
				if word:
					print(word)
					self.rootnode.add(word)

	def valide(self, word):
		if not self.rootnode: return True
		if self.rootnode.search(word): return True
		print('   %s unknown' % word)
		return self.ask_for_word(word)

		"""
		print('	  The word %s is invalid' % word)
		print('	  Do you want to accept %s (y/n) ?' % word)
		while True:
			key = wait_key()
			if key == 'y': return True
			if key == 'n': return False
		"""

	def ask_for_word(self, word):
		dialog = messagebox.askquestion('Invalid word', 'Do you want to add %s to the dictionary ?' % word, icon='warning')
		if dialog == 'yes':
			self.add_word(word)
			return True
		return False

	def add_word(self, word):
		# Add a word to the dictionary
		self.rootnode.add(word)
		self.save(self.filename_dic)
		# Complete the user dictionary
		with open(self.dico_user, 'a') as fhand:
			fhand.write('%s\n' % word)

#####################################
## Nodes of the lexicographic tree ##
#####################################

class node:

	def __init__(self):
		self.desc = {}
		self.isWord = False

	def add(self, word):
		if not word: self.isWord = True; return
		initiale = word[0]
		if not initiale in self.desc.keys():
			self.desc[initiale] = node()
		self.desc[initiale].add(word[1:])

	def search(self, word):
		if not word: return self.isWord
		initiale = word[0]
		if not initiale in self.desc.keys(): return False
		return self.desc[initiale].search(word[1:])
