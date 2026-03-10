<p align="center"><img src="docs/images/banner.svg" alt="PiSpot Deployment banner" width="900"/></p>

<p align="center"><img src="https://github.com/GeiserX/PiSpot-Deployment/blob/main/extra/logo.jpg?raw=true" width="128" height="128" alt="PiSpot Deployment logo"/></p>

<h1 align="center">PiSpot Deployment</h1>

<p align="center">
  <strong>Interactive configuration wizard and fleet management tooling for the PiSpot Wi-Fi voucher ecosystem.</strong>
</p>

<p align="center">
  <a href="https://github.com/GeiserX/PiSpot-Deployment/blob/main/LICENSE"><img src="https://img.shields.io/github/license/GeiserX/PiSpot-Deployment" alt="License: GPL-3.0"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white" alt="Python 3"/></a>
  <a href="https://www.vaultproject.io/"><img src="https://img.shields.io/badge/secrets-Vault-FFEC6E?logo=vault&logoColor=black" alt="HashiCorp Vault"/></a>
  <a href="https://www.ansible.com/"><img src="https://img.shields.io/badge/deploy-Ansible-EE0000?logo=ansible&logoColor=white" alt="Ansible"/></a>
</p>

---

## Overview

PiSpot Deployment is the provisioning and secrets-management layer for the PiSpot IoT ecosystem. It provides an interactive CLI wizard that collects venue details and voucher parameters, validates all inputs, and pushes the resulting configuration into [HashiCorp Vault](https://www.vaultproject.io/). It also manages Vault token lifecycle and includes Ansible inventory for fleet-wide device management.

Part of the **PiSpot ecosystem**:

| Project | Description |
|---|---|
| [PiSpot Watch](https://github.com/GeiserX/PiSpot-Watch) | Wrist-wearable e-ink voucher device |
| [PiSpot Show](https://github.com/GeiserX/PiSpot-Show) | HDMI kiosk display for lobby TVs |
| **PiSpot Deployment** (this repo) | Fleet provisioning and Vault configuration |

---

## Features

- **Interactive configuration wizard** -- terminal-based UI (PyInquirer) collects venue name, town, device ID, Spotipo API credentials, voucher parameters, and Vault connection details with real-time input validation.
- **HashiCorp Vault integration** -- stores per-device configuration as KV secrets with structured paths (`{project}/{venue}_{town}_{id}`), using AppRole authentication.
- **Input validation** -- custom validators enforce UUID format for API keys, URL format for Vault addresses, and token format constraints before any write occurs.
- **Token lifecycle management** -- systemd-compatible renewal script monitors token TTL and auto-renews below a 10-day threshold, with rotating file logs.
- **Ansible fleet inventory** -- grouped inventory file for managing multiple PiSpot Watch and PiSpot Show devices across venues, with SSH and sudo configuration.
- **AWX/Docker support** -- custom Dockerfile template extending AWX with Vault CLI, MinIO client, and jq for CI/CD pipelines.

---

## How It Works

```
  Operator runs creator.py
         |
         v
  +------+------+
  | PyInquirer  |   Collects: venue, town, device ID,
  | CLI wizard  |   Spotipo API key, site number,
  |             |   duration, speed limits, Vault addr
  +------+------+
         |
         v
  +------+------+
  | HashiCorp   |   Writes KV secret:
  | Vault       |   pispot_voucher/{venue}_{town}_{id}
  | (AppRole)   |   containing all device config
  +------+------+
         |
         v
  +------+------+
  | Ansible     |   Playbooks in Watch/Show repos
  | (inventory) |   target grouped devices via SSH
  +-------------+
```

1. The operator runs the interactive wizard to configure a new venue/device.
2. The wizard validates all inputs and writes the configuration to Vault.
3. Ansible playbooks (in the Watch and Show repos) reference the same Vault secrets during provisioning.
4. A cron-scheduled token renewal script keeps Vault tokens alive across the fleet.

---

## Getting Started

### 1. Clone

```bash
git clone https://github.com/GeiserX/PiSpot-Deployment.git
cd PiSpot-Deployment
```

### 2. Install dependencies

```bash
pip3 install -r Interactive_Script/requirements.txt
```

Dependencies: `hvac`, `PyInquirer`, `pyfiglet`

### 3. Run the configuration wizard

```bash
python3 Interactive_Script/creator.py
```

The wizard will prompt for:
- Venue name and town
- Device identifier
- Spotipo API key (UUID format) and site number
- Voucher duration, speed limits (default: 1024/256 Kbps DL/UL)
- Vault address and token

### 4. Configure Ansible inventory

Edit the `hosts` file with your device IPs, SSH ports, and credentials:

```ini
[PiSpot_Voucher]
device1 ansible_host=10.80.1.2

[PiSpot_HDMI]
device2 ansible_host=10.80.2.2
```

Then run the deployment playbooks from the [Watch](https://github.com/GeiserX/PiSpot-Watch) or [Show](https://github.com/GeiserX/PiSpot-Show) repositories.

---

## Token Renewal

`vault-renew-token.py` runs as a cron job (weekly) and at boot. It checks the current token's TTL and renews it if below 10 days remaining. Logs are written to `/var/log/vault/renew-token.log` with automatic rotation.

```bash
# Example cron entry
0 12 * * 0 /usr/bin/python3 /path/to/vault-renew-token.py
```

---

## Project Structure

```
PiSpot-Deployment/
  Interactive_Script/
    creator.py             # Interactive configuration wizard
    requirements.txt       # Python dependencies
  vault-renew-token.py     # Vault token renewal service
  hosts                    # Ansible inventory (device groups, SSH config)
  Dockerfile.task.j2       # AWX custom task image (Vault CLI + MinIO + jq)
  LICENSE                  # GPL-3.0
```

---

## License

[GNU General Public License v3.0](LICENSE)

## Maintainers

[@GeiserX](https://github.com/GeiserX)

## Contributing

Contributions are welcome. [Open an issue](https://github.com/GeiserX/PiSpot-Deployment/issues/new) or submit a pull request.

This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct.
