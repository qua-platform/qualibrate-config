import click

__all__ = ["switch_command"]


@click.command(name="switch")
def switch_command() -> None:
    pass


if __name__ == "__main__":
    switch_command([], standalone_mode=False)
