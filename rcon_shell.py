from rcon_api import *
from argparse import ArgumentParser

"""
Minecraft RCON Client Console
"""


def parse_arguments(args=None):
    """ Provides host, port, and password options for command-line use.
    The RCON API always requires a password to connect.
    """
    parser = ArgumentParser(description="Connect to a Minecraft RCON server")
    parser.add_argument("--host", dest="host", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=25575)
    parser.add_argument("--password", dest="password", type=str, required=True)
    return parser.parse_args()


def rcon_shell(client):
    """ Reads a command from the prompt, sends it to the server, processes the
    response, and returns the output to the user. Allows quitting with "quit"
    or "q", and adds newlines to help page output to improve readability.
    """
    print "\n  Welcome to the rcon shell. Enter commands here to send them"
    print "  to the RCON server. To quit, type \"quit\" or \"q\".\n"
    while True:
        command = raw_input("rcon> ")
        if command in ["quit", "q"]:
            return
        response, response_id = client.send(command)
        if response:
            if command.startswith("help"):
                response = response.replace("/", "\n/")
            print response


def main(args=None, client=None):
    options = parse_arguments(args)
    print "Connecting to %s:%d..." % (options.host, options.port)
    try:
        client = RemoteConsole(
            options.host,
            options.port,
            options.password
        )
        rcon_shell(client)
    except ConnectionError:
        print "Connection failed."
        exit(1)
    except AuthenticationError:
        print "Authentication failed."
    except KeyboardInterrupt:
        print
    finally:
        if client:
            client.disconnect()
        print "Disconnected."

if __name__ == "__main__":
    main()
