import json, os, sys, subprocess, re

impo = "import os\n"

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

def get_command_data( command ):
    command = "os.system( '" + command + "' )"

    proc = subprocess.Popen( [ 'python', '-c', impo + command ], stdout=subprocess.PIPE )
    json_str_ = ""

    while True:
        line = proc.stdout.readline().decode( "utf-8" )
        if not line:
            break
        else:
            json_str_ = json_str_ + line

    proc.kill()

    try:
        return json.loads( json_str_ )
    except:
        return None


server = {
    "group": None,
    "image": "UbuntuLTS",
    "size": "Standard_B1s",
    "location": None
}

locations = [ "uksouth", "ukwest", "westeurope", "northeurope", "centralus" ]
com = "az vm list-sizes --location {0} {1}"  # 0 = location, 1 = query to refine data
query = '--query "[].{name:name}"'

# update the server values if they where set in argv
sys_argv = get_sys_argv()

if "group" not in sys_argv:
    print( "Error: group is a required param" )
    exit()

for key in server:
    if key in sys_argv:
        server[key] = sys_argv[key]

print("RG:", server["group"], "image", server["image"], "size", server["size"])
print("="*25)

# query each of the location for an available server of server_type
for loc in locations:
    _com = com.format( loc, query )
    print( _com )
    data = get_command_data( _com )

    if data is None:
        print( "ERROR: converting json" )
    elif len( data ) > 0:
        for d in data:
            if d[ "name" ] == server["size"]:
                print( "Server is available at", loc )
                server["location"] = loc
                break

        if server["location"] is None:
            print( "Server is unavailable at", loc, ":(" )
        else:
            break
    else:
        print( "No Servers Available?? at", loc )

# now we can spawn a new server at the location if it was available
if server["location"] is None:
    print("Error: can not create server, not available ant any location (", ', '.join(locations), ")")
    exit()

print("Spawning Server at", server["location"], ":)")

query = '--query "[].{pIp:privateIpAddress, Ip:publicIpAddress}"'
create_vm = "az vm create -n auto_created_vm_0 -g {3} --location {0} --size {1} --image {2} {4}"
create_vm = create_vm.format( server["location"], server["size"], server["image"], server["group"], query )

print( create_vm )

data = get_command_data( create_vm )

print( data )
