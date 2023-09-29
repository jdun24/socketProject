import packet
import struct

class Player:
        useless = " "

        def __init__(self, player_idLen, player_id, ip_address, m_port, r_port, p_port):
                self.player_idLen = player_idLen
                self.player_id = player_id
                self.ip_address = ip_address
                self.m_port = m_port
                self.r_port = r_port
                self.p_port = p_port



        def to_bytes(self):
                if not isinstance(self.player_id, str):
                        self.player_id = self.player_id.decode('utf-8')
                if not isinstance(self.ip_address, str):
                        self.ip_address = self.ip_address.decode('utf-8')

                # Convert the packet to bytes for sending
                return struct.pack('!i' + str(len(self.player_id)) + 's15siii', self.player_idLen, self.player_id.encode(), self.ip_address.encode(), self.m_port, self.r_port, self.p_port)

        @classmethod
        def from_bytes(cls, data):
                idLength = int(data[3])

                # Create a SamplePacket object from received bytes
                player_idLen, player_id, ip_address, m_port, r_port, p_port = struct.unpack('!i' + str(idLength) + 's15siii', data)
                return cls(player_idLen, player_id.decode(), ip_address.decode(), m_port, r_port, p_port)


        def print(self):
                print( "Player ID: " + self.player_id + "\nIP Address: " +  self.ip_address + "\nM Port: ", self.m_port, "\nR Port: ", self.r_port, "\nP Port: ", self.p_port)


        @classmethod
        def populateFromPacket(cls, gamePacket):
                print(gamePacket.message.decode() + "\n")
                useless, playerID, iP_address, m_port, r_port, p_port = gamePacket.message.decode().split()
                return cls(len(playerID), str(playerID), str(iP_address), int(m_port), int(r_port), int(p_port), )
