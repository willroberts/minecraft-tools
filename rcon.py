import argparse
import socket
import select
import struct


class MessageTypes(object):
    """ Message types used by the RCON API. Only used when sending data at the
    moment, but could be used to verify the types of incoming data.
    """
    RCON_AUTHENTICATE = 3
    RCON_AUTH_RESPONSE = 2
    RCON_EXEC_COMMAND = 2
    RCON_RESPONSE_VALUE = 0


def parse_arguments(args=None):
    """ Provides host, port, and password options for command-line use. The
    RCON API requires a password.
    """
    parser = argparse.ArgumentParser(description="Connect to a Minecraft RCON server")
    parser.add_argument("--host", dest="host", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=25575)
    parser.add_argument("--password", dest="password", type=str, required=True)
    return parser.parse_args()


def create_packet(message, message_type):
    """ Creates a packed header struct based on the message parameters,
    and returns the combined header, message, and null byte padding.

    Header Struct (little-endian):
        Padded message length (int)
        Message ID (int)
        Message type (int)

    Based on implementation details from http://wiki.vg/Rcon#Packet_Format
    """
    header = struct.pack(
        "<iii",  # format: little-endian byte order, three integers
        len(message) + 10,  # padded message length
        0,  # message id
        message_type
    )
    return header + message + "\x00\x00"  # end with two null bytes


def process_response(client):
    """ Reads the header from the client socket, then streams data until
    no data is left to be read from the socket. The header struct has the
    same format as in process_command(), so we read 12 bytes at a time (to
    receive three 4-byte integers).

    The read loop uses select() to check the client socket for remaining
    data. The client socket is passed in for a readability check, and the
    returned list indicates whether or not data remains to be read. When
    the returned list is empty, the loop ends.

    In this loop, we read from the socket until all data has been received,
    then combine the response and return it along with the response ID,
    which allows us to verify authentication attempts.
    """
    response_length, response_id, response_type = struct.unpack(
        "<iii",
        client.recv(12)
    )
    response = ""
    data_remains = True
    while data_remains:
        response_data = client.recv(response_length - 8)
        response += response_data.strip("\x00\x00")
        data_remains = select.select([client], [], [], 1.0)[0]
    return response, response_id


def authenticate(client, password):
    """ Sends an authentication packet to the RCON server and checks the
    response for a matching message ID. A message ID of -1 indicates
    authentication failure, and a matching message ID (0 in our case)
    indicates success.

    Based on implementation details from http://wiki.vg/Rcon#3:_Login
    """
    auth_packet = create_packet(
        password,
        MessageTypes.RCON_AUTHENTICATE
    )
    client.send(auth_packet)
    response, response_id = process_response(client)
    return response_id


def cli(client):
    """ Reads a command from the prompt, sends it to the server, processes the
    response, and returns the output to the user. Allows quitting with "quit"
    or "q", and adds newlines to help page output to improve readability.
    """
    while True:

        # read a command and quit if requested
        command = raw_input("rcon> ")
        if command in ["quit", "q"]:
            print "Disconnecting."
            return

        # send the command to the rcon server
        packet = create_packet(
            command,
            MessageTypes.RCON_EXEC_COMMAND
        )
        client.send(packet)

        # read and process the response from the server
        response, response_id = process_response(client)
        if response:
            # add some newlines to help page output for cleanliness
            if command.startswith("help"):
                response = response.replace("/", "\n/")
            print response


def main(args=None):
    options = parse_arguments(args)
    print "Connecting to %s:%d..." % (options.host, options.port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((options.host, options.port))
    if authenticate(client, options.password) == 0:
        print "Authenticated."
    else:
        print "Failed to authenticate."
        exit(1)
    print "\n  Welcome to the rcon shell. Enter commands here to send them"
    print "  to the RCON server. To quit, type \"quit\" or \"q\".\n"
    try:
        cli(client)
    except KeyboardInterrupt, k:
        print "\nDisconnected."
        exit(0)
    finally:
        client.close()

if __name__ == "__main__":
    main()
