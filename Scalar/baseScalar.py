import Common.azCommands as azCommands
import Common.hostObject as hostObject
import time
import threading

class BaseScalar:

    def __init__( self, base_instance_name, type_name, update_interval=60, max_instances=1):

        self.az_commands = azCommands.AzCommands()
        self.update_intervals = update_interval         # sec

        self.instance_name = base_instance_name
        self.instance_type = type_name

        self.next_host_id = 0
        self.scalar_type = hostObject.HostObject.TYPE_UNDEFINED
        self.max_instances = max_instances
        self.instances_processed = False
        self.instances = []                             # list of host objects

        self.instances_request_id = -1      # < 0 == no pending request
        self.active_request = {}   # key event id, requested status host object

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
                                                                query="'[].{id:id, ip:ipAddress.ip, type:containers[0].image, status:provisioningState}'")[0]
        else:
            print("Warning: Unable to request a list of instances from azure, a request is already pending")

    def process_az_instances( self, event_id, data ):
        """Processes the data returned by the request_az_instances"""
        # Warning this can only be run once atm else it will overwrite the current host list
        # TODO: add update instances

        print("Instances data", data)

        if data is None or len( data ) == 0:
            print("No instances found")
            self.instances_processed = True
            return

        # process the data only extracting the data that we need.
        for d in data:
            if d["type"] == self.instance_type:
                hobj = hostObject.HostObject(self.next_host_id,
                                             self.scalar_type,
                                             az_id=d["id"],
                                             host_addr=d["ip"],
                                             state=hostObject.HostObject.STATE_INIT)
                self.instances.append(hobj)
                self.request_az_instance_status( hobj )
                self.next_host_id += 1

        self.instances_request_id = -1  # reset the instance_request_id
        self.instances_processed = True

    def request_az_instance_status( self, host_obj ):
        """ virtual
            request the status of the instances from azure
            :param host_obj:    host object to update
            each result must contain 'status'
            ie. az ... --query "[].{status:state}" -o json ...
        """

        if host_obj not in self.active_request.values(): # only request status if there's no pending request waiting to be returned
            request_id = self.az_commands.invoke("status",
                                                 background=True,
                                                 bg_callback=self.process_az_instance_status,
                                                 ids=host_obj.azure_id,
                                                 query="{status:instanceView.state}")[0]

            self.active_request[ request_id ] = host_obj
        else:
            print("Warning: Unable to request the status of a host object, a request is already pending for the object")

    def process_az_instance_status( self, request_id, data ):
        """Virtual: Processes the data returned by the request_az_instance_status"""

        if request_id not in self.active_request:
            return

        if data["status"].lower() == "running":
            self.active_request[ request_id ].status = hostObject.HostObject.STATUS_RUNNING
        else:
            self.active_request[ request_id ].status = hostObject.HostObject.STATUS_INACTIVE

        del self.active_request[ request_id ]    # remove the pending event

    def required_instances( self ):
        """ virtual
            The amount of instances that we require for the current load
            :return:    in the number of instances required for the current load.
        """
        return 1

    def can_spawn( self ):
        """virtual: can spawn a new instance and stay within the max instance limits"""
        return len( self.instances ) < self.max_instances

    def request_new_instance( self ):
        """ request a new instances """
        raise NotImplementedError()

    def process_new_instance( self, event_id, data ):
        raise NotImplementedError()

    def destroy_instance( self ):
        """ virtual
            destroys any idling (unused) instance
        :return: true if successful otherwise false
        """

        return False

    def __spawn_instances( self ):

        if self.can_spawn():
            return self.request_new_instance()

        return False

    def update_instances( self, event_id, data ):
        """Updates the list of instances from azure"""
        pass

    def update( self ):
        """Main update loop (threaded)"""

        while not self.cancel_update:

            required_instances = self.required_instances()
            instances_dif = required_instances - len(self.instances)

            print("Setup Complete:", self.instances_processed, "required ins:", required_instances, "current:", len(self.instances))

            if self.instances_processed:
                if instances_dif > 0:
                    print("create instance")
                    self.__spawn_instances()
                elif instances_dif < 0:
                    print("destroy instance")
                    self.destroy_instance()
                else:
                    print("We're good for now")

            time.sleep( self.update_intervals )
