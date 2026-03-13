# openrct2-actiongen

Parses OpenRCT2 C++ source to extract game action signatures into a structured `actions.json`. This IR feeds Jinja2 templates to generate JS plugin handlers and Python Pydantic models.

## Usage

```bash
uv run openrct2-actiongen generate --openrct2-version v0.4.32
uv run openrct2-actiongen generate --openrct2-version v0.4.32 --output actions.json
uv run openrct2-actiongen generate --openrct2-source /path/to/OpenRCT2
```

## Version compatibility

Works with OpenRCT2 **v0.3.5.1+** (Nov 2021 onwards, 78–81 actions depending on version).

Versions before v0.2.6 have no plugin scripting system. Versions v0.3.0–v0.3.5 have scripting but use an older C-style enum format (`GAME_COMMAND_*`) that the parser doesn't support — v0.3.5.1 switched to `GameCommand::*` scoped enums which is what we parse.
