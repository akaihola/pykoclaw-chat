"""Tests for the chat plugin."""

from __future__ import annotations

from pathlib import Path

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


# ---------------------------------------------------------------------------
# cwd-to-data-dir: _run_chat must not create per-conversation dirs or
# per-conversation CLAUDE.md files.
# ---------------------------------------------------------------------------


def test_run_chat_does_not_create_conversations_dir(tmp_path: "Path") -> None:
    """_run_chat must NOT create data_dir/conversations/{name}/ or conv CLAUDE.md."""
    import asyncio
    import sqlite3
    from unittest.mock import AsyncMock, patch

    from pykoclaw_chat import _run_chat

    data_dir = tmp_path / "workspace"
    data_dir.mkdir()

    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE conversations (
            name TEXT PRIMARY KEY,
            session_id TEXT,
            cwd TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            system_prompt_hash TEXT
        );
        """
    )

    with (
        patch("pykoclaw_chat.settings") as mock_settings,
        patch("pykoclaw_chat.init_db", return_value=db),
        patch("pykoclaw_chat.get_conversation", return_value=None),
        patch("builtins.input", side_effect=EOFError),
        patch("pykoclaw_chat.query_agent", new_callable=AsyncMock),
    ):
        mock_settings.data = data_dir
        mock_settings.db_path = ":memory:"

        asyncio.run(_run_chat("test-chat"))

    conv_dir = data_dir / "conversations" / "test-chat"
    assert not conv_dir.exists(), (
        f"Directory {conv_dir} should not be created. "
        "_run_chat should not create per-conversation subdirectories."
    )
    # Also verify no CLAUDE.md was created in a conversations/ subdir
    assert not (data_dir / "conversations").exists(), (
        "No conversations/ directory should exist at all."
    )
