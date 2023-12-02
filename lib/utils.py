import base64
import hashlib
import json
import math
import os
import platform
import random
import re
import string
import argparse
from cryptography.fernet import Fernet
from aiohttp import web
from .wizard import setup_wizard

# Candy
welcomes = ["Hello", "Hi", "Hey"]
greetings = ["How are you doing?", "Good to see you again.", "How are things?", "Librusik is awesome, isn't it?", "Too lazy to log into Synergia? :D", "Have a wonderful day!", "Nice to see you.", "Synergia still sucks? :D"]


# Data location
PATH = os.getcwd()
DATA_DIR = os.path.join(PATH, "data")
PROFILE_PIC_DIR = "%s/profile_pics" % DATA_DIR


# Some constant globals
ERR_403 = "Couldn't fetch data from Synergia."
ERR_500 = "Server wasn't able to parse this request."

# Some dynamic globals
LAST_SEEN_PEPS = {}


# Host information
uname = platform.uname()
host = {
	"os": uname.system,
	"node": uname.node,
	"version": platform.python_version(),
	"cpus": os.cpu_count()
}


# Core functions
def setup(CONFIG_DEFAULT):
	first_run = not os.path.exists(DATA_DIR)
	if not first_run:
		config = json.loads(open("%s/config.json" % DATA_DIR, "r").read())
		for key in CONFIG_DEFAULT:
			if key not in config:
				config[key] = CONFIG_DEFAULT[key]
		database = json.loads(open("%s/database.json" % DATA_DIR, "r").read())
	else:
		parser = argparse.ArgumentParser()
		parser.add_argument("--skip-wizard", action="store_true", default=False, help="Skip setup wizard on first run")
		args = parser.parse_args()
		new_config = CONFIG_DEFAULT

		if not args.skip_wizard:
			# Start setup wizard
			ip, port = setup_wizard()
			new_config["listen_address"] = ip
			new_config["port"] = port
		else:
			print("Seems it is the first run. Initializing data...")

		os.mkdir(DATA_DIR)
		os.mkdir(PROFILE_PIC_DIR)
		conf = open("%s/config.json" % DATA_DIR, "w")
		conf.write(json.dumps(new_config, indent = 4))
		conf.close()
		config = new_config
		db = open("%s/database.json" % DATA_DIR, "w")
		db.write(json.dumps({}))
		db.close()
		database = {}
		k = open("%s/fernet.key" % DATA_DIR, "w")
		k.write(base64.urlsafe_b64encode(os.urandom(32)).decode())
		k.close()
		os.chmod("%s/fernet.key" % DATA_DIR, 0o400)
	load_encryption_keys()
	return (config, database)

def load_html_resources(config):
    return {
        "index": open("html/index.html", "r").read(),
        "home": open("html/home.html", "r").read(),
        "grades": open("html/grades.html", "r").read(),
        "more": open("html/more.html", "r").read(),
        "timetable": open("html/timetable.html", "r").read(),
        "messages": open("html/messages.html", "r").read(),
        "message": open("html/message.html", "r").read(),
        "attendances": open("html/attendances.html", "r").read(),
        "attendancesold": open("html/attendancesold.html", "r").read(),
        "exams": open("html/exams.html", "r").read(),
        "freedays": open("html/freedays.html", "r").read(),
        "teacherfreedays": open("html/teacherfreedays.html", "r").read(),
        "parentteacherconferences": open("html/parentteacherconferences.html", "r").read(),
        "school": open("html/school.html", "r").read(),
        "settings": open("html/settings.html", "r").read(),
        "login": open("html/login.html", "r").read(),
        "about": open("html/about.html", "r").read(),
        "tiers": open("html/tiers.html", "r").read(),
        "panel": open("html/panel.html", "r").read(),
        "panellogin": open("html/panellogin.html", "r").read(),
        "error": open("html/error.html", "r").read(),
        "errorpage": open("html/geterror.html", "r").read(),
    }


# Encryption & passwords
frt = None
def load_encryption_keys():
	global frt
	key = open("%s/fernet.key" % DATA_DIR, "r").read()
	frt = Fernet(key.encode())

def encrypt(what):
	coded = frt.encrypt(what.encode())
	return coded.decode()

def decrypt(what):
	coded = frt.decrypt(what.encode())
	return coded.decode()

def sha(what):
	return hashlib.sha256(what.encode()).hexdigest()

def randompasswd():
	return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))


# Grade helper functions
def gradeValue(ocen):
	if ocen[:1] in ["1", "2", "3", "4", "5", "6"]:
		if "+" in ocen:
			return int(ocen[:1]) + 0.5
		elif "-" in ocen:
			return int(ocen[:1]) - 0.25
		else:
			return int(ocen)
	return 0

def valueGrade(ocen):
	if ".5" in ocen:
		return "%s+" % ocen[:1]
	elif ".75" in ocen:
		return "%s-" % ocen[:1]
	else:
		return ocen

def predictAverage(hmm):
	fullgrade = math.floor(hmm)
	if hmm >= fullgrade + 0.75:
		return fullgrade + 1
	if hmm >= fullgrade + 0.5:
		return fullgrade + 0.5
	return fullgrade


# aiohttp wrappers
def response(text, code):
	return web.Response(text = text, status = code, headers = {'Content-Type': 'text/html'})

def JSONresponse(text, code):
	return web.Response(text = json.dumps(text), status = code, headers = {'Content-Type': 'application/json'})


# Some helper functions
def checklen(string, minlen, maxlen):
	s = len(string)
	return minlen <= s <= maxlen

def parseDumbs(strink):
	strink = strink.replace("&", "&amp;")
	strink = strink.replace("<", "&lt;")
	strink = strink.replace(">", "&gt;")
	strink = strink.replace("\n", "<br>")
	return strink

def linkify(html_str):
	html_str = html_str.replace("\n", "<br>")
	unmess = " ".join(html_str.replace(").", ") .").split())
	unmess = re.sub(r"\[[^]]*\]", lambda x: x.group(0).replace(' ','&nbsp;'), unmess)
	words = []
	for word in unmess.split(" "):
		if word.startswith("[") and word.endswith(")"):
			name = word.split("[")[1].split("]")[0]
			url = word.split("(")[1].split(")")[0]
			word = """<a href="%s" target="_blank">%s</a>""" % (url, name)
		elif "://" in word:
			nicer = word.split("://")[1]
			word = """<a href="%s" target="_blank">%s</a>""" % (word, nicer)
		words.append(word)
	return " ".join(words).replace("</a> .", "</a>.")

def parseContact(contact):
	if "://" not in contact:
		contact = "mailto:" + contact
	return contact


# Mess
def mktryagainbtn(location, number):
	return """<button onclick="goto('%s', %s, 'true')" class="highlighted">Try again</button><br>""" % (location, number)

def mkbackbtn(location, number):
	return """<button class="back" onclick="goto('%s', %s, true, true)"></button><br>""" % (location, number)

def tierror_(REQ_TIER, backpath, button, where):
	if where:
		button = "<button onclick=\"goto('" + where + "', 2, true)\">" + button + "</button>"
	else:
		button = ""
	if not backpath:
		backpath = ""
	else:
		backpath = mkbackbtn(backpath, 2)
	return (backpath, "Feature unavailable", "This feature is available in <div class=\"tier " + REQ_TIER + "\"></div> tier.", "<button onclick=\"goto('settings', 3, true)\" class=\"highlighted\">Upgrade tier</button>" + button)

def copyable_tr(tr):
	return """Server couldn't process your request. Here's what happened:<div class="traceback">%s</div>""" % parseDumbs(tr)
