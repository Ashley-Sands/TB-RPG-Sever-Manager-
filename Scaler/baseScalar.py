import Common.azCommands as azCommands
import time
import threading

class BaseScalar:

    def __init__( self , update_interval=60, max_instances=1):

        self.az_commands = azCommands.AzCommands()
        self.update_intervals = update_interval         # sec
        self.max_instances = max_instances
        self.instances = []                             # list of host objects

        self.init_commands()

        self.thread_lock = threading.Lock()
        self.update_thread = threading.Thread( target=self.update )
        self.update_thread.start()
        self.cancel_update = False

    def init_commands( self ):
        """ virtual
            Functions to override to initialize command strings
        """
        # TODO: for now this will just use az_command.add, i should add an addJson version az_command
        pass

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

    def update( self ):
        """Main update loop (threaded)"""

        while not self.cancel_update:

            instances_dif = self.required_instances() - len(self.instances)

            if instances_dif > 0:
                self.__spawn_instances()
            elif instances_dif < 0:
                self.destroy_instance()

            time.sleep( self.update_intervals )
