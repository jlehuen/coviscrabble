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

import threading
import time
import sys
import os

from scrabble import Scrabble
from scra_server import Serveur
from utils import *

VERSION = (1,0)

def start_server(port):
	serveur = Serveur(VERSION, port)
	serveur_thread = threading.Thread(target=serveur.run)
	serveur_thread.daemon = True
	serveur_thread.start()
	time.sleep(1)

###################
## Main function ##
###################

def main():
	banner('S C R A B B L E')

	# Checking the Python version
	if sys.version_info < (3,0):
		print('Python 3.x requis')
		sys.exit(1)

	# Reading the command line args
	nbargs = len(sys.argv)
	if nbargs == 3 and sys.argv[1] == '-serv':
		flag = True
		addr = 'localhost'
		port = int(sys.argv[2])
		start_server(port) # Launch server
	elif nbargs == 3:
		flag = False
		addr = sys.argv[1]
		port = int(sys.argv[2])
	else:
		print('Usage for server mode: python scrabble.py -serv <port>')
		print('Usage for client mode: python scrabble.py <address> <port>')
		sys.exit(2)

	# Splash screen and identification dialog
	splash = Tk()
	splash.title('S C R A B B L E  %d.%d' % VERSION)
	splash.resizable(False, False)
	image = PhotoImage(file='data/splash.png')
	Label(splash, image=image).pack()
	center(splash)
	Identification(splash)
	splash.destroy()

	# Opening the main window
	dico = os.environ['DICO']
	root = Scrabble(VERSION, addr, port, splash.login, dico, flag)
	root.after(1000, root.pool) # Start pooling for asynchronous messages
	root.mainloop()

if __name__ == '__main__':
	main()
