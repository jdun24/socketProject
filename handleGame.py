import socket
import select
from packet import SamplePacket
from player import Player
from gameHandler import *
from gameActions import *
import pdb

#dealers loop
def handleGameDealer(sock, serverAddr, dealerIP, m_port, r_port, p_port, numPlayers, playerList):
	sockets = {}
	readyPlayers = 0
	dealerIP = dealerIP.replace('\0', '')
	playerToLeft = playerList[1]
	bindSocket(sockets, m_port, r_port, p_port, dealerIP)
	ringCheckFinished = False
	hasDealt = False

	#in game properties
	deck = shuffleDeck()
	books = list()
	myHand = list()
	playerScores = list()
	playerScoreNum = 0
	gameDone = False
	processed_sqn = set() #makes sure packets are only executing once
	weDone = False
	while weDone == False:
		read_sockets = list(sockets.values())
		readable, _, _ = select.select(read_sockets, [], [])

		for s in readable:
			data, addr = s.recvfrom(1024)
			response = packet.SamplePacket.from_bytes(data)

			if ringCheckFinished == False:
				readyPlayers += 1

			if readyPlayers == numPlayers and ringCheckFinished == False and response.sqn not in processed_sqn:
				#playerList[0] is dealer
				startRingCheck(sock, playerToLeft, playerToLeft.r_port, numPlayers, playerList, response.sqn)
				ringCheckFinished = True
				processed_sqn.add(response.sqn)
			else:
				if hasDealt == False and response.sqn not in processed_sqn and ringCheckFinished == True:
					dealToPlayers(sock, playerList, deck, myHand, response.sqn + 1)
					hasDealt = True
					processed_sqn.add(response.sqn)
				elif gameDone == False and response.sqn not in processed_sqn and ringCheckFinished == True:
					gameDone = dealGameResponse(response, deck, addr, sock, (dealerIP, p_port), playerToLeft, True, playerList, myHand, books)
					if gameDone == None:
						gameDone = False
					checkBookProcedure(books, myHand)
				if gameDone == True and response.sqn not in processed_sqn and ringCheckFinished == True:
					if response.command == 8:
						playerScoreNum += 1
						playerScores.append(response.utilNum)
						if playerScoreNum == numPlayers:
							handleEndGame(playerScores, len(books), playerList, sock, response)
							processed_sqn.add(response.sqn)
							weDone = True
							for p in playerList:
								p.inGame = 0
							break
						

def handleEndGame(playerScores, dealerScore, playerList, sock, response):
	if dealerIsHighest(playerScores, dealerScore) == True:
		for i, p in enumerate(playerList):
			if i == 0:#dealer
				print("Congrats, Dealer Won with, ", dealerScore, " Books!!!")
			else:
				msg = "Sorry, you lost to the Dealer with " + str(dealerScore) +  " books :("
				gamePacket = SamplePacket(len(msg), msg, 9, 0, response.sqn + 1, False)
				sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.r_port))
	else:
		winnerID, score = pairScoresToPlayer(playerList, playerScores, dealerScore)
		if winnerID == "tie":
			for p in playerList:
				msg = "A tire occured with, "+ str(score) + " Books. Better luck next time"
				p.ip_address = p.ip_address.replace("\x00", "")
				gamePacket = SamplePacket(len(msg), msg, 9, 0, response.sqn + 1, False)
				sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.r_port))
		else:		
			for i, p in enumerate(playerList):
				if p.player_id == winnerID:
					maxPlayer_id = p.player_id
					msg = "Congrats " + p.player_id + ", you won with, "+ str(score) + " Books!!!"
					p.ip_address = p.ip_address.replace("\x00", "")
					gamePacket = SamplePacket(len(msg), msg, 9, 0, response.sqn + 1, False)
					sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.r_port))
					break
			for i, p in enumerate(playerList):
				if p.player_id != winnerID:
					msg = "Sorry, you lost to " + winnerID + " with " + str(score) +  " books :("
					p.ip_address = p.ip_address.replace("\x00", "")
					gamePacket = SamplePacket(len(msg), msg, 9, 0, response.sqn + 1, False)
					sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.r_port))
		print("Sorry, you lost to " + winnerID + " with " + str(score) +  " books :(")

def pairScoresToPlayer(playerList, playerScores, dealerScore):
	player_scores = {}
	for i,p in enumerate(playerList):
		if i == 0:
			player_scores[playerList[i].player_id] = dealerScore
		else:
			player_scores[playerList[i].player_id] = playerScores[i - 1]
	highest_score_player = max(player_scores, key=player_scores.get)
	highestScore = player_scores[highest_score_player]

	players_with_max_score = [player for player, score in player_scores.items() if score == highestScore]
	if len(players_with_max_score) != 1:
		return "tie", highestScore

	return highest_score_player, highestScore

def dealerIsHighest(playerScores, dealerScore):
	for score in playerScores:
		if score >= dealerScore:
			return False
	return True
#regular players loop
def handleInGame(sock, serverAddr, cl_ip, m_port, r_port, p_port, dealerIP, dealerPort):
	gamePacket = SamplePacket(0, "", 0, 0, 0, True)
	sockets = {}
	ringCheckFinished = False
	bindSocket(sockets, m_port, r_port, p_port, cl_ip) 
	playerToLeft = Player(0, "", "", 0, 0, 0, 0)
	sock.sendto(gamePacket.to_bytes(), (str(dealerIP), dealerPort))

	#in game properties
	myHand = list()
	books = list()
	processed_sqn = set() 
	weDone = False
	while weDone == False:
		read_sockets = list(sockets.values())
		readable, _, _ = select.select(read_sockets, [], [])
		for s in readable:
			data, addr = s.recvfrom(1024)
			response = packet.SamplePacket.from_bytes(data)
			
			if response.sqn not in processed_sqn and response.command != 9:
				dealGameResponse(response, list(), addr, sockets[p_port], (dealerIP, dealerPort), playerToLeft, False, list(), myHand, books)
				checkBookProcedure(books, myHand)
				processed_sqn.add(response.sqn)
			if response.sqn not in processed_sqn and response.command == 9:
				print(response.message)
				processed_sqn.add(response.sqn)
				weDone = True
				break

def checkBookProcedure(books, hand):
	isBook, retBooks = check_four_of_a_kind(hand)
	if isBook == True:
		for book in retBooks:
			books.append(book)
	print("==========< Book Check >==========")
	printBooks(books)
	printHand(hand)
	print("==================================")

def startRingCheck(sock, l, r_port, numPlayers, playerList, newSqn):
	playerStrs = ''
	#dealer strr always first
	dealerStrs = playerList[0].ip_address.replace('\0', '')  + " " + str(playerList[0].r_port) +  " " + str(playerList[0].p_port) + " "
	playerStrs = ""
	for p in playerList[2:]:
		playerStrs += p.ip_address.replace('\0', '')  + " " +  str(p.r_port) + " " + str(p.p_port) + " "
		p.ip_address = p.ip_address.replace('\0', '')
	playerStrs += dealerStrs
	print(playerStrs)
	l.ip_address = l.ip_address.replace("\x00",  "")
	gamePacket = SamplePacket(len(playerStrs), playerStrs, 1, numPlayers, newSqn, True)
	sock.sendto(gamePacket.to_bytes(), (str(l.ip_address), l.r_port))


def bindSocket(sockets, m, r, p, IPtoBind):
	for port in [m, r, p]:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((str(IPtoBind), port))
		sockets[port] = sock

