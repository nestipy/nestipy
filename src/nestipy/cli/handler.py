import os.path

import autoflake
import isort

from nestipy.cli.templates.generator import TemplateGenerator
import autopep8


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
            open(os.path.join(path, 'interface.py'), 'a').close()
        return path

    def generate_resource_api(self, name):
        self.generate_dto(name)
        self.generate_service(name)
        self.generate_controller(name)
        self.generate_module(name)

    def generate_resource_graphql(self, name):
        self.generate_input(name)
        self.generate_service(name, prefix='graphql')
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
        pref = f"{f'{prefix}_' if prefix is not None else ''}"
        content = self.generator.render_template(f"{pref}{template}.txt", name=name)
        file_path = str(os.path.join(parent_path, f"{name.lower()}_{template}.py"))
        print(file_path)
        f = open(file_path, 'w+')
        f.write(content)
        f.close()

    @classmethod
    def modify_app_module(cls, name):
        name = str(name)
        app_path = os.path.join(os.getcwd(), 'app_module.py')
        if os.path.exists(app_path):
            new_import = f"{str(name).capitalize()}Module"
            with open(app_path, 'r') as file:
                file_content = file.read()
                file.close()
                module_pattern = r'@Module\(\s*(.*?)\s*\)(?=\s*class\s+\w+\(.*\):)'

                text_to_add = f'from src.{name.lower()}.{name.lower()}_module import {name.capitalize()}Module'
                import re
                match = re.search(module_pattern, file_content, re.DOTALL)
                if match:
                    existing_imports_str = match.group(1)
                    existing_imports_match = re.search(r'imports\s*=\s*\[\s*((?:[^][]|\[[^\]]*\])*)\s*]',
                                                       existing_imports_str)
                    if existing_imports_match:
                        existing_imports = existing_imports_match.group(1)
                        new_imports = existing_imports + ',\n\t' + new_import if not existing_imports.strip().endswith(
                            ',') else existing_imports + new_import
                        modified_imports_str = re.sub(r'imports\s*=\s*\[\s*((?:[^][]|\[[^\]]*\])*)\s*]',
                                                      '\n\timports=[\n\t' + new_imports + '\n]',
                                                      existing_imports_str)
                        modified_content = file_content.replace(match.group(0),
                                                                text_to_add + '\n@Module(' + modified_imports_str + ')')
                    else:
                        # If imports=[] doesn't exist, add imports directly
                        modified_content = file_content.replace(match.group(0),
                                                                text_to_add + f'\n@Module(\n\timports=[{new_import}\n],'
                                                                              f'{existing_imports_str})')

                    cleaned_code = autoflake.fix_code(modified_content)
                    sorted_code = isort.code(cleaned_code)
                    fixed_code = autopep8.fix_code(sorted_code)
                    with open(app_path, 'w') as file2:
                        file2.write(fixed_code)
                        file2.close()

                else:
                    print("No @Module decorator found in the file.")
