from abc import ABC, abstractmethod

from litestar import Router


class AbstractModule(ABC):

    @abstractmethod
    def get_router(self) -> Router:
        pass
