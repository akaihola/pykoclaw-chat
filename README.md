# pykoclaw-chat

Interactive terminal chat plugin for [pykoclaw](https://github.com/akaihola/pykoclaw). Provides a
readline-based REPL for conversing with a Claude agent, with persistent
conversations that survive process restarts.

## Usage

```bash
pykoclaw chat <name>
```

The `NAME` argument is the conversation's unique identifier. It determines:

- **Filesystem directory** -- A per-conversation working directory is created at
  `~/.local/share/pykoclaw/conversations/<name>/`. The agent can read and write
  files here. A `CLAUDE.md` file in this directory serves as conversation-specific
  instructions.
- **Session resumption** -- The conversation's Claude SDK session ID is persisted
  in the database. Re-running `pykoclaw chat <name>` resumes the previous
  session with full conversation memory. Using a different name starts a fresh
  conversation.

### Examples

```bash
pykoclaw chat myproject     # Start or resume the "myproject" conversation
pykoclaw chat research      # A separate conversation
pykoclaw chat myproject     # Picks up where you left off
```

### In the REPL

- Type a message and press Enter to send it to the agent.
- The agent's response streams to the terminal as it is generated.
- Press **Ctrl+C** or **Ctrl+D** to exit.
- Command history is persisted across sessions in
  `~/.local/share/pykoclaw/history`.

## System prompts

Two user-editable `CLAUDE.md` files control the agent's behavior:

| File                                                     | Scope                                  |
| -------------------------------------------------------- | -------------------------------------- |
| `~/.local/share/pykoclaw/CLAUDE.md`                      | Global -- applies to all conversations |
| `~/.local/share/pykoclaw/conversations/<name>/CLAUDE.md` | Per-conversation                       |

Both files are created automatically on first use. Edit them to customize the
agent's instructions.

## How it works

1. On startup, the plugin opens the SQLite database and looks up the
   conversation by name.
2. If a previous session exists, its `session_id` is loaded for resumption.
3. Each user message is sent to `query_agent()` from the core library, which
   streams the response via the Claude Agent SDK.
4. After each response, the session ID is persisted so the conversation can be
   resumed later.

The agent has access to standard tools (Bash, file I/O, web search) and the
built-in pykoclaw MCP tools (task scheduling).

## Installation

```bash
uv tool install pykoclaw@git+https://github.com/akaihola/pykoclaw.git \
    --with=pykoclaw-chat@git+https://github.com/akaihola/pykoclaw-chat.git
```

Or with `uv pip install`:

```bash
uv pip install pykoclaw@git+https://github.com/akaihola/pykoclaw.git
uv pip install pykoclaw-chat@git+https://github.com/akaihola/pykoclaw-chat.git
```

See the [pykoclaw README](https://github.com/akaihola/pykoclaw) for more
details.
