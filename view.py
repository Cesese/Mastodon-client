#!/bin/python3

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

import logging
import threading
import time

from mastodon import Mastodon
from mastodon import StreamListener

from html.parser import HTMLParser

import io
import urllib
import PIL.Image
import aalib

import ast # to convert a string into a list
from os import mkdir


""" doesn't work """
class MyStreamListener(StreamListener):

	statuslist = []

	def on_update(self, status):
		self.statuslist.prepend(status)

	# accessor
	def fetchall(self):
		statuslist = self.statuslist
		self.statuslist = []
		return statuslist

	def getStatusList(self):
		return self.statuslist

	def setStatusList(self, statuslist):
		self.statuslist = statuslist

	def debug(self):
		return ("statuslist", self.statuslist)
	

# I think I understand how it works, but I couldn't do the same for the stream listener so I think I don't?
class PostParser(HTMLParser):
	""" Parser for mastodon posts """
	
	# the text-only content of the post
	postContent = ""
	media = []
	debug = []
	
	# accessor
	def get_result_destructively(self):
		postContent = self.postContent
		self.postContent = ""
		return postContent
	
	def handle_starttag(self, tag, attrs):
		
		picture = False
		if tag == "a":
			for e in attrs:
				if e[0] == "class" and e[1] == "":
					picture = True
			if picture:
				for e in attrs:
					if e[0] == "href":
						self.media.append(e[1])
		elif tag == "br":
			self.postContent += "\n"
		self.debug.append((("Picture", picture), ("Tag", tag), attrs))
	
	def handle_data(self, data):
		self.postContent += data
	
	def handle_endtag(self, tag):
		pass
    
parser = PostParser()

listener = MyStreamListener()


KEY_ENTER = 10
KEY_BACKSPACE = 127
curses.KEY_BACKSPACE = KEY_BACKSPACE
SLEEPTIME = 0.05
TIMERLOOPS = 20
PADHEIGHT = 2048
GOODINIT = True
TLLIMIT = 100
LASTID = {
	2: None,
	3: None,
	4: None,
	5: None
	}

try:
	mkdir("logs")
	mkdir("logs/id")
	mkdir("logs/pos")
	mkdir("logs/2")
	mkdir("logs/3")
	mkdir("logs/4")
	mkdir("logs/5")
except:
	pass


for i in range(2, 5+1):
	try:
		lf = open("logs/id/" + str(i) + ".txt", "r")
		LASTID[i] = lf.read()
		lf.close()
	except:
		LASTID[i] = None


optionsString = (
			'Instance :',
			'Username :',
			'Password :'
			)
options = []
try:
	f = open("credentials.txt", "r")
	for line in f:
		options.append(line[:-1])
	f.close()
except:
	print("""Please write your credentials in a file called "credentials.txt", like this :
<instance> (eg https://niu.moe/)
<username> (eg bunni)
<password> (eg MuchPasswordSuch1337)
""")
	GOODINIT = False
	exit

options = options[:len(optionsString)]

app_name = 'bunclient'

try:
	f = open("niuclient_clientcred.secret", "r")
	f.close()
except:
	try:
		create_app(app_name, options[0])
	except:
		print("Couldn't create the app. Please check your instance url.")
		GOODINIT = False
		exit



def create_app(name, url):
	Mastodon.create_app(
		name,
		api_base_url = url,
		to_file = 'niuclient_clientcred.secret'
	)


def login(instance, username, password):
	mastodon = Mastodon(
		client_id = 'niuclient_clientcred.secret',
		api_base_url = instance
	)
	mastodon.log_in(
		username,
		password,
		to_file = 'niuclient_usercred.secret'
	)
	return mastodon

def boot(paddic, windic):
	a = time.time()
	t = threading.currentThread()
	while getattr(t, "do_run", True):
		paddic['pad'].clear()
		paddic['pad'].addstr(0, 0, "loading... (" + str(time.time() - a) + "s)")
		paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
		time.sleep(SLEEPTIME)
	paddic['pad'].clear()
		

def error(errorwin, a, b):
	errorwin['win'].clear()
	errorwin['win'].addstr(0, 0, a)
	errorwin['win'].addstr(1, 0, b)
	errorwin['win'].refresh()

def thread_function(menu, paddic, windic, overdic, errorwin):
	t = threading.currentThread()
	mastodon = -1
	while(mastodon == -1):
		mastodon = getattr(t, "mastodon", -1)

	paddic['pad'].clear()
	overdic['pad'].clear()
	paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
	if menu >= 2 and menu <= 5: # home - notifications - local - public
		size = min(paddic['width']-1, windic['height']*2)
		aascreen = aalib.AsciiScreen(width=size, height=size//2)
		#fp = io.BytesIO(urllib2.urlopen('https://www.python.org/static/favicon.ico').read())
		#image = PIL.Image.open(fp).convert('L').resize(screen.virtual_size)
		#screen.put_image((0, 0), image)
		#print screen.render()
		(lasty, lastx) = (-1, -1)
		i = 0
		y = 0
		mode = False
		test = None
		listener = -1
		userstream = -1
		while(userstream == -1 or listener == -1 or mastodon == -1):
			userstream = getattr(t, "userstream", -1)
			listener = getattr(t, "listener", -1)
		setattr(t, "y", 0)
		setattr(t, "enter", False)
		(head, body, tail) = ([], [], [])
		lasty = 0
		i = 0
		try:
			hf = open("logs/"+str(menu)+"/head.txt", "r")
			head = hf.read()
			head = ast.literal_eval(head)
			hf.close()
			bf = open("logs/"+str(menu)+"/body.txt", "r")	
			body = bf.read()
			body = ast.literal_eval(body)
			bf.close()
			tf = open("logs/"+str(menu)+"/tail.txt", "r")
			tail = tf.read()
			tail = ast.literal_eval(tail)
			tf.close()
			fi = open("logs/pos/" + str(menu) + ".txt", "r")
			tmp = []
			for l in fi:
				tmp.append(l)
			fi.close()
			lasty = int(tmp[0])
			i = int(tmp[1])


		except:
			error(errorwin, 'read logs', "coudln't find them (normal if first time)")
		
		timer = 100
		tmp = lasty
		(lasty, i) = displayPosts(head, body, tail, paddic, windic, overdic, tmp, i, errorwin)
		overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
		(lasty, i) = displayPosts(head, body, tail, paddic, windic, overdic, tmp, i, errorwin)
		overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
		
		while getattr(t, "do_run", True):
			timer += 1
#			error(errorwin, "debug listener", str(listener.debug()))
			if(timer > 100 and i == 0):
				timer = 0
				try:
					tmp = lasty
					paddic['pad'].clear()
					overdic['pad'].clear()
					""" starting here : needs some work """
					"""
					tl = []
					try:
						tl = listener.fetchall()
					except:
						error(errorwin, 'listener', 'fetchall')
					nhead = []
					nbody = []
					for l in tl:
						content = ""
						if menu != 3:
							try:
								parser.feed(l["content"])
							except:
								error(errorwin, 'parser', 'tl')
							content = parser.get_result_destructively()
						else:
							content = l["type"]

						nhead.append(str(l["account"]["display_name"]) +
						            " (@" + str(l["account"]["acct"]) + ")")
						nbody.append(str(content))
					try:
						head = nhead + head
						body = nbody + body
					except:
						error(errorwin, 'prepend', '')
						
					"""
					""" other attempt, with timeline : works! """
					(nhead, nbody, ntail) = downloadPosts(menu, mastodon, aascreen, windic, errorwin)
					head = nhead + head
					tail = ntail + tail
					body = nbody + body
					""" end of messy part """
					try:
						(lasty, i) = displayPosts(head, body, tail, paddic, windic, overdic, tmp, i, errorwin)
					except:
						error(errorwin, 'displayPosts', "didn't work :/ i=" + str(i) + " ; tmp=" + str(tmp))
						lasty = tmp
						i = 1
				except:
					error(errorwin, "Thread function", "End of pad")
					i = 1
			y = getattr(t, "y")
			setattr(t, "y", 0)
			i = (i + y)
			if i > lasty - windic['height']:
				i = lasty - windic['height']
			elif i < 0:
				i = 0

			overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
			time.sleep(SLEEPTIME)
		try:
			hf = open("logs/"+str(menu)+"/head.txt", "w")
			hf.write(str(head))
			hf.close()
			bf = open("logs/"+str(menu)+"/body.txt", "w")
			bf.write(str(body))
			bf.close()
			tf = open("logs/"+str(menu)+"/tail.txt", "w")
			tf.write(str(tail))
			tf.close()
			lf = open("logs/id/" + str(menu) + ".txt", "w")
			lf.write(str(LASTID[menu]))
			lf.close()
			fi = open("logs/pos/" + str(menu) + ".txt", "w")
			fi.write(str(lasty))
			fi.write("\n")
			fi.write(str(i))
			fi.close()
		except:
			error(errorwin, 'write logs', 'coudln\'t find them')
			
	elif menu == 0: # debug
		curses.curs_set(True)
		paddic['pad'].addstr(0, 0, 'Controls : q = quit, d = change between integers and strings')
		(y, x) = paddic['pad'].getyx()
		paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
		boxwin = curses.newwin(1, paddic['width'], paddic['begin_y']+y+1, paddic['begin_x'])
		debug(boxwin)
		curses.curs_set(False)
		
	elif menu == 1: # create post
		curses.curs_set(True)
		paddic['pad'].addstr(0, 0, 'Controls : ctrl+g to finish')
		(y, x) = paddic['pad'].getyx()
		paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
		boxwin = curses.newwin(windic['height']-1-y, windic['width']-2, windic['begin_y']+y+1, windic['begin_x']+1)
		box = Textbox(boxwin)
		box.edit()
		message = box.gather()
		paddic['pad'].clear()
		windic['win'].clear()
		paddic['pad'].addstr(0, 0, 'Do you want to publish the following message? [Y/n]')
		(y,x) = paddic['pad'].getyx()
		paddic['pad'].addstr(y+1, 0, message)
		paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
		c = 0
		while c != ord("y") and c != ord("Y") and c != ord("n") and c != ord("N"):
			c = paddic['pad'].getch()
		if c == ord("y") or c == ord("Y"):
			paddic['pad'].clear()
			media = ["", "", "", ""]
			strings = ["medium #1 :", "medium #2 :", "medium #3 :", "medium #4 :", "Done"]
			paddic['pad'].addstr(0, 0, "You can send up to 4 media.")
			for i in range(4):
				paddic['pad'].addstr(i+1, 0, strings[i] + '"' + media[i] + '"')
			paddic['pad'].addstr(5, 0, strings[4])
			y = 0
			paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
			do_run = True
			paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
			stdscr = getattr(t, "stdscr")
			while(do_run):
				#paddic['pad'].addstr(6, 0, 'DEBUG : y = ' + str(y) + ', c = ' + str(c) + "    ")
				c = stdscr.getch()
				if c == curses.KEY_DOWN:
					paddic['pad'].addstr(y+1, 0, strings[y])
					y = (y+1) % 5
					paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
				elif c == curses.KEY_UP:
					paddic['pad'].addstr(y+1, 0, strings[y])
					y = (y-1) % 5
					paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
				elif c == KEY_ENTER:
					if y < 4:
						boxwin = curses.newwin(1, windic['width'] - len(strings[y]) - 2, windic['begin_y']+y+1, windic['begin_x'] + 1 + len(strings[y]))
						boxwin.addstr(0, 0, media[y])
						boxwin.refresh()
						box = Textbox(boxwin)
						box.edit()
						media[y] = box.gather()[:-1]
						paddic['pad'].move(y+1, len(strings[y]))
						paddic['pad'].clrtoeol()
						paddic['pad'].addstr(y+1, len(strings[y]), '"' + media[y] + '"')
					elif y == 4:
						do_run = False
				paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
			mediadics = []
			for m in media:
				if m != "":
					try:
						f = open(m, "r")
						f.close()
						mediadics.append(mastodon.media_post(m))
					except:
						error(errorwin, 'media', m + ' does not exist')
			post = mastodon.status_post(message, media_ids=mediadics)
			
		curses.curs_set(False)
		
	elif menu == 7: # options
		for y in range(len(optionsString)):
			paddic['pad'].addstr(y+1, 0, optionsString[y])
			(a, x) = paddic['pad'].getyx()
			paddic['pad'].addstr(y+1, x+1, options[y], curses.A_REVERSE)
		for x in range(len(options[2])):
			paddic['pad'].addch(3, len(optionsString[2])+x+1, ord('*') , curses.A_REVERSE)

		about = """Please write these credentials in a file called "credentials.txt" in the same folder as this program, in the form:

<instance> (eg https://niu.moe/)
<username> (eg bunni)
<password> (eg MuchPasswordSuch1337)

(I know, it's not very safe, I'm sorry :/)
This program is not yet finished.
Here you can edit stuff (ctrl+g or enter to submit), but it won't change the file because I'm lazy.
I need to sleep.
"""
		paddic['pad'].addstr(5, 0, "About", curses.A_UNDERLINE)
		paddic['pad'].addstr(6, 0, about)

		i = 0
		setattr(t, "y", 0)
		setattr(t, "edit", False)
		paddic['pad'].addstr(i+1, 0, optionsString[i], curses.A_BOLD)
		while getattr(t, "do_run", True):
			paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
			y = getattr(t, "y")
			setattr(t, "y", 0)
			if(getattr(t, "edit")):
				boxwin = curses.newwin(1, windic['width'] - len(optionsString[i]) - 1, windic['begin_y']+i+1, windic['begin_x'] + len(optionsString[i]) + 1)
				boxwin.addstr(0, 0, options[i])
				box = Textbox(boxwin)
				box.edit()
				options[i] = box.gather()[:-1]
				paddic['pad'].move(i+1, len(optionsString[i]))
				paddic['pad'].clrtoeol()
				paddic['pad'].addstr(i+1, len(optionsString[i])+1, options[i], curses.A_REVERSE)
				if i == 2:
					for x in range(len(options[2])):
						paddic['pad'].addch(3, len(optionsString[2])+x+1, ord('*') , curses.A_REVERSE)
				setattr(t, "edit", False)
				
			paddic['pad'].addstr(i+1, 0, optionsString[i])
			i = (i+y) % len(options)
			paddic['pad'].addstr(i+1, 0, optionsString[i], curses.A_BOLD)
			time.sleep(SLEEPTIME)

	else:
		paddic['pad'].addstr(0, 0, "Not yet implemented.")
  			
	paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)

def downloadPosts(menu, mastodon, aascreen, windic, errorwin):
	tl = []
	if menu == 2:
		tl = mastodon.timeline_home(limit=TLLIMIT, since_id=LASTID[menu])
	elif menu == 3:
		tl = mastodon.notifications(limit=TLLIMIT, since_id=LASTID[menu])
	elif menu == 4:
		tl = mastodon.timeline_local(limit=TLLIMIT, since_id=LASTID[menu])
	elif menu == 5:
		tl = mastodon.timeline_public(limit=TLLIMIT, since_id=LASTID[menu])
		
	head = []
	body = []
	tail = []
	c = 0
	for l in tl:
		c += 1
		windic['win'].addstr(0, 0, "loading... (" + str(c) + "/" + str(len(tl)) + ")")
		if c == 1:
			LASTID[menu] = l['id']
		windic['win'].refresh()
		content = ""
		media = []
		mediadesc = []
		debug = []
		if menu != 3:
			if l['spoiler_text'] != "":
				parser.feed(l['spoiler_text'])
				content += parser.get_result_destructively()
				content = "CW : " + content + "\n\n"
			parser.feed(l["content"])
			content += parser.get_result_destructively()
			#content = l
			for e in l["media_attachments"]:
				if e["type"] == "image":
					media.append(e["url"])
					mediadesc.append("Description : " + str(e["description"]))
		else:
			if l["type"] != "follow":
				try:
					if l['status']['spoiler_text'] != "":
						parser.feed(l['status']['spoiler_text'])
						content += parser.get_result_destructively()
						content = "CW : " + content + "\n\n"
					parser.feed(l["status"]["content"])
					content += parser.get_result_destructively()
					content = l["type"] + ":\n" + content
					for e in l["status"]["media_attachments"]:
						if e["type"] == "image":
							media.append(e["url"])
							mediadesc.append("Description : " + str(e["description"]))
				except:
					error(errorwin, "parser feed", "can't read status")
					content = l["type"]
			else:
				content = l["type"]
				
				
		if menu != 3 and l["reblog"] != None:
			head.append(str(l["account"]["display_name"]) +
			            " (@" + str(l["account"]["acct"]) + ")" +
			            " RT " + str(l["reblog"]["account"]["display_name"]) +
			            " (@" + str(l["reblog"]["account"]["acct"]) + ")"
			)
		else:
			head.append(str(l["account"]["display_name"]) +
			            " (@" + str(l["account"]["acct"]) + ")"
			)
		if media != []:
			s = ""
			for i in range(len(media)):
				m = media[i]
				d = mediadesc[i]
				fp = io.BytesIO(urllib.request.urlopen(m).read())
				image = PIL.Image.open(fp).convert('L').resize(aascreen.virtual_size)
				aascreen.put_image((0, 0), image)
				s = s + aascreen.render() + "\n" + d + "\n\n"
			body.append(str(content) + "\n\nmedia : \n\n" + s)
		else:
			body.append(str(content))
		if menu != 3:
			tail.append(str(l['visibility']) + " - " + str(l['created_at'].astimezone().ctime()))
		elif l["type"] != "follow":
			tail.append(str(l['status']['visibility']) + " - " + str(l['created_at'].astimezone().ctime()))
		else:
			tail.append("")
	return (head, body, tail)

def displayPosts(head, body, tail, paddic, windic, overdic, tmp, i, errorwin):
	l = 0
	py = 0
	try:
		for p in range(len(head)):#len(body)):
			try:
				paddic['pad'].addstr(l, max((windic['width']-2)//2 - len(head[p])//2, 0), head[p], curses.A_INVIS)
				(hy, hx) = paddic['pad'].getyx()
				paddic['pad'].addstr(1+hy, 0, body[p])
				(py, px) = paddic['pad'].getyx()
				rectangle(overdic['pad'], hy, 0, py+2, windic['width']-1)
				paddic['pad'].addstr(l, max((windic['width']-2)//2 - len(head[p])//2, 0), head[p], curses.A_BOLD)
				paddic['pad'].addstr(py+1, windic['width']-2-len(tail[p]), tail[p], curses.A_DIM)
				l = py + 3
			except:
				error(errorwin, "displayPosts", "error in loop - p = " + str(p) + " / head : " + str(len(head)) + " / body : " + str(len(body)) + " / tail : " + str(len(tail)))
	except:
		error(errorwin, "displayPosts", "error in loop")
		
	try:
		paddic['pad'].overlay(overdic['pad'])
	except:
		error(errorwin, "displayPosts", "paddic.overlay()")
	try:
		lasty = l
	except:
		error(errorwin, "displayPosts", "error : lasty = l")
	#(lasty, lastx) = paddic['pad'].getyx()
	try:
		if tmp > 0:
			i = lasty - tmp + i
	except:
		error(errorwin, "displayPosts", "error in : if tmp  > 0")
	try:
		return (lasty, i)
	except:
		error(errorwin, "displayPosts", "error in : return (lasty, i)")
		return (0, 0)
	

def createWindowDict(height, width, begin_y, begin_x, title):
	win = curses.newwin(height, width, begin_y, begin_x)
	dic = {
		'height': height,
		'width': width,
		'begin_y': begin_y,
		'begin_x': begin_x,
		'win': win,
		'title': title
		}
	return dic

def createPadDict(height, width, begin_y, begin_x, title):
	pad = curses.newpad(height, width)
	dic = {
		'height': height,
		'width': width,
		'begin_y': begin_y,
		'begin_x': begin_x,
		'pad': pad,
		'title': title
		}
	return dic

def printTitle(stdscr, windic, attribute):
	stdscr.addstr(windic['begin_y']-1, windic['begin_x'] + windic['width']//2 - len(windic['title'])//2, windic['title'], attribute)

def border(stdscr, windic, attribute):
	rectangle(stdscr, windic['begin_y']-1, windic['begin_x']-1, windic['height'] + windic['begin_y'], windic['width'] + windic['begin_x'])
	printTitle(stdscr, windic, attribute)
	return

def debug(box):
	text = 'Key : '
	y = 0
	x = len(text)
	# getch (int)
	while True:
		c = box.getch()
		box.clear()
		box.addstr(0, 0, text)
		try:
			box.addstr(y, x, str(c))
		except:
			box.addstr(0, 0, "ERROR")
		box.refresh()
		if c == ord('q'):
			return
		elif c == ord('d'):
			break
	# getkey (string)
	while True:
		c = box.getkey()
		box.clear()
		box.addstr(0, 0, text)
		try:
			box.addstr(y, x, c)
		except:
			box.addstr(0, 0, "ERROR")
		box.refresh()
		if c == 'q':
			return
		if c == 'd':
			return debug(box)

def checkWindows(dictlist):
	for dic in dictlist:
		for y in range(dic['height']):
			for x in range(dic['width']):
				if not (x == dic['width']-1 and y == dic['height']-1):
					dic['win'].addch(y, x, ord('a') + (x+y) % 26)

def refresh(windows, strings, cury):
	windows[0].redrawwin()
	windows[0].refresh()
	for w in windows[1:]:
		w['win'].redrawwin()
		w['win'].refresh()
						
def main(stdscr):
	# Clear screen
	stdscr.clear()
	curses.curs_set(False)

	#menu = 0, main = 1
	curwin = 0
	cury = 2
	
	menuString = (
		'Debug',
		'New Post',
		'Home',
		'Notifications',
		'Local',
		'Public',
		'Profile',
		'Options/About'
	)

	keysString = (
		'q : quit',
		'enter/right : ok',
		'backspace/left : return',
		'up/down : navigation',
		'r : redraw'
		)
	strings = (menuString, keysString)
	tmp = 0
	for L in (menuString, keysString):
		for s in L:
			tmp = max(tmp, len(s))

	# createWindowDict(height, width, y, x, title)
	menuwin = createWindowDict(len(menuString), tmp, 1, 1, 'Menu')
	keyswin = createWindowDict(len(keysString), tmp, menuwin['begin_y'] + menuwin['height'] +2, 1, 'Global Keys')
	errorwin = createWindowDict(max(2, curses.LINES - (keyswin['begin_y'] + keyswin['height'] + 4)), tmp, keyswin['begin_y'] + keyswin['height'] + 2, 1, 'Error Messages')
	tmp = (1, menuwin['width']+3)
	mainwin = createWindowDict(curses.LINES - (tmp[0] + 2), curses.COLS - (tmp[1] + 1), tmp[0], tmp[1], menuString[cury])
	mainpad = createPadDict(PADHEIGHT, curses.COLS - (tmp[1] + 3), tmp[0], tmp[1]+1, menuString[cury])
	overlaypad = createPadDict(PADHEIGHT, curses.COLS - (tmp[1] + 1), tmp[0], tmp[1]+1, menuString[cury])

	windows = (stdscr, menuwin, keyswin, errorwin)

	for i in range(len(menuString)):
		menuwin['win'].addstr(i, 0, menuString[i])
	for i in range(len(keysString)):
		keyswin['win'].addstr(i, 0, keysString[i])

	menuwin['win'].addstr(cury, 0, menuString[cury], curses.A_BOLD)
		
	border(stdscr, menuwin, curses.A_BOLD)
	border(stdscr, mainwin, curses.A_NORMAL)
	border(stdscr, keyswin, curses.A_NORMAL)
	border(stdscr, errorwin, curses.A_NORMAL)

	stdscr.refresh()
	
	x = threading.Thread(target=boot, args=(mainpad, mainwin), daemon=True)
	x.start()

	(instance, username, password) = options
	mastodon = 0
#	listener = StreamListener()
	userstream = 0
	publicstream = 0
	localstream = 0
				
	try:		
		mastodon = login(instance, username, password)
	except:
		error(errorwin, 'login', "didn't work")
#	try:
		userstream   = mastodon.stream_user(  listener, run_async=True, timeout=300, reconnect_async=True, reconnect_async_wait_sec=5)
#		publicstream = mastodon.stream_public(listener, run_async=True, timeout=300, reconnect_async=True, reconnect_async_wait_sec=5)
#		localstream  = mastodon.stream_local( listener, run_async=True, timeout=300, reconnect_async=True, reconnect_async_wait_sec=5)
#	except:
#		error(errorwin, 'streaming', "didn't work")
	x.do_run = False
	x.join()

	stdscr.refresh()
	menuwin['win'].refresh()
	mainpad['pad'].refresh(0, 0, mainwin['begin_y'], mainwin['begin_x'], mainwin['height'], mainwin['width'] + mainwin['begin_x'])
	keyswin['win'].refresh()
	errorwin['win'].refresh()
	while True:
		c = stdscr.getch()
		# general
		if c == ord('q'):
			try:
				x.do_run = False
				x.join()
			except:
				pass
			break
		elif c == ord('r'):
			refresh(windows, strings, cury)
		elif curwin == 0:
			# menu
			menuwin['win'].addstr(cury, 0, menuString[cury])
			if c == curses.KEY_UP:
				cury = (cury - 1) % len(menuString)
			elif c == curses.KEY_DOWN:
				cury = (cury + 1) % len(menuString)
			elif c == curses.KEY_RIGHT or c == KEY_ENTER: # 10 : newline
				try:
					x.do_run = False
					x.join()
				except:
					error(errorwin, "Menu", "Thread doesn't exist")
				
				curwin += 1
				mainpad['pad'].clear()
				mainwin['title'] = menuString[cury]
				mainpad['title'] = menuString[cury]
				printTitle(stdscr, menuwin, curses.A_NORMAL)
				border(stdscr, mainwin, curses.A_BOLD)
				stdscr.refresh()
				x = threading.Thread(target=thread_function, args=(cury, mainpad, mainwin, overlaypad, errorwin), daemon=True)
				x.start()
				x.mastodon = mastodon
				if cury == 0 or cury == 1: # keybindings disabled for good reasons
					printTitle(stdscr, keyswin, curses.A_DIM)
					stdscr.refresh()
					x.stdscr = stdscr
					x.join()
					printTitle(stdscr, keyswin, curses.A_NORMAL)
					curwin -= 1
					printTitle(stdscr, menuwin, curses.A_BOLD)
					border(stdscr, mainwin, curses.A_NORMAL)
				elif cury >= 2 and cury <= 5:
					x.userstream = userstream
					x.listener = listener
			menuwin['win'].addstr(cury, 0, menuString[cury], curses.A_BOLD)
		elif curwin == 1:
			# main
			if c == curses.KEY_LEFT or c == KEY_BACKSPACE:
				curwin -= 1
				printTitle(stdscr, menuwin, curses.A_BOLD)
				printTitle(stdscr, mainpad, curses.A_NORMAL)
			elif c == curses.KEY_DOWN:
				x.y = 1
			elif c == curses.KEY_UP:
				x.y = -1
			elif c == curses.KEY_NPAGE:
				x.y = mainwin['height']
			elif c == curses.KEY_PPAGE:
				x.y = -mainwin['height']
			elif c == curses.KEY_HOME:
				x.y = -mainpad['height']
			elif c == curses.KEY_END:
				x.y = mainpad['height']
			elif cury == 7 and (c == curses.KEY_RIGHT or c == KEY_ENTER):
				x.edit = True
				printTitle(stdscr, keyswin, curses.A_DIM)
				stdscr.refresh()
				while(x.edit):
					time.sleep(SLEEPTIME)
				printTitle(stdscr, keyswin, curses.A_NORMAL)
			elif c == curses.KEY_RIGHT or c == KEY_ENTER:
				x.enter = True
		else:
			error(errorwin, 'main loop', 'end of else')

		stdscr.refresh()
		if curwin == 0:
			menuwin['win'].refresh()
		
			
if GOODINIT:
	wrapper(main)
