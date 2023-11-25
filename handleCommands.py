import player
import game
import packet
#<------------------------ reg Player Functions ------------------------>
def handle_reg_player(regPlayers, gamePacket, sock, clientAddr):
	if dupeRegPlayers(regPlayers, gamePacket) == False:
		gamePacket.command += 1
		#check for valid ports for my group
		useless, uselesss, uselessss, m_port, r_port, p_port = gamePacket.message.split()
		if validPorts(int(m_port), int(r_port), int(p_port)) == True:
			regPlayers.append( player.Player.populateFromPacket(gamePacket) )
			sock.sendto(gamePacket.to_bytes(), clientAddr)
			return 1
		else:
			gamePacket.message = "Invalid Port, please use ports 27000 - 27499"
			gamePacketLen = len(gamePacket.message)
			return 1

def dupeRegPlayers(regPlayers, gamePacket):
	splitstr = gamePacket.message.split()
	#ONLY WORKS FOR REGISTER|DE-REGISTER PLAYER, register joe 10.12.130.70, joe is spot 1 in splstr
	for p in regPlayers:
		if p.player_id == splitstr[1]:
			return True
	return False

def validPorts(m_port, r_port, p_port):
	if m_port < 27000 or m_port > 27499:
		return False
	if r_port < 27000 or r_port > 27499:
		return False
	if p_port < 27000 or p_port > 27499:
		return False
	return True
#<------------------------ Start Game Functions ------------------------>
def handle_start_game(regPlayers, regGames, gamePacket, sock, clientAddr):
	splitstr = gamePacket.message.split()
	numPlayers = int(splitstr[3])
	toBeDealer = splitstr[2]
	if not regGames:
		gameID = 1
	else:
		gameID = len(regGames) + 1

	if handleStartGameChecks(regPlayers, numPlayers, toBeDealer, gameID) == 1:
		gamePacket.command += 1
		gamePacket.utilNum = numPlayers + 1
		gamePacket.message = ("Starting game with ID: " + str(gameID))
		gamePacket.messageLen = len(gamePacket.message)

		sock.sendto(gamePacket.to_bytes(), clientAddr)
		playerList = list()
		for p in regPlayers:
			if p.inGame == gameID and p.player_id == toBeDealer:
				sock.sendto(p.to_bytes(), clientAddr)
				playerList.append(p)
				dealerIP = p.ip_address
				m_port = p.m_port
				r_port = p.r_port
				p_port = p.p_port
				break
		for p in regPlayers:
			if p.inGame == gameID and p.player_id != toBeDealer:
				sock.sendto(p.to_bytes(), clientAddr)
				playerList.append(p)
		regGames.append(game.Game.createGame(toBeDealer, dealerIP, m_port, r_port, p_port, numPlayers + 1, gameID, playerList))
	return 1

def handleStartGameChecks(regPlayers, numPlayers, toBeDealer, gameID):
	availPlayers = 0
	dealerFound = False
	i = 0
	for p in regPlayers:
		if p.player_id == toBeDealer:
			if p.inGame == 0:
				dealerFound = True
				regPlayers[i].inGame = gameID
				break
			else:
				print("Error:- handleStartGameChecks()\tDealer already a part of a game")
				return 0
		i += 1
	i = 0
	addedPlayers = 0
	for p in regPlayers:
		if p.inGame == 0 and addedPlayers < numPlayers:
			availPlayers += 1
			regPlayers[i].inGame = gameID
			addedPlayers += 1
		i += 1
	if numPlayers > availPlayers:
		print("Error:- handleStartGameChecks()\tNot enough Available players!\n")
		return 0
	if numPlayers < 1 or numPlayers > 4:
		print("Error:- handleStartGameChecks()\tInvalid number of players!\n")
		return 0
	if dealerFound == False:
		print("Error:- handleStartGameChecks()\ttoBeDealer not registered!\n")
		return 0
	return 1
