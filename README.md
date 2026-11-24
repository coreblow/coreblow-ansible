# CoreBlow Ansible

Idempotent server provisioning and OS-level hardening automation for CoreBlow Sovereign Agent-OS & Gateway.

## Overview

CoreBlow Ansible is part of the CoreBlow public repository family. It provides an automated, idempotent Ansible role and playbook to bootstrap, harden, and manage headless CoreBlow gateway daemon hosts on Linux (Ubuntu, Debian, RHEL).

This repository follows the same ecosystem split that CoreBlow uses to keep release surfaces small, auditable, and independently governed.

## Repository Role

- Status: Active
- Phase: 5
- Priority: infra
- Kind: ansible
- Family: CoreBlow public repository family
- Branding: CoreBlow

## Hardening & Security Features

- **Dedicated Service User**: Isolated `coreblow` system user and group (`create_home: true`, system account).
- **Strict Configuration Permissions**: Enforces `0700` filesystem permissions on `~/.coreblow` state directory.
- **Node.js 22+ Baseline**: Automated validation ensuring LTS Node.js 22 runtime is present.
- **Hardened Systemd Unit**:
  - `NoNewPrivileges=yes`: Prevents privilege escalation.
  - `ProtectSystem=strict`: Mounts `/usr`, `/boot`, and `/etc` read-only.
  - `ProtectHome=read-only`: Restricts home directory modifications with explicit writable `~/.coreblow`.
  - `PrivateTmp=yes` and `PrivateDevices=yes`: Sandboxes `/tmp` and restricts raw hardware device access.
  - `ProtectKernelTunables=yes` & `ProtectControlGroups=yes`: Protects kernel parameters and cgroups.
- **Firewall Integration**: Automated UFW rule opening TCP port 18789 for CoreBlow Gateway.
- **Gateway Healthcheck**: Integrated healthcheck polling `http://127.0.0.1:18789/health` after startup.

## Usage

### Run Playbook

```sh
# Copy inventory sample
cp inventory-sample.yml inventory.yml

# Provision and harden managed servers
ansible-playbook -i inventory.yml playbook.yml
```

### Role Variables (`roles/coreblow_host/defaults/main.yml`)

| Variable | Default | Description |
|---|---|---|
| `coreblow_service_name` | `coreblow` | Systemd service unit name |
| `coreblow_user` | `coreblow` | Dedicated service user |
| `coreblow_gateway_port` | `18789` | Gateway TCP port |
| `coreblow_gateway_host` | `127.0.0.1` | Gateway bind interface |
| `coreblow_version` | `2.1.2` | CoreBlow npm version |
| `coreblow_enable_ufw` | `true` | Manage UFW firewall rule |

## Development & Verification

```sh
# Run deterministic syntax and structural validation
npm test
# Or directly:
python3 scripts/check-ansible-role.py

# If ansible-playbook is installed:
ansible-playbook --syntax-check playbook.yml
```

## Release Policy

Do not publish packages, tags, installers, or release artifacts from this repository without explicit CoreBlow release approval.

Version changes must follow the coordinated CoreBlow release plan.

## Links

- [CoreBlow](https://github.com/coreblow/coreblow)
- [Documentation](https://docs.coreblow.com)
- [Website](https://coreblow.com)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
