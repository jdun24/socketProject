import struct
import sys

REGISTER = 100
QPLAYER = 200
STARTG = 300
QGAME = 400
ENDG = 500
DEREGISTer = 600


class SamplePacket:
        def __init__(self, messageLen, message, command, utilNum):
                self.command = command
                self.utilNum = utilNum      # used to tell the client how many packets to expect
                self.message = message
                self.messageLen = messageLen

        def to_bytes(self):
                if not isinstance(self.message, str):
                        self.message = self.message.decode('utf-8')#not sure why i need this, problem arose with query players, to_bytes states that message is in byte form, when should be in str

                # Convert the packet to bytes for sending
                return struct.pack('!i' + str(self.messageLen) + 'sii', self.messageLen, self.message.encode(), self.command, self.utilNum)

        @classmethod
        def from_bytes(cls, data):
                mLength = int(data[3])

                # Create a SamplePacket object from received bytes
                messageLen, message, command, utilNum = struct.unpack('!i' + str(mLength) + 'sii', data)
                return cls(messageLen, message, command, utilNum)

        def __str__(self):
                return f"Command: {self.command}, Field: {self.field}, Message: {self.message.decode()}"

        def print(self):
                print("------------<PACKET>------------")
                print("\tCommand: ", self.decode(self.command))
                print("\tMessage type: ", self.decode(self.utilNum))
                print("\tMessage: ", self.message)

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
                        if parsedStr[0] == "query" and parsedStr[1] == "players":
                                self.command = 200
                        if parsedStr[0] == "start" and parsedStr[1] == "game":
                                self.command = 300
                        if parsedStr[0] == "query" and parsedStr[1] == "games":
                                self.command = 400
                        if parsedStr[0] == "end":
                                self.command = 500
                        if parsedStr[0] == "de-register":
                                self.command = 600
        @staticmethod
        def decode(str):
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
                print("FATAL ERROR: checkArgs missed all cases\n\n")
                return False
