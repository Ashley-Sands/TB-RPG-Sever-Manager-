import Common.azCli as azCli

class azCommands():

    def __init__( self ):

        self.cli = azCli.az()
        self.commands = { }

    def add( self, command_name, command):
        """ Add a command to the dict of commands

        :param command_name: the name of the command
        :param command:      the command to be executed.
                             command format. example
                             'az group list -g {group}'
                             DO NOT use int inside of the {} ie
                             DO NOT DO, you will have a bad time
                             'az group list -g {0}'
                             Its also worth noting that if --query is use
                             it should be passed in as a param, as it uses curly braces
        """

        if command_name in self.commands:
            print("Warning,",command_name, "exists, overwriting")

        self.commands[ command_name ] = command

    def get( self, command_name, **params ):
        """Gets the command, with the params applied
            :returns:   returns the command with the params applied
                        otherwise returns None, if the command is not found
        """

        if command_name not in self.commands:
            print( "Error, ", command_name, "not found" )
            return None

        return self.commands[ command_name ].format( **params )

    def remove( self, command_name ):

        if command_name in self.commands:
            del self.commands[ command_name ]

    def invoke( self, command_name, background=True, callback=None, **params ):
        """Executes the command om the az cli"""
        return self.cli.invoke(self.get( command_name,
                                         background=background,
                                         callback=callback,
                                         **params ))

