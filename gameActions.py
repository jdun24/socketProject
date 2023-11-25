import random
import time
from packet import SamplePacket
import pdb

def shuffleDeck():
	#deck = [1, 14, 27, 40, 2, 15, 28, 41, 3, 16, 29, 42, 4, 17, 30, 43, 5, 18, 31, 44, 6, 19, 32, 45]
	deck = list(range(1, 53))
	random.shuffle(deck)
	return deck

def pickCard(deck):# for dealing only 
	if not deck:
		return -1
	else:
		card = deck[random.randint(0, len(deck) - 1)]
		deck.remove(card)
		return card

def fishCard(deck, desiredCard):# for Go Fish only
	if not deck:
		return -1, False
	elif not desiredCard:
		card = deck[random.randint(0, len(deck) - 1)]
		deck.remove(card)
		return card, False
	else:
		card = deck[random.randint(0, len(deck) - 1)]
		deck.remove(card)
		if removeSuit(desiredCard) == removeSuit(intToCard(card)):
			return card, True
		return card, False

def removeSuit(cardStr):
	if cardStr[0] == "1":#its a 10
		return "10"
	else:
		return cardStr[0]

def dealToPlayers(sock, playerList, deck, dealerHand, sqn):
	if len(playerList) > 4:#deal 5 to each
		amt = 5
	else:
		amt = 7
	for i in range(0,amt):
		for p in playerList[1:]:#skips dealer
			drawnCard = pickCard(deck)
			if not drawnCard:
				return -1
			sqn += 1
			if i == amt - 1:#last card, modify msg to tell client to print their hand
				gamePacket = SamplePacket(4, "Last", 2, drawnCard, sqn + 1, True)	
			else:
				gamePacket = SamplePacket(0, "", 2, drawnCard, sqn + 1, True)
			ip = p.ip_address.replace('\x00', '')
			sock.sendto(gamePacket.to_bytes(), (str(ip), p.r_port))
		#deal to dealer last
		dealtCard = pickCard(deck)
		dealerHand.append( dealtCard )

	yourTurnPacket = SamplePacket(0, "", 10, 0, sqn + 2, True)
	ip = playerList[1].ip_address.replace('\x00', '')#player to his left
	sock.sendto(yourTurnPacket.to_bytes(), (str(ip), playerList[1].r_port))
	printHand(dealerHand)
	return 1

def printHand(hand):
	print("My Hand = [", end = "")
	for i, card in enumerate(hand):
		print(intToCard(card), end="")
		if i != len(hand) - 1:
			print(", ", end = "")
	print("]")

def intToCard(card_num):
	suits = ['C', 'D', 'H', 'S']
	ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
	if 1 <= card_num <= 52:
		rank_index = (card_num - 1) % 13
		suit_index = (card_num - 1) // 13

		cardName = ranks[rank_index] + suits[suit_index]
		return cardName
	elif card_num ==  -1:
		return "Pond is out of fish :("
	else:
		print("Invalid Card Number")

def cardToInt(card):
	suits = ['C', 'D', 'H', 'S']
	ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

	rank = card[:-1]
	suit = card[-1]
	if rank in ranks and suit in suits:
		rank_index = ranks.index(rank)
		suit_index = suits.index(suit)
		card_num = suit_index * 13 + rank_index + 1
		return card_num
	else:
		print("Invalid Card Format")
		return None

def check_four_of_a_kind(hand):
	rank_counts = {}  # Dictionary to store counts of each rank

	for card in hand:
		#card_int = cardToInt(card)
		rank = intToCard(card)[:-1]  
		rank_counts[rank] = rank_counts.get(rank, 0) + 1
	ranksToRemove = []
	for rank, count in rank_counts.items():
		if count == 4:
			ranksToRemove.append(rank)

	for rank in ranksToRemove:
		hand[:] = [card for card in hand if intToCard(card)[:-1] != rank]
	return len(ranksToRemove) > 0, ranksToRemove  

def printBooks(books):
	print(len(books), " Book/s = [", end = "")
	for i, book in enumerate(books):
		print(str(book) + "s", end="")
		if i != len(books) - 1:
			print(", ", end = "")
	print(" ]")

