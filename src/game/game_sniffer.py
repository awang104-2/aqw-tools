from game.aqw_backend import *
from network.sniffing import Sniffer
from network.layers import Raw


class GameSniffer(Sniffer):

    def __init__(self, server, *, daemon=False):
        if server not in AQW_SERVER_NAMES and server not in AQW_SERVER_IPS:
            raise ValueError('Not a valid server.')
        server = AQW_SERVERS.get(server, server)
        super().__init__(f'tcp and src host {server}', layers=[Raw], daemon=daemon)
        self._server = server

    @property
    def server(self):
        return self.server




