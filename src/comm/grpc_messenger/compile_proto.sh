#!/bin/bash

# Force the bash to execute on the folder where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Current working directory: $(pwd)"



python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    --mypy_out=. \
    --mypy_grpc_out=. \
    messenger.proto