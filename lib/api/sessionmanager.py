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

	def getL(self, user):
		try:
			return self.sessions[user]
		except:
			return None

	def saveL(self, user, session):
		try:
			self.sessions[user] = session
		except:
			pass

	def getL2(self, user):
		try:
			return self.sessions[user]
		except:
			return None

	def saveL2(self, user, session):
		try:
			self.sessions[user] = session
		except:
			pass
