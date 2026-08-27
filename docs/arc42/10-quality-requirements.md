# §10 Qualitätsanforderungen — ATV-KNX Bridge

## Qualitätsszenarien

### QS-01: Statusaktualisierung bei direktem ATV-Einschalten

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | Benutzer schaltet Apple TV mit physischer Fernbedienung ein |
| **Reaktion** | Bridge erkennt den State-Wechsel und publiziert an MQTT |
| **Messbar** | Verzögerung ≤ **20 Sekunden** (Poll-Intervall als Worst Case) |
| **Aktuell** | Erfüllt — Polling alle 20 s + Event-Listener als Primärkanal |

---

### QS-02: Befehlsausführung mit sofortiger Rückmeldung

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | KNX-Szene sendet AN-Befehl via MQTT |
| **Reaktion** | KNX-Bus erhält Statusrückmeldung (AN) ohne wahrnehmbare Verzögerung |
| **Messbar** | Rückmeldung innerhalb von **< 2 Sekunden** (optimistisches Feedback) |
| **Aktuell** | Erfüllt — optimistisches Feedback wird sofort nach `home()`-Aufruf publiziert |

---

### QS-03: Selbstheilung nach ATV Deep Sleep

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | Apple TV im Tiefschlaf; Bridge versucht Verbindung für Steuerbefehl |
| **Reaktion** | Bridge weckt das ATV durch wiederholte Verbindungsversuche |
| **Messbar** | Verbindungsaufbau in ≤ **10 Sekunden** (5 Retries × 2 s) |
| **Aktuell** | Erfüllt — `connect_with_retry()` mit max_retries=5, sleep=2s |

---

### QS-04: Wiederverbindung nach Monitoring-Fehler

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | Verbindung im Monitor-Loop bricht ab (ATV nicht erreichbar) |
| **Reaktion** | Bridge versucht automatisch erneut zu verbinden |
| **Messbar** | Neuer Verbindungsversuch nach ≤ **30 Sekunden** (15 s bei Fehler, 30 s wenn nicht gefunden) |
| **Aktuell** | Erfüllt — Reconnect-Logik in `monitor_atv()` |

---

### QS-05: Startup-Resilienz bei MQTT-Broker-Ausfall

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | Bridge startet, MQTT-Broker noch nicht verfügbar |
| **Reaktion** | Bridge wartet und verbindet sich, sobald der Broker erreichbar ist |
| **Messbar** | Retry-Intervall **5 Sekunden**; kein Prozessabsturz |
| **Aktuell** | Erfüllt — Startup-Loop in `main()` |

---

### QS-06: Zuverlässigkeit bei latentem Companion-Fehler

| Aspekt | Beschreibung |
|--------|-------------|
| **Stimulus** | PyATV wirft "No request handler"-Fehler beim Polling |
| **Reaktion** | Bridge ignoriert den Fehler still und pollt beim nächsten Intervall erneut |
| **Messbar** | Kein Log-Spam; keine falsche MQTT-Publikation |
| **Aktuell** | Erfüllt — spezifischer Fehler-Check im Poll-Loop |

---

## Bekannte Qualitätslücken

| ID | Qualitätsmerkmal | Lücke | Schwere |
|----|-----------------|-------|---------|
| QL-01 | Sicherheit | MQTT-Credentials im Quellcode | kritisch |
| QL-02 | Betriebsstabilität | Kein MQTT-Reconnect bei Verbindungsverlust im Betrieb | hoch |
| QL-03 | Betreibbarkeit | Kein Autostart als launchd-Daemon | mittel |
| QL-04 | Betreibbarkeit | Keine Log-Rotation (`/tmp/atvbridge.log`) | mittel |
| QL-05 | Testbarkeit | Keine automatisierten Tests | mittel |
| QL-06 | Nachvollziehbarkeit | OFFLINE (2) und FEHLER (3) States definiert aber nie publiziert | niedrig |
