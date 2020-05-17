
class HostObject:

    TYPE_PROXY = 0
    TYPE_CONTAINER = 1
    TYPE_DB = 2

    STATE_INIT = 0
    STATE_IDLE = 1
    STATE_ALLOCATED = 2
    STATE_SHUTDOWN = 3

    STATUS_FAILED   = -1
    STATUS_INACTIVE = 0
    STATUS_RUNNING  = 1

    def __init__( self, host_id, az_id="", host_addr=None, state=STATE_INIT ):

        self.azure_id = az_id

        self.id = host_id   # ?? needed?? or just use it for the request id
        self.host_address = host_addr

        self.state = state
        self.status = HostObject.STATUS_INACTIVE

    def complete_setup( self, host_address ):

        self.host_address = host_address
        self.state = HostObject.STATE_IDLE

    def is_active( self ):
        return self.host_address is not None

    def is_available( self ):
        return self.state == HostObject.STATE_IDLE

    def can_shutdown( self ):
        return self.state == HostObject.STATE_IDLE  # and some time condision

    def shutdown( self ):
        self.state = HostObject.STATE_SHUTDOWN
        # some logic?