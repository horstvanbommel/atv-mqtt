# atv-mqtt

Python daemon bridging KNX home automation (via Gira HomeServer + MQTT) with Apple TVs.

## Directory Overview

```
atv-mqtt/
├── scripts/                       # Production and operational scripts
│   ├── atv_mqtt_bridge.py         # Main daemon: KNX ↔ MQTT ↔ Apple TV bridge
│   ├── com.fbn.atvbridge.plist    # launchd plist config for MacOS
│   ├── com.fbn.atvbridge.newsyslog.conf  # newsyslog rotation for launchd stdout/stderr logs
├── docs/
│   └── arc42/                     # Architecture documentation (§01–§12)
└── .claude/                       # Claude Code configuration (hooks, rules, commands)
```

## Setup

Requires Python 3.9.6 (as used by `/usr/bin/python3` on the deployment host).
Dependencies are hard-pinned in `requirements.txt` for exact recovery.

### Installation (deployment host)

1. Clone the repo onto the host:
   ```bash
   git clone https://github.com/horstvanbommel/atv-mqtt.git /Users/Shared/atv-mqtt
   ```
2. Create the credentials file from the template and fill in real values
   (see [Credentials](#credentials) below):
   ```bash
   cd /Users/Shared/atv-mqtt
   cp scripts/env.example scripts/.env
   ```
3. Install the pinned dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
4. Install and start the launchd service:
   ```bash
   cp scripts/com.fbn.atvbridge.plist ~/Library/LaunchAgents/com.fbn.atvbridge.plist
   launchctl load ~/Library/LaunchAgents/com.fbn.atvbridge.plist
   ```
5. Install log rotation for the launchd stdout/stderr redirects
   (`/tmp/atvbridge.out`, `/tmp/atvbridge.err`). The application's own log
   file (`/tmp/atvbridge.log`) rotates itself:
   ```bash
   sudo cp scripts/com.fbn.atvbridge.newsyslog.conf /etc/newsyslog.d/
   ```

To recover on a new/replacement host, repeat these five steps — steps 1 and 3
reproduce the exact code and dependency versions, step 2 restores credentials
from a backed-up `.env`.

### Credentials

`atv_mqtt_bridge.py` reads MQTT and Apple TV pairing credentials from a `.env`
file next to the script (never committed — see `.gitignore`). Copy the
template and fill in real values:

```bash
cp scripts/env.example scripts/.env
```

On the deployment host, the script runs from `/Users/Shared/atv-mqtt/scripts/`
(see `com.fbn.atvbridge.plist`), so `.env` must live there too:
`/Users/Shared/atv-mqtt/scripts/.env`.

## Architecture

See `docs/arc42/` for full arc42 documentation.
