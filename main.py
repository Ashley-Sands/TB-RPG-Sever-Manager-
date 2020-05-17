import json, os, sys, subprocess, re
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

def event_compleat(event_id, data):

    print(event_id, ":", data)

def count_results(event_id, data):

    if data and len( data ) > 0:
        event_id = az.invoke( "show containers", background=True, bg_callback=event_compleat, **DEFAULT_VM,
                              query='"[].{name:name, location:location, ip:ipAddress.ip, image:containers[0].image, '
                                    'state:containers[0].instanceView.state, p_state:provisioningState, tags:tags}"' )

        print( event_id, "has been sent" )
    else:
        print("No Results for event:", event_id)


if __name__ == "__main__":

    lobbies = lobbyScalar.LobbyScalar("gizzmo123456/game_server:server_lobby-1.0")
