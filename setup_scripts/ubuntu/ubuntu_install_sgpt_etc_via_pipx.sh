#!/bin/bash

set -e  # Exit on error
set -x # Report commands executed
export DEBIAN_FRONTEND=noninteractive

# Install pipx if not already installed
if ! command -v pipx &>/dev/null; then
    echo "Installing pipx..."
    sudo apt update -y
    sudo apt install -y pipx
    pipx ensurepath
else
    echo "pipx is already installed."
fi

# Ensure pipx binary path is in the user's profile and current session
PIPX_BIN_PATH="$HOME/.local/bin"

if ! grep -q "$PIPX_BIN_PATH" "$HOME/.profile"; then
    echo "" >> "$HOME/.profile"
    echo "# Add pipx to PATH" >> "$HOME/.profile"
    echo "export PATH=\"$PIPX_BIN_PATH:\$PATH\"" >> "$HOME/.profile"
fi

# Ensure the path is updated in the current shell session
export PATH="$PIPX_BIN_PATH:$PATH"

# Function to install a tool via pipx only if not already available
install_pipx_tool() {
    local tool_cmd="$1"
    local install_cmd="$2"

    if ! command -v "$tool_cmd" &>/dev/null; then
        echo "Installing $tool_cmd via pipx..."
        pipx install "$install_cmd"
    else
        echo "$tool_cmd is already installed."
    fi
}

# Install grep-ast if not available
install_pipx_tool "grep-ast" "grep-ast"

# Install shell-gpt if sgpt is not available
install_pipx_tool "sgpt" "shell-gpt"

# Install aider-chat if aider is not available
install_pipx_tool "aider" "aider-chat"

echo "All installations are completed. Restart your shell or run 'source ~/.profile' to apply changes."

