import click

__all__ = ["delete_command"]


@click.command(name="delete")
def delete_command() -> None:
    pass


if __name__ == "__main__":
    delete_command([], standalone_mode=False)
