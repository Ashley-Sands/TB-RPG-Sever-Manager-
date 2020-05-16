import Common.azCommands as azCommands


class BaseScalar:

    def __init__( self ):

        self.az_commands = azCommands.AzCommands()

        self.init_commands()

    def init_commands( self ):
        """Functions to override to initialize command strings"""
        # TODO: for now this will just use az_command.add, i should add an addJson version az_command
        pass

    def update( self ):
        """Main update loop"""
        pass
