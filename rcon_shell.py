import argparse
import getpass
import sys

from api.rcon import *

'''Minecraft RCON Client Console'''


def parse_arguments():
    '''Provides host and port options for command-line use.

    @return: options namespace based on provided arguments
    '''
    parser = argparse.ArgumentParser(
        description='Connect to a Minecraft RCON server',
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='default: 127.0.0.1',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=25575,
        help='default: 25575',
    )
    return parser.parse_args()


def rcon_shell(rcon):
    '''Reads a command from the prompt, sends it to the server, processes the
    response, and returns the output to the user. Allows quitting with 'quit'
    or 'q', and adds newlines to help page output to improve readability.

    @param rcon: Instance of api.rcon.RemoteConsole()
    '''
    print('\n  Welcome to the rcon shell. Enter commands here to send them')
    print('  to the RCON server. To quit, type \'quit\' or \'q\'.\n')
    while True:
        command = input('rcon> ')
        if command in ('quit', 'q'):
            return
        response, _ = rcon.send(command)
        if response:
            if command.startswith('help'):
                response = response.replace('/', '\n/')
            print(response)


def main(options, rcon=None):
    '''Reads command-line arguments, connects to the RCON server, and starts
    the rcon_shell loop. Handles exceptions and interrupts, and disconnects
    when finished.
    '''
    print('Connecting to {}:{}...'.format(options.host, options.port))
    password = getpass.getpass()
    try:
        rcon = RemoteConsole(
            options.host,
            options.port,
            password,
        )
        rcon_shell(rcon)
    except ConnectionError:
        print('Connection failed.')
    except AuthenticationError:
        print('Authentication failed.')
    except KeyboardInterrupt:
        print()
    finally:
        if rcon:
            rcon.disconnect()
        print('Disconnected.')

if __name__ == '__main__':
    # Use raw_input() as input() for Python 2
    if sys.version_info.major == 2:
        input = raw_input
    options = parse_arguments()
    main(options)
