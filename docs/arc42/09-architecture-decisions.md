# §09 Architekturentscheidungen — ATV-KNX Bridge

## ADR-001: MQTT als Integrationsbus

**Kontext:** Die Bridge muss mit dem Gira HomeServer kommunizieren. Der HomeServer
unterstützt verschiedene Protokolle für externe Integration.

**Entscheidung:** MQTT (Message Queuing Telemetry Transport) als einziger
Kommunikationskanal zwischen Gira HomeServer und Bridge.

**Begründung:**
- Der Gira HomeServer hat einen eingebauten MQTT-Client und Logikbausteine
  für MQTT-Pub/Sub
- MQTT ist leichtgewichtig, latenzarm und für Heimautomatisierung etabliert
- Retained Messages lösen das State-Recovery-Problem beim Neustart der Bridge
- Entkopplung: Bridge und HomeServer kennen sich nicht direkt

**Konsequenzen:** MQTT-Broker (Mosquitto) muss auf dem Mac Mini laufen und verfügbar
sein. Ein Broker-Ausfall legt die gesamte Integration lahm.

---

## ADR-002: PyATV Companion Protocol

**Kontext:** Apple TVs bieten verschiedene Protokolle für externe Steuerung
(MRP, AirPlay, Companion, RAOP). PyATV unterstützt alle davon.

**Entscheidung:** Ausschließlich **Companion Protocol** für Steuerung und
Status-Monitoring.

**Begründung:**
- Companion ist das einzige Protokoll, das **Power-State-Events** liefert
  (kein Polling nötig für Zustandsänderungen)
- Companion ermöglicht `turn_off()` und `remote_control.home()`
- MRP würde zusätzliches Pairing erfordern; AirPlay ist auf Medienwiedergabe beschränkt

**Konsequenzen:** Companion-Pairing muss einmalig durchgeführt werden; die langen
Pairing-Tokens werden im Code gespeichert. Der bekannte "No request handler"-Bug
bei Deep Sleep erfordert `connect_with_retry()`.

---

## ADR-003: asyncio als Nebenläufigkeitsmodell

**Kontext:** Die Bridge muss zwei Apple TVs gleichzeitig überwachen und gleichzeitig
Steuerbefehle entgegennehmen.

**Entscheidung:** Python **asyncio** mit einem einzigen Event-Loop; zwei parallele
`monitor_atv()`-Tasks; MQTT-Callbacks werden via `run_coroutine_threadsafe()` in
den Event-Loop eingebracht.

**Begründung:**
- PyATV ist asyncio-nativ; alle PyATV-Operationen sind `async/await`
- paho-mqtt hat eigene Threads → `run_coroutine_threadsafe()` ist die saubere Brücke
- Threading (statt asyncio) würde shared-state-Probleme mit `last_states` erzeugen
- asyncio ist single-threaded → kein Mutex für `last_states` nötig

**Konsequenzen:** Jede blockierende Operation im Event-Loop blockiert alle Tasks.
PyATV-`scan()` mit Timeout ist die kritische Stelle; ist aber als `async` implementiert.

---

## ADR-004: Optimistisches Feedback

**Kontext:** Apple TVs brauchen nach dem Aufwachen aus dem Deep Sleep mehrere Sekunden,
bevor sie ihren Power-State via Companion melden. KNX-Szenen warten auf Rückmeldung.

**Entscheidung:** Nach dem Senden eines Steuerbefehls wird der **erwartete** Zustand
**sofort** (optimistisch) an MQTT publiziert, ohne auf ATV-Bestätigung zu warten.

**Begründung:**
- Ohne optimistisches Feedback: Gira-Logik wartet 10–30 s auf State-Rückmeldung
- Mit optimistisches Feedback: KNX-Szene bekommt sofort Quittung; Visualisierung
  aktualisiert sich ohne spürbare Verzögerung
- Fehlerfälle (Befehl nicht ausgeführt) werden durch den Monitoring-Loop
  spätestens in 20 s korrigiert

**Konsequenzen:** Kurzzeitige State-Inkonsistenz möglich, wenn ein Befehl hardwareseitig
scheitert, nachdem das optimistische Feedback bereits gesendet wurde. Akzeptiertes Risiko.

---

## ADR-005: Hybrides Monitoring (Events + Polling)

**Kontext:** PyATV's `StateMonitor` liefert Events bei Statuswechseln. Events können
jedoch ausbleiben (bekannter Companion-Bug, Netzwerkprobleme).

**Entscheidung:** **Doppelte Überwachungsstrategie** — Events als primärer Kanal,
Polling alle 20 Sekunden als Fallback.

```python
# Event-Listener
atv_mon.power.listener = StateMonitor(device_key, mqtt_client)

# Fallback-Poll
while True:
    state = atv_mon.power.power_state
    process_power_state(...)
    await asyncio.sleep(20)
```

**Begründung:**
- Nur Events: anfällig für verpasste Statuswechsel
- Nur Polling: höhere Last auf ATV und Netzwerk; höhere Latenz
- Beide kombiniert: zuverlässig mit akzeptabler Latenz

**Konsequenzen:** Maximal 20 s Verzögerung bei verpasstem Event. Polling erzeugt
konstante aber geringe Netzwerklast.

---

## ADR-006: MQTT-Retained-Messages für State-Recovery

**Kontext:** Nach einem Neustart der Bridge ist `last_states` leer. Der MQTT-Broker
weiß den letzten State.

**Entscheidung:** Alle State-Publishes erfolgen mit `retain=True`.

**Begründung:**
- Beim Bridge-Neustart liefert der Broker sofort die letzten bekannten States an
  den Gira HomeServer
- Der Gira HomeServer bekommt beim (Re-)Connect automatisch den aktuellen State
- Keine zusätzliche Persistenzlogik in der Bridge nötig

**Konsequenzen:** Der Broker speichert pro Topic dauerhaft eine Nachricht. Bei einem
kompletten System-Neustart (Broker + Bridge + ATV) muss der ATV-State neu etabliert
werden (erster Poll nach Reconnect).
