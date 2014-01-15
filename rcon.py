#!/usr/bin/env python

import argparse
import socket
import select
import struct


class MessageTypes(object):
    RCON_AUTHENTICATE = 3
    RCON_AUTH_RESPONSE = 2
    RCON_EXEC_COMMAND = 2
    RCON_RESPONSEVALUE = 0


def parse_arguments(args=None):
    """ Accepts arguments for host, port, and password. Sets defaults for
    host and port. Note that a password is required for RCON.
    """
    parser = argparse.ArgumentParser(description="Connect to a Minecraft RCON server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", default=25575)
    parser.add_argument("--password", dest="password", default="")
    return parser.parse_args()


def create_packet(message, message_type):
    """ Creates a packet/struct based on the Minecraft RCON API specification.
    """
    header = struct.pack(
        "<iii",  # format: little-endian byte order, three integers
        10 + len(message),  # message length
        0,  # message id
        message_type
    )
    return header + message + "\x00\x00"


def process_response(client, response="", data_remains=True):
    """ Reads output from the client socket and formats it into a string.
    """
    response_len, response_id, response_type = struct.unpack(
        "<iii",  # same packet structure as before
        client.recv(12)  # read three 4-byte integers
    )

    # initialized as True, but eventually will be a list of the socket
    # object ready for reads. when there's no data left to be read,
    # data_remains will be an empty list and the loop will end.
    while data_remains:

        # continue reading, but don't re-read the extra fields
        # to be quite honest i don't fully understand this
        response_data = client.recv(response_len - 8)

        # add the fragment to our response output
        response += response_data.strip("\x00\x00")

        # check the client socket for reading
        data_remains = select.select(
            [client],  # check the socket for readability
            [],  # no writability checks
            [],  # no "exceptional condition" checks
            1.0  # 1s timeout
        )[0]  # store the "read" field from the returned array

    return response, response_type


def interact(client):
    """ Handles the back-and-forth communication between the client and the
    remote server.
    """
    while True:

        # read a command and send it to the rcon server
        command = raw_input("rcon> ")
        packet = create_packet(
            command,
            MessageTypes.RCON_EXEC_COMMAND,
        )
        client.send(packet)

        # read and process the response from the server
        response, response_type = process_response(client)
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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((options.host, int(options.port)))

    # authenticate
    auth_packet = create_packet(
        options.password,
        MessageTypes.RCON_AUTHENTICATE,
    )
    client.send(auth_packet)
    print "Connecting to %s:%d. Press Ctrl-C to exit." % (
        options.host,
        int(options.port)
    )

    # check for message type "RCON_AUTH_RESPONSE"
    response, response_type = process_response(client)
    if response_type == MessageTypes.RCON_AUTH_RESPONSE:
        print "Authenticated."
    else:
        print "Failed to authenticate."
        exit(1)

    # poll the user for commands to send
    try:
        interact(client)
    except KeyboardInterrupt, k:
        print "\nDisconnected."
        exit(0)
    finally:
        client.close()

if __name__ == "__main__":
    main()
