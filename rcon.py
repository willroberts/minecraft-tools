#!/usr/bin/env python

import argparse
import socket
import select
import struct


class MessageTypes(object):
    RCON_AUTHENTICATE = 3
    RCON_AUTH_RESPONSE = 2
    RCON_EXEC_COMMAND = 2
    RCON_RESPONSE_VALUE = 0


def parse_arguments(args=None):
    """ Accepts arguments for host, port, and password. Sets defaults for
    host and port. Note that a password is required for RCON.
    """
    parser = argparse.ArgumentParser(
        description="Connect to a Minecraft RCON server"
    )
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", default=25575)
    parser.add_argument("--password", dest="password", required=True)
    return parser.parse_args()


def create_packet(message, message_type):
    """ Creates a packet/struct based on the Minecraft RCON API specification.
    See http://wiki.vg/Rcon#Packet_Format
    """
    header = struct.pack(
        "<iii",  # format: little-endian byte order, three integers
        len(message) + 10,  # padded message length
        0,  # message id
        message_type
    )
    return header + message + "\x00\x00"  # end with two null bytes


def process_response(client, response="", data_remains=True):
    """ Reads output from the client socket and formats it into a string.
    """
    response_length, response_id, response_type = struct.unpack(
        "<iii",  # same packet structure as before
        client.recv(12)  # read three 4-byte integers
    )

    # initialized as True, but eventually will be a list of the socket
    # object ready for reads. when there's no data left to be read,
    # data_remains will be an empty list and the loop will end.
    while data_remains:

        # continue reading, but don't re-read the message id or type
        response_data = client.recv(response_length - 8)

        # add the fragment to our response output
        # strip the null bytes off each fragment
        response += response_data.strip("\x00\x00")

        # check the client socket for reading
        data_remains = select.select(
            [client],  # check the socket for readability
            [],  # no writability checks
            [],  # no "exceptional condition" checks
            1.0  # 1s timeout
        )[0]  # store the "read" field from the returned array

    return response, response_type, response_id


def authenticate(client, password):
    """ Sends an authentication packet to the RCON server (type
    RCON_AUTHENTICATE), and checks the response for a matching message ID. A
    message ID of -1 indicates authentication failure.
    See http://wiki.vg/Rcon#3:_Login
    """
    auth_packet = create_packet(
        password,
        MessageTypes.RCON_AUTHENTICATE
    )

    client.send(auth_packet)

    response, response_type, response_id = process_response(client)
    if response_id == 0:
        print "Authenticated."
    else:
        print "Failed to authenticate."
        exit(1)


def interact(client):
    """ Handles the back-and-forth communication between the client and the
    remote server.
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
        response, response_type, response_id = process_response(client)
        if response:
            # add some newlines to help page output for cleanliness
            if command.startswith("help"):
                response = response.replace("/", "\n/")
            print response


def main(args=None):
    """ Interact with a Minecraft RCON server for remote administration.
    """

    # parse command-line arguments
    options = parse_arguments(args)

    # create a socket and connect to the minecraft server
    print "Connecting to %s:%d..." % (
        options.host,
        int(options.port)
    )
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((options.host, int(options.port)))
    authenticate(client, options.password)

    # poll the user for commands to send
    print "\n  Welcome to the rcon shell. Enter commands here to send them"
    print "  to the RCON server. To quit, type \"quit\" or \"q\".\n"
    try:
        interact(client)
    except KeyboardInterrupt, k:
        print "\nDisconnected."
        exit(0)
    finally:
        client.close()

if __name__ == "__main__":
    main()
