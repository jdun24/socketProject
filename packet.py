import struct
import sys

REGISTER = 100
QPLAYER = 200
STARTG = 300
QGAME = 400
ENDG = 500
DEREGISTer = 600


class SamplePacket:
	def __init__(self, messageLen, message, command, utilNum, sqn, isPond):
		self.command = command
		self.utilNum = utilNum      # used to tell the client how many packets to expect
		self.message = message
		self.messageLen = messageLen
		self.sqn = sqn
		self.isPond = isPond

	def to_bytes(self):
		if not isinstance(self.message, str):
			self.message = self.message.decode('utf-8')#not sure why i need this, problem arose with query players, to_bytes states that message is in byte form, when should be in str

		# Convert the packet to bytes for sending
		return struct.pack('!i' + str(self.messageLen) + 'siiib', self.messageLen, self.message.encode(), self.command, self.utilNum, self.sqn, self.isPond)

	@classmethod
	def from_bytes(cls, data):
		mLength = int(data[3])

		# Create a SamplePacket object from received bytes
		messageLen, message, command, utilNum, sqn, isPond = struct.unpack('!i' + str(mLength) + 'siiib', data)
		return cls(messageLen, message.decode(), command, utilNum, sqn, isPond)

	def __str__(self):
		return f"Command: {self.command}, Field: {self.field}, Message: {self.message.decode()}"

	def print(self):
		print("------------<PACKET>------------")
		print("\tCommand: ", self.command, ":" , self.decode(self.command))
		print("\tutilNum: ", self.utilNum)
		print("\tMessage: ", self.message)
		print("\tSqn: ", self.sqn)
		print("\tisPond: ", self.isPond)

	def parseInput_ForPacket(self, clientInput):
		parsedStr = clientInput.split()
		self.message = clientInput
		self.messageLen = len(clientInput)
		self.utilNum = 0

		if not parsedStr:
			print("Client Input INVALID")
			return none

		if self.checkArgs(parsedStr, clientInput) == True:
			if parsedStr[0] == "register":
				self.command = 100
				return 1
			if parsedStr[0] == "query" and parsedStr[1] == "players":
				self.command = 200
				return 1
			if parsedStr[0] == "start" and parsedStr[1] == "game":
				self.command = 300
				return 1
			if parsedStr[0] == "query" and parsedStr[1] == "games":
				self.command = 400
				return 1
			if parsedStr[0] == "end":
				self.command = 500
				return 1
			if parsedStr[0] == "de-register":
				self.command = 600
				return 1
			if parsedStr[0] == "find" and parsedStr[1] == "game":
				self.command = 700
				return 1
		else:
			return False


	@staticmethod
	def decode(str):
		#in game packets
		if str == 1:
			return "ring Setup"
		if str == 2:
			return "dealt card"
		if str == 3:
			return "asked for card"
		if str == 4:
			return "player responding to dealer"
		if str == 5:
			return "from dealer to player about cards they recieve or go fish"
		if str == 6:
			return "querying for books"
		if str == 7:
			return "responning to query books"
		if str == 8:
			return "dealer confirming a win!"
		if str == 9:
			return "dealer confirming a loss."
		if str == 10:
			return "your-turn"
		if str == 11:
			return "passing"

		#out of game packets
		if str == 100:
			return "register"
		if str == 200:
			return "queryP"
		if str == 300:
			return "startG"
		if str == 400:
			return "queryG"
		if str == 500:
			return "endG"
		if str == 600:
			return "de-register"

	def checkArgs(self, parsedStr, string):
		if parsedStr[0] == "register":
			if string.count(' ') == 5:
				return True
			else:
				print("Error - INCORRECT USAGE -: register <player> <IP-Addy> <mport> <r-port> <p-port>\n")
			return False
		if parsedStr[0] == "query" and parsedStr[1] == "players":
			if string.count(' ') == 1:
				return True
			else:
				print("Error - INCORRECT USAGE -: query players\n")
				return False
		if parsedStr[0] == "start" and parsedStr[1] == "game":
			if string.count(' ') == 3:
				return True
			else:
				print("Error - INCORRECT USAGE -: start game <player to deal> <# of players>\n")
				return False
		if parsedStr[0] == "query" and parsedStr[1] == "games":
			if string.count(' ') == 1:
				return True
			else:
				print("Error - INCORRECT USAGE -: query games\n")
				return False
		if parsedStr[0] == "end":
			if string.count(' ') == 2:
				return True
			else:
				print("Error - INCORRECT USAGE -: end <game-ID> <dealer>\n")
				return False
		if parsedStr[0] == "de-register":
			if string.count(' ') == 1:
				return True
			else:
            			print("Error - INCORRECT USAGE -: de-register <player>\n")
            			return False
		if parsedStr[0] == "find" and parsedStr[1] == "game":
			if string.count(' ') == 2:
				return True
			else:
				print("Error - INCORRECT USAGE -: find game <player_id> :- to find a game\n")
				return False
		print("Invalid Command\n\n")
		return False
