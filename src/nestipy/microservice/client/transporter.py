from abc import ABC, abstractmethod


class CustomTransportStrategy(ABC):
    @abstractmethod
    def listen(self, callback):
        pass

    @abstractmethod
    def close(self):
        pass
