import pytest
from unittest.mock import patch, MagicMock

from nestipy.metadata import ClassMetadata, Reflect


# Mock ModuleMetadata for testing
class ModuleMetadata:
    Providers = 'providers'
    Imports = 'imports'
    Exports = 'exports'


# Helper mock classes to simulate modules
class MockModule:
    pass


class MockImportedModule:
    pass


def test_class_metadata_initialization():
    # Test basic initialization
    module = MockModule()
    global_providers = ['global_provider1', 'global_provider2']

    metadata = ClassMetadata(module, global_providers)

    assert metadata.get_module() == module
    assert metadata.get_global_providers() == global_providers


def test_get_service_providers_no_imports():
    # Setup: Mock module and Reflect
    module = MockModule()
    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata', return_value=[]):
        providers, import_providers = metadata.get_service_providers()

    assert providers == []  # No providers set
    assert import_providers == []  # No import providers


def test_get_service_providers_with_providers():
    # Setup: Mock module and Reflect to return providers
    module = MockModule()
    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata') as mock_get_metadata:
        mock_get_metadata.side_effect = [
            ['provider1', 'provider2'],  # Providers for the current module
            []  # Imports for the current module (empty)
        ]
        providers, import_providers = metadata.get_service_providers()

    assert providers == ['provider1', 'provider2']
    assert import_providers == []


def test_get_service_providers_with_imports():
    module = MockModule()
    imported_module = MockImportedModule()

    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata') as mock_get_metadata:
        mock_get_metadata.side_effect = [
            [],  # Providers for the current module
            [imported_module],  # Imports (imported_module is being imported)
            ['exported_provider1'],
              False,  # Exports from imported module
        ]
        providers, import_providers = metadata.get_service_providers()

    assert providers == []  # No providers in the current module
    assert import_providers == ['exported_provider1']



def test_get_service_providers_with_re_exported_modules():
    module = MockModule()
    imported_module = MockImportedModule()

    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata') as mock_get_metadata:
        mock_get_metadata.side_effect = [
            [],
            [imported_module],  
            [imported_module],
            True,
            ['re_exported_provider'],
        ]
        providers, import_providers = metadata.get_service_providers()

    assert providers == []  # No providers in the current module
    assert import_providers == ['re_exported_provider']



def test_get_service_providers_with_dynamic_module():
    module = MockModule()
    dynamic_module = MagicMock()
    dynamic_module.module = MockImportedModule()

    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata') as mock_get_metadata:
        mock_get_metadata.side_effect = [
            [],  # No providers for the current module
            [dynamic_module],  # Imports, including the dynamic module
            [dynamic_module], 
             True,
              ['dynamic_provider'], # No exports from the dynamic module
            [],  # Providers from the dynamic module
        ]
        providers, import_providers = metadata.get_service_providers()

    assert providers == []  # No providers for the current module
    assert import_providers == ['dynamic_provider']



def test_get_service_providers_no_re_export():
    # Test case where an imported module has no exports
    module = MockModule()
    imported_module = MockImportedModule()

    metadata = ClassMetadata(module)

    with patch.object(Reflect, 'get_metadata') as mock_get_metadata:
        mock_get_metadata.side_effect = [
            [],  # Providers for the current module
            [imported_module],  # Imports
            [],  # No exports from imported module
        ]
        providers, import_providers = metadata.get_service_providers()

    assert providers == []
    assert import_providers == []


def test_get_global_providers():
    # Setup global providers check
    module = MockModule()
    global_providers = ['global_provider1', 'global_provider2']

    metadata = ClassMetadata(module, global_providers)
    assert metadata.get_global_providers() == global_providers

