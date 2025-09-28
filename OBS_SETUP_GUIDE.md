# OBS Integration Setup Guide

🎬 **PoE Stats Tracker - OBS Studio Integration**

## 📋 Übersicht

Das PoE Stats Tracker OBS Integration Feature erstellt schöne HTML-Overlays für OBS Studio, die live deine Loot-Analyse und Session-Stats anzeigen.

## 🚀 Quick Start

### 1. Flask installieren
```bash
pip install flask
```

### 2. PoE Stats Tracker starten
Starte den Tracker normal - OBS Integration ist automatisch verfügbar wenn Flask installiert ist.

### 3. OBS Server aktivieren
- Drücke **F9** im Tracker um den OBS Web Server zu starten
- Du siehst: `🎬 OBS Web Server started: http://localhost:5000`

### 4. OBS Browser Source hinzufügen

#### Option A: Item Value Table (Empfohlen) 📊
1. In OBS Studio: **Sources** → **Add** → **Browser**
2. **URL:** `http://localhost:5000/obs/item_table`
3. **Width:** 600px, **Height:** 400px
4. **Refresh browser when scene becomes active:** ✅
5. **Shutdown source when not visible:** ✅

#### Option B: Session Stats 📈  
1. **URL:** `http://localhost:5000/obs/session_stats`
2. **Width:** 300px, **Height:** 200px

## 🎯 Features

### Item Value Table
- ✅ Zeigt alle gefundenen Items nach jeder Map
- ✅ Farbcodierte Rarity (Normal, Magic, Rare, Unique)
- ✅ Exalted Orb Werte
- ✅ Session Stats Integration
- ✅ Map Information
- ✅ Auto-Refresh alle 2 Sekunden

### Session Stats
- ✅ Maps completed
- ✅ Total session value
- ✅ Session runtime
- ✅ Auto-Refresh alle 5 Sekunden

## 🔧 Erweiterte Konfiguration

### Custom Styling
Die HTML-Overlays können angepasst werden:
- Edit `obs_overlay_manager.py` 
- Ändere CSS in `_create_item_table_html()` oder `_create_session_overlay_html()`

### Different Port 
```python
# In poe_stats_refactored_v2.py
self.obs_server = OBSWebServer(port=8080)
```

### Test URLs
- Setup Guide: `http://localhost:5000`
- Test Item Table: `http://localhost:5000/test/item_table`
- Test Session Stats: `http://localhost:5000/test/session_stats`

## 🎨 OBS Styling Tips

### Positioning
- **Top-left corner:** Session Stats
- **Bottom-right corner:** Item Value Table
- **Transparency:** Works automatisch mit den Overlays

### Filters
Du kannst OBS Filters hinzufügen:
- **Color Correction** für bessere Sichtbarkeit
- **Chroma Key** falls nötig (sollte nicht nötig sein)
- **Scaling/Aspect Ratio** für perfekte Größe

## 🐛 Troubleshooting

### "OBS integration not available"
```bash
pip install flask
```

### Server startet nicht
- Port 5000 bereits in Verwendung?
- Windows Firewall blocking?
- Drücke F9 erneut zum retry

### Overlay zeigt keine Daten
- Führe mindestens eine Map durch (F2 → F3)
- Check `http://localhost:5000/test/item_table` für Test-Daten

### Performance Issues
- Overlays sind sehr leichtgewichtig (~2KB HTML)
- Auto-refresh kann in OBS ausgeschaltet werden
- Server läuft nur lokal (kein Internet traffic)

## 💡 Pro Tips

1. **Test zuerst:** Nutze `/test/` URLs um das Layout zu testen
2. **Multiple Scenes:** Du kannst die gleiche Browser Source in mehreren Scenes nutzen  
3. **Hotkey:** F9 toggle den Server an/aus während dem Spielen
4. **Mobile:** URLs funktionieren auch auf Handy/Tablet für remote monitoring
5. **Backup:** Die generierten HTML Files sind in `obs_overlays/` gespeichert
6. **No Flicker:** Kein Auto-Refresh mehr - Updates nur nach Map-Completion
7. **Right-Aligned:** Overlays sind rechtsbündig für bessere OBS-Positionierung

## 🚨 Known Limitations

- Server läuft nur lokal (localhost)
- Flask ist single-threaded, aber für Overlays vollkommen ausreichend
- Keine Authentifizierung (nur für lokale Nutzung gedacht)
- Windows Terminal Unicode kann Probleme machen (behoben in der neuesten Version)

## 📱 Mobile/Remote Access

Für access von anderen Geräten:
```python
# In obs_web_server.py ändern:
server = OBSWebServer(host='0.0.0.0', port=5000)
```

**⚠️ ACHTUNG:** Nur in sicheren Netzwerken nutzen!

---

**🎉 Happy Streaming!** 

Wenn alles funktioniert, hast du jetzt live Item-Analysis in deinem Stream! 🎬✨