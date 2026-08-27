# §12 Glossar — ATV-KNX Bridge

| Begriff | Erklärung |
|---------|-----------|
| **asyncio** | Python-Standardbibliothek für asynchrone, kooperative Nebenläufigkeit in einem einzigen Thread via `async/await` und Event-Loop |
| **ATV** | Apple TV — Streaming-Mediaplayer von Apple |
| **Bonjour** | Apple-Implementierung von mDNS (Multicast DNS); ermöglicht automatische Geräteerkennung im lokalen Netz ohne feste IP-Adressen |
| **Companion Protocol** | Apple-proprietäres Protokoll für die Steuerung von Apple TVs durch autorisierte Clients. Baut auf Bonjour-Erkennung und TCP auf. Unterstützt Power-Events, Remote-Control und Status-Abfragen |
| **Deep Sleep** | Tiefschlaf-Zustand eines Apple TVs. Im Deep Sleep antwortet der Companion-Dienst auf dem ATV nicht sofort — daher ist `connect_with_retry()` notwendig |
| **Gira HomeServer** | Heimautomatisierungsserver von Gira. Verbindet KNX-Bus mit IP-basierten Protokollen (MQTT, HTTP). Erlaubt Logikbausteine für Automatisierungen |
| **KNX** | Konnex — offener Standard für Heimautomatisierungsbusse. Typisch: twisted-pair Verkabelung (KNX TP) mit Gruppenadressen für Steuerung und Rückmeldung |
| **KNX-Gruppenadresse** | Logische Adresse im KNX-Bus (z. B. `1/2/3`). Mehrere Geräte können dieselbe Adresse abonnieren. Wird für Schalten, Dimmen, Statusrückmeldung verwendet |
| **KNX-Szene** | Vordefinierter Zustand mehrerer KNX-Geräte gleichzeitig. Z. B. "Heimkino AN" schaltet Licht, Jalousien und Apple TV in einem Telegramm |
| **Logikbaustein** | Programmierbare Logikkomponente im Gira HomeServer. Hier: liest KNX-Gruppenadresse und sendet MQTT-Befehl; bzw. liest MQTT-State und schreibt KNX-Gruppenadresse |
| **last_states** | In-Memory-Dictionary in der Bridge (`dict[str, str]`). Speichert den zuletzt an MQTT publizierten State pro Gerät; verhindert redundante Publishes |
| **MQTT** | Message Queuing Telemetry Transport — leichtgewichtiges Publish/Subscribe-Protokoll für IoT. Broker nimmt Nachrichten entgegen und verteilt sie an Subscriber |
| **MQTT Broker** | Zentraler Nachrichtenserver (hier: Mosquitto auf localhost:1883). Vermittelt Nachrichten zwischen Publisher (Bridge, Gira HS) und Subscriber |
| **mDNS** | Multicast DNS — Protokoll zur Namensauflösung ohne zentralen DNS-Server im lokalen Netz. Wird von PyATV für `scan()` verwendet |
| **Mosquitto** | Verbreitete Open-Source-MQTT-Broker-Implementierung |
| **Optimistisches Feedback** | Designentscheidung: Bridge publiziert den erwarteten neuen State sofort nach dem Senden eines Befehls, ohne auf Bestätigung durch das ATV zu warten |
| **paho-mqtt** | Python-Client-Bibliothek für MQTT (Eclipse Paho Projekt). Verwaltet Verbindung, Subscription und Publish; läuft intern in eigenem Thread |
| **PowerListener** | Interface der PyATV-Bibliothek. Implementiert `powerstate_update(old_state, new_state)`. Wird als Callback bei Statusänderungen des ATVs aufgerufen |
| **PowerState** | Enum der PyATV-Bibliothek: `On`, `Off`, `Dimming`, `Suspended` u. a. Bridge normalisiert auf `"1"` (On, Dimming) und `"0"` (alle anderen) |
| **PyATV** | Open-Source-Python-Bibliothek für die Steuerung von Apple TVs. Unterstützt Companion, MRP, AirPlay und RAOP-Protokolle |
| **Retained Message** | MQTT-Nachricht mit `retain=True`. Der Broker speichert die letzte Nachricht pro Topic und liefert sie sofort an neue Subscriber |
| **run_coroutine_threadsafe** | Python asyncio-Funktion: übergibt eine Coroutine aus einem anderen Thread sicher an den laufenden Event-Loop |
| **Schlafzimmer** | Deutsch für "Bedroom" — Bezeichnung für den Standort des zweiten Apple TVs |
| **Wohnzimmer** | Deutsch für "Living Room" — Bezeichnung für den Standort des ersten Apple TVs |
