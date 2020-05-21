import Scalar.baseScalar as baseScalar
import Common.hostObject as hostObject


class ContainerScalar( baseScalar.BaseScalar ):

    def __init__( self, base_instance_name, type_name, update_interval=60, max_instances=1 ):
        super().__init__(base_instance_name, type_name, update_interval, max_instances)

        self.scalar_type = hostObject.HostObject.TYPE_CONTAINER
        self.docker_auth = self.az_commands.invoke("docker pass", background=False)[1]


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
                                    "--registry-password {} "
                                    "--restart-policy Never "
                                    "--ip-address Private "
                                    "--subnet /subscriptions/f3679ebd-da87-4256-9659-f5984d7c156f/resourceGroups/RPG_Network_WE/providers/Microsoft.Network/virtualNetworks/VNet-WE/subnets/container-net "
                                    "--query {}")

        # we must make sure the container is stopped befor deleting it
        # otherwise it does not run the exit code, ie. delete kills the process immediately
        self.az_commands.add("remove", "az container stop -g rpg_network_we --name {} && " 
                                       "az container delete -g rpg_network_we --name {} --yes ")

        self.az_commands.add("docker pass", "az keyvault secret show --vault-name rpg-network-services --name docker --query 'value' ")

    def request_new_instance( self ):
        """ request a new instances """

        request_id = self.az_commands.invoke( "add",
                                              background=True,
                                              bg_callback=self.process_new_instance,
                                              name="{0}-{1}".format( self.instance_name, self.next_host_id ),
                                              registrypassword=self.docker_auth,
                                              image=self.instance_type,
                                              query="'{id:id, name:name, ip:ipAddress.ip, type:containers[0].image, status:provisioningState}'")[0]

        # create a new host object
        hobj = hostObject.HostObject(self.next_host_id, hostObject.HostObject.TYPE_CONTAINER)

        self.active_request[ request_id ] = hobj
        self.instances.append( hobj )

        self.next_host_id += 1


    def process_new_instance( self, request_id, data ):
        """"""
        if request_id in self.active_request:
            print(data) # todo Remove
            # update the host object now that the instance has been created
            hobj = self.active_request[ request_id ]
            hobj.complete_setup( data["id"], data["name"], data["ip"] )

            # request a status update
            self.request_az_instance_status( hobj )

            del self.active_request[ request_id ]
        else:
            print("Error: Request id ", request_id, "does not exist")

    def request_destroy_instance( self ):

        shutdown_inst = self._deallocate_instance()

        request_id = self.az_commands.invoke("remove",
                                background=True,
                                bg_callback=self.process_destroy_instance,
                                name=shutdown_inst.azure_name )[0]

        self.active_request[ request_id ] = shutdown_inst

    def process_destroy_instance( self, request_id, data ):

        if request_id in self.active_request:
            self.instances.remove( self.active_request[ request_id ] )
            del self.active_request[ request_id ]
        else:
            print("Error: Request id ", request_id, "does not exist")