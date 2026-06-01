---
name: elevated-task-runner
description: >
  Runs a user-provided maintenance task bundle, optionally requiring
  elevated (sudo/root) privileges. Use when a task explicitly needs
  admin access: package installs, system config changes, service
  management, etc. The task files are reviewed before execution.
  Only use for trusted operations.
---

# Elevated Task Runner

Executes maintenance tasks that require root/sudo access.

## Use When

- Installing system packages (`apt-get`, `yum`, etc.)
- Managing system services (`systemctl`, etc.)
- Modifying system configuration files in `/etc/`
- Operations that explicitly need root privileges

## Execution Pattern

1. **Read** the task file or command list
2. **Show** the user exactly what will be run and what privileges are needed
3. **Get explicit approval** (unless in auto-approve mode and task is trusted)
4. **Prepend `sudo`** to commands that need elevation (when available)
5. **Execute** and report results

## Example

```bash
# Package installation
sudo apt-get update && sudo apt-get install -y package-name

# Service management
sudo systemctl restart service-name

# System config (always backup first)
cp /etc/config-file /etc/config-file.bak
sudo nano /etc/config-file
```

## Safety Rules

- **Always show the command** before executing
- **Backup files** before modifying system config
- **Prefer package managers** over manual file edits
- **Log all elevated operations** for audit trail
- **Never run untrusted scripts** with elevation
- **When in doubt, ask first**

## Railway / Container Notes

- This container runs as `hermes` (uid 10000) — `sudo` is not installed
- Use Railway CLI (`railway run <command>`) for privileged operations in Railway
- For local dev, ensure `sudo` is installed and the user has passwordless sudo configured
