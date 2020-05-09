import subprocess
import threading
import json

class az:

    def __init__( self ):
        self.event_id = -1

    def invoke( self, command, background=True, callback=None ):
        """ invokes a command on the azure CLI

        :param command:         command to be executed
        :param background:      should the command be executed in the background
                                if false waits for command to finish executions
        :param callback:        (optional) callback must have paras
                                    - event_id (int)
                                    - data (type dict)
                                Only used if background is true. the callback is invoked
                                when the command finishes execution.
                                if data is None an error occurred
        :return:                if not background, returns json data as dict, if error None
                                if is  background, returns the event id.
                                use callback to get data for event_id
                                once executions has finished.
        """

        if background:
            self.event_id += 1
            threading.Thread( target=self.__background_invoke, args=(command, self.event_id, callback))
            return self.event_id
        else:
            return self.__invoke_az_command( command )

    def __background_invoke( self, command, event_id, callback ):

        data = self.__invoke_az_command( command )

        if callback is not None:
            callback( event_id, data )

    def __invoke_az_command( self, command ):

        # execute the command via a subprocess.
        # we use a subprocess to access the stdout,
        # and get the results of the command

        # python to be executed in sub process
        impo = "import os;"
        command = "os.system( '" + command + "' )"

        proc = subprocess.Popen( [ 'python', '-c', impo + command ], stdout=subprocess.PIPE )

        # retrieve the outcome of the subprocess
        json_str = ""

        # read all the lines from the stdout
        while True:

            line = proc.stdout.readline().decode( "utf-8" )

            if not line:
                break
            else:
                json_str = json_str + line

        proc.kill()

        # convert the json string into a dict.
        try:
            return json.loads( json_str )
        except Exception as e:
            print("Error:", e)
            print( "az response:", json_str)
            return None
