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
		diff = notifs.copy()
		if not self.notifications[user]:
			self.notifications[user] = notifs
		for sub in self.notifications[user]:
			diff[sub] -= self.notifications[user][sub]
		self.notifications[user] = notifs
		return diff
