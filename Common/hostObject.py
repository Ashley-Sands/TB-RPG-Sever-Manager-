
class HostObject:

    TYPE_UNDEFINED = -1
    TYPE_VM = 0
    TYPE_CONTAINER = 1

    STATE_INIT = 0
    STATE_IDLE = 1
    STATE_ALLOCATED = 2
    STATE_SHUTDOWN = 3

    STATUS_FAILED   = -1
    STATUS_INACTIVE = 0
    STATUS_RUNNING  = 1

    def __init__( self, scalar_id, host_type, az_id="", az_name="", host_addr=None, state=STATE_INIT ):

        self.azure_id = az_id
        self.azure_name = az_name

        self.type = host_type
        self.state = state
        self.status = HostObject.STATUS_INACTIVE

        self.scalar_host_id = scalar_id
        self.host_address = host_addr

    def complete_setup( self, az_id, az_name, host_address, state=STATE_IDLE ):

        self.azure_id = az_id
        self.azure_name = az_name
        self.host_address = host_address
        self.state = state

    def is_active( self ):
        return self.host_address is not None

    def is_available( self ):
        return self.state == HostObject.STATE_IDLE

    def can_shutdown( self ):
        return self.state == HostObject.STATE_IDLE  # and some time condision

    def shutdown( self ):
        self.state = HostObject.STATE_SHUTDOWN
        # some logic?