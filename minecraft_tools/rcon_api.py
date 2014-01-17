import select
import socket
import struct

"""
Minecraft RCON Client API

Based on implementation details from http://wiki.vg/Rcon
"""


class MessageTypes(object):
    """ Message types used by the RCON API. Only used when sending data at the
    moment, but could be used to verify the types of incoming data.
    """
    RCON_AUTHENTICATE = 3
    RCON_AUTH_RESPONSE = 2
    RCON_EXEC_COMMAND = 2
    RCON_EXEC_RESPONSE = 0


class ConnectionError(Exception):
    """ Occurs when the client socket fails to connect to the listening RCON
    server.
    """
    pass


class AuthenticationError(Exception):
    """ Occurs when the wrong password is provided to an RCON server.
    """
    pass


class RemoteConsole(object):
    """ The core piece of rcon_api. Connects to a requested server and
    authenticates, then allows commands to be sent with send(). Can also close
    its client socket with disconnect().
    """

    def __init__(self, host, port, password):
        """ Sets up our RemoteConsole, creates the socket, connects to the
        RCON API, and authenticates.

        @param host: Address of the Minecraft server (default: 127.0.0.1)
        @param port: Port RCON is running on (default: 25575)
        @param password: RCON password for the server (required)
        """
        self.host = host
        self.port = port
        self.password = password

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(1.0)
        try:
            self.client.connect((self.host, self.port))
        except:
            raise ConnectionError

        if not self.authenticate():
            raise AuthenticationError

    def send(self, command, authenticate=False):
        """ Creates a packed header struct based on the command parameters,
        and sends the combined header, command, and null byte padding to the
        RCON server.

        Header Struct (little-endian):
            Padded command length (int)
            Message ID (int)
            Message type (int)

        Reads the header from the client socket, then streams data until
        no data is left to be read from the socket. We read 12 bytes at a time
        to receive three 4-byte integers.

        The read loop uses select() to check the client socket for remaining
        data. The client socket is passed in for a readability check, and the
        returned list indicates whether or not data remains to be read. When
        the returned list is empty, the loop ends.

        In this loop, we read from the socket until all data has been received,
        then combine the response and return it along with the response ID,
        which allows us to verify authentication attempts.

        @param command: RCON command to send to the server (e.g. "say hi")
        @param authenticate: Set to True to use the auth message type
        @return: response text (str), message ID (int)
        """
        response = ""
        data_remains = True

        # send the command
        header = struct.pack(
            "<iii",
            len(command) + 10,
            0,
            MessageTypes.RCON_AUTHENTICATE if authenticate is True
            else MessageTypes.RCON_EXEC_COMMAND
        )
        self.client.send(header + command + "\x00\x00")

        # return the response
        response_length, response_id, response_type = struct.unpack(
            "<iii",
            self.client.recv(12)
        )
        while data_remains:
            response_fragment = self.client.recv(response_length - 8)
            response += response_fragment.strip("\x00\x00")
            data_remains = select.select([self.client], [], [], 1.0)[0]
        return response, response_id

    def authenticate(self):
        """ Sends an authentication packet to the RCON server and checks the
        response for a matching message ID. A message ID of -1 indicates
        authentication failure, and a matching message ID (0 in our case)
        indicates success.

        @return: True or False based on authentication success/failure
        """
        response, response_id = self.send(self.password, authenticate=True)
        return response_id == 0

    def disconnect(self):
        """ Close the client socket if connected to the RCON server.
        """
        self.client.close()
