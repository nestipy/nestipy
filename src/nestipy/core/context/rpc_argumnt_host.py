from .argument_host import ArgumentHost


class RpcArgumentHost(ArgumentHost):
    def get_args(self):
        pass

    def get_data(self):
        return self._socket_data
