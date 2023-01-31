class SessionManager:
	def __init__(self, database):
		self.sessions = {}
		self.updatedb(database)

	def updatedb(self, database):
		for user in database:
			if user not in self.sessions:
				self.sessions[user] = None
		s_ = self.sessions.copy()
		for user in s_:
			if user not in database:
				del self.sessions[user]

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
