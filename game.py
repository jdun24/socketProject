import struct

class Game:
	def __init__(self, dealerLen, toBeDealer, dealerIP, dealer_m_port, dealer_r_port, dealer_p_port, numPlayers, gameID, playerList):
		self.dealerIdLen = dealerLen
		self.dealerId = toBeDealer
		self.dealerIP = dealerIP
		self.dealer_m_port = dealer_m_port
		self.dealer_r_port = dealer_r_port
		self.dealer_p_port = dealer_p_port

		self.playerAmt = numPlayers
		self.gameId = gameID
		self.playerList = playerList

	def to_bytes(self):
		if not isinstance(self.dealerId, str):
			self.dealerId = self.dealerId.decode('utf-8')
		return struct.pack('!i' + str(len(self.dealerId)) + 's15siiiii', self.dealerIdLen, self.dealerId.encode(), self.dealerIP.encode(), self.dealer_m_port, self.dealer_r_port, self.dealer_p_port, self.playerAmt, self.gameId)

	@classmethod
	def from_bytes(cls, data):
		idLength = int(data[3])

		dealerIdLen, dealerId, dealerIP, dealer_m_port, dealer_r_port, dealer_p_port, playerAmt, gameId = struct.unpack('!i' + str(idLength) + 's15siiiii', data)
		return cls(dealerIdLen, dealerId.decode(), dealerIP, dealer_m_port, dealer_r_port, dealer_p_port, playerAmt, gameId, list())

	def print(self):
		print("<---------- GameID " + str(self.gameId) + "---------->\nDealer:\t" + str(self.dealerId))

	@classmethod
	def createGame(cls, dealerID, dealerIP, dealer_m_port, dealer_r_port, dealer_p_port, numPlayers, gameID, playerList):
		return cls(len(dealerID) ,dealerID, dealerIP, dealer_m_port, dealer_r_port, dealer_p_port, numPlayers, gameID, playerList)
