#!/bin/bash

# Script aimed to install on fresh Ubuntu
# glow - terminal Markdown hilighter https://github.com/charmbracelet/glow
# mods - CLI for LLMs https://github.com/charmbracelet/mods/
#
# It has failover strategies to handle old Ubuntu insallations,
# tips from: https://gist.github.com/gwpl/26846ef3c066b3109a03101cb58349f0
# 
# Also in case of running e.g. on small VM, it will try to detect
# if compilation crashed due to little RAM
# and try to add temporarily extra swap file.

#!/bin/bash

set -e  # Exit on error
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

# Function to install Go with failover
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

# Ensure Go environment is set up properly
export GOPATH="$GO_PATH"
export PATH="$GO_BIN:$PATH"

# Function to check Go version
get_go_version() {
    go version | awk '{print $3}' | cut -d. -f2
}

GO_VERSION=$(get_go_version)

# Function to check available RAM
check_ram() {
    free -m | awk '/^Mem:/ { print $2 }'
}

AVAILABLE_RAM=$(check_ram)

# Cleanup function for swap file
cleanup_swap() {
    echo "Removing temporary swap file..."
    sudo swapoff /swapfile
    sudo rm -f /swapfile
    echo "Swap file removed."
}

# Function to create a temporary swap file
create_swap() {
    # Ensure cleanup on exit
    trap cleanup_swap EXIT

    echo "Adding temporary 2GB swap file to mitigate memory issues..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "Swap file added."
}

# Function to install a Go tool with fallback
install_go_tool() {
    local tool_cmd="$1"
    local install_cmd="$2"

    if command -v "$tool_cmd" &>/dev/null; then
        echo "$tool_cmd is already installed."
        return 0
    fi

    echo "Installing $tool_cmd via go install..."

    if go install "$install_cmd"; then
        echo "$tool_cmd successfully installed."
    else
        echo "Failed to install $tool_cmd with go install."

        # Check if the failure was caused by out-of-memory
        if dmesg | tail -n 20 | grep -q 'Out of memory'; then
            echo "It looks like Go installation was killed due to low memory."

            if [[ $(id -u) -ne 0 ]]; then
                echo "Warning: You are not running as root."
                echo "Available RAM: ${AVAILABLE_RAM}MB"
                echo "Consider increasing memory or adding swap manually."
                exit 1
            fi

            if [[ "$AVAILABLE_RAM" -lt 4000 ]]; then
                create_swap
                echo "Retrying installation of $tool_cmd after adding swap..."
                if go install "$install_cmd"; then
                    echo "$tool_cmd installed successfully after adding swap."
                    return 0
                else
                    echo "Failed to install $tool_cmd even after adding swap."
                    exit 1
                fi
            else
                echo "You have sufficient memory. Please check system logs for other issues."
                exit 1
            fi
        else
            echo "Installation failed for an unknown reason. Please check your system."
            exit 1
        fi
    fi
}

# Install `glow`
install_go_tool "glow" "github.com/charmbracelet/glow@latest"

# Install `mods`
install_go_tool "mods" "github.com/charmbracelet/mods@latest"

echo "All installations are completed. Restart your shell or run 'source ~/.profile' to apply changes."

