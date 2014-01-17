from rcon_api import *
from argparse import ArgumentParser

"""
Minecraft RCON Client Console
"""


def parse_arguments():
    """ Provides host, port, and password options for command-line use.
    The RCON API always requires a password to connect.

    @return: options namespace based on provided arguments
    """
    parser = ArgumentParser(description="Connect to a Minecraft RCON server")
    parser.add_argument("--host", dest="host", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=25575)
    parser.add_argument("--password", dest="password", type=str, required=True)
    return parser.parse_args()


def rcon_shell(rcon):
    """ Reads a command from the prompt, sends it to the server, processes the
    response, and returns the output to the user. Allows quitting with "quit"
    or "q", and adds newlines to help page output to improve readability.

    @param rcon: Instance of rcon_api.RemoteConsole()
    """
    print "\n  Welcome to the rcon shell. Enter commands here to send them"
    print "  to the RCON server. To quit, type \"quit\" or \"q\".\n"
    while True:
        command = raw_input("rcon> ")
        if command in ["quit", "q"]:
            return
        response, response_id = rcon.send(command)
        if response:
            if command.startswith("help"):
                response = response.replace("/", "\n/")
            print response


def main():
    """ Reads command-line arguments, connects to the RCON server, and starts
    the rcon_shell loop. Handles exceptions and interrupts, and disconnects
    when finished.
    """
    options = parse_arguments()
    rcon = None
    print "Connecting to %s:%d..." % (options.host, options.port)
    try:
        rcon = RemoteConsole(
            options.host,
            options.port,
            options.password
        )
        rcon_shell(rcon)
    except ConnectionError:
        print "Connection failed."
        exit(1)
    except AuthenticationError:
        print "Authentication failed."
    except KeyboardInterrupt:
        print
    finally:
        if rcon:
            rcon.disconnect()
        print "Disconnected."

if __name__ == "__main__":
    main()