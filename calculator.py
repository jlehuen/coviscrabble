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

from common import *

def calculer_score(plateau, liste, dico):
	print('   Calculating the score...')

	# Checking an empty word
	if not len(liste):
		print('   Place at least one letter')
		return False,False

	# Put the letters of the word in the right order
	liste.sort(key=lambda lettre: lettre.ligne) # Sort on the lines
	liste.sort(key=lambda lettre: lettre.colonne) # Sort on columns
	list_li = list(map(lambda lettre: lettre.ligne, liste)) # List of lines
	list_co = list(map(lambda lettre: lettre.colonne, liste)) # List of columns

	# Determining the orientation of the word
	singleton = len(liste) == 1
	mot_horiz = not singleton and len(set(list_li)) == 1
	mot_verti = not singleton and len(set(list_co)) == 1

	# Checking the first word
	li,co = liste[0].ligne,liste[0].colonne
	if singleton and (li,co) == (7,7):
		print('   Place at least two letters')
		return False,False

	# Checking the alignment of the word
	if not singleton and not mot_horiz and not mot_verti:
		print('   The letters are not aligned')
		return False,False

	# Checking the consistency of the word
	liste_horiz = cree_liste_horiz(plateau, liste[0].ligne, liste[0].colonne)
	liste_verti = cree_liste_verti(plateau, liste[0].ligne, liste[0].colonne)
	for lettre in liste:
		if not lettre in liste_horiz + liste_verti:
			print('   The letters are not contiguous')
			return False,False

	# Checking the connection of the word
	linked = False
	for lettre in liste:
		li,co = lettre.ligne,lettre.colonne
		if (li,co) == (7,7): linked = True
		if li > 0 and plateau[li-1][co] and not plateau[li-1][co] in liste: linked = True
		if co > 0 and plateau[li][co-1] and not plateau[li][co-1] in liste: linked = True
		if li < 14 and plateau[li+1][co] and not plateau[li+1][co] in liste: linked = True
		if co < 14 and plateau[li][co+1] and not plateau[li][co+1] in liste: linked = True
	if not linked:
		print('   The word is not connected')
		return False,False

	# Calculating the score for a single letter
	if singleton:
		score = 0
		mot1 = mot2 = ''
		liste_horiz = cree_liste_horiz(plateau, liste[0].ligne, liste[0].colonne)
		liste_verti = cree_liste_verti(plateau, liste[0].ligne, liste[0].colonne)
		if len(liste_horiz) > 1:
			sc = subscore(plateau, liste_horiz, liste)
			mot1 = lst2str(liste_horiz)
			if not dico.valide(mot1): return False,False
			print('   %s = %d' % (mot1, sc))
			score += sc
		if len(liste_verti) > 1:
			sc = subscore(plateau, liste_verti, liste)
			mot1 = lst2str(liste_verti)
			if not dico.valide(mot1): return False,False
			print('   %s = %d' % (mot1, sc))
			score += sc
		if len(mot1) > len(mot2): mot = mot1
		else: mot = mot2

	# Calculating the score for a horizontal word
	elif mot_horiz:
		score = 0
		liste_horiz = cree_liste_horiz(plateau, liste[0].ligne, liste[0].colonne)
		sc = subscore(plateau, liste_horiz, liste)
		mot = lst2str(liste_horiz)
		if not dico.valide(mot): return False,False
		print('   %s = %d' % (mot, sc))
		score += sc
		# Secondary vertical words
		for lettre in liste:
			liste_verti = cree_liste_verti(plateau, lettre.ligne, lettre.colonne)
			if len(liste_verti) > 1:
				sc = subscore(plateau, liste_verti, liste)
				mot2 = lst2str(liste_verti)
				if not dico.valide(mot2): return False,False
				print('   %s = %d' % (mot2, sc))
				score += sc

	# Calculating the score for a vertical word
	elif mot_verti:
		score = 0
		liste_verti = cree_liste_verti(plateau, liste[0].ligne, liste[0].colonne)
		sc = subscore(plateau, liste_verti, liste)
		mot = lst2str(liste_verti)
		if not dico.valide(mot): return False,False
		print('   %s = %d' % (mot, sc))
		score += sc
		# Secondary horizontal words
		for lettre in liste:
			liste_horiz = cree_liste_horiz(plateau, lettre.ligne, lettre.colonne)
			if len(liste_horiz) > 1:
				sc = subscore(plateau, liste_horiz, liste)
				mot2 = lst2str(liste_horiz)
				if not dico.valide(mot2): return False,False
				print('   %s = %d' % (mot2, sc))
				score += sc
	else:
		print('   ERROR in function calculate_score')
		exit()

	if len(liste) == 7: score += 50 # Scrabble
	print('   Total = %d' % score)
	return mot,score

####################################################################################
# Returns a string from a list of letters

def lst2str(liste):
	return ''.join(map(lambda lettre: lettre.key, liste))

####################################################################################
# Calculate the score of a list of words

def subscore(plateau, liste1, liste2):
	# First list = the letters of the word to be scored
	# Second list = the letters posed by the player
	score = 0
	for lettre in liste1:
		if lettre in liste2:
			score += lettre.value * BOARD_VAL1[lettre.ligne][lettre.colonne]
		else: score += lettre.value
	# Apply score multipliers
	for lettre in liste1:
		if lettre in liste2:
			score *= BOARD_VAL2[lettre.ligne][lettre.colonne]
	return score

####################################################################################
# Builds a list of letters horizontally from a position

def cree_liste_horiz(plateau, li, co):
	liste = []
	while co > 0 and plateau[li][co-1]: co -= 1
	while co < 15 and plateau[li][co]:
		liste.append(plateau[li][co])
		co += 1
	return liste

####################################################################################
# Builds a list of letters vertically from a position

def cree_liste_verti(plateau, li, co):
	liste = []
	while li > 0 and plateau[li-1][co]: li -= 1
	while li < 15 and plateau[li][co]:
		liste.append(plateau[li][co])
		li += 1
	return liste
