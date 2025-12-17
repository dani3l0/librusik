import aiohttp
import json
import os
import traceback
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

REQUESTS = [0] * 7
PATH_ = os.getcwd()

class Librus:
	def __init__(self, session=None):
		self.host = "https://synergia.librus.pl/gateway/api/2.0/"
		self.msg_host = "https://synergia.librus.pl"
		self.headers = session

	async def activate_api_access(self):
		arr_index = datetime.now().weekday()
		status = 0
		text = None
		try:
			async with aiohttp.ClientSession(cookies = self.headers) as session:
				resp = await session.get(self.host + "Auth/TokenInfo", timeout = 5)
				REQUESTS[arr_index] += 1
				identifier = (await resp.json())["UserIdentifier"]
				resp2 = await session.get(self.host + "Auth/UserInfo/" + identifier, timeout = 5)
				REQUESTS[arr_index] += 1
				return await resp2.status == 200
		except:
			pass
		return {"code": status, "text": text}

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
		status = 0
		for i in range(5):
			try:
				async with aiohttp.ClientSession(cookies = self.headers) as session:
					async with session.get(link, timeout = 5) as resp:
						REQUESTS[arr_index] += 1
						status = resp.status
						if status in [200, 401]:
							return {"code": status, "text": await resp.text()}
			except:
				pass
		return {"code": status, "text": None}

	async def get_data(self, method):
		try:
			r = await self.curl(self.host + method)
			if r["code"] == 200:
				return json.loads(r["text"])
		except:
			return None

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
			teacher = {
				"FirstName": "unknown",
				"LastName": "teacher"
			}
			if x["AddedBy"]["Id"] in teachers:
				teacher["FirstName"] = teachers[x["AddedBy"]["Id"]]["FirstName"]
				teacher["LastName"] = teachers[x["AddedBy"]["Id"]]["LastName"]
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
				"AddedBy": teacher
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
		for i in r["TeacherFreeDays"]:
			try:
				i.pop("Id")
				i["Teacher"] = teachers[i["Teacher"]["Id"]]
			except KeyError:
				pass
		return r["TeacherFreeDays"]

	async def get_lucky_number(self):
		try:
			return (await self.get_data("LuckyNumbers"))["LuckyNumber"]["LuckyNumber"]
		except:
			return None

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
		
		start_pivot = today + timedelta(days=2)
		weekStart = start_pivot - timedelta(days=start_pivot.weekday())
		weekEnd = weekStart + timedelta(days=6)
		
		thisweek = today.isocalendar()[1]
		autoweek = weekStart.isocalendar()[1]
		
		date_from_str = weekStart.strftime('%Y-%m-%d')
		date_to_str = weekEnd.strftime('%Y-%m-%d')
		
		r = await self.get_data(f"Timetables?weekStart={date_from_str}")
		additional = await self.get_data(f"Timetables/OtherActivitiesRegister?dateFrom={date_from_str}&dateTo={date_to_str}&hideOutdatedEntries=false")
		c = await self.get_classrooms()
		
		if r is None or c is None:
			return None

		time_to_lesson = {}
		if r and "Timetable" in r:
			for date_key in r["Timetable"]:
				for entry in r["Timetable"][date_key]:
					if entry and len(entry) > 0:
						time_to_lesson[entry[0]["HourFrom"]] = entry[0]["LessonNo"]

		days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		timetable = {day: [] for day in days_map}

		for date_str in r["Timetable"]:
			if not r["Timetable"][date_str]: continue
			
			dt = datetime.strptime(date_str, "%Y-%m-%d")
			day_name = days_map[dt.weekday()]
			
			for entry_list in r["Timetable"][date_str]:
				if not entry_list: continue
				lesson = entry_list[0]
				
				# Resolve Classroom
				classroom_name = "unknown"
				if "Classroom" in lesson:
					try:
						classroom_name = c[lesson["Classroom"]["Id"]]["Symbol"]
					except (KeyError, TypeError):
						classroom_name = "unknown"

				timetable[day_name].append({
					"Lesson": lesson["LessonNo"],
					"Subject": lesson["Subject"]["Name"],
					"isSubstitution": lesson["IsSubstitutionClass"],
					"isCancelled": lesson["IsCanceled"],
					"Teacher": {
						"FirstName": lesson["Teacher"]["FirstName"],
						"LastName": lesson["Teacher"]["LastName"]
					},
					"HourFrom": lesson["HourFrom"],
					"HourTo": lesson["HourTo"],
					"Classroom": classroom_name
				})

		if additional and 'data' in additional:
			for item in additional['data']:
				dt = datetime.strptime(item['date'], "%Y-%m-%d")
				day_name = days_map[dt.weekday()]
				
				t_name_parts = item['teacherName'].split(' ')
				t_last = t_name_parts[0] if len(t_name_parts) > 0 else ""
				t_first = " ".join(t_name_parts[1:]) if len(t_name_parts) > 1 else ""

				cls = "unknown"
				if item.get('classroom') and item['classroom'].get('symbol'):
					cls = item['classroom']['symbol']

				lesson_num = time_to_lesson.get(item['startTime'], "-")

				timetable[day_name].append({
					"Lesson": lesson_num,
					"Subject": item['title'],
					"isSubstitution": False,
					"isCancelled": False,
					"Teacher": {
						"FirstName": t_first,
						"LastName": t_last
					},
					"HourFrom": item['startTime'],
					"HourTo": item['endTime'],
					"Classroom": cls
				})

		final_timetable = {}
		for day in days_map:
			if timetable[day]:
				timetable[day].sort(key=lambda x: x['HourFrom'])
				final_timetable[day] = timetable[day]

		return {
			"nextWeek": thisweek < autoweek,
			"Timetable": final_timetable
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
		return ptc["ParentTeacherConferences"]

	def parseAddDate(self, date):
		return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

	def parseDate(self, date):
		return datetime.strptime(date, "%Y-%m-%d")

	def check_period(self, date, period):
		return (datetime.now() - self.parseAddDate(date)).days <= period

	async def get_notifications(self, days=14):
		grades = len((await self.get_data("Grades"))["Grades"])
		exams = len((await self.get_data("HomeWorks"))["HomeWorks"])
		attendances = (await self.get_data("Attendances"))["Attendances"]
		attendances_types = {str(x["Id"]): x["IsPresenceKind"] for x in (await self.get_data("Attendances/Types"))["Types"]}
		absences = 0
		for attendance in attendances:
			absences += not attendances_types[str(attendance["Type"]["Id"])]
		conferences = len(await self.get_parent_teacher_conferences())
		return {
			"grades": grades,
			"exams": exams,
			"absences": absences,
			"conferences": conferences
		}

	async def get_messages(self):
		try:
			async with aiohttp.ClientSession(cookies = self.headers) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci" % (self.msg_host))
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
			async with aiohttp.ClientSession(cookies = self.headers) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci/%s" % (self.msg_host, link.replace("-", "/")))
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
								cl = self.msg_host + cl.split('("')[1].split('",')[0]
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
			async with aiohttp.ClientSession(cookies = self.headers) as session:
				arr_index = datetime.now().weekday()
				REQUESTS[arr_index] += 1
				resp = await session.get("%s/wiadomosci/pobierz_zalacznik/%s" % (self.msg_host, link))
				respF = await session.get("%s/get" % (resp.url))
				headers = respF.headers
				file_I_guess = await respF.read()
			return {
				"headers": headers,
				"content": file_I_guess
			}
		except:
			return None
