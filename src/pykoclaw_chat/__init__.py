"""Chat plugin for pykoclaw."""

from __future__ import annotations

import asyncio
import atexit
import re
import readline
from pathlib import Path

import click

from pykoclaw.agent_core import query_agent
from pykoclaw.config import settings
from pykoclaw.db import get_conversation, init_db
from pykoclaw.plugins import PykoClawPluginBase


def _setup_readline(history_path: Path) -> None:
    """Configure readline with persistent history."""
    history_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        readline.read_history_file(history_path)
    except FileNotFoundError:
        pass
    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, str(history_path))


def _readline_prompt(styled: str) -> str:
    """Wrap ANSI escapes with readline markers so prompt width is correct."""
    return re.sub(r"\x1b\[[0-9;]*m", lambda m: f"\x01{m.group()}\x02", styled)


async def _run_chat(name: str) -> None:
    """Run the interactive chat REPL."""
    db = init_db(settings.db_path)
    data_dir = settings.data

    _setup_readline(data_dir / "history")

    global_claude_md = data_dir / "CLAUDE.md"
    if not global_claude_md.exists():
        global_claude_md.touch()

    global_content = global_claude_md.read_text().strip()
    system_prompt = global_content if global_content else None

    existing = get_conversation(db, name)
    session_id = existing.session_id if existing else None

    prompt = _readline_prompt(click.style("> ", fg="green", bold=True))

    while True:
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            click.echo()
            break

        if not user_input:
            continue

        async for message in query_agent(
            user_input,
            db=db,
            data_dir=data_dir,
            conversation_name=name,
            system_prompt=system_prompt,
            resume_session_id=session_id,
        ):
            if message.type == "text":
                click.echo(click.style(message.text, fg="cyan"), nl=False)
            elif message.type == "result":
                session_id = message.session_id

        click.echo()


class ChatPlugin(PykoClawPluginBase):
    """Chat plugin that provides interactive chat functionality."""

    def register_commands(self, group: click.Group) -> None:
        """Register chat command with the Click group."""

        @group.command()
        @click.argument("name")
        def chat(name: str) -> None:
            """Start a chat session."""
            asyncio.run(_run_chat(name))

        return None
