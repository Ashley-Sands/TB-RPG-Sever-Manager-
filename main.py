import json, os, sys, subprocess, re
import Common.azCommands as azCommands
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
    az = azCommands.azCommands()

    # setup the commands
    az.add("new group", "az group create --name {} --location {}")
    az.add("new vm", "az vm create --name {} --resource-group {} -p --location {} --size {Standard_b1s} --image {UbuntuLTS}")
    az.add("list vms", "az vm list --resource-group {}")
    az.add("new container", "az container create --resource-group {} --size {}")
    az.add("list containers", "az container list --resource-group {}")
    # add some aliases
    az.add_param_alias("new vm", "resource-group", "group")
    az.add_param_alias("list vms", "resource-group", "group")
    az.add_param_alias("new container", "resource-group", "group")

    print( az.get("new container", group="bbbb", size="abc") )

    # the plan, is to orchestrate the tb_rpg game network
    # the network is made up of a backend database, and
    # lobby and game instance containers (managed)
    # and front end reverse proxy, with it own
    # private auth and lobby-directory containers (self-managed)
    #
    # See the plan in "cli commands and notes.md" for more info

    hosts = [] # list of all our current host ie. vm's, containers and databases
    print(DEFAULT_VM)
    # once we first connect find if we already have any containers running
    event_id, response = az.invoke("list vms", background=False, **DEFAULT_VM)
