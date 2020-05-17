import Scalar.baseScalar as baseScalar


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
                                       "--query {}" )