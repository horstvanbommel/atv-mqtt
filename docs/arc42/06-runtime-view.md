# §06 Laufzeitsicht — ATV-KNX Bridge

## Szenario 1: Apple TV einschalten (KNX → ATV)

Auslöser: KNX-Szene (z. B. "Heimkino AN") setzt Gruppenadresse → Gira HomeServer
publiziert MQTT-Befehl.

```mermaid
sequenceDiagram
    participant K as KNX Bus
    participant G as Gira HomeServer
    participant M as MQTT Broker
    participant B as ATV Bridge
    participant A as Apple TV

    K->>G: KNX-Szene auslösen
    G->>M: Publish home/atv/wohnzimmer = "1"
    M->>B: on_message() [MQTT-Thread]
    B->>B: asyncio.run_coroutine_threadsafe(control_atv)
    B->>A: scan(identifier, timeout=4s)
    A-->>B: Gerät gefunden
    B->>A: connect() — bei Fehler connect_with_retry()
    Note over B,A: ATV schläft tief: bis zu 5 Retries à 2 s
    A-->>B: Verbindung hergestellt
    B->>A: remote_control.home()
    B->>B: process_power_state(PowerState.On, "Steuerung-Feedback")
    B->>M: Publish home/atv/wohnzimmer/state = "1" [retain]
    M->>G: State-Update empfangen
    G->>K: KNX-Gruppenadresse ATV-Status = AN
    Note over A: Apple TV wacht auf, zeigt Home Screen
    A-->>B: PowerState.On Event via StateMonitor
    B->>B: process_power_state() — last_states["wohnzimmer"] == "1", kein Publish
```

**Schlüsselpunkt — Optimistisches Feedback:** Die Bridge publiziert den neuen State
(`"1"`) sofort nach dem Senden des Befehls, ohne auf die Bestätigung des Apple TVs zu
warten. Das ist notwendig, weil das ATV nach dem Deep Sleep mehrere Sekunden braucht,
bevor es PyATV-Events liefert. Der KNX-Bus bekommt so sofort Rückmeldung.

---

## Szenario 2: Apple TV ausschalten (KNX → ATV)

```mermaid
sequenceDiagram
    participant K as KNX Bus
    participant G as Gira HomeServer
    participant M as MQTT Broker
    participant B as ATV Bridge
    participant A as Apple TV

    K->>G: KNX-Szene (z. B. Licht AUS)
    G->>M: Publish home/atv/wohnzimmer = "0"
    M->>B: on_message()
    B->>A: scan() + connect()
    A-->>B: Verbindung
    B->>A: power.turn_off()
    B->>B: process_power_state(PowerState.Off, "Steuerung-Feedback")
    B->>M: Publish home/atv/wohnzimmer/state = "0" [retain]
    M->>G: State-Update
    G->>K: KNX-Gruppenadresse ATV-Status = AUS
    Note over A: ATV geht in Standby
    A-->>B: PowerState.Off Event via StateMonitor
    B->>B: last_states["wohnzimmer"] == "0", kein Publish
```

---

## Szenario 3: Statusrückmeldung — ATV selbst eingeschaltet

Jemand schaltet das Apple TV per physischer Fernbedienung oder Apple Remote ein,
ohne eine KNX-Szene zu aktivieren. Die Bridge erkennt dies proaktiv.

```mermaid
sequenceDiagram
    participant A as Apple TV
    participant B as monitor_atv()
    participant M as MQTT Broker
    participant G as Gira HomeServer
    participant K as KNX Bus

    Note over B: Monitoring-Loop aktiv, Verbindung besteht
    A->>B: PowerState.On Event (StateMonitor.powerstate_update)
    B->>B: process_power_state("wohnzimmer", On, "Event")
    Note over B: last_states war "0" — Änderung erkannt
    B->>M: Publish home/atv/wohnzimmer/state = "1" [retain]
    M->>G: State-Update
    G->>K: KNX-Gruppenadresse ATV-Status = AN
    Note over K: KNX-Aktor / Visualisierung aktualisiert
```

Falls der Event ausbleibt (Companion-Bug), greift der Polling-Mechanismus
spätestens nach **20 Sekunden**.

---

## Szenario 4: Monitoring-Loop (Dauerbetrieb)

Läuft permanent als asyncio-Task parallel für `wohnzimmer` und `schlafzimmer`.

```mermaid
sequenceDiagram
    participant B as monitor_atv()
    participant A as Apple TV
    participant M as MQTT Broker

    loop Endlosschleife
        B->>A: scan(identifier, timeout=5s)
        alt Gerät erreichbar
            B->>A: connect_with_retry()
            A-->>B: PyATV-Verbindung
            B->>A: power.listener = StateMonitor(device_key)
            loop Polling alle 20 s
                B->>A: power.power_state
                alt Status geändert
                    B->>M: Publish /state [retain]
                end
                alt "No request handler" Fehler
                    Note over B: Bekannter Companion-Bug, ignorieren
                end
                alt Verbindungsfehler (echter Fehler)
                    B->>B: Exception → Reconnect-Schleife
                end
            end
        else Gerät nicht gefunden (Deep Sleep oder offline)
            B->>B: sleep(30 s)
        end
        alt Exception / Verbindungsverlust
            B->>B: atv_mon.close(), sleep(15 s)
        end
    end
```

---

## Szenario 5: Startup und Shutdown

```mermaid
sequenceDiagram
    participant P as Prozess
    participant M as MQTT Broker
    participant A1 as ATV Wohnzimmer
    participant A2 as ATV Schlafzimmer

    P->>M: connect() — Loop mit 5 s Retry bis Broker erreichbar
    M-->>P: Verbindung hergestellt
    M-->>P: on_connect() — subscribe("home/atv/#")
    P->>A1: asyncio.create_task(monitor_atv("wohnzimmer"))
    P->>A2: asyncio.create_task(monitor_atv("schlafzimmer"))
    Note over P: Hauptschleife: asyncio.sleep(1) — wartet auf Abbruch

    alt KeyboardInterrupt / SIGTERM
        P->>P: asyncio.CancelledError
        P->>A1: task.cancel()
        P->>A2: task.cancel()
        P->>P: asyncio.gather(*tasks, return_exceptions=True)
        P->>M: client.loop_stop()
    end
```

---

## Nebenläufigkeitsmodell

Die Bridge verwendet **Python asyncio** mit einem einzigen Event-Loop-Thread.

| Komponente | Thread / Kontext | Kommunikationsweg |
|------------|-----------------|------------------|
| `monitor_atv()` (×2) | asyncio-Task | `await` |
| `control_atv()` | asyncio-Coroutine | `await` |
| `on_message()` (paho-mqtt) | MQTT-eigener Thread | `run_coroutine_threadsafe()` |
| `on_connect()` | MQTT-eigener Thread | direkt (kein shared state) |

`asyncio.run_coroutine_threadsafe()` ist der einzige Thread-Übergang. Das `loop`-Objekt
wird beim Start in `mqtt.Client.userdata` gespeichert und ist von `on_message` aus
zugreifbar.
