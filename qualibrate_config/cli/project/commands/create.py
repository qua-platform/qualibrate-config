import click

__all__ = ["create_command"]


@click.command(name="create")
def create_command() -> None:
    pass


if __name__ == "__main__":
    create_command([], standalone_mode=False)
