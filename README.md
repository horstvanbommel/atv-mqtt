# atv-mqtt

Python daemon bridging KNX home automation (via Gira HomeServer + MQTT) with Apple TVs.

## Directory Overview

```
atv-mqtt/
├── scripts/                       # Production and operational scripts
│   ├── atv_mqtt_bridge.py         # Main daemon: KNX ↔ MQTT ↔ Apple TV bridge
│   ├── com.fbn.atvbridge.plist    # launchd plist config for macOS
│   ├── com.fbn.atvbridge.newsyslog.conf  # newsyslog rotation for launchd stdout/stderr logs (macOS)
│   ├── atv-mqtt.logrotate         # logrotate rotation for OpenRC stdout/stderr logs (Alpine)
├── docs/
│   └── arc42/                     # Architecture documentation (§01–§12)
└── .claude/                       # Claude Code configuration (hooks, rules, commands)
```

## Setup

Requires Python 3.9.6 (as used by `/usr/bin/python3` on the deployment host).
Dependencies are hard-pinned in `requirements.txt` for exact recovery.

The script itself only logs to stdout/stderr — it writes no log file of its
own. Each platform's service manager redirects that output into files and is
also responsible for rotating them, so those files never grow unbounded.

### Installation (macOS / launchd)

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
   (`/tmp/atvbridge.out`, `/tmp/atvbridge.err`):
   ```bash
   sudo cp scripts/com.fbn.atvbridge.newsyslog.conf /etc/newsyslog.d/
   ```

To recover on a new/replacement host, repeat these five steps — steps 1 and 3
reproduce the exact code and dependency versions, step 2 restores credentials
from a backed-up `.env`.

### Installation (Alpine Linux / OpenRC)

The service is defined as an OpenRC init script at `/etc/init.d/atv-mqtt`
(`RC_SVCNAME=atv-mqtt`), which captures stdout/stderr into `output_log`/
`error_log`:

```sh
#!/sbin/openrc-run

# Name des Dienstes im Status
description="ATV-MQTT Bridge"

# Bestimmt die Startreihenfolge: Startet erst NACH Mosquitto und Netzwerk
depend() {
    need net mosquitto
    after mosquitto
}

# Pfad zu Python und deinem Skript
command="/usr/bin/python3"
command_args="/opt/atv-mqtt/scripts/atv_mqtt_bridge.py"

# Lässt den Prozess im Hintergrund als Daemon laufen
command_background=true

# Speicherort für Prozess-ID und Logs
pidfile="/run/${RC_SVCNAME}.pid"
output_log="/var/log/${RC_SVCNAME}.log"
error_log="/var/log/${RC_SVCNAME}.err"
```

1. Clone the repo and set up `.env` and dependencies as in steps 1–3 above
   (adjust paths, e.g. `/opt/atv-mqtt`).
2. Install and start the OpenRC service (using an init script like the one
   above):
   ```bash
   rc-update add atv-mqtt default
   rc-service atv-mqtt start
   ```
3. Install log rotation for `/var/log/atv-mqtt.log` / `.err`:
   ```bash
   apk add logrotate
   cp scripts/atv-mqtt.logrotate /etc/logrotate.d/atv-mqtt
   rc-update add crond default
   rc-service crond start
   ```
   `scripts/atv-mqtt.logrotate` rotates weekly or at 5 MB, keeping 5
   compressed backups, and uses `copytruncate` since OpenRC keeps
   `output_log`/`error_log` open for the lifetime of the process.

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
