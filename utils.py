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
import sys, os

def banner(str):
	l = len(str) + 6
	print('-' * l)
	print(str.center(l))
	print('-' * l)

######################################
## Screen size and window centering ##
######################################

def screen_size():
	root = Tk()
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen
	root.destroy()
	return ws,hs

def center(win, parent=None):
	win.update_idletasks()
	width = win.winfo_width()
	height = win.winfo_height()

	if parent:
		parent.update_idletasks()
		x = parent.winfo_x() + parent.winfo_width() // 2 - width // 2
		y = parent.winfo_y() + parent.winfo_height() // 2 - height // 2
		win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
	else:
		screenwidth, screenheight = screen_size()
		x = screenwidth // 2 - width // 2
		y = screenheight // 2 - height // 2
		win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

################################
## Waiting for keyboard event ##
################################

def wait_key():
	result = None
	if os.name == 'nt':
		import msvcrt
		result = msvcrt.getch()
	else:
		import termios
		fd = sys.stdin.fileno()
		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)
		try: result = sys.stdin.read(1)
		except IOError: pass
		finally: termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
	return result

###################################
## Splash screen in modal window ##
###################################

class Splashwin(Toplevel):

	def __init__(self, root, title, filename, bloquante):

		Toplevel.__init__(self, root)

		self.title(title)
		self.resizable(False, False)
		self.transient(root) # Modal window
		self.grab_set()

		image = PhotoImage(file=filename)
		Label(self, image=image).pack()
		Button(self, text='  OK  ', command=self.destroy).pack(side=TOP)
		center(self, parent=root)

		if bloquante: self.wait_window(self) # Blocking window

############################
## Ask for login & passwd ##
############################

class Identification(Toplevel):

	def __init__(self, root):

		Toplevel.__init__(self, root)

		self.root = root
		self.login = StringVar(value='Your login')
		self.passwd = StringVar()

		self.title('Identification')
		self.resizable(False, False)
		self.transient(root) # Modal window
		self.grab_set()

		e1 = Entry(self, textvariable=self.login)
		e1.grid(row=0, column=0, padx=5, pady=5)
		e1.select_range(0, END)
		e1.focus() # Focus on login field
		e2 = Entry(self, textvariable=self.passwd, show='*')
		e2.grid(row=1, column=0, padx=0, pady=0)
		button = Button(self, text='  valider  ', command=self.valider)
		button.grid(row=2, column=0, padx=5, pady=5)
		center(self, parent=root)

		self.bind('<Return>', (lambda e, button=button: button.invoke()))
		self.wait_window(self) # Blocking window

	def valider(self):
		self.root.login = self.login.get().replace(' ', '')
		self.root.passwd = self.passwd.get().replace(' ', '')
		self.destroy()

