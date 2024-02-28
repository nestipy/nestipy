import os.path

from nestipy.common.templates.generator import TemplateGenerator


class NestipyCliHandler:
    generator: TemplateGenerator

    def __init__(self):
        self.generator = TemplateGenerator()

    def create_project(self, name) -> bool:
        destination = os.path.join(os.getcwd(), name)
        if os.path.exists(destination):
            return False
        self.generator.copy_project(destination)
        return True

    @classmethod
    def mkdir(cls, name):
        path = os.path.join(os.getcwd(), 'src', name)
        if not os.path.exists(path):
            os.mkdir(path)
            open(os.path.join(path, '__init__.py'), 'a').close()
        return path

    def generate_resource_api(self, name):
        self.generate_dto(name)
        self.generate_service(name)
        self.generate_controller(name)
        self.generate_module(name)

    def generate_resource_graphql(self, name):
        self.generate_input(name)
        self.generate_service(name)
        self.generate_resolver(name)
        self.generate_module(name, prefix='graphql')

    def generate_module(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'module', prefix=prefix)
        self.modify_app_module(name)

    def generate_controller(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'controller', prefix=prefix)

    def generate_service(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'service', prefix=prefix)

    def generate_resolver(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'resolver', prefix=prefix)

    def generate_dto(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'dto', prefix=prefix)

    def generate_input(self, name: str, prefix: str = None):
        path = self.mkdir(name)
        self.generate(name, path, 'input', prefix=prefix)

    def generate(self, name, parent_path, template, prefix: str = None):
        content = self.generator.render_template(
            f'{prefix}_' if prefix is not None else ''
                                                    f"{template}.txt", name=name)
        file_path = str(os.path.join(parent_path, f"{name.lower()}_{template}.py"))
        print(file_path)
        f = open(file_path, 'w+')
        f.write(content)
        f.close()

    @classmethod
    def modify_app_module(cls, name):
        name = str(name)
        app_path = os.path.join(os.getcwd(), 'src', 'app_module.py')
        if os.path.exists(app_path):
            new_import = f"{str(name).capitalize()}Module"
            with open(app_path, 'r') as file:
                file_content = file.read()
                file.close()
                module_pattern = r'@Module\(([^)]*)\)'
                text_to_add = f'from .{name.lower()}.{name.lower()}_module import {name.capitalize()}Module'
                import re
                match = re.search(module_pattern, file_content)
                if match:
                    existing_imports_str = match.group(1)
                    existing_imports_match = re.search(r'imports=\[(.*?)\]', existing_imports_str)
                    if existing_imports_match:
                        existing_imports = existing_imports_match.group(1)
                        new_imports = existing_imports + ', ' + new_import
                        modified_imports_str = re.sub(r'imports=\[(.*?)\]', 'imports=[' + new_imports + ']',
                                                      existing_imports_str)
                        modified_content = file_content.replace(match.group(0),
                                                                text_to_add + '\n@Module(' + modified_imports_str + ')')
                    else:
                        # If imports=[] doesn't exist, add imports directly
                        modified_content = file_content.replace(match.group(0),
                                                                text_to_add + f'\n@Module(\n\timports=[{new_import}],'
                                                                              f'{existing_imports_str})')
                    with open(app_path, 'w') as file2:
                        file2.write(modified_content)
                        file2.close()
                else:
                    print("No @Module decorator found in the file.")
