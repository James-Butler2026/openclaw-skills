# Self-Improving Skill

Self-Reflection + kontinuierliches Lernen für OpenClaw Agents.

## Features

- 🧠 **Learn from Corrections** - Aus Fehlern lernen
- 📝 **Tiered Memory** - HOT/WARM/COLD Speicherung
- 📂 **Project & Domain Patterns** - Kontext-spezifisches Wissen
- 🔄 **Automatic Promotion/Demotion** - Dynamische Priorisierung

## Architektur

```
~/self-improving/
├── memory.md          # HOT: ≤100 lines, immer geladen
├── corrections.md     # Letzte 50 Korrekturen
├── projects/          # Project-spezifisches Wissen
├── domains/           # Domain-spezifisch (code, writing)
└── archive/           # COLD: archivierte Patterns
```

## Konzept

### Learning Triggers

**Automatisch loggen bei:**
- "Nein, das ist falsch..."
- "Eigentlich sollte es..."
- "Ich bevorzuge X, nicht Y"
- "Hör auf X zu tun"
- "Für [Projekt], verwende..."

### Tiered Storage

| Tier | Ort | Limit | Verhalten |
|------|-----|-------|-----------|
| HOT | memory.md | ≤100 lines | Immer geladen |
| WARM | projects/, domains/ | ≤200 lines | Bei Bedarf laden |
| COLD | archive/ | Unbegrenzt | Explizit anfragen |

### Promotion Rules

- Pattern 3x verwendet in 7 Tagen → HOT
- Pattern 30 Tage nicht verwendet → WARM
- Pattern 90 Tage nicht verwendet → COLD

## Verwendung

Dieser Skill wird automatisch von OpenClaw genutzt. Keine manuelle Konfiguration nötig.

### Memory Stats

```
📊 Self-Improving Memory

HOT (always loaded):
  memory.md: X entries

WARM (load on demand):
  projects/: X files
  domains/: X files

COLD (archived):
  archive/: X files
```

### User Queries

- "What do you know about X?" → Durchsucht alle Tiers
- "What have you learned?" → Zeigt letzte 10 Korrekturen
- "Show my patterns" → Zeigt memory.md (HOT)
- "Memory stats" → Zeigt Übersicht aller Tiers

---

*Teil der OpenClaw Skills Collection* 🎩
