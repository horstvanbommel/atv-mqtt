import asyncio
import os
import paho.mqtt.client as mqtt
from pathlib import Path
from pyatv import connect, scan
from pyatv.const import Protocol, PowerState, DeviceState
from pyatv.interface import PowerListener, PushListener
import logging
import sys

# --- KONFIGURATION ---
# Zugangsdaten liegen NICHT im Code, sondern in einer .env-Datei neben
# diesem Skript (siehe README für das erwartete Format).

def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())

load_env_file(Path(__file__).resolve().parent / ".env")

MQTT_BROKER = os.environ["MQTT_BROKER"]
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ["MQTT_USER"]
MQTT_PW = os.environ["MQTT_PW"]

DEVICES = {
    "wohnzimmer": {
        "id": os.environ["ATV_WOHNZIMMER_ID"],
        "companion": os.environ["ATV_WOHNZIMMER_COMPANION"],
        "airplay": os.environ["ATV_WOHNZIMMER_AIRPLAY"],
    },
    "schlafzimmer": {
        "id": os.environ["ATV_SCHLAFZIMMER_ID"],
        "companion": os.environ["ATV_SCHLAFZIMMER_COMPANION"],
        "airplay": os.environ["ATV_SCHLAFZIMMER_AIRPLAY"],
    }
}

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ATV-Bridge] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('/tmp/atvbridge.log')]
)

# --- ZUSTANDSSPEICHER ---
last_states      = {}   # Power-States  {device_key: "0"|"1"}
last_play_states = {}   # Play-States   {device_key: int}

# DeviceState → MQTT-Payload Mapping
#   0 = Idle/Gestoppt  1 = Play  2 = Pause  3 = Loading
DEVICE_STATE_TO_MQTT = {
    DeviceState.Idle:     0,
    DeviceState.Stopped:  0,
    DeviceState.Playing:  1,
    DeviceState.Paused:   2,
    DeviceState.Seeking:  2,
    DeviceState.Loading:  3,
}
PLAY_STATE_LABELS = {0: "IDLE", 1: "PLAY", 2: "PAUSE", 3: "LOADING"}

# ─────────────────────────────────────────────────────────────
# MQTT Publish Helpers
# ─────────────────────────────────────────────────────────────

def send_status(client, device_key, numeric_val):
    topic = f"home/atv/{device_key}/state"
    label = {"0": "AUS", "1": "AN", "2": "OFFLINE", "3": "FEHLER"}.get(str(numeric_val), "???")
    client.publish(topic, str(numeric_val), retain=True)
    logging.info(f"📤 [MQTT] Power: {device_key} → {numeric_val} ({label})")

def send_play_status(client, device_key, numeric_val: int):
    topic = f"home/atv/{device_key}/play_state"
    label = PLAY_STATE_LABELS.get(numeric_val, "?")
    client.publish(topic, str(numeric_val), retain=True)
    logging.info(f"🎬 [MQTT] Play:  {device_key} → {numeric_val} ({label})")

# ─────────────────────────────────────────────────────────────
# State Processing (nur bei Änderung senden)
# ─────────────────────────────────────────────────────────────

def process_power_state(device_key, state, mqtt_client, source="Monitor"):
    state_name = state.name if hasattr(state, 'name') else str(state)
    val = "1" if state_name in ["On", "Dimming"] else "0"
    if last_states.get(device_key) != val:
        logging.info(f"🔄 [Power] {device_key}: {last_states.get(device_key)} → {val} via {source}")
        send_status(mqtt_client, device_key, val)
        last_states[device_key] = val
    else:
        logging.debug(f"🤫 [Power] {device_key} unverändert {val}")

def process_play_state(device_key, device_state, mqtt_client, source="Push"):
    val = DEVICE_STATE_TO_MQTT.get(device_state, 0)
    if last_play_states.get(device_key) != val:
        logging.info(f"🔄 [Play]  {device_key}: {last_play_states.get(device_key)} → {val} "
                     f"({device_state.name}) via {source}")
        send_play_status(mqtt_client, device_key, val)
        last_play_states[device_key] = val
    else:
        logging.debug(f"🤫 [Play]  {device_key} unverändert {val} ({device_state.name})")

# ─────────────────────────────────────────────────────────────
# Verbindung mit Retry
# ─────────────────────────────────────────────────────────────

async def connect_with_retry(atv_conf, loop, max_retries=5):
    last_error = None
    for i in range(max_retries):
        try:
            return await connect(atv_conf, loop=loop)
        except Exception as e:
            last_error = e
            if "No request handler" in str(e) or "ProtocolError" in str(e):
                logging.info(f"⏳ [Connect] Dienst antwortet noch nicht (Retry {i+1}/{max_retries})...")
                await asyncio.sleep(2)
                continue
            logging.error(f"❌ [Connect] Unerwarteter Fehler: {e}")
            break
    logging.error(f"💥 [Connect] Nach {max_retries} Versuchen fehlgeschlagen: {last_error}")
    return None

# ─────────────────────────────────────────────────────────────
# Listener: Power (Companion Protocol)
# ─────────────────────────────────────────────────────────────

class PowerStateMonitor(PowerListener):
    def __init__(self, device_key, mqtt_client):
        self.device_key = device_key
        self.mqtt_client = mqtt_client

    def powerstate_update(self, old_state, new_state):
        process_power_state(self.device_key, new_state, self.mqtt_client, source="Event")

# ─────────────────────────────────────────────────────────────
# Listener: Play (AirPlay Protocol → PushUpdater)
#
# Warum AirPlay und nicht MRP?
#   MRP (Media Remote Protocol) wurde von Apple mit tvOS 15+ deprecated
#   und ist in aktuellen pyatv-Versionen nicht mehr verfügbar.
#   Der FacadePushUpdater wählt Protokolle nach Priorität:
#   MRP > DMAP > Companion > AirPlay > RAOP
#   Da MRP wegfällt, muss AirPlay explizit als Credential eingetragen
#   werden, damit pyatv es als PushUpdater-Quelle nutzt.
# ─────────────────────────────────────────────────────────────

class PlayStateMonitor(PushListener):
    def __init__(self, device_key, mqtt_client):
        self.device_key = device_key
        self.mqtt_client = mqtt_client

    def playstatus_update(self, updater, playstatus):
        process_play_state(
            self.device_key,
            playstatus.device_state,
            self.mqtt_client,
            source="AirPlay-Push"
        )

    def playstatus_error(self, updater, exception):
        logging.warning(f"⚠️ [Play] {self.device_key} PushUpdater Fehler: {exception}")

# ─────────────────────────────────────────────────────────────
# Steuerung (Befehle vom KNX/Gira)
# ─────────────────────────────────────────────────────────────

async def control_atv(device_key, action, mqtt_client):
    dev = DEVICES.get(device_key)
    atv_instance = None
    try:
        logging.info(f"📥 [MQTT] Empfangen: {device_key} → {action}")
        found = await scan(loop=asyncio.get_event_loop(), identifier=dev['id'], timeout=4)
        if not found:
            logging.warning(f"❌ {device_key} für Steuerung nicht gefunden.")
            return

        conf = found[0]
        conf.set_credentials(Protocol.Companion, dev["companion"])

        try:
            atv_instance = await connect(conf, loop=asyncio.get_event_loop())
        except Exception as conn_err:
            if "No request handler" in str(conn_err):
                atv_instance = await connect_with_retry(conf, loop=asyncio.get_event_loop())
            else:
                raise conn_err

        if atv_instance:
            if action in ["1", "2"]:
                await atv_instance.remote_control.home()
                logging.info(f"✅ [Steuerung] {device_key} → AN")
                process_power_state(device_key, PowerState.On, mqtt_client, source="Steuerung-Feedback")
            elif action == "0":
                await atv_instance.power.turn_off()
                logging.info(f"💤 [Steuerung] {device_key} → AUS")
                process_power_state(device_key, PowerState.Off, mqtt_client, source="Steuerung-Feedback")

    except Exception as e:
        logging.error(f"💥 [Steuerung] {device_key}: {e}")
    finally:
        if atv_instance:
            await atv_instance.close()

# ─────────────────────────────────────────────────────────────
# Background Monitor: Power + Play in einem Task
# ─────────────────────────────────────────────────────────────

async def monitor_atv(device_key, mqtt_client):
    """
    Verbindet mit Companion (Power) + AirPlay (Play-State).
    PushUpdater läuft über AirPlay, da MRP nicht mehr verfügbar.
    """
    logging.info(f"🚀 [Monitor] Task für {device_key} gestartet.")
    dev_info = DEVICES[device_key]
    has_airplay = "airplay" in dev_info and not dev_info["airplay"].startswith("AIRPLAY_CREDENTIALS")

    if not has_airplay:
        logging.warning(
            f"⚠️  [Monitor] {device_key}: Kein AirPlay-Credential konfiguriert.\n"
            f"    Play-State wird NICHT überwacht.\n"
            f"    Credentials holen: atvremote --id {dev_info['id']} --protocol airplay pair"
        )

    while True:
        atv_mon = None
        try:
            found = await scan(loop=asyncio.get_event_loop(), identifier=dev_info['id'], timeout=5)

            if not found:
                await asyncio.sleep(30)
                continue

            conf = found[0]
            conf.set_credentials(Protocol.Companion, dev_info["companion"])

            if has_airplay:
                conf.set_credentials(Protocol.AirPlay, dev_info["airplay"])

            atv_mon = await connect_with_retry(conf, loop=asyncio.get_event_loop())

            if not atv_mon:
                await asyncio.sleep(15)
                continue

            logging.info(
                f"✅ [Monitor] {device_key} verbunden. "
                f"Protokolle: Companion (Power) + "
                f"{'AirPlay (Play)' if has_airplay else 'kein Play-Monitor'}"
            )

            # Power-Listener registrieren
            atv_mon.power.listener = PowerStateMonitor(device_key, mqtt_client)

            # Play-Listener registrieren (nur wenn AirPlay-Credentials vorhanden)
            if has_airplay:
                play_monitor = PlayStateMonitor(device_key, mqtt_client)
                atv_mon.push_updater.listener = play_monitor
                atv_mon.push_updater.start()
                logging.info(f"▶️  [Monitor] {device_key} PushUpdater gestartet.")

            # Poll-Loop: Power-State alle 20s prüfen + Verbindung halten
            while True:
                try:
                    state = atv_mon.power.power_state
                    process_power_state(device_key, state, mqtt_client, source="Poll")
                except Exception as poll_err:
                    if "No request handler" in str(poll_err):
                        logging.debug(f"⏳ [Poll] {device_key} schläft noch.")
                    else:
                        raise poll_err

                await asyncio.sleep(20)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.debug(f"🔄 [Monitor] {device_key} Reconnect in 15s... ({e})")
            await asyncio.sleep(15)
        finally:
            if atv_mon:
                try:
                    if has_airplay:
                        atv_mon.push_updater.stop()
                    await atv_mon.close()
                except Exception:
                    pass
                atv_mon = None

# ─────────────────────────────────────────────────────────────
# MQTT Setup
# ─────────────────────────────────────────────────────────────

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("🌐 [MQTT] Broker verbunden.")
        # Power-Topics (Steuerung)
        client.subscribe("home/atv/+/set")
        # Fallback: altes Topic-Schema
        for dev_key in DEVICES:
            client.subscribe(f"home/atv/{dev_key}")
    else:
        logging.error(f"❗ [MQTT] Verbindungsfehler. Code: {rc}")

def on_message(client, userdata, msg):
    if "/state" in msg.topic or "/play_state" in msg.topic:
        return
    try:
        parts = msg.topic.split('/')
        device_key = parts[-1] if parts[-1] != "set" else parts[-2]
        payload = msg.payload.decode()
        if device_key in DEVICES:
            asyncio.run_coroutine_threadsafe(
                control_atv(device_key, payload, client),
                userdata['loop']
            )
    except Exception as e:
        logging.error(f"🚫 [MQTT] Fehler: {e}")

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

async def main():
    loop = asyncio.get_running_loop()
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata={'loop': loop}
    )
    client.username_pw_set(MQTT_USER, MQTT_PW)
    client.on_connect = on_connect
    client.on_message = on_message

    logging.info("⚙️  [System] Starte Bridge...")
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            break
        except Exception:
            logging.warning("❗ [MQTT] Broker nicht erreichbar, warte 5s...")
            await asyncio.sleep(5)

    background_tasks = []
    for dev_key in DEVICES:
        task = asyncio.create_task(monitor_atv(dev_key, client))
        background_tasks.append(task)

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        logging.info("🧹 [System] Beende Hintergrund-Tasks...")
        for task in background_tasks:
            task.cancel()
        await asyncio.gather(*background_tasks, return_exceptions=True)
        client.loop_stop()
        logging.info("🔌 [System] MQTT-Verbindung getrennt.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 [System] Durch Benutzer beendet.")
