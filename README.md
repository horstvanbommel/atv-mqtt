# atv-mqtt

Python daemon bridging KNX home automation (via Gira HomeServer + MQTT) with Apple TVs.

## Directory Overview

```
atv-mqtt/
├── scripts/                       # Production and operational scripts
│   ├── atv_mqtt_bridge.py         # Main daemon: KNX ↔ MQTT ↔ Apple TV bridge
│   ├── com.fbn.atvbridge.plist    # launchd plist config for MacOS
├── docs/
│   └── arc42/                     # Architecture documentation (§01–§12)
└── .claude/                       # Claude Code configuration (hooks, rules, commands)
```

## Setup

Requires Python 3.9.6 (as used by `/usr/bin/python3` on the deployment host).
Dependencies are hard-pinned in `requirements.txt` for exact recovery:

```bash
python3 -m pip install -r requirements.txt
```

### Credentials

`atv_mqtt_bridge.py` reads MQTT and Apple TV pairing credentials from a `.env`
file next to the script (never committed — see `.gitignore`). Copy the
template and fill in real values:

```bash
cp scripts/env.example scripts/.env
```

On the deployment host, the script runs from `/Users/Shared/atv-mqtt/`
(see `com.fbn.atvbridge.plist`), so `.env` must live there too:
`/Users/Shared/atv-mqtt/.env`.

## Architecture

See `docs/arc42/` for full arc42 documentation.
