import Scalar.baseScalar as baseScalar
import Common.hostObject as hostObject

class LobbyScalar( baseScalar.BaseScalar ):

    def __init__( self, type_name, update_interval=60, max_instances=1 ):
        super().__init__(type_name, update_interval, max_instances)

    def init_commands( self ):
        self.az_commands.add("list", "az container list "
                                     "--resource-group rpg_network_we "
                                     "--query {} "
                                     "--output json")

        self.az_commands.add("status", "az container show "
                                       "--ids {}"
                                       "--query {}")

        self.az_commands.add("add", "az container create "
                                    "-g rpg_network_we "
                                    "--name {} "
                                    "--cpu 0.25 "
                                    "--memory 0.2 "
                                    "--location westeurope "
                                    "--port 8223 "
                                    "--protocol TCP "
                                    "--image {} "
                                    "--registry-login-server index.docker.io "
                                    "--registry-username gizzmoazure "
                                    "--registry-password 'ghgi8754yt6iuregh95&85478^$%t6yg45rg45ut8rgu@_)7986utyhGBFv£!$^Y%ETHBGVFDhtuL<>&$^U%YGT$EVdcsx' "
                                    "--restart-policy Never "
                                    "--ip-address Private "
                                    "--subnet /subscriptions/f3679ebd-da87-4256-9659-f5984d7c156f/resourceGroups/RPG_Network_WE/providers/Microsoft.Network/virtualNetworks/VNet-WE/subnets/container-net "
                                    "--query {}")

    def request_new_instance( self ):
        """ request a new instances """

        request_id = self.az_commands.invoke( "add",
                                 background=True,
                                 bg_callback=self.process_new_instance,
                                 name="{0}-{1}".format( self.instance_type.split("/")[1], self.next_host_id ),
                                 image=self.instance_type,
                                 query="{id:id, ip:ipAddress.ip, type:containers[0].image, status:provisioningState}")[0]

        # create a new host object
        hobj = hostObject.HostObject(self.next_host_id)

        self.active_request[ request_id ] = hobj
        self.instances.append( hobj )

        self.next_host_id += 1


    def process_new_instance( self, event_id, data ):
        """"""

        print(data)
