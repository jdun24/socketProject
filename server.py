import socket
import struct
import sys
import packet
import player
from player import Player
from util import handleCommand

import pdb
ECHOMAX = 1024  # Adjust this to your maximum packet size

def main():
	# Check for the correct number of parameters
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: {} <UDP SERVER PORT>\n".format(sys.argv[0]))
		sys.exit(1)

	echoServPort = int(sys.argv[1])  # First argument: local port

	# Create a socket for sending/receiving datagrams
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Bind to the local address
	sock.bind(('', echoServPort))

	print("Server is listening on port:", echoServPort)

	registeredPlayers = []
	registeredGames = []

	while True:  # Run forever
		# Block until receive a message from a client
		data, clientAddr = sock.recvfrom(ECHOMAX)

		# Unpack the received data into the packet structure
		gamePacket = packet.SamplePacket.from_bytes(data)

		#pdb.set_trace()
		if handleCommand(registeredPlayers, registeredGames, gamePacket , sock, clientAddr) == 1:
			print("Successful CommandHandle on IP address:", clientAddr[0], "\n")
		else:
			print("server.py, main():- handleCommand() FAILED\n")
			sock.sendto(packet.SamplePacket(0, "", -2, -2, 0, 1).to_bytes() , clientAddr)


if __name__ == "__main__":
	main()
