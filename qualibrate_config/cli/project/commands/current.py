import click

__all__ = ["current_command"]


@click.command(name="current")
def current_command() -> None:
    pass


if __name__ == "__main__":
    current_command([], standalone_mode=False)
