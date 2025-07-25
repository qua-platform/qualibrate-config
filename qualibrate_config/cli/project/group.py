import click

from .commands import (
    create_command,
    current_command,
    delete_command,
    list_command,
    switch_command,
)


@click.group(name="project", help="Manage projects")
def project_group() -> None:
    pass


project_group.add_command(create_command)
project_group.add_command(current_command)
project_group.add_command(delete_command)
project_group.add_command(list_command)
project_group.add_command(switch_command)
