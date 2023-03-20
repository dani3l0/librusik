class SessionManager:
	def __init__(self, database):
		self.sessions = {}
		self.notifications = {}
		self.updatedb(database)

	def updatedb(self, database):
		for user in database:
			if user not in self.sessions:
				self.sessions[user] = None
				self.notifications[user] = []
		s_ = self.sessions.copy()
		for user in s_:
			if user not in database:
				del self.sessions[user]
				del self.notifications[user]

	def get(self, user):
		try:
			return self.sessions[user]
		except:
			return None

	def save(self, user, session):
		try:
			self.sessions[user] = session
		except:
			pass

	def get_notifications(self, user, notifs):
		# try:
		# 	notifs_cached = []
		# 	count = True
		# 	if not self.notifications[user]:
		# 		count = False
		# 	for n in self.notifications[user]:
		# 		notifs_cached = n
		# 	notifs_str = []
		# 	for n in notifs:
		# 		notifs_str.append(str(n))
		# 	n_count = len(notifs) - len(set(notifs_cached) & set(notifs_str))
		# 	self.notifications[user] = notifs
		# 	return {
		# 		"new": n_count * count,
		# 		"notifications": self.notifications[user]
		# 	}
		# except:
		# 	return {
		# 	"new": 0,
		# 	"notifications": self.notifications[user]
		# }