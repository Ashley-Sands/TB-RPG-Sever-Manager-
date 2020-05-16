import subprocess
import threading
import json

class az:

    event_id = -1

    def invoke( self, command, background=True, bg_callback=None ):
        """ invokes a command on the azure CLI

        :param command:         command to be executed
        :param background:      should the command be executed in the background
                                if false waits for command to finish executions
        :param bg_callback:     (optional) callback must have paras
                                    - event_id (int)
                                    - data (type dict)
                                Only used if background is true. the callback is invoked
                                when the command finishes execution.
                                if data is None an error occurred
        :return:                if not background, returns tuple (event_id, json data as dict), if error None
                                if is  background, returns tuple (event id, thread).
                                use callback to get data for event_id
                                once executions has finished.
        """

        az.event_id += 1

        if background:
            thread = threading.Thread( target=self.__background_invoke,
                                       args=(command, az.event_id, bg_callback) )
            thread.start()
            return az.event_id, thread
        else:
            return az.event_id, self.__invoke_az_command( command )

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
        command = "command='{0}';".format( command.replace("'", '"') )  # make sure the correct " or ' was used
        cmd = "os.system( command )"

        proc = subprocess.Popen( [ 'python', '-c', impo + command + cmd], stdout=subprocess.PIPE )

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

        print( "az response:", json_str )
        # convert the json string into a dict.
        try:
            return json.loads( json_str )
        except Exception as e:
            print("Error:", e)
            return None
