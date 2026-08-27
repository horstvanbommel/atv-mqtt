# §01 Einführung und Ziele — ATV-KNX Bridge

## Systemzweck

`atv_mqtt_bridge.py` ist ein Python-Daemon auf einem Mac Mini, der als bidirektionale
Schnittstelle zwischen dem **KNX-Heimautomatisierungsbus** (über den Gira HomeServer)
und den **Apple TVs** im Haus dient. MQTT wird als nachrichtenbasierter Broker eingesetzt.

**Kernfunktion:** KNX-Szenen können Apple TVs ein- und ausschalten; Statuswechsel der
Apple TVs (z. B. Einschalten per Fernbedienung) werden zurück an den KNX-Bus gemeldet.

---

## Wesentliche Aufgaben

| # | Aufgabe | Richtung |
|---|---------|----------|
| 1 | KNX-Szene schaltet Apple TV **ein** | KNX → Gira HS → MQTT → Bridge → Apple TV |
| 2 | KNX-Szene schaltet Apple TV **aus** | KNX → Gira HS → MQTT → Bridge → Apple TV |
| 3 | Apple TV-Statuswechsel wird an KNX zurückgemeldet | Apple TV → Bridge → MQTT → Gira HS → KNX |
| 4 | Kontinuierliches Monitoring beider Apple TVs | Bridge → Apple TV (Polling + Events) |
| 5 | Selbstheilung nach Verbindungsunterbrechungen | Bridge intern (Reconnect-Logik) |

---

## Qualitätsziele

| Priorität | Ziel | Messgröße |
|-----------|------|-----------|
| 1 | **Zuverlässigkeit** — Bridge erholt sich automatisch ohne manuellen Eingriff | Reconnect nach Verbindungsverlust in ≤ 30 s |
| 2 | **Aktualität** — Statusänderungen werden zeitnah an KNX gemeldet | Maximale Verzögerung ≤ 20 s (Poll-Intervall) |
| 3 | **Fehlertoleranz** — Apple TV-Tiefschlaf wird korrekt behandelt | Bis zu 5 Verbindungsversuche bei Deep Sleep |
| 4 | **Betriebstransparenz** — Alle Aktionen werden nachvollziehbar geloggt | Log nach stdout + `/tmp/atvbridge.log` |

---

## Stakeholder

| Stakeholder | Erwartung |
|-------------|-----------|
| Mike Fabian (Eigentümer, Entwickler) | Nahtlose KNX-Integration; Apple TVs verhalten sich wie andere KNX-Geräte |
| Gira HomeServer (techn. System) | Empfängt MQTT-States; sendet MQTT-Steuerbefehle |
| KNX-Szenenlogik | AN/AUS-Befehle werden zuverlässig ausgeführt; Status wird korrekt zurückgemeldet |
