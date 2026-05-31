default:
  @echo "openbci-mcp"
  @just --list

sync:
  uv sync --all-extras

test:
  uv run pytest

serve:
  uv run openbci-mcp --serve

stdio:
  uv run openbci-mcp --stdio

lint:
  uv run ruff check src tests
