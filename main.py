import json, os, sys, subprocess

impo = "import os\n"


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


server_image = "UbuntuLTS"
server_size = "Standard_B1ms"  # (1 vcpus, 2 GiB memory)    # TODO: change to sys arg
server_location = None
locations = [ "uksouth", "ukwest", "westeurope", "northeurope" ]
com = "az vm list-sizes --location {0} {1}"  # 0 = location, 1 = query to refine data
query = '--query "[].{name:name}"'


# query each of the location for an available server of server_type
for loc in locations:
    _com = com.format( loc, query )
    print( _com )
    data = get_command_data( _com )

    if data is None:
        print( "ERROR: converting json" )
    elif len( data ) > 0:
        for d in data:
            if d[ "name" ] == server_size:
                print( "Server is available at", loc )
                server_location = loc
                break

        if server_location is None:
            print( "Server is unavailable at", loc, ":(" )
        else:
            break
    else:
        print( "No Servers Available?? at", loc )

# now we can spawn a new server at the location if it was available
if server_location is None:
    print("Error: can not create server, not available ant any location (", ' ,'.join(locations), ")")
    exit()

print("Spawning Server at", server_location, ":)")

create_vm = "az vm create -n auto_created_vm_0 -g rpg_scale_services --location {0} --size {1} --image {2}"
create_vm = create_vm.format( server_location, server_size, server_image )

print( create_vm )

data = get_command_data( create_vm )

print( data )
