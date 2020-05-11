import json, os, sys, subprocess, re
import Common.azCommands as azCommands

# notes
# locations: "uksouth", "ukwest", "westeurope", "northeurope", "centralus"
# my standard vm config
# server = {
#    "group": None,
#    "image": "UbuntuLTS",
#    "size": "Standard_B1s",
#    "location": None
# }
#

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

## testing.

azcom = azCommands.azCommands()
azcom.add("test", "az vm create --location {} -g --size {  fdgs gf gfds} --image { f4fa }")
print( azcom.get("test", image="ubuntu", bop="gfds") )
