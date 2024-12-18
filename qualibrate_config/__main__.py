import click

from qualibrate_config.cli.config import config_command


@click.group()
def cli() -> None:
    pass


cli.add_command(config_command)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
