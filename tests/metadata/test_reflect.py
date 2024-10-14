import unittest

from nestipy.metadata import Reflect


class TestReflect(unittest.TestCase):
    def setUp(self):
        # Create a sample class and function for testing
        class SampleClass:
            pass

        def sample_function():
            pass

        self.sample_class = SampleClass
        self.sample_function = sample_function
        self.sample_instance = SampleClass()

    def test_set_metadata_on_class(self):
        # Set metadata on a class and verify it's stored correctly
        Reflect.set_metadata(self.sample_class, "test_key", "test_value")
        metadata = Reflect.get_metadata(self.sample_class, "test_key")
        self.assertEqual(metadata, "test_value")

    def test_set_metadata_on_instance(self):
        # Set metadata on an instance and verify it's stored correctly
        Reflect.set_metadata(self.sample_instance, "instance_key", "instance_value")
        metadata = Reflect.get_metadata(self.sample_instance, "instance_key")
        self.assertEqual(metadata, "instance_value")

    def test_set_metadata_on_function(self):
        # Set metadata on a function and verify it's stored correctly
        Reflect.set_metadata(self.sample_function, "function_key", "function_value")
        metadata = Reflect.get_metadata(self.sample_function, "function_key")
        self.assertEqual(metadata, "function_value")

    def test_get_metadata_with_default(self):
        # Test getting metadata that doesn't exist returns the default value
        default_value = Reflect.get_metadata(
            self.sample_class, "non_existent_key", "default_value"
        )
        self.assertEqual(default_value, "default_value")

    def test_get_metadata_without_default(self):
        # Test getting metadata that doesn't exist returns None when no default is provided
        metadata = Reflect.get_metadata(self.sample_class, "non_existent_key")
        self.assertIsNone(metadata)

    def test_get_metadata_direct_access(self):
        # Set metadata and directly access the entire metadata dictionary
        Reflect.set_metadata(self.sample_class, "key1", "value1")
        Reflect.set_metadata(self.sample_class, "key2", "value2")

        all_metadata = Reflect.get(self.sample_class)
        self.assertEqual(all_metadata["key1"], "value1")
        self.assertEqual(all_metadata["key2"], "value2")


if __name__ == "__main__":
    unittest.main()
