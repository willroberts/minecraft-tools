# minecraft-tools

Tools for managing Minecraft servers.

## Requirements

* Python 2.7 or 3.x

If you are using Python 2.6, you may need to install `argparse` via `pip`.

## Files

* api/rcon.py: A fully-featured RCON client API
* rcon_shell.py: An interactive console shell for the client API

## Command-line options

    $ python rcon_shell.py -h
    usage: rcon_shell.py [-h] [--host HOST] [--port PORT]

    Connect to a Minecraft RCON server

    optional arguments:
      -h, --help   show this help message and exit
      --host HOST  default: 127.0.0.1
      --port PORT  default: 25575

## Sample usage

    $ python rcon_shell.py --host minecraft.example.net
    Connecting to minecraft.example.net:25575...
    Password: 

      Welcome to the rcon shell. Enter commands here to send them
      to the RCON server. To quit, type "quit" or "q".

    rcon> help 2
    --- Showing help page 2 of 7 (/help <page>) ---
    /deop <player>
    /difficulty <new difficulty>
    /effect <player> <effect> [seconds] [amplifier]
    /enchant <player> <enchantment ID> [level]
    /gamemode <mode> [player]
    /gamerule <rule name> <value> OR 
    /gamerule <rule name>
    /give <player> <item> [amount] [data] [dataTag]
    rcon> difficulty 2
    Set game difficulty to Normal
    rcon> quit
    Disconnected.

## Plaintext Passwords Warning

The Minecraft RCON server API expects passwords in plaintext, so your password
will not be encrypted before being sent across the network. If you would like
to keep your RCON password secure, consider using an SSH tunnel.
