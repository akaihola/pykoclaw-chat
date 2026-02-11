"""Chat plugin for pykoclaw."""

from __future__ import annotations

import click

from pykoclaw.plugins import PykoClawPluginBase


class ChatPlugin(PykoClawPluginBase):
    """Chat plugin that provides interactive chat functionality."""

    def register_commands(self, group: click.Group) -> None:
        """Register chat command with the Click group."""

        @group.command()
        def chat() -> None:
            """Start an interactive chat session."""
            click.echo("Chat plugin loaded (stub implementation)")

        return None
