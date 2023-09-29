import player
import packet

#for server to handle requests
def handleCommand(regPlayers, gamePacket, sock, clientAddr):
        #returns 1 on succes, 0 on failure

        if gamePacket.command == 100: #register
                if dupeRegPlayers(regPlayers, gamePacket) == False:
                        regPlayers.append( player.Player.populateFromPacket(gamePacket) )
                        return 1
        if gamePacket.command == 200:#query players
                if not regPlayers:
                        print("NO REGISTERED PLAYERS: RETURN SET 0\n")
                        return 0
                else:
                        print("Beginning to send", len(regPlayers), " byte/s to ip:", clientAddr[0], " port: ", clientAddr[1], " ------------\n")
                        i = 1
                        gamePacket.command = gamePacket.command + 1 #commands with a 1 at the end indicate that commands response, 
                        gamePacket.utilNum = len(regPlayers) #indicate they need to wait for more packets

                        #begin sending list of the players to client
                        sock.sendto(gamePacket.to_bytes(), clientAddr)
                        for p in regPlayers:
                                playerData = p.to_bytes()
                                sock.sendto(playerData, clientAddr)
                        return 1
        if gamePacket.command == 400:#query game
                gamePacket.command = gamePacket.command + 1
                gamePacket.message = ("No games have been started!!")
                sock.sendto(gamePacket.to_bytes(), clientAddr)
                return 1
        if gamePacket.command == 600:#de-register

                if dupeRegPlayers(regPlayers, gamePacket) == False:
                        print("Error:- handleCommand()\tPlayer doesn't exist!\n")
                        return 0
                #remove from regPlayers
                else:
                        gamePacket.command = gamePacket.command + 1
                        splitStr = gamePacket.message.decode().split()
                        player_to_dereg = splitStr[1]

                        for p in regPlayers:
                                if p.player_id == player_to_dereg:
                                        regPlayers.remove(p)
                                        print("Removed: ", p.player_id)
                                        return 1
                return 0

        print("FATAL ERROR :- handleCommand missed ALL cases!!! command = ", gamePacket.command)
        return -1

#for client to handle responses
def handleResponse(response, sock, fromAddr):

        expected_responses = response.utilNum
        recieved_responses = 0
        if response.command == 201: #201 indicates a response for register, later this will be put into a handleResponse function inside util.py
                print("Received Query Players Response from server on IP address:", fromAddr[0])
                response.print()
                while recieved_responses < expected_responses:
                        playerData, server_address = sock.recvfrom(1024)
                        playerToPrint = player.Player.from_bytes(playerData)
                        playerToPrint.print()
                        recieved_responses += 1
        if response.command == 101:#register respones
                print("Player successfully registered!!\n")
        if response.command == 401:#query games  response
                print("No games are currently started!")
        if response.command == 601:#de-register
                print("Player successfully de-registered\n")




def dupeRegPlayers(regPlayers, gamePacket):
        splitstr = gamePacket.message.decode().split()
        #ONLY WORKS FOR REGISTER|DE-REGISTER PLAYER, register joe 10.12.130.70, joe is spot 1 in splstr
        print("printing from dupeReg spltstr[1] =  " + splitstr[1] + "\n")
        for p in regPlayers:
                if p.player_id == splitstr[1]:
                        return True
        return False
