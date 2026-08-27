# §08 Querschnittliche Konzepte — ATV-KNX Bridge

## Logging

Alle Aktionen werden konsistent mit Emoji-Präfixen geloggt, die den Kontext sofort
erkennbar machen:

| Präfix | Bedeutung |
|--------|-----------|
| `📤 [MQTT]` | Ausgehende MQTT-Nachricht |
| `📥 [MQTT]` | Eingehende MQTT-Nachricht |
| `🔄 [SBC]` | Statuswechsel erkannt |
| `🤫 [SBC]` | Status unverändert, kein Publish |
| `⏳ [Connect]` | Verbindungsversuch (Retry) |
| `✅ [Monitor/Steuerung]` | Erfolgreiche Verbindung / Befehl |
| `💤 [Steuerung]` | AUS-Befehl ausgeführt |
| `❌` | Fehler / Gerät nicht gefunden |
| `💥` | Kritischer Fehler |
| `🚀 [Monitor]` | Task gestartet |
| `🧹 [System]` | Cleanup beim Beenden |

**Log-Ziele:** stdout (für Betriebsüberwachung) + `/tmp/atvbridge.log` (persistente Datei).
Log-Level: `INFO` für den Normalbetrieb; `DEBUG` für interne Polling-Details.

---

## Statusdeduplizierung

Das `last_states`-Dictionary verhindert, dass der MQTT-Broker mit redundanten
`retain`-Nachrichten geflutet wird.

```python
last_states = {}  # {"wohnzimmer": "1", "schlafzimmer": "0"}
```

**Regel:** `process_power_state()` publiziert nur dann, wenn sich der normalisierte
Wert (`"0"` oder `"1"`) gegenüber dem gespeicherten Wert geändert hat.

**Dreiquellen-Prinzip:** Alle drei Informationsquellen (Event, Poll, optimistisches
Feedback) laufen durch denselben `process_power_state()`-Eingang. Die Quelle wird
im Log vermerkt (`source`-Parameter), aber der Deduplizierungslogik ist sie egal.

---

## Optimistisches Feedback

**Problem:** Nach einem AN-Befehl schläft das Apple TV noch mehrere Sekunden. Der
KNX-Bus würde sonst keine sofortige Rückmeldung erhalten, was Szenen und Visualisierungen
blockiert.

**Lösung:** Die Bridge publiziert den erwarteten neuen State **sofort** nach dem Senden
des Befehls (vor der ATV-Bestätigung):

```python
# Nach remote_control.home()
process_power_state(device_key, PowerState.On, mqtt_client, source="Steuerung-Feedback")
```

**Konsequenz:** Im seltenen Fall, dass ein Befehl die Hardware-Ebene nicht erreicht
(z. B. Netzwerkproblem nach dem optimistischen Publish), ist der KNX-State kurzzeitig
inkonsistent. Der Monitoring-Loop korrigiert dies spätestens nach 20 Sekunden.

---

## Fehlerbehandlung

### Companion-"No request handler"-Fehler

Bekannter PyATV-Bug: Beim Verbinden mit einem Apple TV, das gerade aus dem Tiefschlaf
erwacht, antwortet der Companion-Dienst noch nicht.

**Behandlung:**
- In `connect_with_retry()`: bis zu 5 Retries mit je 2 s Pause (nur bei diesem Fehlertyp)
- Im Polling-Loop von `monitor_atv()`: still ignoriert, nächster Poll in 20 s
- In `control_atv()`: fallback auf `connect_with_retry()`

Andere Fehler (z. B. falsche Credentials) werden nicht wiederholt und sofort geloggt.

### MQTT-Verbindungsverlust

**Startup:** Loop mit 5 s Pause bis der Broker erreichbar ist.
**Betrieb:** Kein automatischer Reconnect bei Verbindungsabbruch während des Betriebs
(→ §11 Risiken).

### Gerät nicht erreichbar

`scan()` liefert eine leere Liste → `control_atv()` bricht mit Warning ab;
`monitor_atv()` wartet 30 s und versucht erneut.

---

## Nebenläufigkeit (Thread-Safety)

Die Bridge verwendet ein hybrides Modell:

- **asyncio-Event-Loop** (Single Thread): alle ATV-Operationen, Monitoring, State-Updates
- **paho-mqtt interner Thread**: MQTT-Callback-Verarbeitung

Die einzige Thread-Grenze ist `asyncio.run_coroutine_threadsafe()` in `on_message()`.
Das `last_states`-Dictionary wird ausschließlich aus dem asyncio-Thread geschrieben
(alle schreibenden Aufrufe kommen über `process_power_state()`, die via
`run_coroutine_threadsafe` in den Event-Loop eingebettet ist).

---

## Konfigurationsmanagement

Alle Konfigurationswerte sind derzeit direkt im Quellcode definiert:

| Wert | Variable | Typ |
|------|----------|-----|
| MQTT-Broker-Adresse | `MQTT_BROKER` | hardcodiert: `"localhost"` |
| MQTT-Port | `MQTT_PORT` | hardcodiert: `1883` |
| MQTT-Credentials | `MQTT_USER`, `MQTT_PW` | hardcodiert (kritisch) |
| Gerätekonfiguration | `DEVICES` dict | hardcodiert |
| Retry-Anzahl | `max_retries=5` | Default-Parameter |
| Poll-Intervall | `asyncio.sleep(20)` | literal |
| Reconnect-Pausen | `sleep(30)` / `sleep(15)` | literal |

**Handlungsbedarf:** Überführung in `.env`-Datei oder `config.yaml` (→ §11).
