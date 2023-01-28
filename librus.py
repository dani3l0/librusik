import asyncio, aiohttp, json, os
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

REQUESTS = [0] * 7
PATH_ = os.path.dirname(os.path.abspath(__file__)) + "/"

class Librus:
	def __init__(self, session):
		self.host = "https://synergia.librus.pl/gateway/api/2.0/"
		self.headers = None
		if session != None:
			self.headers = session

	# Used in deprecated auth method
	# async def request(self, link, postdata):
	# 	arr_index = datetime.now().weekday()
	# 	for i in range(0, 5):
	# 		try:
	# 			async with aiohttp.ClientSession(headers = self.headers) as session:
	# 				async with session.post(link, data = postdata, timeout = 5) as resp:
	# 					REQUESTS[arr_index] += 1
	# 					if resp.status == 200:
	# 						return {"code": resp.status, "text": await resp.text()}
	# 					elif resp.status == 401:
	# 						return {"code": 000, "text": None}
	# 		except:
	# 			pass
	# 	return {"code": 000, "text": None}

	# Old auth method (stopped working on 27 January 2023)
	# async def mktoken(self, login, passw):
	# 	if (await self.get_data("Me")):
	# 		return True
	# 	try:
	# 		self.headers = {"Authorization": "Basic Mjg6ODRmZGQzYTg3YjAzZDNlYTZmZmU3NzdiNThiMzMyYjE="}
	# 		response = await self.request(self.host + "OAuth/Token", {
	# 			"username": login,
	# 			"password": passw,
	# 			"librus_long_term_token": "1",
	# 			"grant_type": "password"
	# 		})
	# 		if response["code"] == 200:
	# 			token = json.loads(response["text"])["access_token"]
	# 			self.headers["Authorization"] = "Bearer " + token
	# 			return True
	# 		return False
	# 	except:
	# 		return False

	async def activate_api_access(self):
		arr_index = datetime.now().weekday()
		for i in range(0, 5):
			try:
				async with aiohttp.ClientSession(cookies = self.headers, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}) as session:
					resp = await session.get("https://synergia.librus.pl/gateway/api/2.0/Auth/TokenInfo", timeout = 5)
					REQUESTS[arr_index] += 1
					identifier =  (await resp.json())["UserIdentifier"]
					resp2 = await session.get("https://synergia.librus.pl/gateway/api/2.0/Auth/UserInfo/" + identifier, timeout = 5)
					REQUESTS[arr_index] += 1
					return await resp2.status == 200

			except:
				pass
		return {"code": 000, "text": None}

	async def mktoken(self, login, passw):
		if (await self.get_data("Me")):
			return True
		try:
			async with aiohttp.ClientSession() as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata")
				form = aiohttp.FormData()
				form.add_field("action", "login")
				form.add_field("login", login)
				form.add_field("pass", passw)
				REQUESTS[arr_index] += 1
				resp = await session.post("https://api.librus.pl/OAuth/Authorization?client_id=46", data = form)
				REQUESTS[arr_index] += 1
				resp = await session.get("https://api.librus.pl/OAuth/Authorization/Grant?client_id=46")
				self.headers = resp.cookies
				ok = resp.status == 200
				res = False
				if ok:
					res = await self.activate_api_access()
				return res
		except:
			return False

	async def curl(self, link):
		arr_index = datetime.now().weekday()
		for i in range(0, 5):
			try:
				async with aiohttp.ClientSession(cookies = self.headers) as session:
					async with session.get(link, timeout = 5) as resp:
						REQUESTS[arr_index] += 1
						if resp.status == 200:
							return {"code": resp.status, "text": await resp.text()}
						elif resp.status == 401:
							return {"code": 000, "text": None}
			except:
				pass
		return {"code": 000, "text": None}

	async def get_data(self, method):
		r = await self.curl(self.host + method)
		if r["code"] != 200:
			return None
		return json.loads(r["text"])

	async def get_subjects(self):
		r = await self.get_data("Subjects")
		if r == None:
			return None
		subjects = {x["Id"]: x["Name"] for x in r["Subjects"]}
		return subjects

	async def get_teachers(self):
		r = await self.get_data("Users")
		if r == None:
			return None
		teachers = {
			i["Id"]: {
				"FirstName": i["FirstName"],
				"LastName": i["LastName"]
			} for i in r["Users"]
		}
		return teachers

	async def get_categories(self):
		r = await self.get_data("Grades/Categories")
		if r == None:
			return None
		categories = {}
		for i in r["Categories"]:
			if "Weight" in i:
				w = i["Weight"]
			else:
				w = "none"
			categories[i["Id"]] = {
				"Name": i["Name"],
				"Weight": w,
			}
		return categories

	async def get_categories2(self):
		r = await self.get_data("HomeWorks/Categories")
		if r == None:
			return None
		categories = {}
		for i in r["Categories"]:
			categories[i["Id"]] = {
				"Name": i["Name"]
			}
		return categories

	async def get_comments(self):
		r = await self.get_data("Grades/Comments")
		if r == None:
			return None
		comments = {i["Id"]: {"Text": i["Text"]} for i in r["Comments"]}
		return comments

	async def get_grades(self):
		response = await self.get_data("Grades")
		categories = await self.get_categories()
		comments = await self.get_comments()
		subjects = await self.get_subjects()
		teachers = await self.get_teachers()
		if response == None or categories == None or comments == None or subjects == None or teachers == None:
			return None
		grades = {i: [] for i in subjects.values()}
		for x in response["Grades"]:
			comment = "No comment"
			if "Comments" in x:
				comment = comments[x["Comments"][0]["Id"]]["Text"]
			grades[subjects[x["Subject"]["Id"]]].append({
				"Grade": x["Grade"],
				"Weight": categories[x["Category"]["Id"]]["Weight"],
				"Comment": comment,
				"Category": categories[x["Category"]["Id"]]["Name"],
				"isFinal": x["IsFinal"] or x["IsFinalProposition"],
				"isSemester": x["IsSemester"] or x["IsSemesterProposition"],
				"separator": x["IsSemester"],
				"underlined": x["IsSemester"] or x["IsFinal"],
				"Semester": x["Semester"],
				"AddDate": x["AddDate"],
				"AddedBy": {
					"FirstName": teachers[x["AddedBy"]["Id"]]["FirstName"],
					"LastName": teachers[x["AddedBy"]["Id"]]["LastName"]
				}
			})
		return grades

	async def get_me(self):
		g = await self.get_data("Me")
		u = await self.get_data("UserProfile")
		w = await self.get_teachers()
		n = await self.get_data("Classes")
		if g == None or u == None or w == None or n == None:
			return None
		o = {
			"FirstName": g["Me"]["Account"]["FirstName"],
			"LastName": g["Me"]["Account"]["LastName"],
			"Tutor": w[n["Class"]["ClassTutor"]["Id"]],
			"SchoolYearStarts": n["Class"]["BeginSchoolYear"],
			"SchoolYearMiddles": n["Class"]["EndFirstSemester"],
			"SchoolYearEnds": n["Class"]["EndSchoolYear"],
			"Type": u["UserProfile"]["UnitType"].title(),
			"Class": "%s %s" % (str(n["Class"]["Number"]), n["Class"]["Symbol"].upper())
		}
		return o

	async def get_school(self):
		buda = await self.get_data("Schools")
		if buda == None:
			return None
		return buda["School"]

	async def get_free_days(self):
		r = await self.get_data("SchoolFreeDays")
		if r == None:
			return None
		for i in r["SchoolFreeDays"]:
			for e in ["Id", "Units"]:
				i.pop(e)
		return r["SchoolFreeDays"]

	async def get_teacher_free_days(self):
		r = await self.get_data("TeacherFreeDays")
		teachers = await self.get_teachers()
#		teacherfreedaystypes = await self.get_data("TeacherFreeDays/Types")
#		types = {
#			i["Id"]: i["Name"] for i in teacherfreedaystypes["Types"]
#		}
		for i in r["TeacherFreeDays"]:
			i.pop("Id")
			i["Teacher"] = teachers[i["Teacher"]["Id"]]
#			i["Type"] = types[i["Type"]["Id"]]
		return r["TeacherFreeDays"]

	async def get_behaviour_grade(self):
		try:
			grade_ids = ["nothing","wzorowe","bardzo dobre","dobre","poprawne","nieodpowiednie","naganne","nothing"]
			grade_raw = (await self.get_data("BehaviourGrades"))["Grades"][-0]
			teacher = (await self.get_teachers())[grade_raw["Teacher"]["Id"]]
			grade = {
				"Grade": grade_ids[grade_raw["GradeType"]["Id"]],
				"Teacher":{
					"FirstName": teacher["FirstName"],
					"LastName": teacher["LastName"]
				}
			}
		except KeyError:
			grade = None
		return grade

	async def get_classrooms(self):
		d = await self.get_data("TimetableEntries")
		classrooms = {}
		for x in d["TimetableEntries"]:
			if "Classroom" in x:
				classrooms[str(x["Classroom"]["Id"])] = x["Classroom"]["Name"]
		return classrooms

	async def get_timetable(self):
		today = datetime.now()
		weekStart = today + timedelta(days = 2)
		weekStart = weekStart - timedelta(days = weekStart.weekday())
		thisweek = today.isocalendar()[1]
		autoweek = weekStart.isocalendar()[1]
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		r = await self.get_data("Timetables?weekStart=%s-%s-%s" % (weekStart.year, weekStart.month, weekStart.day))
		c = await self.get_classrooms()
		if r == None or c == None:
			return None
		timetable = {}
		day = 0
		for x in r["Timetable"]:
			curr = r["Timetable"][x]
			timetable[days[day]] = []
			for i in curr:
				if i:
					if "Classroom" in i[0]:
						try:
							classroom = c[i[0]["Classroom"]["Id"]]
						except KeyError:
							classroom = "unknown"
					else:
						classroom = "unknown"
					timetable[days[day]].append({
						"Lesson": i[0]["LessonNo"],
						"Subject": i[0]["Subject"]["Name"],
						"isSubstitution": i[0]["IsSubstitutionClass"],
						"isCancelled": i[0]["IsCanceled"],
						"Teacher": {
							"FirstName": i[0]["Teacher"]["FirstName"],
							"LastName": i[0]["Teacher"]["LastName"]
						},
						"HourFrom": i[0]["HourFrom"],
						"HourTo": i[0]["HourTo"],
						"Classroom": classroom
					})
			if not timetable[days[day]]:
				del timetable[days[day]]
			day += 1
		return {
			"nextWeek": thisweek < autoweek,
			"Timetable": timetable
		}

	async def get_exams(self):
		r = await self.get_data("HomeWorks")
		teachers = await self.get_teachers()
		categories = await self.get_categories2()
		subjects = await self.get_subjects()
		if r == None or teachers == None or categories == None or subjects == None:
			return None
		exams = []
		for x in r["HomeWorks"]:
			try:
				leson = subjects[x["Subject"]["Id"]]
			except KeyError:
				leson = "Lesson %s" % x["LessonNo"]
			exams.append({
				"Lesson": leson,
				"AddedBy": {
					"FirstName": teachers[x["CreatedBy"]["Id"]]["FirstName"],
					"LastName": teachers[x["CreatedBy"]["Id"]]["LastName"]
				},
				"Type": categories[x["Category"]["Id"]]["Name"],
				"StartTime": x["TimeFrom"],
				"EndTime": x["TimeTo"],
				"Date": x["Date"],
				"AddDate": x["AddDate"],
				"Content": x["Content"]
			})
		return exams

	async def get_attendances(self):
		g = await self.get_data("Attendances")
		u = await self.get_teachers()
		w = await self.get_data("Lessons")
		n = await self.get_subjects()
		o = await self.get_data("Attendances/Types")
		if g == None or u == None or w == None or n == None or o == None:
			return None
		lesons = {}
		for a in w["Lessons"]:
			lesons[a["Id"]] = a["Subject"]["Id"]
		types = {}
		for a in o["Types"]:
			types[a["Id"]] = {
				"isPresence": a["IsPresenceKind"],
				"Type": a["Name"],
				"Short": a["Short"]
			}
		attends = []
		for x in g["Attendances"]:
			attends.append({
				"Lesson": n[lesons[x["Lesson"]["Id"]]],
				"Type": types[x["Type"]["Id"]]["Type"],
				"Short": types[x["Type"]["Id"]]["Short"],
				"isPresence": types[x["Type"]["Id"]]["isPresence"],
				"Added": x["AddDate"],
				"Date": x["Date"],
				"AddedBy": {
					"FirstName": u[x["AddedBy"]["Id"]]["FirstName"],
					"LastName": u[x["AddedBy"]["Id"]]["LastName"]
				}
			})
		return attends

	async def get_parent_teacher_conferences(self):
		ptc = await self.get_data("ParentTeacherConferences")
		if ptc == None:
			return None
		return ptc["ParentTeacherConferences"]

	async def get_messages(self):
		try:
			k = await self.get_data("WhatsNew")
			if k and "WhatsNew" in k:
				return len(k["WhatsNew"]["Messages"])
			return "-"
		except:
			return "-"


class Librus2:
	def __init__(self, session):
		self.cookies = session
		self.host = "https://synergia.librus.pl"

	async def mktoken(self, login, password):
		if await self.get_messages():
			return True
		self.cookies = None
		async with aiohttp.ClientSession() as session:
			arr_index = datetime.now().weekday()
			REQUESTS[arr_index] += 1
			resp = await session.get("https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata")
			form = aiohttp.FormData()
			form.add_field("action", "login")
			form.add_field("login", login)
			form.add_field("pass", password)
			REQUESTS[arr_index] += 1
			resp = await session.post("https://api.librus.pl/OAuth/Authorization?client_id=46", data = form)
			REQUESTS[arr_index] += 1
			resp = await session.get("https://api.librus.pl/OAuth/Authorization/Grant?client_id=46")
			self.cookies = resp.cookies
			return resp.status == 200
		return False

	async def get_messages(self):
		try:
			async with aiohttp.ClientSession(cookies = self.cookies) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci" % (self.host))
				html = await resp.text()
				messages = []
				soup = BeautifulSoup(html, "html.parser")
				table = soup.find("table", class_ = "decorated stretch")
				for row in table.find_all("tr"):
					try:
						cols = row.find_all("td")
						sender = cols[2].text
						link = cols[2].find("a", href = True)["href"][1:]
						messages.append({
							"from": sender[:(sender.index("(") - 1)],
							"subject": cols[3].text,
							"date": cols[4].text,
							"link": link[link.index("/") + 1:].replace("/", "-")
						})
					except:
						pass
			return messages
		except:
			return []

	async def get_message(self, link):
		try:
			async with aiohttp.ClientSession(cookies = self.cookies) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci/%s" % (self.host, link.replace("-", "/")))
				html = await resp.text()
				soup = BeautifulSoup(html, "html.parser")
				main = soup.find("table", class_ = "stretch container-message")
				data = main.find_all("table", class_ = "stretch")
				data_p = data[2].find_all("td")
				message = soup.find("div", class_ = "container-message-content").decode_contents()
				files_div = main.find_all("table")[6]
				files = []
				for file in files_div.find_all("tr"):
					try:
						f = file.find_all("td")
						imgs = file.find_all("img")
						for img in imgs:
							cl = str(img.get("onclick")).strip().replace(" ", "").replace("\n", "").replace("\\", "")
							if cl.startswith("otworz"):
								cl = self.host + cl.split('("')[1].split('",')[0]
						name = f[0].text.strip()
						if "." in name:
							files.append({
								"name": name,
								"source": cl,
								"direct": "/get",
								"nice": cl.split("/pobierz_zalacznik/")[1]
							})
					except:
						pass
				btf = data_p[1].text
				btf = btf[:btf.index("(")] + btf[btf.index(")") + 2:]
				return {
					"subject": data_p[3].text,
					"from": btf,
					"date": data_p[5].text,
					"read": data[3].find("td", class_ = "left").text,
					"content": message,
					"attachments": files
				}
		except:
			tr = traceback.format_exc().replace(PATH_, "")
			return {
				"subject": "Internal Server Error",
				"from": "nobody",
				"date": "",
				"read": "failed",
				"content": tr,
				"attachments": []
			}

	async def download_file(self, link):
		try:
			async with aiohttp.ClientSession(cookies = self.cookies) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci/pobierz_zalacznik/%s" % (self.host, link))
				respF = await session.get("%s/get" % (resp.url))
				headers = respF.headers
				file_I_guess = await respF.read()
			return {
				"headers": headers,
				"content": file_I_guess
			}
		except:
			return None
