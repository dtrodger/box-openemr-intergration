import asyncio
import shlex
import subprocess

import click
import aioredis


# Command line interface to flush Redis cache
@click.command()
def clear_cache():

    # Define coroutine
    async def clear_cache_task():
        cache_connection = await aioredis.create_redis(f'redis://localhost:6379', db=0)
        cache_conn = await aioredis.Redis(cache_connection)
        print(await cache_conn.flushdb())

    # Get event loop
    loop = asyncio.get_event_loop()

    # Send task to event loop
    loop.run_until_complete(clear_cache_task())


# Command line interface to kill celery process
@click.command()
def kill_celery():
    subprocess.call(shlex.split('pkill -9 celery'))


@click.group()
def cli():
    pass

# Expose command line interface to user if module run directly
if __name__ == '__main__':
    cli.add_command(clear_cache)
    cli.add_command(kill_celery)
    cli()
