import asyncio
import click
import json
from .config import load_config
from .glue import create_servers


@click.group()
def cli():
    pass


@cli.command(help="Start tallyd.")
@click.argument("CONFIG", type=click.File("r"))
def start(config):
    tallyd_config = load_config(json.load(config))
    asyncio.get_event_loop().run_until_complete(
        create_servers(tallyd_config))


if __name__ == "__main__":
    cli()
