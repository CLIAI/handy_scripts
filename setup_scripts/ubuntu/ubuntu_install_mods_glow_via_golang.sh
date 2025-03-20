#!/bin/bash

set -e  # Exit on error
set -x # Report commands executed
export DEBIAN_FRONTEND=noninteractive

# Detect Ubuntu version
UBUNTU_VERSION=$(grep -oP '(?<=VERSION_ID=")[0-9]+' /etc/os-release)

# Define Go paths
GO_ROOT="/usr/local/go"
GO_PATH="$HOME/go"
GO_BIN="$GO_PATH/bin"

# Ensure the system PATH includes Go binary path
if ! grep -q "$GO_BIN" "$HOME/.profile"; then
    echo "" >> "$HOME/.profile"
    echo "# Add Go and Go bin paths to PATH" >> "$HOME/.profile"
    echo "export PATH=\"$GO_BIN:\$PATH\"" >> "$HOME/.profile"
fi

# Apply the updated PATH in this session
export PATH="$GO_BIN:$PATH"

# Function to install Go with fallbacks
install_go() {
    if command -v go &>/dev/null; then
        echo "Go is already installed."
        return 0
    fi

    echo "Installing Go..."

    if [[ "$UBUNTU_VERSION" -ge 22 ]]; then
        sudo apt update -y
        sudo apt install -y golang-go || {
            echo "Failed to install Go using apt, attempting fallback..."
            sudo add-apt-repository -y ppa:longsleep/golang-backports
            sudo apt update
            sudo apt install -y golang-go
        }
    elif [[ "$UBUNTU_VERSION" -eq 20 ]]; then
        sudo add-apt-repository -y ppa:longsleep/golang-backports
        sudo apt update
        sudo apt install -y golang-go
    else
        echo "Unsupported Ubuntu version: $UBUNTU_VERSION. Please install Go manually."
        exit 1
    fi
}

# Install Go
install_go

# Ensure the Go environment is set up properly
export GOPATH="$GO_PATH"
export PATH="$GO_BIN:$PATH"

# Function to install a Go tool with fallback strategies
install_go_tool() {
    local tool_cmd="$1"
    local install_cmd="$2"
    local fallback_cmd="$3"

    if command -v "$tool_cmd" &>/dev/null; then
        echo "$tool_cmd is already installed."
        return 0
    fi

    echo "Installing $tool_cmd via go install..."
    if go install "$install_cmd"; then
        echo "$tool_cmd successfully installed."
    else
        echo "Failed to install $tool_cmd with go install, attempting fallback..."
        export GO111MODULE=on
        if go get "$fallback_cmd"; then
            echo "$tool_cmd installed using fallback method."
        else
            echo "Failed to install $tool_cmd. Please check your Go installation."
            exit 1
        fi
    fi
}

# Install `glow`
install_go_tool "glow" "github.com/charmbracelet/glow@latest" "github.com/charmbracelet/glow"

# Install `mods`
install_go_tool "mods" "github.com/charmbracelet/mods@latest" "github.com/charmbracelet/mods"

echo "All installations are completed. Restart your shell or run 'source ~/.profile' to apply changes."

