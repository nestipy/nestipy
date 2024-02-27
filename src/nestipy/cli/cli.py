import click
import questionary

from nestipy.cli.handler import NestipyCliHandler
from nestipy.cli.style import CliStyle
from click_aliases import ClickAliasedGroup

handler = NestipyCliHandler()
echo = CliStyle()


@click.group(cls=ClickAliasedGroup)
def main():
    pass


@main.command()
@click.argument('name')
def new(name):
    """ Create new project """
    # if not shutil.which('poetry'):
    # curl -sSL https://install.python-poetry.org | python3 -
    click.clear()
    created = handler.create_project(name)
    if not created:
        echo.error(f"Folder {name} already exist.")
    echo.info(f"Project {name} created successfully.\nStart your project by running:\n\tcd {name}"
              f"\n\tpython -m pip install -r requirements.py\n\tpython main.py")
    # else:
    #     echo.error(f"Nestipy need poetry as dependency manager.")


@main.group(cls=ClickAliasedGroup, name='generate', aliases=['g', 'gen'])
def make():
    """ Generate resource, module, controller, service, resolver, graphql input """
    pass


@make.command(name='resource', aliases=['r', 'res'])
@click.argument('name')
def resource(name):
    """Create new resource for project."""
    name = str(name).lower()
    choice = questionary.select('Select resource type:', choices=['api', 'graphql']).ask()
    if choice == 'graphql':
        handler.generate_resource_graphql(name)
    else:
        handler.generate_resource_api(name)
    echo.success(f"Resource created successfully inside src/{name}.")


@make.command(aliases=['mod'])
@click.argument('name')
def module(name):
    """Create new module"""
    name = str(name).lower()
    handler.generate_module(name, prefix='single')
    echo.success(f"Module created successfully inside src/{name}.")


@make.command()
@click.argument('name')
def controller(name):
    """ Create new controller """
    name = str(name).lower()
    handler.generate_controller(name, prefix='single')
    echo.success(f"Controller created successfully inside src/{name}.")


@make.command()
@click.argument('name')
def resolver(name):
    """ Create new graphql resolver """
    handler.generate_resolver(name, prefix='single')
    echo.success(f"Resolver created successfully inside src/{name}.")


@make.command()
@click.argument('name')
def service(name):
    """ Create new service """
    name = str(name).lower()
    handler.generate_service(name, prefix='single')
    echo.success(f"Service created successfully inside src/{name}.")


@make.command(name='input')
@click.argument('name')
def graphql_input(name):
    """ Create new service """
    name = str(name).lower()
    handler.generate_service(name, prefix='single')
    echo.success(f"Graphql Input created successfully inside src/{name}.")


if __name__ == "__main__":
    main()
