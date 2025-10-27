#!/usr/bin/env bash
set -euo pipefail

echo "Checking for leftover Nix installation files..."

if [ -f "/etc/bashrc.backup-before-nix" ]; then
  echo "Found /etc/bashrc.backup-before-nix"
  if grep -q "nix" /etc/bashrc.backup-before-nix; then
    echo "Error: /etc/bashrc.backup-before-nix contains 'nix' related content. Please clean it up manually."
    exit 1
  else
    echo "Restoring /etc/bashrc"
    sudo mv /etc/bashrc.backup-before-nix /etc/bashrc
  fi
fi

if [ -f "/etc/zshrc.backup-before-nix" ]; then
  echo "Found /etc/zshrc.backup-before-nix"
  if grep -q "nix" /etc/zshrc.backup-before-nix; then
    echo "Error: /etc/zshrc.backup-before-nix contains 'nix' related content. Please clean it up manually."
    exit 1
  else
    echo "Restoring /etc/zshrc"
    sudo mv /etc/zshrc.backup-before-nix /etc/zshrc
  fi
fi

echo "Running Nix installer in non-interactive mode..."
sh <(curl -L https://nixos.org/nix/install) --daemon --yes
