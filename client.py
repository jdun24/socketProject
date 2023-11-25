import socket
import struct
import sys
from packet import SamplePacket
import packet
from util import handleResponse


ECHOMAX = 1024
ITERATIONS = 25  # Adjust this to the desired number of iterations


def main():
	if len(sys.argv) < 3:
		sys.stderr.write("Usage: {} <Server IP address> <Echo Port>\n".format(sys.argv[0]))
		sys.exit(1)

	servIP = sys.argv[1]
	echoServPort = int(sys.argv[2])

	print("Arguments passed: server IP {}, port {}".format(servIP, echoServPort))

	# Create a datagram/UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Construct the server address
	echoServAddr = (servIP, echoServPort)

	validInput = True
	for i in range(ITERATIONS):

		clientInput = input("Enter Command: ")

		gamePacket = SamplePacket(0, "", 0, 0, 0, True)
		#sets gamePacket according to input
		validInput = gamePacket.parseInput_ForPacket(clientInput)

		# Send the struct to the server
		data = gamePacket.to_bytes()
		sock.sendto(data, echoServAddr)

		# Receive response
		data, fromAddr = sock.recvfrom(ECHOMAX)
		#pdb.set_trace()
		response = packet.SamplePacket.from_bytes(data)
		if response.command != -2 and response.utilNum != -2 and validInput != False:
			if handleResponse(response, sock, fromAddr) == 99:
				break

	sock.close()

if __name__ == "__main__":
	main()
