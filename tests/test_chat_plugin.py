"""Tests for the chat plugin."""

from __future__ import annotations

import click

from pykoclaw_chat import ChatPlugin


def test_chat_plugin_implements_protocol() -> None:
    """Test that ChatPlugin implements PykoClawPlugin protocol."""
    from pykoclaw.plugins import PykoClawPlugin

    plugin = ChatPlugin()
    assert isinstance(plugin, PykoClawPlugin)


def test_register_commands_adds_chat_command() -> None:
    """Test that register_commands adds chat command to Click group."""
    plugin = ChatPlugin()
    group = click.Group()

    plugin.register_commands(group)

    assert "chat" in group.commands
    assert isinstance(group.commands["chat"], click.Command)


def test_chat_command_has_name_argument() -> None:
    """Test that chat command has name argument."""
    plugin = ChatPlugin()
    group = click.Group()

    plugin.register_commands(group)

    chat_cmd = group.commands["chat"]
    params = chat_cmd.params

    assert len(params) == 1
    assert params[0].name == "name"
    assert isinstance(params[0], click.Argument)


def test_chat_plugin_default_methods() -> None:
    """Test that ChatPlugin has default implementations for other methods."""
    import sqlite3

    plugin = ChatPlugin()

    db = sqlite3.connect(":memory:")
    servers = plugin.get_mcp_servers(db, "test")
    assert servers == {}

    migrations = plugin.get_db_migrations()
    assert migrations == []

    config_cls = plugin.get_config_class()
    assert config_cls is None
