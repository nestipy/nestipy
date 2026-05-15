import pytest
from nestipy.ioc import NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer


@pytest.fixture(autouse=True)
def auto_clear_container():
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()
    yield
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()
