import player
import game
import packet
from handleResponses import *
from handleCommands import *
from handleGame import handleInGame
import pdb
#for server to handle requests
def handleCommand(regPlayers, regGames, gamePacket, sock, clientAddr):
	#returns 1 on succes, 0 on failure
	if gamePacket.command == 100: #register
		return handle_reg_player(regPlayers, gamePacket, sock, clientAddr)
	if gamePacket.command == 200:#query players
		if not regPlayers:
			gamePacket.message = "Currently No Registered Players, returned 0!"
			gamePacket.messageLen = len(gamePacket.message)
			return 1
		else:
			print("Beginning to send", len(regPlayers), " packet/s to ip:", clientAddr[0], " port: ", clientAddr[1], " ------------\n")
			gamePacket.command += 1
			gamePacket.utilNum = len(regPlayers) #indicate they need to wait for more packets

			#begin sending list of the players to client
			sock.sendto(gamePacket.to_bytes(), clientAddr)
			for p in regPlayers:
				sock.sendto(p.to_bytes(), clientAddr)
			return 1
	if gamePacket.command == 300:#Start Game
		return handle_start_game(regPlayers, regGames, gamePacket, sock, clientAddr)

	if gamePacket.command == 400:#query games
		if len(regGames) == 0:
			gamePacket.message = ("No games have been started!!")
			gamePacket.messageLen = len(gamePacket.message)
			sock.sendto(gamePacket.to_bytes(), clientAddr)
			return 1

		gamePacket.utilNum = len(regGames)
		for game in regGames:
			gamePacket.utilNum += game.playerAmt
		gamePacket.command += 1
		gamePacket.message = (str(len(regGames)) + " game/s are active!!")
		gamePacket.messageLen = len(gamePacket.message)
		sock.sendto(gamePacket.to_bytes(), clientAddr)
		for game in regGames:
			sock.sendto(game.to_bytes(), clientAddr)
			for p in game.playerList:
				sock.sendto(p.to_bytes(), clientAddr)

		return 1

	if gamePacket.command == 600:#de-register
		if dupeRegPlayers(regPlayers, gamePacket) == False:
			print("Error:- handleCommand()\tPlayer doesn't exist!\n")
			return 0
		#remove from regPlayers
		else:
			gamePacket.command += 1
			splitStr = gamePacket.message.split()
			player_to_dereg = splitStr[1]

			for p in regPlayers:
				if p.player_id == player_to_dereg:
					regPlayers.remove(p)
					print("Removed: ", p.player_id)
					gamePacket.message = "Thank you for Playing!"
					gamePacket.messageLen = len(gamePacket.message)
					sock.sendto(gamePacket.to_bytes(), clientAddr)
					return 1
		return 0
	if gamePacket.command == 700:

		splitStr = gamePacket.message.split()
		player = splitStr[2]

		for p in regPlayers:
			if player == p.player_id:
				for game in regGames:
					if game.gameId == p.inGame:
						if p.inGame != 0:
							gamePacket.command += 1
							gamePacket.message = p.ip_address + ' ' + str(p.m_port) + ' ' +  str(p.r_port) + ' ' + str(p.p_port)
							gamePacket.message += ' ' + str(game.dealerIP) + ' '+ str(game.dealer_p_port)
							gamePacket.messageLen = len(gamePacket.message)
							sock.sendto(gamePacket.to_bytes(), clientAddr)
							return 1
						else:
							gamePacket.message = "Player ", player, " is not registered"
							gamePacket.messageLen = len(gamePacket.message)
							sock.sendto(gamePacket.to_bytes(), clientAddr)
							return 1
		gamePacket.message = "Player ", player, " has not yet found a game"
		gamePacket.messageLen = len(gamePacket.message)
		sock.sendto(gamePacket.to_bytes(), clientAddr)
		return 1

	print("FATAL ERROR :- handleCommand missed ALL cases!!! command = ", gamePacket.command)
	return -1

#for client to handle responses
def handleResponse(response, sock, fromAddr):
	expected_responses = response.utilNum
	recieved_responses = 0
