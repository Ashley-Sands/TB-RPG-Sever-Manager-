import Common.azCommands as azCommands
import Common.hostObject as hostObject
import time
import threading

class BaseScalar:

    def __init__( self , type_name, update_interval=60, max_instances=1):

        self.az_commands = azCommands.AzCommands()
        self.update_intervals = update_interval         # sec

        self.instance_type = type_name

        self.max_instances = max_instances
        self.instances = []                             # list of host objects

        self.instances_request_id = -1      # < 0 == no pending request
        self.instance_status_request = {}   # key event id, requested status host object

        self.init_commands()
        self.request_az_instances()


        self.cancel_update = False
        self.thread_lock = threading.Lock()
        self.update_thread = threading.Thread( target=self.update )
        self.update_thread.start()

    def init_commands( self ):
        """ virtual
            Must contain at least add, remove, list and status
        """
        # TODO: for now this will just use az_command.add, i should add an addJson version az_command
        raise NotImplementedError()

    def request_az_instances( self ):
        """ request a list of instances from azure. (to be processed in process_az_instances)
            each result must contain azure_id, ip, status and type
            ie. az ... --query "[].{azure_id:id, ip:privateIp, status:state, type:image}" -o json ...
        """

        if self.instances_request_id < 0:   # only request if there's no pending request to be returned.
            self.instances_request_id = self.az_commands.invoke("list",
                                                                background=True,
                                                                bg_callback=self.process_az_instances,
                                                                query="'[].{id:id, ip:ipAddress.ip, image:containers[0].image, status:provisioningState}'")[0]
        else:
            print("Warning: Unable to request a list of instances from azure, a request is already pending")

    def process_az_instances( self, event_id, data ):
        """Processes the data returned by the request_az_instances"""
        # ATM this can only be run once
        # TODO: add update instances

        print("Instances data", data)

        if data is None or len( data ) == 0:
            print("No instances found")
            return

        # process the data only extracting the data that we need.
        for d in data:
            if d["type"] == self.instance_type:
                hobj = hostObject.HostObject(0, d["id"], d["ip"], hostObject.HostObject.STATE_INIT)
                self.instances.append(hobj)
                # TODO: request the instances status

    def request_az_instance_status( self, hostObj ):
        """ virtual
            request the status of the instances from azure
            :param azure_id:    azures resource id
            each result must contain 'status'
            ie. az ... --query "[].{status:state}" -o json ...
        """

        if hostObj not in self.instance_status_request.values(): # only request status if there's no pending request waiting to be returned
            request_id = self.az_commands.invoke("status", background=True, bg_callback=self.process_az_instance_status)[0]
            self.instance_status_request[request_id] = hostObj
        else:
            print("Warning: Unable to request the status of a host object, a request is already pending for the object")

    def process_az_instance_status( self, event_id, data ):
        """Virtual: Processes the data returned by the request_az_instance_status"""
        raise NotImplementedError()

    def required_instances( self ):
        """ virtual
            The amount of instances that we require for the current load
            :return:    in the number of instances required for the current load.
        """
        return 1

    def can_spawn( self ):
        """virtual: can spawn a new instance and stay within the max instance limits"""
        return len( self.instances ) < self.max_instances

    def spawn_new_instance( self ):
        """ virtual
            Spawns a new instances
            :return: true if successful otherwise false
        """
        return False

    def destroy_instance( self ):
        """ virtual
            destroys any idling (unused) instance
        :return: true if successful otherwise false
        """

        return False

    def __spawn_instances( self ):

        if self.can_spawn():
            return self.spawn_new_instance()

        return False

    def update_instances( self, event_id, data ):
        """Updates the list of instances from azure"""
        pass

    def update( self ):
        """Main update loop (threaded)"""

        while not self.cancel_update:

            instances_dif = self.required_instances() - len(self.instances)

            if instances_dif > 0:
                self.__spawn_instances()
            elif instances_dif < 0:
                self.destroy_instance()

            time.sleep( self.update_intervals )
