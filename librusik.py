import asyncio, aiohttp, json, math, time, os, hashlib, re, subprocess, random, uuid, string, traceback
from aiohttp import web
from datetime import datetime
from datetime import date
from glob import glob
from cryptography.fernet import Fernet
from librus import Librus, Librus2
from sessionmanager import SessionManager
import ssl

LIBRUSIK_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

BOOT = round(time.time())
ERR_403 = "Couldn't fetch data from Synergia."
ERR_500 = "Server wasn't able to parse this request."

statvfs = os.statvfs("/")
host = {
	"name": subprocess.check_output(". /etc/os-release; echo -n $PRETTY_NAME", shell = True).decode(),
	"cpus": int(subprocess.check_output("echo -n `nproc --all`", shell = True).decode()),
	"memory": round(int(subprocess.check_output("cat /proc/meminfo | grep 'MemTotal' | grep -o '[0-9]*'", shell = True).rstrip().decode()) / 1000 / 1000, 2),
	"freq": round(int(subprocess.check_output("lscpu | grep 'CPU max MHz:' | grep -o '[0-9]*' | sed -n 1p", shell = True).rstrip().decode()) / 1000, 2),
	"storage": round(statvfs.f_bsize * statvfs.f_blocks / 1000 / 1000 / 1000, 2)
}

welcomes = ["Hello", "Hi", "Hey"]
greetings = ["How are you doing?", "Good to see you again.", "How are things?", "Librusik is awesome, isn't it?", "Too lazy to log into Synergia? :D", "Have a wonderful day!", "Nice to see you.", "Synergia still sucks? :D"]
welcome = random.choice(welcomes)
greeting = random.choice(greetings)

database = json.loads(open("database.json", "r").read())
config = json.loads(open("config.json", "r").read())

SESSIONS = SessionManager(database)

async def updatetitles():
	global welcome
	global greeting
	while True:
		await asyncio.sleep(2700)
		welcome = random.choice(welcomes)
		greeting = random.choice(greetings)

asyncio.gather(updatetitles())

frt = Fernet(b"47hltIVR5xK4H44tog6vI7EaGgBzWB7H_Ufvwx4n7dw=")  # Use your own Fernet key to increase security
resources = {
	"index": open("html/index.html", "r").read() % (config["subdirectory"], "konfeti()" if config["isKonfeti"] else ""),
	"home": open("html/home.html", "r").read(),
	"grades": open("html/grades.html", "r").read(),
	"more": open("html/more.html", "r").read(),
	"timetable": open("html/timetable.html", "r").read(),
	"messages": open("html/messages.html", "r").read(),
	"message": open("html/message.html", "r").read(),
	"attendances": open("html/attendances.html", "r").read(),
	"exams": open("html/exams.html", "r").read(),
	"freedays": open("html/freedays.html", "r").read(),
	"teacherfreedays": open("html/teacherfreedays.html", "r").read(),
	"parentteacherconferences": open("html/parentteacherconferences.html", "r").read(),
	"school": open("html/school.html", "r").read(),
	"settings": open("html/settings.html", "r").read(),
	"login": open("html/login.html", "r").read(),
	"panel": open("html/panel.html", "r").read() % config["subdirectory"],
	"panellogin": open("html/panellogin.html", "r").read() %config["subdirectory"],
	"error": open("html/error.html", "r").read(),
	"errorpage": open("html/geterror.html", "r").read(),
}

def updatedb():
	open("database.json", "w").write(json.dumps(database, indent = 4))

def updateconf():
	open("config.json", "w").write(json.dumps(config, indent = 4))

def encrypt(what):
	coded = frt.encrypt(what.encode())
	return coded.decode()
def decrypt(what):
	coded = frt.decrypt(what.encode())
	return coded.decode()
def sha(what):
	return hashlib.sha256(what.encode()).hexdigest()

def auth(data):
	if "username" in data and "password" in data:
		if data["username"] in database:
			return sha(data["password"]) == database[data["username"]]["passwd"]
	return False

def response(text, code):
	return web.Response(text = text, status = code, headers = {'Content-Type': 'text/html'})

def JSONresponse(text, code):
	return web.Response(text = json.dumps(text), status = code, headers = {'Content-Type': 'application/json'})

def getRSS():
	try:
		pid = open("/proc/%s/status" % os.getpid(), "r").read()
		for x in pid.split("\n"):
			if x.startswith("VmRSS:"):
				return round(int(re.sub("[^0-9]", "", x)) / 1000, 2);
		return None
	except:
		return None

def gettemp():
	try:
		d = int(open("/sys/class/thermal/thermal_zone0/temp", "r").read().rstrip())
	except:
		try:
			c0 = int(open("/sys/class/hwmon/hwmon0/temp1_input", "r").read().rstrip())
			#c1 = int(open("/sys/class/hwmon/hwmon1/temp2_input", "r").read().rstrip())
			#c2 = int(open("/sys/class/hwmon/hwmon1/temp4_input", "r").read().rstrip())
			#c3 = int(open("/sys/class/hwmon/hwmon1/temp5_input", "r").read().rstrip())
			d = c0
		except:
			d = 0
	if len(str(d)) > 3:
		d = d / 1000
	return d
def getloadavg():
	d = open("/proc/loadavg", "r").read()
	d = d.split()
	return float(d[0])
def getrawloadavg():
	d = open("/proc/loadavg", "r").read()
	d = d.split()
	return "%s %s %s" % (d[0], d[1], d[2])

def checklen(string, minlen, maxlen):
	s = len(string)
	return s >= minlen and s <= maxlen

def mktryagainbtn(location, number):
	return """<button onclick="goto('%s', %s, 'true')" class="highlighted">Try again</button><br>""" % (location, number)
def mkbackbtn(location, number):
	return """<button class="back" onclick="goto('%s', %s, true, true)"></button><br>""" % (location, number)

def parseDumbs(strink):
	strink = strink.replace("&", "&amp;")
	strink = strink.replace("<", "&lt;")
	strink = strink.replace(">", "&gt;")
	strink = strink.replace("\n", "<br>")
	return strink

def gradeValue(ocen):
	if ocen[:1] in ["1", "2", "3", "4", "5", "6"]:
		if "+" in ocen:
			return int(ocen[:1]) + 0.5
		elif "-" in ocen:
			return int(ocen[:1]) - 0.25
		else:
			return int(ocen)
	return None

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
		return fullgrade + 1;
	if hmm >= fullgrade + 0.5:
		return fullgrade + 0.5;
	return fullgrade;

async def mkaccount(data):
	global database
	if config["max_users"] <= len(database):
		return "Database is full."
	if data["username"] in database:
		return "Account with provided username already exists!"
	for x in database:
		if data["librusLogin"] == database[x]["l_login"]:
			return "Provided login is already in use."
	librus = Librus(SESSIONS.getL(data["username"]))
	if await librus.mktoken(data["librusLogin"], data["librusPassword"]):
		userInfo = await librus.get_me()
		if userInfo == None:
			return "error"
		if config["max_users"] <= len(database):
			return "Database is full."
		if data["username"] in database:
			return "Account with provided username already exists!"
		for x in database:
			if data["librusLogin"] == database[x]["l_login"]:
				return "Provided login is already in use."
		database[data["username"]] = {}
		database[data["username"]]["first_name"] = userInfo["FirstName"]
		database[data["username"]]["last_name"] = userInfo["LastName"]
		database[data["username"]]["passwd"] = sha(data["password"])
		database[data["username"]]["l_login"] = data["librusLogin"]
		database[data["username"]]["l_passwd"] = encrypt(data["librusPassword"])
		database[data["username"]]["year_starts"] = userInfo["SchoolYearStarts"]
		database[data["username"]]["year_ends"] = userInfo["SchoolYearEnds"]
		database[data["username"]]["custom_pic"] = None
		database[data["username"]]["grades_cleanup"] = False
		timgs = glob("static/img/profile/*")
		timg = []
		for x in timgs:
			if not x.endswith("/custom"):
				timg.append(x)
		timg = random.choice(timg)
		database[data["username"]]["profile_pic"] = timg[timg.rindex("/") + 1:]
		updatedb()
		SESSIONS.updatedb(database)
		return True
	return "Wrong Synergia credentials."

async def scaccount(data):
	global database
	for x in database:
		if data["librusLogin"] == database[x]["l_login"] and x != data["username"]:
			return "Provided login is already in use."
	librus = Librus(SESSIONS.getL(data["username"]))
	if await librus.mktoken(data["librusLogin"], data["librusPassword"]):
		userInfo = await librus.get_me()
		if userInfo == None:
			return False
		for x in database:
			if data["librusLogin"] == database[x]["l_login"] and x != data["username"]:
				return "Provided login is already in use."
		database[data["username"]]["first_name"] = userInfo["FirstName"]
		database[data["username"]]["last_name"] = userInfo["LastName"]
		database[data["username"]]["l_login"] = data["librusLogin"]
		database[data["username"]]["l_passwd"] = encrypt(data["librusPassword"])
		database[data["username"]]["year_starts"] = userInfo["SchoolYearStarts"]
		database[data["username"]]["year_ends"] = userInfo["SchoolYearEnds"]
		updatedb()
		SESSIONS.updatedb(database)
		return True
	return "Wrong Synergia credentials."

async def api(request):
	global database
	try:
		data = await request.json()
		if "method" in data and data["method"] in ["mkaccount", "delaccount", "chgpasswd", "chglibrus", "chglibruspasswd", "getstuff", "grades_cleanup"]:
			method = data["method"]
			if method == "mkaccount":
				if "username" in data and "password" in data and "librusLogin" in data and "librusPassword" in data:
					if isinstance(data["username"], str) and isinstance(data["password"], str) and isinstance(data["librusLogin"], str) and isinstance(data["librusPassword"], str):
						reg = re.compile("[a-z0-9]+")
						if not reg.fullmatch(data["username"]):
							return response("", 400)
						if checklen(data["username"], 4, 16) and checklen(data["password"], 4, 32):
							make = await mkaccount(data)
							if make == True:
								return response("", 200)
							return response(make, 403)
				return response("", 400)
			elif auth(data):
				if method == "chgpasswd":
					if "newpassword" in data and isinstance(data["newpassword"], str):
						if not checklen(data["newpassword"], 4, 32):
							return response("", 400)
						database[data["username"]]["passwd"] = sha(data["newpassword"])
						updatedb()
						return response("", 200)
				elif method == "chglibruspasswd":
					if "newLibrusPassword" in data and isinstance(data["newLibrusPassword"], str):
						data["librusLogin"] = database[data["username"]]["l_login"]
						data["librusPassword"] = data["newLibrusPassword"]
						make = await scaccount(data)
						if make == True:
							return response("", 200)
						return response(make, 403)
				elif method == "grades_cleanup":
					if "value" in data and isinstance(data["value"], bool):
						database[data["username"]]["grades_cleanup"] = data["value"]
						updatedb()
						return response("", 200)
				elif method == "chglibrus":
					if "newLibrusLogin" in data and "newLibrusPassword" in data and isinstance(data["newLibrusLogin"], str) and isinstance(data["newLibrusPassword"], str):
						data["librusLogin"] = data["newLibrusLogin"]
						data["librusPassword"] = data["newLibrusPassword"]
						make = await scaccount(data)
						if make == True:
							return response("", 200)
						return response(make, 403)
				elif method == "getstuff":
					librus = Librus(SESSIONS.getL(data["username"]))
					if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
						SESSIONS.saveL(data["username"], librus.headers)
						try:
							lucky = (await librus.get_data("LuckyNumbers"))["LuckyNumber"]["LuckyNumber"]
						except:
							lucky = "None"
						try:
							m = (await librus.get_data("Classes"))["Class"]
							if database[data["username"]]["year_ends"] != m["EndSchoolYear"] or database[data["username"]]["year_starts"] != m["BeginSchoolYear"]:
								database[data["username"]]["year_starts"] = m["BeginSchoolYear"]
								database[data["username"]]["year_ends"] = m["EndSchoolYear"]
								updatedb()
						except:
							pass
						mesgs = await librus.get_messages()
						return response(json.dumps({
							"messages": mesgs,
							"luckynum": lucky
						}), 200)
					return response("", 403)
				elif method == "delaccount":
					try:
						os.remove("static/img/profile/custom/%s" % (database[data["username"]]["custom_pic"]))
					except FileNotFoundError:
						pass
					del database[data["username"]]
					updatedb()
					SESSIONS.updatedb(database)
					return response("", 200)
				return response("", 400)
			return response("", 401)
		return response("", 400)
	except SystemExit:
		return response("", 500)

async def authenticate(request):
	try:
		data = await request.json()
		if auth(data):
			return response("", 200)
		return response("", 401)
	except:
		return response("", 400)


async def index(request):
	return response(resources["index"], 200)

async def login(request):
	f = open("static/app/version")
	c = f.read().split("\n")[0]
	m = os.path.getctime("static/app/version")
	m = datetime.fromtimestamp(m).strftime("%d %B %Y")
	return response(resources["login"] % (c, m, c), 200)


####################################################################################################################################################################################################


async def home(request):
	try:
		data = await request.json()
		if auth(data):
			now = datetime.now()
			day = now.strftime("%d")
			month = now.strftime("%B, %Y")
			scholstarts = datetime.strptime(database[data["username"]]["year_starts"], '%Y-%m-%d')
			scholends = datetime.strptime(database[data["username"]]["year_ends"], '%Y-%m-%d')
			dayspassed = (now - scholstarts).days
			daysleft = (scholends - now).days
			daystotal = daysleft + dayspassed
			percent = dayspassed * 100 / daystotal
			progbar = 220 - 2.2 * percent
			if progbar > 220:
				progbar = 220
			addon = "s"
			if daysleft == 1:
				addon = ""
			if daysleft < 0:
				daysleft = "--"
			a = date(date.today().year, 1, 1)
			b = date(date.today().year, 12, 31)
			day_of_year = datetime.now().timetuple().tm_yday - 1
			ddaysleft = (b - a).days - day_of_year
			dpercent = day_of_year * 100 / (b - a).days
			dprogbar = 220 - 2.2 * dpercent
			if dprogbar > 220:
				dprogbar = 220
			daddon = "s"
			if ddaysleft == 1:
				daddon = ""
			return response(resources["home"] % (welcome, database[data["username"]]["first_name"], greeting, progbar, round(percent), daysleft, addon, dprogbar, round(dpercent), ddaysleft, daddon, progbar, dprogbar), 200)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % ("Internal server error", tr, mktryagainbtn("/home", 0)), 500)

async def grades(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = await librus.get_grades()
				grades = 0
				page = ""
				divz = ""
				rcnt = ""
				averages = ""
				allocens = []
				avgdict = {}
				for s in result:
					notshowempty = database[data["username"]]["grades_cleanup"] and result[s] == []
					if notshowempty:
						continue
					savgarr = []
					savg = ""
					page += """<button class="bubble" onclick="showdiv('main', '%s')"><div class="name">%s</div><div class="value"><code>""" % (s.lower(), s)
					sdivz = ""
					ocenk = ""
					startnewsmstr = False
					koniec = False
					for x in result[s]:
						grades += 1
						weight = ", weight %s" % x["Weight"]
						if weight == ", weight none":
							weight = ""
						else:
							grd = gradeValue(x["Grade"])
							if grd:
								for unusedshit in range(0, x["Weight"]):
									savgarr.append(grd)
						ocenq = """<button class="bubble wide unclickable"><div class="name ocen">%s</div><div class="oceninfo"><div class="value"><b>%s</b>%s</div><div class="value">%s</div><div class="value"><i>%s</i></div><div class="value">Added by %s %s</div><div class="value">%s</div></div></button>""" % (x["Grade"], x["Category"].title(), weight, s, parseDumbs(x["Comment"]), x["AddedBy"]["FirstName"], x["AddedBy"]["LastName"], x["AddDate"])
						ocenk = """<button class="bubble wide unclickable"><div class="name ocen">%s</div><div class="oceninfo"><div class="value"><b>%s</b>%s</div><div class="value"><i>%s</i></div><div class="value">Added by %s %s</div><div class="value">%s</div></div></button>%s""" % (x["Grade"], x["Category"].title(), weight, parseDumbs(x["Comment"]), x["AddedBy"]["FirstName"], x["AddedBy"]["LastName"], x["AddDate"], ocenk)
						allocens.append({
							"string": ocenq,
							"AddDate": (datetime.strptime(x["AddDate"], '%Y-%m-%d %H:%M:%S') - datetime(1970, 1, 1)).total_seconds()
						})
						if x["underlined"]:
							page += "<b><u>%s</u></b><br>" % x["Grade"]
						else:
							page += ("%s " % x["Grade"])
						if x["separator"]:
							ocenk = """<div class="marker">Previous semester</div>%s""" % ocenk
						else:
							startnewsmstr = True
						if (x["isSemester"] and (result[s].index(x) + 1) == len(result[s])) or x["isFinal"]:
							koniec = True
							avgdict[s] = gradeValue(x["Grade"])
					if startnewsmstr:
						ocenk = """<div class="marker">Current semester</div>%s""" % ocenk
					sdivz += ocenk
					if len(result[s]) == 0:
						page += "No grades"
					page += "</code></div></button>"
					sdivz += "</div>"
					if len(savgarr) > 0:
						tempavg = round(sum(savgarr) / len(savgarr), 2)
						if not koniec:
							avgdict[s] = round(tempavg)
						savg = "<code> | </code>Average: %.02f" % tempavg
					divz += """<div id="%s" class="hidden" style="display: none"><button class="back" onclick="showdiv('%s', 'main', true)"></button><br><div class="header">%s</div><div class="subheader grades">Grades: %s%s</div>%s""" % (s.lower(), s.lower(), s, len(result[s]), savg, sdivz)
				score = 0
				if len(avgdict) >= 3:
					avg = "%.02f" % round(sum(avgdict.values()) / len(avgdict), 2)
					for x in avgdict:
						score += avgdict[x]
						fajnal = valueGrade(str(avgdict[x]))
						averages += """<div class="item"><div class="name">%s</div><div class="value"><i>%s</i><input class="fgrade" oninput="calc(this)" value="%s"></div></div>""" % (x, fajnal, fajnal)
				else:
					avg = "Unavailable"
				allocens.sort(key = lambda h: h["AddDate"], reverse = True)
				allocens = allocens[:50]
				for ocen in allocens:
					rcnt += ocen["string"]
				return response(resources["grades"] % (avg, grades, page, avg, len(avgdict), score, averages, len(allocens), rcnt, divz), 200)
			return response(resources["error"] % ("Error", ERR_403, mktryagainbtn("/grades", 1)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % ("Internal server error", tr, mktryagainbtn("/grades", 1)), 500)

async def more(request):
	try:
		data = await request.json()
		if auth(data):
			return response(resources["more"], 200)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % ("Internal server error", tr, mktryagainbtn("/more", 2)), 500)

async def settings(request):
	try:
		data = await request.json()
		if auth(data):
			timgs = glob("static/img/profile/*")
			imgs = ""
			if database[data["username"]]["custom_pic"]:
				imgs += """<button onclick="setProfilePic('%s')"><img onload="loadimg(this)" src="img/profile/custom/%s"></button>""" % (database[data["username"]]["custom_pic"], database[data["username"]]["custom_pic"])
			for img in timgs:
				img = img[img.rindex("/") + 1:]
				if img.endswith(".png"):
					imgs += """<button onclick="setProfilePic('%s')"><img onload="loadimg(this)" src="img/profile/%s"></button>""" % (img, img)
			f = ""
			if database[data["username"]]["profile_pic"] == database[data["username"]]["custom_pic"]:
				f = "custom/"
			grades_cleanup = ""
			if database[data["username"]]["grades_cleanup"]:
				grades_cleanup = "ed"
			return response(resources["settings"] % (f + database[data["username"]]["profile_pic"], database[data["username"]]["first_name"], database[data["username"]]["last_name"], data["username"], imgs, parseDumbs(database[data["username"]]["l_login"]), parseDumbs(decrypt(database[data["username"]]["l_passwd"])), grades_cleanup), 200)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % ("Internal server error", tr, mktryagainbtn("/settings", 3)), 500)

async def timetable(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				res = await librus.get_timetable()
				week = "This week"
				if res["nextWeek"]:
					week = "Next week"
				result = res["Timetable"]
				page = ""
				details = ""
				lessons = 0
				for day in result:
					changes = "koolredb"
					lessons += len(result[day])
					details += """<div id="%s" class="hidden" style="display:none"><button class="back" onclick="showdiv('%s', 'overview', true)"></button><div class="header">%s</div><div class="subheader">%s lessons</div>""" % (day.lower(), day.lower(), day, len(result[day]))
					for x in result[day]:
						teacher = "%s %s" % (x["Teacher"]["FirstName"], x["Teacher"]["LastName"])
						change = ""
						changediv = "koolredb"
						if x["isSubstitution"]:
							change = " (Substitution)"
							changediv = "highlighted"
							changes = "highlighted"
						elif x["isCancelled"]:
							teacher = "nobody"
							change = " (Cancelled)"
							changediv = "highlighted"
							changes = "highlighted"
						if x["Classroom"] != "unknown":
							details += """<button class="bubble unclickable wide %s"><div class="name">%s</div><div class="value">with %s</div><div class="value">Classroom %s</div><div class="value">%s - %s</div></button>""" % (changediv, x["Subject"] + change, teacher, x["Classroom"], x["HourFrom"], x["HourTo"])
						else:
							details += """<button class="bubble unclickable wide %s"><div class="name">%s</div><div class="value">with %s</div><div class="value">%s - %s</div></button>""" % (changediv, x["Subject"] + change, teacher, x["HourFrom"], x["HourTo"])
					hours = len(result[day]);
					page += """<button class="bubble %s" onclick="showdiv('overview', '%s')"><div class="name">%s</div><div class="value">%s lesson%s</div><div class="value">%s - %s</div></button>""" % (changes, day.lower(), day, hours, "s" if (hours != 1) else "", result[day][0]["HourFrom"], result[day][hours - 1]["HourTo"])
					details += "</div>"
				return response(resources["timetable"] % (week, lessons, page, details), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/timetable", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/timetable", 2)), 500)

async def attendances(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = (await librus.get_attendances())[::-1]
				page = ""
				lessons = 0
				presences = 0
				absences = 0
				for x in result:
					lessons += 1
					if x["isPresence"]:
						presences += 1
						color = "green"
					else:
						absences += 1
						if x["Short"] == "u":
							color = "yellow"
						else:
							color = "red"
					page += """<button class="bubble unclickable %s"><div class="name">%s</div><div class="value"><i>%s</i>, %s</div><div class="value">Added by %s %s</div><div class="value">%s</div></button>""" % (color, x["Lesson"], x["Type"], x["Date"], x["AddedBy"]["FirstName"], x["AddedBy"]["LastName"], x["Added"])
				wasted = "%sh %sm" % (math.floor(presences * 45 / 60), (presences * 45 % 60))
				if lessons > 0:
					return response(resources["attendances"] % (round((presences / lessons) * 100, 1), "%", presences, absences, lessons, wasted, page), 200)
				else:
					return response(resources["attendances"] % ("Unavailable", "", presences, absences, lessons, wasted, page), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/attendances", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/attendances", 2)), 500)

async def exams(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = (await librus.get_exams())[::-1]
				page = ""
				for x in result:
					page += """<button class="bubble unclickable"><div class="name">%s</div><div class="value"><b>%s, %s - %s</b></div><div class="value">%s</div><div class="value"><i>%s</i></div><div class="value">Added by %s %s</div><div class="value">%s</div></button>""" % (x["Lesson"], x["Date"], x["StartTime"][:-3], x["EndTime"][:-3], x["Type"].title(), parseDumbs(x["Content"]), x["AddedBy"]["FirstName"], x["AddedBy"]["LastName"], x["AddDate"])
				return response(resources["exams"] % (len(result), page), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/exams", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/exams", 2)), 500)

async def freedays(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = await librus.get_free_days()
				page = ""
				for x in result:
					page += """<button class="bubble unclickable"><div class="name">%s</div><div class="value"><code>From &nbsp</code>%s</div><div class="value"><code>To &nbsp&nbsp&nbsp</code>%s</div></button>""" % (x["Name"], x["DateFrom"], x["DateTo"])
				return response(resources["freedays"] % (len(result), page), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/freedays", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/freedays", 2)), 500)

async def teacherfreedays(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = (await librus.get_teacher_free_days())[::-1]
				page = ""
				for x in result:
					teacher = "%s %s" % (x["Teacher"]["FirstName"], x["Teacher"]["LastName"])
					if "TimeTo" in x:
						page += """<button class="bubble unclickable"><div class="name">%s</div><div class="value"><code>From &nbsp</code>%s, %s</div><div class="value"><code>To &nbsp&nbsp&nbsp</code>%s, %s</div></button>""" % (teacher, x["DateFrom"], x["TimeFrom"][:-3], x["DateTo"], x["TimeTo"][:-3])
					else:
						page += """<button class="bubble unclickable"><div class="name">%s</div><div class="value"><code>From &nbsp</code>%s</div><div class="value"><code>To &nbsp&nbsp&nbsp</code>%s</div></button>""" % (teacher, x["DateFrom"], x["DateTo"])
				return response(resources["teacherfreedays"] % (len(result), page), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/teacherfreedays", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/teacherfreedays", 2)), 500)

async def parentteacherconferences(request):
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = (await librus.get_parent_teacher_conferences())[::-1]
				page = ""
				for x in result:
					page += """<button class="bubble unclickable wide"><div class="name">%s</div><div class="value"><i>%s</i></div><div class="value">Classroom %s</div><div class="value">%s at %s</div></button>""" % (x["Name"], x["Topic"], x["Room"], x["Date"], (x["Time"])[:-3])
				return response(resources["parentteacherconferences"] % (len(result), page), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/parentteacherconferences", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/parentteacherconferences", 2)), 500)

async def school(request):
	global database
	try:
		data = await request.json()
		if auth(data):
			librus = Librus(SESSIONS.getL(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL(data["username"], librus.headers)
				result = await librus.get_school()
				me = await librus.get_me()
				student = "%s %s" % (database[data["username"]]["first_name"], database[data["username"]]["last_name"])
				student_new = "%s %s" % (me["FirstName"], me["LastName"])
				if student != student_new:
					database[data["username"]]["first_name"] = me["FirstName"]
					database[data["username"]]["last_name"] = me["LastName"]
				tutor = "%s %s" % (me["Tutor"]["FirstName"], me["Tutor"]["LastName"])
				address = "%s %s, %s %s" % (result["Street"], result["BuildingNumber"], result["PostCode"], result["Town"])
				scholends = datetime.strptime(database[data["username"]]["year_ends"], '%Y-%m-%d')
				sendz = datetime.strptime(me["SchoolYearMiddles"], '%Y-%m-%d').strftime("%d %B %Y")
				endz = datetime.strptime(me["SchoolYearEnds"], '%Y-%m-%d').strftime("%d %B %Y")
				return response(resources["school"] % (result["Name"], address, student, tutor, me["Class"], me["Type"], sendz, endz), 200)
			return response(resources["error"] % (mkbackbtn("/more", 2) + "Error", ERR_403, mktryagainbtn("/school", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("/more", 2) + "Internal server error", tr, mktryagainbtn("/school", 2)), 500)

async def messages(request):
	global database
	try:
		data = await request.json()
		if auth(data):
			librus = Librus2(SESSIONS.getL2(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL2(data["username"], librus.cookies)
				inbox = await librus.get_messages()
				html = ""
				for mesg in inbox:
					html += """<button class="bubble wide" onclick="goto('message/%s', 2, true)"><div class="name">%s</div><div class="value">from <b>%s</b></div><div class="value">%s</div></div>""" % (mesg["link"], mesg["subject"], mesg["from"], mesg["date"])
				return response(resources["messages"] % (len(inbox), html), 200)
			return response(resources["error"] % (mkbackbtn("messages", 2) + "Error", ERR_403, mktryagainbtn("/messages", 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn("messages", 2) + "Internal server error", tr, mktryagainbtn("/messages", 2)), 500)


async def message(request):
	global database
	uri = request.match_info["uri"]
	uri_full = "message/%s" % uri
	try:
		data = await request.json()
		if auth(data):
			librus = Librus2(SESSIONS.getL2(data["username"]))
			if await librus.mktoken(database[data["username"]]["l_login"], decrypt(database[data["username"]]["l_passwd"])):
				SESSIONS.saveL2(data["username"], librus.cookies)
				mesg = await librus.get_message(uri)
				attachments = ""
				for file in mesg["attachments"]:
					attachments += """<div>%s</div>""" % file
				return response(resources["message"] % (mesg["subject"], mesg["from"], mesg["date"], mesg["content"], attachments, mesg["read"]), 200)
			return response(resources["error"] % (mkbackbtn(uri_full, 2) + "Error", ERR_403, mktryagainbtn(uri_full, 2)), 403)
		return response("", 401)
	except:
		tr = traceback.format_exc().replace(LIBRUSIK_PATH, "")
		return response(resources["error"] % (mkbackbtn(uri_full, 2) + "Internal server error", tr, mktryagainbtn(uri_full, 2)), 500)


####################################################################################################################################################################################################

async def panelapi(request):
	try:
		data = await request.json()
		if "name" in data and "password" in data and "method" in data:
			if data["name"] == config["name"] and sha(data["password"]) == config["passwd"]:
				if data["method"] == "get_data":
					loadavg = round(getloadavg() / host["cpus"] * 100)
					uptime = round(time.time()) - BOOT
					cpu_temp = gettemp()
					users = list()
					for x in database:
						users.append({"first_name": database[x]["first_name"], "last_name": database[x]["last_name"], "username": x})
					maxusers = config["max_users"]
					db_usage = round(len(users) / maxusers * 100)
					db_size = round(os.stat("database.json").st_size / 10) / 100;
					return JSONresponse({
						"os": host["name"],
						"cores": host["cpus"],
						"cpu_freq": host["freq"],
						"memory": host["memory"],
						"rss": getRSS(),
						"storage": host["storage"],
						"loadavg_raw": getrawloadavg(),
						"loadavg": loadavg,
						"cpu_temp": cpu_temp,
						"users": users[::-1],
						"userscount": len(users),
						"max_users": maxusers,
						"db_usage": db_usage,
						"uptime": uptime,
						"db_size": db_size
					}, 200)
				elif data["method"] == "auth":
					return response("", 200)
				elif data["method"] == "passwd":
					if "newpass" in data and isinstance(data["newpass"], str) and checklen(data["newpass"], 4, 32):
						config["passwd"] = sha(data["newpass"])
						updateconf()
						return response("", 200)
				elif data["method"] == "name":
					if "newname" in data and isinstance(data["newname"], str) and checklen(data["newname"], 4, 16):
						reg = re.compile("[a-z0-9]+")
						if not reg.fullmatch(data["newname"]):
							return response("", 400)
						config["name"] = data["newname"]
						updateconf()
						return response("", 200)
				elif data["method"] == "reboot":
					raise SystemExit
				elif data["method"] == "chgmaxusers":
					if "maxusers" in data and isinstance(data["maxusers"], int) and data["maxusers"] <= 64 and data["maxusers"] >= 2:
						config["max_users"] = data["maxusers"]
						updateconf()
						return response("", 200)
				elif data["method"] == "deluser":
					if "username" in data and isinstance(data["username"], str):
						if data["username"] in database:
							if database[data["username"]]["custom_pic"]:
								os.remove("static/img/profile/custom/%s" % (database[data["username"]]["custom_pic"]))
							del database[data["username"]]
							updatedb()
							return response("", 200)
						return response("", 403)
				elif data["method"] == "genuserpass":
					if "username" in data and isinstance(data["username"], str):
						if data["username"] in database:
							newpassw = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
							database[data["username"]]["passwd"] = sha(newpassw);
							updatedb()
							return response(newpassw, 200)
						return response("", 403)
				return response("", 400)
			return response("", 401)
		return response("", 400)
	except SystemExit:
		raise SystemExit
	except:
		return response("", 500)

async def panel(request):
	return response(resources["panel"], 200)

async def panell(request):
	return response(resources["panellogin"], 200)

async def upload_handler(request):
	try:
		data = await request.post()
		if not auth(data):
			return web.Response(text = json.dumps({"ok": False}), status = 401, headers = {'Content-Type': 'application/json'})
		size = int(request.headers.get("Content-Length")) / 1000 / 1000
		if data["username"] not in database or size > 10:
			return response("", 401)
		img = data["file"]
		extension = img.filename[img.filename.rindex(".") + 1:].lower()
		if extension.lower() not in ["jpg", "png", "jpeg", "gif", "svg", "webp"]:
			return response("", 400)
		uid = str(uuid.uuid1())
		filename = uid[0:uid.rindex("-")]
		filename = filename.replace("-", "")
		with open(os.path.join("static/img/profile/custom/", filename), "wb") as f:
			f.write(img.file.read())
		if database[data["username"]]["custom_pic"]:
			os.remove("static/img/profile/custom/%s" % (database[data["username"]]["custom_pic"]))
		database[data["username"]]["custom_pic"] = filename
		database[data["username"]]["profile_pic"] = filename
		updatedb()
		return response("", 200)
	except SystemExit:
		return response("", 500)

async def set_profile_pic(request):
	try:
		data = await request.json()
		if auth(data):
			database[data["username"]]["profile_pic"] = data["picture"]
			updatedb()
			return response("", 200)
		return response("", 401)
	except:
		return response("", 500)


@web.middleware
async def error_middleware(request, handler):
	exc = None
	try:
		respons = await handler(request)
		status = respons.status
		return respons
	except web.HTTPException as ex:
		status = ex.status
		exc = ex
	except Exception as ex:
		exc = ex
		status = 500
	return response(resources["errorpage"] % (str(status), str(exc)), status)


app = web.Application(middlewares=[error_middleware], client_max_size=1024**2*4)


# DEBUG ONLY
#app = web.Application(client_max_size=1024**2*4)

app.add_routes([
	web.route('GET', '/', index),
	web.route('GET', '/login', login),
	web.route('POST', '/auth', authenticate),
	web.route('POST', '/api', api),
	web.route('POST', '/home', home),
	web.route('POST', '/grades', grades),
	web.route('POST', '/more', more),
	web.route('POST', '/settings', settings),
	web.route('POST', '/timetable', timetable),
	web.route('POST', '/attendances', attendances),
	web.route('POST', '/exams', exams),
	web.route('POST', '/freedays', freedays),
	web.route('POST', '/teacherfreedays', teacherfreedays),
	web.route('POST', '/parentteacherconferences', parentteacherconferences),
	web.route('POST', '/school', school),
	web.route('POST', '/messages', messages),
	web.route('POST', '/message/{uri}', message),
	web.route('GET', '/panel', panel),
	web.route('GET', '/panel/login', panell),
	web.route('POST', '/panel/api', panelapi),
	web.route("POST", "/api/uploadProfilePic", upload_handler),
	web.route("POST", "/api/setProfilePic", set_profile_pic),
	web.static('/', 'static')
])

loop = asyncio.get_event_loop()

if config["ssl"]:
	ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	ssl_context.load_cert_chain(config["pubkey"], config["privkey"])
	loop.create_task(web._run_app(app, port = config["port"], ssl_context = ssl_context))
else:
	loop.create_task(web._run_app(app, port = config["port"]))

loop.run_forever()
