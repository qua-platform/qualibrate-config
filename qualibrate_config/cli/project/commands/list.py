import click

__all__ = ["list_command"]


@click.command(name="list")
def list_command() -> None:
    pass


if __name__ == "__main__":
    list_command([], standalone_mode=False)
