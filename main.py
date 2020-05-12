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
        event_id = az.invoke( "list containers", background=True, bg_callback=event_compleat, **DEFAULT_VM,
                              query='"[].{name:name, location:location, ip:ipAddress.ip, image:containers[0].image, '
                                    'state:containers[0].instanceView.state, p_state:provisioningState, tags:tags}"' )

        print( event_id, "has been sent" )
    else:
        print("No Results for event:", event_id)


if __name__ == "__main__":
    az = azCommands.azCommands()

    # setup the commands
    # resource groups
    az.add("new group", "az group create --name {} --location {} --tags {}")
    # vms
    az.add("new vm", "az vm create --name {} --resource-group {} -p --location {} --size {Standard_b1s} --image {UbuntuLTS} --tags {}")
    az.add("list vms", 'az vm show -d --ids $(az vm list --resource-group {} --query "[].id" -o tsv) --query {} --output {json}')
    # containers
    az.add("new container", "az container create --resource-group {} --size {} --tags {}")

    az.add("list container", "az container list --resource-group {} --query {} --output {json}")
    az.add("show containers", 'az container show --ids $(az container list --resource-group {} --query "[].id" -o tsv) --query {} --output {json}')

    # add some aliases
    az.add_param_alias("new vm", "resource-group", "group")
    az.add_param_alias("list vms", "resource-group", "group")
    az.add_param_alias("new container", "resource-group", "group")
    az.add_param_alias("list containers", "resource-group", "group")
    az.add_param_alias("show containers", "resource-group", "group")

    # the plan, is to orchestrate the tb_rpg game network
    # the network is made up of a backend database, and
    # lobby and game instance containers (managed)
    # and front end reverse proxy, with it own
    # private auth and lobby-directory containers (self-managed)
    #
    # See the plan in "cli commands and notes.md" for more info

    hosts = {} # dict of list, key: hostObj.TYPE value list of hostObjects

    print("="*25, "initial setup up complete", "="*25, sep="\n")

    # once we first connect find if we already have any containers running
    event_id = az.invoke("list vms", background=True, bg_callback=event_compleat, **DEFAULT_VM,
                         query='"[].{name:name, location:location, ip:privateIps, state:powerState, tags:tags}"')

    print(event_id, "has been sent")

    event_id = az.invoke("show containers", bg_callback=count_results, **DEFAULT_VM, query='"[].{name:name}"')

    print(event_id, "has been sent")