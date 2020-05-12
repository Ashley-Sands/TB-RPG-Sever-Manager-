import Common.azCli as azCli
import re

class azCommands():

    def __init__( self ):

        self.cli = azCli.az()
        self.commands = { }

    def add( self, command_name, command):
        """ Add a command to the dict of commands

        :param command_name: the name of the command
        :param command:      the command to be executed.
        The commands must be formatted in the azure cli style
        except, replace values with {}. ie.
        'az vm create --group {} --location {} --size {}'
        You are also required to use the long parameter names,
        short hand params are ignored! This is by design, for
        clarity purposes.
        any value contained within the curly braces is treated as
        the default value and always emitted, unless overridden.

        Lastly if you rather use short param names to rebuild the commands
        use the set_param_alias function

        It might be worth noting anything not extracted from the command string will be left in
        """

        if command_name in self.commands:
            print("Warning,",command_name, "exists, overwriting")

        extracted_params = [] # list of tuples (param_name, default_value)

        # extract the params and replace with '{param_name}' ready for re-build
        com = re.split("(-{2,}[\w-]{2,}\s*\{[\s]*[-_\w\d]*[\s]*\})", command) # split command into sub sections

        # replace the params we are interested in with {param name}
        for i in range(0, len(com)):
            param = re.split( "(\{[\s]*[-_\w\d\s]*[\s]*\})", com[i] )

            # if the length is more than one we need to extract the param name and default value
            if len(param) > 1:
                param_name = re.sub("^--| +", "", param[0])  
                param_default = re.sub("[\{\} ]+", "", param[1])
                com[i] = "{"+param_name+"}"
                extracted_params.append( (param_name, param_default) )

        command_str = ' '.join(com).replace("  ", " ")

        self.commands[command_name] = Command(command_str, extracted_params)

    def add_param_alias( self, command_name, param_name, alias_name ):

        if command_name in self.commands:
            self.commands[command_name].param_alias[alias_name] = param_name

    def get( self, command_name, **params ):
        """ Rebuild the command for command_name, with only the supplied
            params and default values.
            :returns:   returns the command with the params applied
                        otherwise returns None, if the command is not found
        """

        if command_name not in self.commands:
            print( "Error, ", command_name, "not found" )
            return None

        return self.commands[ command_name ].build( **params )

    def remove( self, command_name ):

        if command_name in self.commands:
            del self.commands[ command_name ]

    def invoke( self, command_name, background=True, callback=None, **params ):
        """Executes the command om the az cli"""
        return self.cli.invoke(self.get( command_name,
                                         background=background,
                                         callback=callback,
                                         **params ))


class Command:

    def __init__( self, command, params):
        """

        :param command:  the az command. format: az vm create {param_1} {param_2} --fixed_param
        :param params:   list of tuples (param_name, default) default may be empty or none
                         the param names must match the params in the command
        """
        self.command = command
        # dict of all available params
        self.params = {}              # key param name, param string, ie --location {0}
        # dict of param alias
        self.param_alias = {}         # key alias name, value param name

        # dict with each default params output
        # default param string #
        # if theres no default value empty otherwise --location uksouth
        # the idea is to copy the template when we are building the az command
        # and update with the required values
        self.template_params_str = {}        # key param name, default param string.

        # build the param definitions and template
        for p in params:
            param_name, param_default = p

            # if the param name is illegal create an alias
            if re.search( "\w-\w", param_name ) is not None:
                alias_name = param_name.replace("-", "")
                self.param_alias[alias_name] = param_name
                print("found illegal function param name in command:", ' '.join(command.split(" ")[:3])  ,
                      "creating alias: ", alias_name, "for", param_name)

            self.params[param_name] = "--"+param_name+" {0}"

            self.template_params_str[param_name] = ""

            if param_default and param_default.strip():
                self.template_params_str[param_name] = self.params[param_name].format(param_default)

    def build( self, **params ):

        # copy the template and update the params that have been supplied
        params_str = dict( self.template_params_str )

        for p in params:
            if p in params_str:
                params_str[p] = self.params[p].format(params[p])
            elif p in self.param_alias:
                alias_name = self.param_alias[p]
                print(p, self.param_alias, self.params, '\n', self.template_params_str)

                if alias_name in params_str:
                    params_str[alias_name] = \
                        self.params[alias_name].\
                        format(params[p])

            else:
                print(p, self.param_alias)

        return self.command.format(**params_str)
        # return re.sub("[ ]+", " ", self.command.format(**params_str) )
