from typing import Optional, Any

import click


class CliStyle:

    @classmethod
    def info(cls, info: Optional[Any] = None, ):
        click.secho(info, fg='green')

    @classmethod
    def error(cls, info: Optional[Any] = None, ):
        click.secho(info, fg='red')

    @classmethod
    def warning(cls, info: Optional[Any] = None, ):
        click.secho(info, fg='orange')

    @classmethod
    def success(cls, info: Optional[Any] = None, ):
        click.secho(info, fg='green', bold=True)
