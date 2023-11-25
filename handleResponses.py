import player
import game
from handleGame import handleGameDealer
#<-------------------- Query Responses -------------------->

def handle_successfull_query_players(response, sock, fromAddr, expected_responses, recieved_responses):
	print("Received Query Players Response from server on IP address:", fromAddr[0])
	#response.print()
	while recieved_responses < expected_responses:
		playerData, server_address = sock.recvfrom(1024)
		playerToPrint = player.Player.from_bytes(playerData)
		playerToPrint.print()
		recieved_responses += 1

#<-------------------- Query Games -------------------->
#def handle_failed_start_game(response, sock, fromAddr):
#	print("Start Game returned 0, Failed!")

def handle_successfull_start_game(response, sock, fromAddr, expected_responses, recieved_responses):
	print(response.message)
	firstRecieve = True
	playerList = list()
	while recieved_responses < expected_responses:
		if firstRecieve == True:
			dealerData, server_address = sock.recvfrom(1024)
			dealer = player.Player.from_bytes(dealerData)
			dealerIP, m_port, r_port, p_port = dealer.ip_address, dealer.m_port, dealer.r_port, dealer.p_port
			dealer.print()
			playerList.append(dealer)
			firstRecieve = False
		else:
			playerData, server_address = sock.recvfrom(1024)
			playerObj = player.Player.from_bytes(playerData)
			playerObj.print()
			playerList.append(playerObj)
		recieved_responses += 1
	handleGameDealer(sock, fromAddr, dealerIP, m_port, r_port, p_port, expected_responses - 1, playerList)
	return


#<-------------------- Query Games -------------------->
def handle_failed_query_games(response, sock, fromAddr):
	print(response.message)

def handle_successfull_query_games(response, sock, fromAddr, expected_responses, recieved_responses):
	print(response.message)
	#pdb.set_trace()
	while recieved_responses < expected_responses:
		gameData, server_address = sock.recvfrom(1024)
		gameToPrint = game.Game.from_bytes(gameData)
		gameToPrint.print()
		recieved_responses += 1
		for i in range(0, gameToPrint.playerAmt):
			playerData, server_address = sock.recvfrom(1024)
			playerToPrint = player.Player.from_bytes(playerData)
			playerToPrint.print()
			recieved_responses += 1
