# Session Statistics Analyzer

Ein eigenständiges Modul zur Analyse aller Sessions aus der `sessions.jsonl` Datei. Bietet umfassende Statistiken über Spielsessions, Maps, Loot-Werte und Effizienz.

## Module

### 🔍 `session_analyzer.py`
Das Kernmodul mit der `SessionAnalyzer` Klasse:
- Lädt und parsed Session-Daten aus `sessions.jsonl`
- Berechnet umfassende Statistiken
- Unterstützt verschiedene Analysemethoden

### 🎨 `session_display.py` 
Erweiterte Anzeige mit Farben und formatierter Ausgabe:
- Farbcodierte Ausgabe basierend auf Performance
- Übersichtliche Kategorisierung der Statistiken
- Tägliche Aufschlüsselung der Aktivitäten

### 🧪 `test_session_analyzer.py`
Test- und Demo-Script:
- Testet alle Kernfunktionen
- Zeigt verschiedene Analyse-Views
- Performance-Vergleiche zwischen Zeiträumen

## Verwendung

### Schnelle Analyse
```bash
# Basis-Analyse mit allen Statistiken
python session_analyzer.py

# Erweiterte Analyse mit Farben und täglicher Aufschlüsselung
python session_display.py

# Vollständige Tests und Demos
python test_session_analyzer.py
```

### Programmierbare Verwendung
```python
from session_analyzer import SessionAnalyzer
from session_display import SessionStatsDisplay

# Analyzer initialisieren
analyzer = SessionAnalyzer("sessions.jsonl")

# Gesamtstatistiken abrufen
stats = analyzer.get_total_statistics()
print(f"Total Value: {stats['total_value']:.2f} exalted")
print(f"Total Maps: {stats['total_maps']}")

# Top Sessions anzeigen
top_sessions = analyzer.get_top_sessions(5, 'value')
for session in top_sessions:
    print(f"{session.start_time}: {session.total_value:.2f} chaos")

# Charakterspezifische Statistiken
char_stats = analyzer.get_character_statistics()
for char, stats in char_stats.items():
    print(f"{char}: {stats['total_value']:.2f} exalted")

# Farbige Anzeige
display = SessionStatsDisplay(analyzer)
display.display_overview()
```

## Berechnete Metriken

### 📊 Gesamtstatistiken
- **Total Sessions**: Anzahl aller abgeschlossenen Sessions
- **Sessions with Maps**: Sessions die mindestens eine Map enthielten
- **Total Runtime**: Gesamte Spielzeit (formatiert als HH:MM:SS)
- **Total Value**: Gesamtwert aller gefundenen Items in Exalted Orbs
- **Total Maps**: Gesamtanzahl absolvierter Maps

### ⚡ Effizienz-Metriken
- **Maps per Hour**: Durchschnittliche Maps pro Stunde
- **Value per Hour**: Durchschnittlicher Exalted-Wert pro Stunde
- **Avg Map Value**: Durchschnittlicher Wert pro Map
- **Avg Map Time**: Durchschnittliche Zeit pro Map

### 📈 Session-Durchschnitte
- **Avg Session Value**: Durchschnittlicher Wert pro Session
- **Avg Session Runtime**: Durchschnittliche Session-Dauer
- **Avg Maps per Session**: Durchschnittliche Maps pro Session

### 🏆 Rekord-Sessions
- **Best Session by Value**: Session mit höchstem Exalted-Wert
- **Best Session by Maps**: Session mit den meisten Maps

### 👤 Charakter-Aufschlüsselung
Alle Statistiken aufgeschlüsselt nach Charakteren

### 📅 Tägliche Statistiken
Aktivitäts-Aufschlüsselung nach Tagen mit:
- Sessions pro Tag
- Maps pro Tag
- Exalted-Wert pro Tag
- Spielzeit pro Tag

## Features

### 🎨 Farbcodierung
- 🟢 **Grün**: Gute Performance-Werte
- 🟡 **Gelb**: Durchschnittliche Werte
- 🔴 **Rot**: Niedrige Performance
- 🟨 **Gold**: Hohe Exalted-Werte
- 🔵 **Blau**: Zeitangaben und Daten

### 📊 Performance-Vergleiche
Das Test-Script zeigt Performance-Entwicklung zwischen verschiedenen Zeiträumen:
- Frühere vs. spätere Sessions
- Effizienz-Trends
- Verbesserungen oder Verschlechterungen

### 🔍 Flexible Sortierung
Top-Sessions können sortiert werden nach:
- **Value**: Höchster Chaos-Wert
- **Maps**: Meiste Maps
- **Duration**: Längste Sessions
- **Efficiency**: Beste Exalted/Stunde Rate

## Ausgabe-Beispiel

```
📊 PATH OF EXILE 2 - SESSION STATISTICS OVERVIEW
======================================================================

🎯 OVERALL STATISTICS
├─ Total Sessions: 204
├─ Sessions with Maps: 42
├─ Total Runtime: 19:09:31
├─ Total Value: 15,704.00 exalted
└─ Total Maps: 91

⚡ EFFICIENCY METRICS
├─ Maps per Hour: 4.75
├─ Value per Hour: 819.68 exalted
├─ Avg Map Value: 158.73 exalted
└─ Avg Map Time: 0:09:36

🏆 TOP 5 SESSIONS BY VALUE
1. 2025-09-25 | 1,843.41 exalted | 5 maps | 0:43:16
2. 2025-09-24 | 1,505.85 exalted | 6 maps | 0:58:28
3. 2025-09-24 | 1,440.82 exalted | 4 maps | 0:47:30
```

## Anforderungen

- Python 3.6+
- `sessions.jsonl` Datei im selben Verzeichnis
- Keine externen Dependencies erforderlich

Das System ist vollständig eigenständig und benötigt nur die Standard-Python-Bibliotheken.