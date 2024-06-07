from unittest.mock import MagicMock, patch, Mock

import pytest

from nestipy.common.decorator.class_ import Controller, Module, ModuleMetadata, RouteKey


# Mocks for NestipyContainer and Reflect
@pytest.fixture
def mock_container() -> Mock:
    with patch('nestipy.ioc.container.NestipyContainer') as MockContainer:
        instance = MockContainer.get_instance.return_value
        yield instance


@pytest.fixture
def mock_reflect() -> Mock:
    with patch('nestipy.metadata.Reflect') as MockReflect:
        yield MockReflect


# Controller tests
def test_controller(mock_container: Mock, mock_reflect: Mock) -> None:
    @Controller(path='/test')
    class TestClass:
        pass

    mock_container.add_singleton.assert_called_once_with(TestClass)
    mock_reflect.set_metadata.assert_any_call(TestClass, RouteKey.path, '/test')
    mock_reflect.set_metadata.assert_any_call(TestClass, RouteKey.kwargs, {})


# Module tests
def test_module(mock_container, mock_reflect):
    providers = [MagicMock()]
    controllers = [MagicMock()]
    imports = [MagicMock()]
    exports = [MagicMock()]
    is_global = True

    @Module(providers=providers, controllers=controllers, imports=imports, exports=exports, is_global=is_global)
    class TestModule:
        pass

    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Providers, providers)
    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Controllers, controllers)
    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Imports, imports)
    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Exports, exports)
    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Global, is_global)
    mock_reflect.set_metadata.assert_any_call(TestModule, ModuleMetadata.Module, True)
    mock_container.add_singleton.assert_called_once_with(TestModule)
