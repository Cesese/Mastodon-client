#!/bin/python3

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

import logging
import threading
import time
try:
	from mastodon import Mastodon
	from mastodon import StreamListener
except:
	from dependencies.mastodon import Mastodon
	from dependencies.mastodon import StreamListener

from html.parser import HTMLParser

import io
import urllib
import PIL.Image
try:
	import aalib
except:
	from dependencies import aalib

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
		media = self.media
		self.postContent = ""
		self.media = []
		self.debug = []
		return (postContent, [])
	
	def handle_starttag(self, tag, attrs):
		pass
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

MINX = 62
MINY = 25
KEY_ENTER = 10
KEY_BACKSPACE = 127
curses.KEY_BACKSPACE = KEY_BACKSPACE
SLEEPTIME = 0.05
TIMERLOOPS = 20
PADHEIGHT = 16384
GOODINIT = True
TLLIMIT = None
POSTLIMIT = 100
TIMERTOP = 100
TIMERBODY = 10000
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

def create_app(name, url):
	Mastodon.create_app(
		name,
		api_base_url = url,
		to_file = 'niuclient_clientcred.secret'
	)

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

def breakpoint(errorwin, a):
	errorwin['win'].clear()
	errorwin['win'].addstr(0, 0, "Break point")
	errorwin['win'].addstr(1, 0, a)
	errorwin['win'].refresh()
	time.sleep(1)



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
		setattr(t, "backspace", False)
		(head, body, tail, idlist) = ([], [], [], [])
		lasty = 0
		i = 0
		pos = 0
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
			idf = open("logs/"+str(menu)+"/ids.txt", "r")
			idlist = idf.read()
			idlist = ast.literal_eval(idlist)
			idf.close()
			
			pf = open("logs/pos/" + str(menu) + ".txt", "r")
			tmp = []
			for l in pf:
				tmp.append(l)
			pf.close()
			lasty = int(tmp[0])
			pos = int(tmp[1])
		except:
			error(errorwin, 'read logs', "coudln't find them (normal if first time)")

		if len(head) != len(body) or len(body) != len(tail) or len(tail) != len(idlist):
			breakpoint(errorwin, "error : " + str(len(head)) + "!=" + str(len(body)) + "!=" + str(len(tail)) + "!=" + str(len(idlist)))
		updated = False
		timer = 100
		tmp = lasty
		posts = []
		posb = max(len(head) - POSTLIMIT, 0)
		(lasty, posts) = displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin)
		if len(posts) > 0:
			posb = max(len(head) - POSTLIMIT, 0)
			i = posts[pos][1]
			if i > lasty - windic['height']:
				i = lasty - windic['height']
			elif i < 0:
				i = 0
			
		overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])

		(lasty, posts) = displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin)
		if len(posts) > 0:
			try:
				sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_REVERSE)
				paddic['pad'].overlay(overdic['pad'])
			except:
				error(errorwin, "TL loop", "pos = " + str(pos) + ", posb = " + str(posb))
		overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
		
		while getattr(t, "do_run", True):
			timer += 1
			if(i == 0 and timer >= TIMERTOP):
				#breakpoint(errorwin, "beginning")
				timer = 0
				try:
					tmp = lasty
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
					#breakpoint(errorwin, "before download posts")
					(nhead, nbody, ntail, nidlist) = downloadPosts(menu, mastodon, aascreen, windic, errorwin)
					#breakpoint(errorwin, "after download posts")
					head = nhead + head
					tail = ntail + tail
					body = nbody + body
					idlist = nidlist + idlist
					#breakpoint(errorwin, "before posts to delete")
					posts_to_delete = min(len(head), 2*POSTLIMIT-1) - POSTLIMIT # could be '- min(len(head), POSTLIMIT)' so I wouldn't need the max later, but that would be less readable
					posts_to_delete = max(posts_to_delete, 0) # -1 because I want to keep the last read post (else the user might feel lost, and we couldn't see if something went wrong)
					#breakpoint(errorwin, "posts to delete : " + str(posts_to_delete))
					newnum = posts_to_delete
					if newnum == 0:
						newnum = len(nhead)
						if len(head) == len(nhead):
							newnum -= 1
					pos = newnum
					#breakpoint(errorwin, "before delete : head = " + str(head))
					if posts_to_delete > 0:
						head = head[:-posts_to_delete]
						body = body[:-posts_to_delete]
						tail = tail[:-posts_to_delete]
						idlist = idlist[:-posts_to_delete]
					#breakpoint(errorwin, "after posts to delete")
					#breakpoint(errorwin, "after delete : head = " + str(head))
					
					""" end of messy part """
					if len(nhead) > 0:
						updated = True
						paddic['pad'].clear()
						overdic['pad'].clear()
						error(errorwin, "New posts!", str(time.ctime()) + "\n" + str(len(nhead)) + " new posts")
						try:
							(lasty, posts) = displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin)
							posb = max(len(head) - POSTLIMIT, 0)
							sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_REVERSE)
							paddic['pad'].overlay(overdic['pad'])
						except:
							error(errorwin, 'displayPosts', "didn't work :/ i=" + str(i) + " ; tmp=" + str(tmp))
							lasty = tmp
					else:
						if updated:
							updated = False
							error(errorwin, "", "")
				except:
					error(errorwin, "Thread function", "Download or Display error")
					i = 1
			elif timer >= TIMERBODY:
				timer = 0
				try:
					#breakpoint(errorwin, "before download posts")
					(nhead, nbody, ntail, nidlist) = downloadPosts(menu, mastodon, aascreen, windic, errorwin)
					#breakpoint(errorwin, "after download posts")
					head = nhead + head
					tail = ntail + tail
					body = nbody + body
					idlist = nidlist + idlist
					tmp = posb
					posb = max(len(head) - POSTLIMIT, 0)
					error(errorwin, "Download successful", "Current number of posts in database : " + str(len(head)) + " / " + str(POSTLIMIT))
					#breakpoint(errorwin, "posb " + str(posb) + " == tmp " + str(tmp) + "?")
					#breakpoint(errorwin, "len(nhead) " + str(len(nhead)) + " != 0?")
					#if posb == tmp and len(nhead) != 0:
					if len(nhead) > 0:
						updated = True
						paddic['pad'].clear()
						overdic['pad'].clear()
						pos += len(nhead) - (posb - tmp)
						#breakpoint(errorwin, "new pos : " + str(pos))
						try:
							(lasty, posts) = displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin)
							sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_REVERSE)
							paddic['pad'].overlay(overdic['pad'])
						except:
							error(errorwin, 'displayPosts', "didn't work :/ i=" + str(i) + " ; tmp=" + str(tmp))
							lasty = tmp
					else:
						if updated:
							updated = False
							error(errorwin, "", "")
				except:
					error(errorwin, "downloadPosts", "timer >= 10000")
			"""
			elif timer % 100 == 0:
				error(errorwin, 'displayTimer', 'timer : ' + str(timer * 100 / 10000.0) + '%')
			if timer == 0:
				breakpoint(errorwin, "pos : " + str(pos))
			"""
			y = getattr(t, "y")
			setattr(t, "y", 0)
			if y != 0:
				paddic['pad'].clear()
				try:
					sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_BOLD)
				except:
					error(errorwin, "TL loop", "pos = " + str(pos) + ", posb = " + str(posb))
				pos = (pos + y)
				if pos >= len(posts):
					pos = len(posts)-1
				if pos < 0:
					pos = 0
				try:
					sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_REVERSE)
				except:
					error(errorwin, "TL loop", "pos = " + str(pos) + ", posb = " + str(posb))
			try:
				i = posts[pos][1]
				if i > lasty - windic['height']:
					i = lasty - windic['height']
				elif i < 0:
					i = 0
			except:
				error(errorwin, "thread loop", "posts[pos][1] out of range")
				i = 0
				pos = 0

			if getattr(t, "backspace"):
				setattr(t, "backspace", False)
					
			if getattr(t, "enter"):
				setattr(t, "enter", False)
				openPost(mastodon, t, posts[pos][0], head[posb+pos], body[posb+pos], tail[posb+pos], paddic, windic, overdic, errorwin, menu)
				(lasty, posts) = displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin)
				try:
					sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, curses.A_REVERSE)
				except:
					error(errorwin, "TL loop", "pos = " + str(pos) + ", posb = " + str(posb))
				paddic['pad'].overlay(overdic['pad'])
					
			if y != 0:
				paddic['pad'].overlay(overdic['pad'])
			overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
			time.sleep(SLEEPTIME)
		try:
			#breakpoint(errorwin, "quit : head = " + str(head))
			hf = open("logs/"+str(menu)+"/head.txt", "w")
			hf.write(str(head))
			hf.close()
			bf = open("logs/"+str(menu)+"/body.txt", "w")
			bf.write(str(body))
			bf.close()
			tf = open("logs/"+str(menu)+"/tail.txt", "w")
			tf.write(str(tail))
			tf.close()
			idf = open("logs/"+str(menu)+"/ids.txt", "w")
			idf.write(str(idlist))
			idf.close()
			lf = open("logs/id/" + str(menu) + ".txt", "w")
			lf.write(str(LASTID[menu]))
			lf.close()			
			pf = open("logs/pos/" + str(menu) + ".txt", "w")
			pf.write(str(lasty))
			pf.write("\n")
			pf.write(str(pos))
			pf.close()
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
		(errors, message, mediadics) = newPost(t, paddic, windic, "")
		if getattr(t, "do_run", True) and not errors:
			paddic['pad'].addstr(0, 0, 'Do you want to publish the following message with ' + str(len(mediadics)) + " media?")
			(y,x) = paddic['pad'].getyx()
			paddic['pad'].addstr(y+1, 0, message)
			paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
			while not(getattr(t, "enter", False) or getattr(t, "backspace", False)) and getattr(t, "do_run", True):
				time.sleep(SLEEPTIME)
			if getattr(t, "enter", False):
				post = mastodon.status_post(message, media_ids=mediadics)
		elif getattr(t, "do_run", True) and errors:
			paddic['pad'].addstr(0, 0, 'Aborting, there was an error.')
			paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
			time.sleep(3)
			
		
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

	windic['win'].clear()
	paddic['pad'].clear()
	#paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
	windic['win'].refresh()

def downloadPosts(menu, mastodon, aascreen, windic, errorwin):
	head = []
	body = []
	tail = []
	idlist = []
	nfirstid = None
	flastid = LASTID[menu]
	tl = []
	tmp = ["Start"]
	while tmp != []:
		#breakpoint(errorwin, "lastid = " + str(flastid) + "\nfirstid = " + str(nfirstid))
		if menu == 2:
			tmp = mastodon.timeline_home(limit=TLLIMIT, since_id=flastid, max_id=nfirstid)
		elif menu == 3:
			tmp = mastodon.notifications(limit=TLLIMIT, since_id=flastid, max_id=nfirstid)
		elif menu == 4:
			tmp = mastodon.timeline_local(limit=TLLIMIT, since_id=flastid, max_id=nfirstid)
		elif menu == 5:
			tmp = mastodon.timeline_public(limit=TLLIMIT, since_id=flastid, max_id=nfirstid)
		tl = tl + tmp
		if flastid == None:
			tmp = []
		if tmp != []:
			nfirstid = tmp[-1]['id']
	
	c = 0
	for l in tl:
		idlist.append(l['id'])
		c += 1
		error(errorwin, "loading...", str(c) + "/" + str(len(tl)))
		if c == 1:
			LASTID[menu] = l['id']
		content = ""
		media = []
		mediadesc = []
		debug = []
		try:
			if menu != 3:
				if l['spoiler_text'] != "":
					parser.feed(l['spoiler_text'])
					(content, media) = parser.get_result_destructively()
					content = "CW : " + content + "\n\n"
				parser.feed(l["content"])
				(tmp, media) = parser.get_result_destructively()
				for m in media:
					mediadesc.append("Description : None")
				content = content + tmp
				for e in l["media_attachments"]:
					if e["type"] == "image":
						media.append(e["url"])
						mediadesc.append("Description : " + str(e["description"]))
			else:
				if l["type"] != "follow":
					if l['status']['spoiler_text'] != "":
						parser.feed(l['status']['spoiler_text'])
						(content, media) = parser.get_result_destructively()
						content = "CW : " + content + "\n\n"
					parser.feed(l["status"]["content"])
					(tmp, media) = parser.get_result_destructively()
					for m in media:
						mediadesc.append("Description : None")
					content = l["type"] + ":\n" + content + tmp
					for e in l["status"]["media_attachments"]:
						if e["type"] == "image":
							media.append(e["url"])
							mediadesc.append("Description : " + str(e["description"]))
				else:
					content = l["type"]
		except:
			error(errorwin, "parser feed", "can't read status")
				
				
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
		try:
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
		except:
			breakpoint(errorwin, "Error with media " + str(i) + " : " + media[i])
			body.append(str(content))

		if menu != 3:
			tail.append(str(l['visibility']) + " - " + str(l['created_at'].astimezone().ctime()))
		elif l["type"] != "follow":
			tail.append(str(l['status']['visibility']) + " - " + str(l['created_at'].astimezone().ctime()))
		else:
			tail.append(str(l['created_at'].astimezone().ctime()))
	return (head, body, tail, idlist)

def sublimeHead(t, paddic, windic, overdic, posts, pos, posb, head, sublime):
	paddic['pad'].addstr(posts[pos][1], max((windic['width']-2)//2 - len(head[posb+pos])//2, 0), head[posb+pos], sublime)
	(py, px) = paddic['pad'].getyx()
	if px == 0:
		px = 1
	tmp = [posts[pos][1], max((windic['width']-2)//2 - len(head[posb+pos])//2+1, 1)]
	while getattr(t, "do_run", True) and (tmp[0] != py or tmp[1] != px):
		if tmp[0] != py:
			s = " "
		else:
			s = "─"
		overdic['pad'].addstr(tmp[0], tmp[1], s, sublime)
		tmp[1] += 1
		if tmp[1] >= windic['width']-1:
			tmp[1] = 1
			tmp[0] += 1
	paddic['pad'].addstr(posts[pos][1], max((windic['width']-2)//2 - len(head[posb+pos])//2, 0), head[posb+pos], sublime)

def displayPosts(head, body, tail, idlist, paddic, windic, overdic, errorwin):
	paddic['pad'].clear()
	overdic['pad'].clear()
	l = 0
	py = 0
	posts = []
	end = len(head)
	begin = max(end - POSTLIMIT, 0)
	for p in range(begin, end):#len(body)):
		try:
			posts.append((idlist[p],l)) 
			paddic['pad'].addstr(l, max((windic['width']-2)//2 - len(head[p])//2, 0), head[p], curses.A_INVIS)
			(hy, hx) = paddic['pad'].getyx()
			paddic['pad'].addstr(1+hy, 0, body[p])
			(py, px) = paddic['pad'].getyx()
			rectangle(overdic['pad'], hy, 0, py+2, windic['width']-1)
			paddic['pad'].addstr(l, max((windic['width']-2)//2 - len(head[p])//2, 0), head[p], curses.A_BOLD)
			try:
				paddic['pad'].addstr(py+1, windic['width']-2-len(tail[p]), tail[p], curses.A_DIM)
			except:
				error(errorwin, "displayPosts", "tail empty for post " + str(p-begin+1))
			paddic['pad'].addstr(py+1, 0, str(p-begin+1)+"/"+str(end-begin), curses.A_DIM)
			l = py + 3
			#posts.append((idlist[p],l))
		except:
			error(errorwin, "displayPosts", "error in loop - p = " + str(p))# + " / begin = " + str(begin) + " / newnum : " + str(newnum) + " / head : " + str(len(head)) + " / body : " + str(len(body)) + " / tail : " + str(len(tail)) + " / lasty : " + str(l) + "\nhead : " + head[p] + "\nbody : " + body[p] + "\ntail : " + tail[p])
		
	paddic['pad'].overlay(overdic['pad'])
	lasty = l
	#(lasty, lastx) = paddic['pad'].getyx()
	return (lasty, posts)

def openPost(mastodon, t, ID, head, body, tail, paddic, windic, overdic, errorwin, menu):
	do_run_local = True
	i = 0
	j = 0
	(lasty, posts) = displayPosts([head], [body], [tail], [ID], paddic, windic, overdic, errorwin)
	while getattr(t, "do_run", True) and do_run_local:
		y = getattr(t, "y")
		setattr(t, "y", 0)
		i = (i + y)
		if i > lasty - windic['height']:
			i = lasty - windic['height']
		elif i < 0:
			i = 0
		if getattr(t, "backspace"):
			setattr(t, "backspace", False)
			do_run_local = False
		if getattr(t, "enter"):
			setattr(t, "enter", False)
			interactPost(mastodon, t, ID, paddic, windic, menu)
		overdic['pad'].refresh(i, 0, windic['begin_y'], windic['begin_x'], windic['height'], windic['width'] + windic['begin_x'])
		time.sleep(SLEEPTIME)

def interactPost(mastodon, t, ID, paddic, windic, menu):
	do_run_local = True
	o = 0
	options = [
		"reply",
		"boost",
		"favourite"
		]
	if menu != 3:
		post = mastodon.status(ID)
	else:
		post = mastodon.notifications(id=ID)['status']
		ID = post['id']
	if post["reblogged"]:
		options[1] = "un" + options[1]
	if post["favourited"]:
		options[2] = "un" + options[2]
	
	windic['win'].clear()
	windic['win'].addstr(0, 0, "Post ID : " + str(ID))
	for i in range(len(options)):
		windic['win'].addstr(i+2, 0, options[i])
	while getattr(t, "do_run", True) and do_run_local:
		windic['win'].addstr(o+2, 0, options[o] + "  ")
		y = getattr(t, "y")
		setattr(t, "y", 0)
		if y > 1 or y < -1:
			y = 0
		o = (o + y) % len(options)
		windic['win'].addstr(o+2, 0, options[o] + "  ", curses.A_BOLD)
		if getattr(t, "backspace"):
			setattr(t, "backspace", False)
			do_run_local = False
		if getattr(t, "enter"):
			setattr(t, "enter", False)
			if o == 0:
				(errors, message, mediadics) = newPost(t, paddic, windic, "")
				if getattr(t, "do_run", True) and not errors:
					paddic['pad'].addstr(0, 0, 'Do you want to publish the following message with ' + str(len(mediadics)) + " media?")
					(y,x) = paddic['pad'].getyx()
					paddic['pad'].addstr(y+1, 0, message)
					paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
					while not(getattr(t, "enter", False) or getattr(t, "backspace", False)) and getattr(t, "do_run", True):
						time.sleep(SLEEPTIME)
					if getattr(t, "enter", False):
						mastodon.status_reply(to_status=post, status=message, media_ids=mediadics)
					elif getattr(t, "do_run", True) and errors:
						paddic['pad'].addstr(0, 0, 'Aborting, there was an error.')
						paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
						time.sleep(3)
				setattr(t, "enter", False)
				setattr(t, "backspace", False)
				windic['win'].clear()
				windic['win'].addstr(0, 0, "Post ID : " + str(ID))
				for i in range(len(options)):
					windic['win'].addstr(i+2, 0, options[i])
			elif o == 1:
				if post["reblogged"]:
					post["reblogged"] = False
					mastodon.status_unreblog(ID)
					options[1] = options[1][2:]
				else:
					post["reblogged"] = True
					mastodon.status_reblog(ID)
					options[o] = "un" + options[o]
			elif o == 2:
				if post["favourited"]:
					post["favourited"] = False
					mastodon.status_unfavourite(ID)
					options[o] = options[o][2:]
				else:
					post["favourited"] = True
					mastodon.status_favourite(ID)
					options[o] = "un" + options[o]
			
		windic['win'].refresh()
		time.sleep(SLEEPTIME)
			
	windic['win'].clear()

def newPost(t, paddic, windic, s):
	windic['win'].clear()
	windic['win'].addstr(0, 0, "Press any key to start (One day we won't need that, but right now I have other priorities)")
	windic['win'].refresh()
	setattr(t, "edit", True)
	while not(getattr(t, "sleep", False)):
		time.sleep(SLEEPTIME)
	curses.curs_set(True)
	windic['win'].clear()
	windic['win'].refresh()
	paddic['pad'].addstr(0, 0, 'Controls : ctrl+g to finish')
	(y, x) = paddic['pad'].getyx()
	paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
	boxwin = curses.newwin(windic['height']-1-y, windic['width']-2, windic['begin_y']+y+1, windic['begin_x']+1)
	boxwin.addstr(0, 0, s)
	box = Textbox(boxwin)
	if getattr(t, "do_run", True):
		box.edit()
	setattr(t, "edit", False)
	message = box.gather()
	paddic['pad'].clear()
	windic['win'].clear()
	paddic['pad'].clear()
	media = ["/home/username/Pictures/", "", "", "", ""] # not sure how to make it work with ~. Anyway that will change cause it's only good for linux
	strings = ["directory : ", "medium #1 : ", "medium #2 : ", "medium #3 : ", "medium #4 : ", "Done "]
	paddic['pad'].addstr(0, 0, "You can send up to 4 media.")
	for i in range(len(strings)-1):
		paddic['pad'].addstr(i+1, 0, strings[i] + '"' + media[i] + '"')
	paddic['pad'].addstr(len(strings), 0, strings[len(strings)-1])
	y = 0
	paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
	do_run = True
	paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
	while(getattr(t, "do_run", True) and do_run):
		#paddic['pad'].addstr(6, 0, 'DEBUG : y = ' + str(y) + ', c = ' + str(c) + "    ")
		c = getattr(t, "y", 0)
		setattr(t, "y", 0)
		if c == 1:
			paddic['pad'].addstr(y+1, 0, strings[y])
			y = (y+1) % len(strings)
			paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
		elif c == -1:
			paddic['pad'].addstr(y+1, 0, strings[y])
			y = (y-1) % len(strings)
			paddic['pad'].addstr(y+1, 0, strings[y], curses.A_BOLD)
		elif getattr(t, "enter", False):
			setattr(t, "enter", False)
			if y < 5:
				boxwin = curses.newwin(1, windic['width'] - len(strings[y]) - 2, windic['begin_y']+y+1, windic['begin_x'] + 1 + len(strings[y]))
				boxwin.addstr(0, 0, media[y])
				boxwin.refresh()
				setattr(t, "edit", True)
				box = Textbox(boxwin)
				box.edit()
				setattr(t, "edit", False)
				media[y] = box.gather()[:-1]
				if y == 0 and len(media[y]) > 0 and  media[y][-1] != "/":
					media[y] = media[y] + "/"
				paddic['pad'].move(y+1, len(strings[y]))
				paddic['pad'].clrtoeol()
				paddic['pad'].addstr(y+1, len(strings[y]), '"' + media[y] + '"')
			elif y == 5:
				do_run = False
		paddic['pad'].refresh(0, 0, windic['begin_y'], windic['begin_x']+1, windic['height'], windic['width'] + windic['begin_x'] - 2)
	mediadics = []
	errors = False
	for i in range(1, len(media)):
		m = media[i]
		if m != "":
			try:
				f = open(media[0]+m, "r")
				f.close()
				mediadics.append(mastodon.media_post(media[0]+m))
			except:
				error(errorwin, 'media', media[0]+m + ' does not exist')
				errors = True
			

	paddic['pad'].clear()
	curses.curs_set(False)
	return (errors, message, mediadics)
	
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
	for w in windows:
		try:
			w['win'].redrawwin()
			w['win'].refresh()
		except:
			try:
				w.redrawwin()
				w.refresh()
			except:
				pass
						
def main(stdscr):
	if MINY > curses.LINES or MINX > curses.COLS:
		return "Your window is too small. Minimum : " + str(MINX) + "x" + str(MINY) + ", Current : " + str(curses.COLS) + "x" + str(curses.LINES)

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
		'enter/backspace : yes/no',
		'left/right : change window',
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
	errorwin = createWindowDict(max(2, curses.LINES - (keyswin['begin_y'] + keyswin['height'] + 4)), tmp, keyswin['begin_y'] + keyswin['height'] + 2, 1, 'Debug Messages')
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
		try:
			if x.edit:
				x.sleep = True
				while x.edit:
					time.sleep(SLEEPTIME)
				x.sleep = False
		except:
			pass
		c = stdscr.getch()
		# general
		if c == ord('q'):
			try:
				x.do_run = False
				x.sleep = True
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
			elif c == KEY_ENTER: # 10 : newline
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
				if cury == 0: # keybindings disabled for good reasons
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
			elif c == curses.KEY_RIGHT:
				curwin += 1
				printTitle(stdscr, mainpad, curses.A_BOLD)
				printTitle(stdscr, menuwin, curses.A_NORMAL)
			elif c == curses.KEY_BACKSPACE:
				try:
					x.do_run = False
					x.join()
					mainwin['win'].clear()
					mainwin['win'].refresh()
				except:
					pass
			menuwin['win'].addstr(cury, 0, menuString[cury], curses.A_BOLD)
		elif curwin == 1:
			# main
			if c == curses.KEY_LEFT:
				curwin -= 1
				printTitle(stdscr, menuwin, curses.A_BOLD)
				printTitle(stdscr, mainpad, curses.A_NORMAL)
			elif c == curses.KEY_DOWN:
				x.y = 1
			elif c == curses.KEY_UP:
				x.y = -1
			elif c == curses.KEY_NPAGE:
				x.y = 10
			elif c == curses.KEY_PPAGE:
				x.y = -10
			elif c == curses.KEY_HOME:
				x.y = -POSTLIMIT
			elif c == curses.KEY_END:
				x.y = POSTLIMIT
			elif cury == 7 and c == KEY_ENTER:
				x.edit = True
				printTitle(stdscr, keyswin, curses.A_DIM)
				stdscr.refresh()
				while(x.edit):
					time.sleep(SLEEPTIME)
				printTitle(stdscr, keyswin, curses.A_NORMAL)
			elif c == KEY_ENTER:
				x.enter = True
			elif c == KEY_BACKSPACE:
				x.backspace = True
		else:
			error(errorwin, 'main loop', 'end of else')

		stdscr.refresh()
		if curwin == 0:
			menuwin['win'].refresh()
		if curwin < 0 or curwin > 1:
			error(errorwin, "main loop", "curwin = " + str(curwin))
		
			
if GOODINIT:
	print(wrapper(main))
	
