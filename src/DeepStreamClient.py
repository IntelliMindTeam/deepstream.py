from src.Connection import Connection
from src import Constants
import json
from src.EventHandler import EventHandler
from pyee import EventEmitter


class DeepStreamClient(EventEmitter):

    def __init__(self, ip, port):
        super().__init__()
        self._ip = ip
        self._port = port
        self._connection = Connection(self, self._ip, self._port)
        self.event = EventHandler(self._connection, self)

    def login(self, credentials, callback):
        """
        :param credentials: A dict of credentials to authenticate against the server
        :param callback: Callback to be executed upon authentication
        :return: None
        """
        credentials = json.dumps(credentials, sort_keys=True)
        self._connection.authenticate(credentials, callback)

    def get_connection_state(self):
        return self._connection.state

    def _on_error(self, topic, event, message):
        print('======== You can catch all deepstream errors by subscribing to the error event ========')
        error_msg = event + ': ' + message

        if len(self.listeners('error')) != 0:
            self.emit('error', message, event, topic)
            self.emit(event, topic, message)
            return

        if topic is not None:
            error_msg += ' (' + topic + ')'

        #hack and a half. Clearing any remaining ack timeouts
        #not sure if need to do this
        for a in self.event._ack_timeout_register._register.values():
            a.cancel()

        raise Exception(error_msg) from None

    def _on_message(self, message):
        if message["topic"] == Constants.TOPIC_EVENT:
            self.event.handle(message)

