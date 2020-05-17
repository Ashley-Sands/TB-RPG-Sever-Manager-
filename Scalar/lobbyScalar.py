import Scalar.baseScalar as baseScalar


class LobbyScalar( baseScalar.BaseScalar ):

     def init_commands( self ):
         self.az_commands.add("list", "az container list "
                                      "--resource-group rpg_network_we "
                                      "--query '[].{id:id, ip:ipAddress.ip, image:containers[0].image, status:provisioningState}' "
                                      "--output json")
