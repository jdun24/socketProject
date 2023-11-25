import packet
import socket
import struct
import player
from packet import SamplePacket
from gameActions import *

import pdb

def dealGameResponse(response, deck, fromAddr, sock, dealerAddr, playerToLeft, isDealer, playerList, myHand, books):
	if response.command == 1:#ring checking
		if response.utilNum == 0:#ring check done, return to dealer
			gamePacket = SamplePacket(0, "", 1, 0, response.sqn + 1, response.isPond)
			sock.sendto(gamePacket.to_bytes(), dealerAddr)
		else:
			parsedStr = response.message.split()
			ip, r, p = parsedStr[:3]
			playerToLeft.ip_address = ip
			playerToLeft.r_port = int(r)
			playerToLeft.p_port = int(p)

			remaining = ' '.join(parsedStr[3:])
			response.utilNum -= 1
			response.message = remaining
			response.messageLen = len(response.message)
			response.sqn += 1

			sock.sendto(response.to_bytes() , (playerToLeft.ip_address, playerToLeft.r_port))

	if response.command == 2:#dealt a card
		myHand.append(response.utilNum)
		if len(response.message) > 0:
			print(intToCard(response.utilNum))

	if response.command == 3:#askedForCard command sent to dealer
		splitStr = response.message.split()
		player = splitStr[0]
		if checkPlayerInGame(player, playerList) == False:
			gamePacket = SamplePacket(0, "", 0, 0, 0, response.isPond)
			gamePacket.message = player + " does not exist in this game"
			gamePacket.command = 11
			sock.sendto(gamePacket.to_bytes(), fromAddr)
			return
		if checkPlayerInGame(player, playerList) == False and isDealer:
			print(player, " does not exist in this game")
			takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
			return
		card = splitStr[1]
		if player == "dealer":
			gamePacket = checkHand(card, myHand, response)
			if gamePacket.utilNum == 0:
				goFishedCard, isCatch = fishCard(deck, card)
				gamePacket.message = goFishProcedure(goFishedCard, card, isCatch, response)
				gamePacket.messageLen = len(gamePacket.message)
				gamePacket.isPond = response.isPond
				gamePacket.utilNum = response.utilNum
			sock.sendto(gamePacket.to_bytes(), fromAddr)
		else:
			#forward packet but add the ip it came from
			message = player + " " + card + " " + str(fromAddr[0]) + " " + str(fromAddr[1])
			for p in playerList:
				if player == p.player_id:
					gamePacket = SamplePacket(len(message), message, 4, 0, response.sqn + 1, response.isPond)
					sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.p_port))
					break
		
	if response.command == 4:#asked for a card
		askedForCard = response.message.split()[1]
		gamePacket = checkHand(askedForCard, myHand, response)
		sock.sendto(gamePacket.to_bytes(), dealerAddr)

	if response.command == 5:#returning to dealer or player
		if isDealer == True:#forward this to the player
			if response.utilNum == 0 and forwardable(response):
				no, desiredCard, forwardToIP, forwardToPort = response.message.split()
				goFishedCard, isCatch = fishCard(deck, desiredCard)
				response.message = goFishProcedure(goFishedCard, desiredCard, isCatch, response)
				response.messageLen = len(response.message)
				if goFishedCard == -1:
					response.utilNum = -1
				sock.sendto(response.to_bytes(), (forwardToIP, int(forwardToPort)))
				return
			elif forwardable(response):
				splitStr = response.message.split()
				forwardToIP = splitStr[response.utilNum + 2]
				forwardToPort = int(splitStr[response.utilNum + 3])
				sock.sendto(response.to_bytes(), (forwardToIP, forwardToPort))
				return
			#cases where no forwarding is needed because asker was the dealer
			elif response.utilNum == 0:
				desiredCard = response.message.split()[1]
				goFishedCard, isCatch = fishCard(deck, desiredCard)
				if goFishedCard == -1:
					print("They didn't have the card and there are no fish left :(")
					passPacket = SamplePacket(0, "", 12, 1, response.sqn + 1, False)
					sock.sendto(passPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
				else:
					myHand.append(goFishedCard)
					
					if isCatch == True:
						print("HOW AWFUL LUCKY!! You fished what you were looking for a ", intToCard(goFishedCard), "!!!")
						takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
					else:
						print("You GoFished for", intToCard(goFishedCard))
						printHand(myHand)
						yourTurnPacket = SamplePacket(0, "", 10, 0, response.sqn + 1, response.isPond)
						sock.sendto(yourTurnPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
			else:
				addCardsFromPacket(response, myHand, books)
				takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
				return
			
		else:
			if response.utilNum > 0:
				addCardsFromPacket(response, myHand, books)
				takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
			else:
				if response.utilNum != -1:
					print("You GoFished")
					response.utilNum += 1
					addCardsFromPacket(response, myHand, books)
					if response.message.split()[1] == "True":#isCatch was true
						takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
						return
					else:

						yourTurnPacket = SamplePacket(0, "", 10, 0, response.sqn + 1, response.isPond)
						sock.sendto(yourTurnPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
				else:
					print(response.message)
					yourTurnPacket = SamplePacket(0, "", 10, 0, response.sqn + 1, False)
					sock.sendto(yourTurnPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
			return
				
	if response.command == 6:#forced goFish to dealer
		if isDealer == False:
			print("Forced GoFish (command 6) packet was sent to a non dealer")
		else:
			goFishedCard, isCatch = fishCard(deck, None)
			msg = goFishProcedure(goFishedCard, None, False, response)
			gamePacket = SamplePacket(len(msg), msg, 5, response.utilNum, response.sqn + 1, response.isPond)
			sock.sendto(gamePacket.to_bytes(), fromAddr)
	if response.command == 7:
		gamePacket = SamplePacket(0, "", 8, len(books), response.sqn + 1, False)
		sock.sendto(gamePacket.to_bytes(), dealerAddr)
	if response.command == 10:#your-turn
		takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
	if response.command == 11:#take a turn and print message, an error happened with your command
		print(response.message)
		takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
	if response.command ==12:

		if isDealer == True and response.utilNum >= len(playerList):
			findWinner(sock, playerList, response)
			return True
		elif not myHand and response.isPond == True:
			gamePacket = SamplePacket(0, "", 6, response.utilNum, response.sqn + 1, response.isPond)
			sock.sendto(gamePacket.to_bytes(), dealerAddr)
		elif not myHand and response.isPond == False:
			passPacket =  SamplePacket(0, "", 12, response.utilNum + 1, response.sqn + 1, False)
			sock.sendto(passPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
		else:
			takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck)
		

def findWinner(sock, playerList, response):
	gamePacket = SamplePacket(0, "", 7, 0, response.sqn + 1, False)
	for i, p in enumerate(playerList):
		if i != 0: 
			p.ip_address = p.ip_address.replace("\x00", "")
			sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.r_port))

def checkPlayerInGame(player, playerList):
	for p in playerList:
		if p.player_id == player or player == "dealer":
			return True
	return False

def goFishProcedure(goFishedCard, desiredCard, isCatch, response):
	if goFishedCard == -1:#create an actualy packet, set utilNum to -1, set message len too
		response.isPond = False
		response.utilNum = -1
		return "They didn't have the card and there are no fish left :("
		
	else:
		if isCatch == True:
			return intToCard(goFishedCard) + " True"
		else:
			return intToCard(goFishedCard) + " False"

def takeATurn(response, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, deck):
	print("Your Turn!")
	printHand(myHand)
	print(response.message)
	
	if not myHand:#a Forced GoFish
		if isDealer == True:
			goFishedCard, isCatch = fishCard(deck, None)
			if goFishedCard == -1:
				print("No fish left in the pond:(")
				yourTurnPacketPass = SamplePacket(0, "", 12, 0, response.sqn + 1, False)
				sock.sendto(yourTurnPacketPass.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
			else:
				print("You GoFished for", intToCard(goFishedCard))
				myHand.append(goFishedCard)
				printHand(myHand)
				yourTurnPacket = SamplePacket(0, "", 10, 0, response.sqn + 1, response.isPond)
				sock.sendto(yourTurnPacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
		else:
			gamePacket = SamplePacket(0, "", 6, 0, response.sqn + 1, response.isPond)
			sock.sendto(gamePacket.to_bytes(), dealerAddr)
	else:
		command = input("Enter Command: ")
		while parseInput(command, response.sqn, sock, dealerAddr, playerToLeft, myHand, playerList, isDealer, response.isPond) == False:
			print("Invalid Command")
			command = input("Enter Command: ")


def addCardsFromPacket(response, myHand, books):
	cardsToAdd = list()
	response.message = response.message.replace("\x00" , "")
	splitStr = response.message.split()
	for i in range(0, response.utilNum):
		cardsToAdd.append(cardToInt(splitStr[i]))
		myHand.append(cardToInt(splitStr[i]))

	print("You Recieved: ", ", ".join(intToCard(card) for card in cardsToAdd))
	checkBookProcedure(books, myHand)

def forwardable(response):
		splitStr = response.message.split()
		if len(splitStr) > response.utilNum + 2:
			return True
		else:
			return False

def checkHand(forCard, hand, response):
	print("You got asked for", forCard + "s")
	utilNumToRespondWith = 0
	cardsToGiveAway = list()
	for card in hand:
		if forCard == removeSuit(intToCard(card)).lower():
			utilNumToRespondWith += 1
			cardsToGiveAway.append(card)

	for card in cardsToGiveAway:
		hand.remove(card)
	if utilNumToRespondWith == 0:#didnt have card
		print("You didn't have, ", str(forCard), "s, responding with Go Fish!!!")
		packetMessage = response.message
	else:
		print("Giving away: ",  ", ".join(intToCard(card) for card in cardsToGiveAway))
		packetMessage = " ".join(intToCard(card) for card in cardsToGiveAway) + " " + response.message
	return SamplePacket(len(packetMessage), packetMessage, 5, utilNumToRespondWith, response.sqn + 1, response.isPond)
			

def parseInput(command, sqn, sock, dealerAddr, playerToLeft, hand, playerList, isDealer, isPond):
	gamePacket = SamplePacket(0, "", 0, 0, 0, isPond)
	parsedStr = command.split()
	if parsedStr[0] == "your-turn":
		gamePacket = SamplePacket(0, "", 10, 0, sqn + 1, isPond)
		sock.sendto(gamePacket.to_bytes(), (playerToLeft.ip_address, playerToLeft.p_port))
		return True

	if parsedStr[0].lower() == "ask" and parsedStr[2].lower() == "for" and hasCard(hand, parsedStr[3]):
		playerID = parsedStr[1]
		desiredCard = parsedStr[3]
		message = playerID + " " + desiredCard
		gamePacket = SamplePacket(len(message), message, 3, 0, sqn + 1, isPond)
		if isDealer == False:
			sock.sendto(gamePacket.to_bytes(), dealerAddr)
		else:
			gamePacket.command = 4
			for p in playerList:
				if playerID == p.player_id:
					sock.sendto(gamePacket.to_bytes(), (p.ip_address, p.p_port))
					break
	else:
		if hasCard(hand, parsedStr[3]) == False:
			print("You don't have any versions of that card!")
			return False
		print("incorrect usage!  ask <playerID | dealer> for <card>")
		return False
		
def hasCard(hand, desiredCard):#checks to make sure you have a card you're asking for
	for card in hand:
		if desiredCard[0] == removeSuit(intToCard(card)).lower()[0]:
			return True
	return False

def checkBookProcedure(books, hand):
	isBook, retBooks = check_four_of_a_kind(hand)
	if isBook == True:
		for book in retBooks:
			books.append(book)
	print("==========< Book Check >==========")
	printBooks(books)
	printHand(hand)
	print("==================================")
