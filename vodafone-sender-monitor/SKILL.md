# Vodafone Sender Monitor Skill

Überwacht Vodafone Kabel-Senderlisten per Enigma2-Export. Scannt wöchentlich nach neuen Sendern und benachrichtigt bei Änderungen.

## Features

- 📡 **Enigma2-Export**: Nutzt strukturierte Senderliste (kein HTML-Parsing)
- 🔔 **Automatische Alerts**: Benachrichtigung bei neuen Sendern
- 📊 **SQLite-Datenbank**: Speichert alle Sender mit Metadaten
- 🔄 **Wöchentlicher Scan**: Jeden Samstag um 20:00 Uhr

## Schnellstart

### 1. Initialisierung
```bash
python3 skills/vodafone-sender-monitor/scripts/vodafone_monitor.py --init
```

### 2. Manuelles Scannen
```bash
python3 skills/vodafone-sender-monitor/scripts/vodafone_monitor.py --scan
```

### 3. Liste aller Sender
```bash
python3 skills/vodafone-sender-monitor/scripts/vodafone_monitor.py --list
```

## Automatischer Cron-Job

```bash
# Wöchentlich (Samstags 20:00 Uhr)
0 20 * * 6 python3 skills/vodafone-sender-monitor/scripts/vodafone_monitor.py --cron
```

Bei neuen Sendern: Exit-Code 0  
Keine neuen Sender: Exit-Code 1 (für Cron-Integration)

## Datenbank

**Pfad:** `~/.openclaw/workspace/data/vodafone_senders.db`

**Tabellen:**
- `senders`: Alle bekannten Sender
- `scan_history`: Scan-Verlauf

## Konfiguration

Das Skill arbeitet mit dem Vodafone Helpdesk für Regensburg (Netz 380).  
Andere Regionen können durch Änderung der URL im Script unterstützt werden.

---
*Skill erstellt für Eure Lordschaft* 🎩
