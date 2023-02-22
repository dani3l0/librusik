import base64
import hashlib
import json
import math
import os
import random
import re
import string
from cryptography.fernet import Fernet
from aiohttp import web

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
		print("It seems this is the first run. Initializing data...")
		os.mkdir(DATA_DIR)
		os.mkdir(PROFILE_PIC_DIR)
		conf = open("%s/config.json" % DATA_DIR, "w")
		conf.write(json.dumps(CONFIG_DEFAULT, indent = 4))
		conf.close()
		config = CONFIG_DEFAULT
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
    hidetiers = "" if config["enable_tiers"] else ".tiers{display:none !important}"
    return {
        "index": open("html/index.html", "r").read() % (config["subdirectory"], hidetiers),
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
        "about": open("html/about.html", "r").read() % config["contact_uri"],
        "tiers": open("html/tiers.html", "r").read() % (config["tiers_requirements"]["free"], config["tiers_requirements"]["plus"], config["tiers_requirements"]["pro"], config["tiers_text"]),
        "panel": open("html/panel.html", "r").read() % (config["subdirectory"], hidetiers),
        "panellogin": open("html/panellogin.html", "r").read() % config["subdirectory"],
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



# Host information
statvfs = os.statvfs(".")

host = {
	"storage": round(statvfs.f_bsize * statvfs.f_blocks / 1000 / 1000 / 1000, 2),
	"cpus": os.cpu_count()
}

def getRSS():
	try:
		pid = open("/proc/%s/status" % os.getpid(), "r").read()
		for x in pid.split("\n"):
			if x.startswith("VmRSS:"):
				return round(int(re.sub("[^0-9]", "", x)) / 1000, 2)
		return None
	except:
		return None

def getval(path, toInt = False):
	f = open(path, "r").read().rstrip()
	if toInt: f = int(f)
	return f

def gettemp():
	d = 0
	sensors = ["coretemp", "cputhermal", "k10temp"]
	path = "/sys/class/hwmon"
	hwmon = [f"{path}/{x}" for x in os.listdir(path)]
	for sensor in hwmon:
		for name in sensors:
			if name in open(f"{sensor}/name", "r").read():
				contents = [f"{sensor}/{x}" for x in os.listdir(sensor)]
				temps = [0]
				for x in contents:
					try:
						if x.endswith("_input"):
							temps.append(int(
								open(f"{x}", "r").read()
							))
					except:
						pass
				d = max(temps)
				break
	if len(str(d)) > 3:
		d /= 1000
	return d

def getloadavg():
	try:
		d = open("/proc/loadavg", "r").read()
		d = d.split()
		return float(d[0])
	except:
		return 0

def getrawloadavg():
	try:
		d = open("/proc/loadavg", "r").read()
		d = d.split()
		return "%s %s %s" % (d[0], d[1], d[2])
	except:
		return "N/A"


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


# Some helper functions?
def checklen(string, minlen, maxlen):
	s = len(string)
	return minlen <= s <= maxlen

def parseDumbs(strink):
	strink = strink.replace("&", "&amp;")
	strink = strink.replace("<", "&lt;")
	strink = strink.replace(">", "&gt;")
	strink = strink.replace("\n", "<br>")
	return strink


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