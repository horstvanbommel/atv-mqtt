# §11 Risiken und technische Schulden — ATV-KNX Bridge

## Risiken

### R-01: Hardcodierte Credentials im Quellcode 🔴 KRITISCH

**Beschreibung:** MQTT-Benutzername und Passwort sowie die Companion-Pairing-Tokens
beider Apple TVs sind direkt im Python-Quellcode (und damit in der Versionsverwaltung)
gespeichert.

```python
# Zeilen 12-13 — atv_mqtt_bridge.py
MQTT_USER = "mqtt_user"
MQTT_PW = "4Uu9uGDd"

# Zeilen 16-23 — Companion-Tokens (ebenfalls sensitiv)
DEVICES = {
    "wohnzimmer": {"id": "...", "companion": "1f8d7c..."},
    ...
}
```

**Auswirkung:** Credentials sind für jeden sichtbar, der Zugriff auf das Repository hat.
Widerspricht direkt der Projektsicherheitsregel in `.claude/rules/security.md`.

**Empfehlung:**
1. MQTT-Credentials in `.env`-Datei (gitignored) auslagern, `python-dotenv` verwenden
2. Companion-Tokens in separate, gitignorierte Konfigurationsdatei
3. MQTT-Passwort rotieren

---

### R-02: Kein MQTT-Reconnect bei Verbindungsverlust im Betrieb 🟠 HOCH

**Beschreibung:** Die Bridge verbindet sich beim Start in einer Retry-Schleife mit dem
MQTT-Broker. Bricht die Verbindung **während des Betriebs** ab (Broker-Neustart, kurzer
Netzwerkfehler), gibt es keinen automatischen Reconnect-Mechanismus.

```python
# main() — nur Startup-Retry, kein Runtime-Reconnect
while True:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        break  # bricht nach dem ersten Erfolg aus
    except:
        await asyncio.sleep(5)
```

**Auswirkung:** Nach einem MQTT-Broker-Neustart sendet die Bridge keine States mehr
und empfängt keine Befehle. Manuelle Intervention (Bridge neu starten) erforderlich.

**Empfehlung:** paho-mqtt `reconnect_delay_set()` + `on_disconnect`-Callback mit
automatischem Reconnect konfigurieren.

---

### R-03: Kein Service-Management / Autostart 🟡 MITTEL

**Beschreibung:** Die Bridge wird manuell gestartet. Nach einem Mac Mini Neustart
(Updates, Stromausfall) läuft sie nicht.

**Auswirkung:** Nach jedem Systemneustart muss die Bridge manuell gestartet werden.
KNX-Apple TV-Integration ist bis dahin außer Betrieb.

**Empfehlung:** launchd-Daemon-Konfiguration (Beispiel in §07).

---

### R-04: Log-Rotation fehlt 🟡 MITTEL

**Beschreibung:** Logs werden in `/tmp/atvbridge.log` geschrieben ohne Größenlimit
oder Rotation.

**Auswirkung:** Auf einem dauerhaft laufenden System wächst die Datei unbegrenzt.
`/tmp` kann unter macOS bei Systemneustart bereinigt werden — dann sind Logs verloren.

**Empfehlung:** `logging.handlers.RotatingFileHandler` mit sinnvollem Limit verwenden;
Logpfad aus `/tmp` in ein persistentes Verzeichnis verlegen.

---

### R-05: Python-Abhängigkeiten nicht deklariert 🟡 MITTEL

**Beschreibung:** Es gibt weder eine `requirements.txt` noch eine `pyproject.toml`.
Benötigte Pakete (`pyatv`, `paho-mqtt`) sind nicht dokumentiert.

**Auswirkung:** Ein neues Setup oder ein Update erfordert manuelles Ermitteln der
Abhängigkeiten. Versionsinkompatibilitäten können unbemerkt entstehen.

**Empfehlung:**
```bash
pip freeze > requirements.txt  # Mindestmaßnahme
# oder: pyproject.toml mit pinned versions
```

---

### R-06: OFFLINE/FEHLER-States definiert aber nie gesendet 🔵 NIEDRIG

**Beschreibung:** Die `send_status()`-Funktion kennt die Codes `2=OFFLINE` und
`3=FEHLER`, aber die Logik in `process_power_state()` normalisiert alle States auf
`"0"` oder `"1"`. OFFLINE und FEHLER werden nie publiziert.

**Auswirkung:** Der Gira HomeServer kann nicht unterscheiden, ob ein ATV `AUS` oder
tatsächlich `OFFLINE` (nicht erreichbar) ist.

**Empfehlung:** OFFLINE-State publizieren, wenn `scan()` dauerhaft kein Gerät findet
(z. B. nach 3 fehlgeschlagenen Scan-Zyklen).

---

### R-07: Companion-Pairing-Tokens im Code 🔴 KRITISCH

**Beschreibung:** Die Companion-Pairing-Tokens (lange Hex-Strings in `DEVICES`) sind
sensitiv — sie ermöglichen unbeschränkte Steuerung der Apple TVs.

**Auswirkung:** Wer die Tokens hat, kann die Apple TVs programmatisch steuern.

**Empfehlung:** Zusammen mit R-01 in gitignorierte Konfigurationsdatei auslagern.

---

## Technische Schulden

| ID | Schuld | Aufwand | Priorität |
|----|--------|---------|-----------|
| TD-01 | Keine Tests | hoch | mittel — PyATV lässt sich mocken |
| TD-02 | Konfiguration hartcodiert | mittel | hoch — Voraussetzung für sichere Credentials |
| TD-03 | Kein MQTT-Reconnect | niedrig | hoch — einfach lösbar mit paho-Konfiguration |
| TD-04 | README nicht projektspezifisch | niedrig | niedrig — template wurde nie angepasst |
| TD-05 | Keine requirements.txt | sehr niedrig | mittel — schnell nachholbar |
| TD-06 | OFFLINE/FEHLER-States ungenutzt | niedrig | niedrig — nützliche Erweiterung |
| TD-07 | Kein launchd-Setup | niedrig | mittel — nötig für produktiven Betrieb |
