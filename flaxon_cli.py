"""Expose commands owned by feature modules to the Flaxon CLI.

Run these commands from the project directory. Add another module's
install_cli_commands(globals()) call here when you add its commands.
"""

from modules.welcome.module import welcome

welcome.install_cli_commands(globals())


from flaxon.cli.base import Command


def seed_command(args, console):
    import asyncio
    from seed import seed
    asyncio.run(seed())
    return 0


seed = Command("seed", seed_command, help_text="Create sample projects and published help content")
