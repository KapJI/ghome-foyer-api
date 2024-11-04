#!/bin/bash

set -e

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd "$SCRIPT_DIR/.."
uv sync
uv run python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. --mypy_out=readable_stubs:. --mypy_grpc_out=readable_stubs:.  ghome_foyer_api/api.proto
uv run pre-commit run --hook-stage manual --all-files
