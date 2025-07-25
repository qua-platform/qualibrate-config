import click

from qualibrate_config.cli import (
    config_command,
    migrate_command,
    project_group,
)


@click.group()
def cli() -> None:
    pass


cli.add_command(config_command)
cli.add_command(migrate_command)
cli.add_command(project_group)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
