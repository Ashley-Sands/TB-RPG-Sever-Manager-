import json, os, sys, subprocess, re, time
import Common.azCommands as azCommands
import Scalar.lobbyScalar as lobbyScalar
import Common.globals as global_config
consts = global_config.Global

# notes
# locations: "uksouth", "ukwest", "westeurope", "northeurope", "centralus"
# my standard vm config

DEFAULT_VM = {
    "group": "RPG_Network_WE",
    "image": "UbuntuLTS",
    "size": "Standard_B1s",
    "location": "westeurope"
}

TAG_SPAWNER = "spawner=cli_auto"
TAG_MNET    = "RPG"

def get_sys_argv():
    """Get all argv's that start with '--'
        and return them in a dict
    """
    argv = ' '.join(sys.argv)

    match = re.findall( "(--[\w\d_]*[ ]*[\w\d_]*)\w*", argv )
    argvs = {}

    for m in match:
        v = m.split(" ")
        argvs[v[0][2:]] = v[1]

    print(argvs)
    return argvs


if __name__ == "__main__":

    lobbies = lobbyScalar.LobbyScalar("lobbies-cli", "gizzmo123456/game_server:server_lobby-1.0", update_interval=1)

    inp = ""

    while inp != "y":
        inp = input("y to exit")

    for i in lobbies.instances:
        print("-------", i.azure_id, i.host_address, i.status)

    lobbies.cancel_update = True
