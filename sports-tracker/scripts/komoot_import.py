#!/usr/bin/env python3
"""
Komoot Tour Importer - Importiert Komoot-Touren in den Sport-Tracker

Lädt Touren von Komoot (via kompy + export-komoot) und trägt sie in die
sports_tracker.db ein. Dedup anhand der komoot_id.

Verwendung:
  python3 scripts/komoot_import.py                    # Neue Touren importieren
  python3 scripts/komoot_import.py --full             # Alle Touren neu importieren
  python3 scripts/komoot_import.py --dry-run           # Nur anzeigen, nicht eintragen
  python3 scripts/komoot_import.py --export-gpx       # GPX-Dateien herunterladen
"""

import os
import sys
import json
import sqlite3
import argparse
import subprocess
from datetime import datetime

# .env laden
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ.setdefault(key.strip(), val.strip())

KOMOOT_EMAIL = os.environ.get('KOMOOT_EMAIL', '')
KOMOOT_PASSWORD = os.environ.get('KOMOOT_PASSWORD', '') or os.environ.get('KOMOOT_PASSWD', '')
KOMOOT_USER_ID = os.environ.get('KOMOOT_USER_ID', '')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sports_tracker.db')
GPX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'komoot_gpx')
EXPORT_BIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'export-komoot')

# Komoot Sport-Typ -> Sport-Tracker Kategorie
SPORT_MAP = {
    'touring_cycling': 'Fahrrad',
    'cycling': 'Fahrrad',
    'mtb': 'Fahrrad',
    'race_cycling': 'Fahrrad',
    'e_cycling': 'Fahrrad',
    'e_mtb': 'Fahrrad',
    'e_touring_cycling': 'Fahrrad',
    'hiking': 'Wandern',
    'hike': 'Wandern',
    'walking': 'Spazieren',
    'walk': 'Spazieren',
    'running': 'Laufen',
    'run': 'Laufen',
    'trail_running': 'Laufen',
    'nordic_walking': 'Spazieren',
    'skiing': 'Skifahren',
    'ski_touring': 'Skifahren',
    'snowboard': 'Skifahren',
    'snowshoe': 'Spazieren',
    'inline_skating': 'Fahrrad',
    'kayaking': 'Sonstiges',
    'climbing': 'Sonstiges',
}


def get_db():
    """Datenbankverbindung herstellen."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_existing_komoot_ids(conn):
    """Bereits importierte Komoot-IDs abrufen."""
    rows = conn.execute("SELECT komoot_id FROM activities WHERE komoot_id IS NOT NULL AND komoot_id != ''").fetchall()
    return {row['komoot_id'] for row in rows}


def fetch_tours_api():
    """Touren direkt via Komoot v007 API abrufen (zuverlässiger als kompy)."""
    try:
        import requests as req_lib
        from requests.auth import HTTPBasicAuth
        
        session = req_lib.Session()
        
        # Login (v006 endpoint, works reliably)
        login_url = f'https://api.komoot.de/v006/account/email/{KOMOOT_EMAIL}/'
        r = session.get(login_url, auth=HTTPBasicAuth(KOMOOT_EMAIL, KOMOOT_PASSWORD), timeout=15)
        if r.status_code != 200:
            print(f"❌ Login fehlgeschlagen: {r.status_code}")
            return []
        
        user_id = r.json().get('username', KOMOOT_USER_ID)
        print(f"✅ Login erfolgreich (User: {user_id})")
        
        # Alle Touren laden (paginiert, v007 API)
        all_tours = []
        page = 0
        while True:
            url = f'https://api.komoot.de/v007/users/{user_id}/tours/'
            params = {
                'limit': 100,
                'page': page,
                'sort_field': 'date',
                'sort': 'desc',
            }
            r = session.get(url, params=params, auth=HTTPBasicAuth(KOMOOT_EMAIL, KOMOOT_PASSWORD), timeout=30)
            if r.status_code != 200:
                print(f"❌ Tours API Fehler: {r.status_code}")
                break
            
            data = r.json()
            tours = data.get('_embedded', {}).get('tours', [])
            if not tours:
                break
            
            all_tours.extend(tours)
            page_info = data.get('page', {})
            total_pages = page_info.get('totalPages', 1)
            page += 1
            if page >= total_pages:
                break
        
        print(f"📊 {len(all_tours)} Touren gefunden")
        return all_tours
    except Exception as e:
        print(f"❌ API Fehler: {e}")
        return []


def fetch_tours_kompy():
    """Touren via kompy Library abrufen (Fallback)."""
    try:
        from kompy import KomootConnector
        connector = KomootConnector(KOMOOT_EMAIL, KOMOOT_PASSWORD)
        user_id = connector.authentication.get_username()
        print(f"✅ Login erfolgreich (User: {user_id})")
        
        tours = connector.get_tours(limit=100, sort_field='date')
        print(f"📊 {len(tours)} Touren gefunden")
        return tours
    except Exception as e:
        print(f"❌ Kompy Fehler: {e}")
        return []


def tour_to_activity(tour):
    """Komoot-Tour (Dict von API oder kompy-Objekt) in Activity-Dict umwandeln."""
    # Support both raw dict (from API) and kompy Tour objects
    def get_val(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default) if hasattr(obj, key) else default
    
    tour_id = str(get_val(tour, 'id', ''))
    if not tour_id:
        return None
    
    # Datum
    date_raw = get_val(tour, 'date', '')
    if date_raw:
        try:
            from dateutil.parser import parse as parse_date
            date_str = parse_date(date_raw).strftime('%Y-%m-%d')
        except Exception:
            date_str = date_raw[:10] if len(date_raw) >= 10 else date_raw
    else:
        date_str = None
    
    # Distanz (Meter -> km)
    distance_m = get_val(tour, 'distance', 0) or 0
    distance_km = round(distance_m / 1000, 2) if distance_m else None
    
    # Dauer (Sekunden -> Minuten)
    duration_s = get_val(tour, 'duration', 0) or get_val(tour, 'total_duration', 0) or 0
    duration_min = round(duration_s / 60) if duration_s else None
    
    # Dauer in Bewegung
    time_in_motion_s = get_val(tour, 'time_in_motion', 0) or 0
    time_in_motion_min = round(time_in_motion_s / 60) if time_in_motion_s else None
    
    # Höhenmeter
    elevation_gain = get_val(tour, 'elevation_up', 0)
    elevation_loss = get_val(tour, 'elevation_down', 0)
    
    # Kalorien
    kcal_active = get_val(tour, 'kcal_active', 0) or 0
    
    # Sport-Art
    sport = get_val(tour, 'sport', 'walking') or 'walking'
    category = SPORT_MAP.get(sport, 'Sonstiges')
    
    # Name
    name = get_val(tour, 'name', f'Komoot {sport}') or f'Komoot {sport}'
    
    # Durchschnittsgeschwindigkeit berechnen
    avg_speed = None
    if distance_km and time_in_motion_min and time_in_motion_min > 0:
        avg_speed = round(distance_km / (time_in_motion_min / 60), 1)
    elif distance_km and duration_min and duration_min > 0:
        avg_speed = round(distance_km / (duration_min / 60), 1)
    
    # Typ bestimmen
    tour_type = get_val(tour, 'type', 'tour_recorded') or 'tour_recorded'
    type_label = 'Aufgezeichnet' if tour_type == 'tour_recorded' else 'Geplant'
    
    return {
        'date': date_str,
        'category': category,
        'value': str(distance_km) if distance_km else None,
        'description': f'{name} ({type_label})',
        'type': sport,
        'duration_min': duration_min,
        'calories': int(kcal_active) if kcal_active else None,
        'speed_kmh': avg_speed,
        'elevation_gain_m': elevation_gain,
        'elevation_loss_m': elevation_loss,
        'avg_speed_kmh': avg_speed,
        'source': 'komoot',
        'komoot_id': tour_id,
        'weight_kg': None,
        'max_speed_kmh': None,
        'gpx_file': None,
    }


def import_tour(conn, activity, dry_run=False):
    """Einzelne Tour in DB eintragen."""
    if not activity or not activity.get('komoot_id'):
        return False
    
    # Prüfe ob bereits importiert
    existing = conn.execute(
        "SELECT id FROM activities WHERE komoot_id = ?", 
        (activity['komoot_id'],)
    ).fetchone()
    
    if existing:
        return False  # Bereits vorhanden
    
    if dry_run:
        print(f"  🏃 WÜRDE importieren: {activity['date']} | {activity['category']} | {activity['description']} | {activity['value']} km")
        return True
    
    conn.execute("""
        INSERT INTO activities (date, category, value, description, type, 
                                duration_min, calories, speed_kmh, weight_kg,
                                elevation_gain_m, elevation_loss_m, avg_speed_kmh, 
                                max_speed_kmh, source, komoot_id, gpx_file)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        activity['date'],
        activity['category'],
        activity['value'],
        activity['description'],
        activity['type'],
        activity['duration_min'],
        activity['calories'],
        activity['speed_kmh'],
        activity['weight_kg'],
        activity['elevation_gain_m'],
        activity['elevation_loss_m'],
        activity['avg_speed_kmh'],
        activity['max_speed_kmh'],
        activity['source'],
        activity['komoot_id'],
        activity['gpx_file'],
    ))
    conn.commit()
    return True


def export_gpx_files():
    """GPX-Dateien mit export-komoot Binary herunterladen."""
    if not os.path.exists(EXPORT_BIN):
        print(f"❌ export-komoot Binary nicht gefunden: {EXPORT_BIN}")
        return False
    
    os.makedirs(GPX_DIR, exist_ok=True)
    
    env = os.environ.copy()
    env['KOMOOT_EMAIL'] = KOMOOT_EMAIL
    env['KOMOOT_PASSWORD'] = KOMOOT_PASSWORD
    env['KOMOOT_USER_ID'] = KOMOOT_USER_ID
    
    cmd = [
        EXPORT_BIN,
        '--email', KOMOOT_EMAIL,
        '--password', KOMOOT_PASSWORD,
        '--userid', KOMOOT_USER_ID,
        '--to', GPX_DIR,
    ]
    
    print(f"📁 Exportiere GPX-Dateien nach {GPX_DIR}...")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    
    if result.returncode != 0:
        print(f"❌ export-komoot Fehler: {result.stderr}")
        return False
    
    print(result.stdout)
    return True


def generate_elevation_chart(gpx_dir=None, output_path=None):
    """Höhenprofil-Chart aus GPX-Dateien generieren."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import xml.etree.ElementTree as ET
    except ImportError:
        print("⚠️ matplotlib nicht installiert - Chart-Generierung übersprungen")
        return None
    
    if gpx_dir is None:
        gpx_dir = GPX_DIR
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'komoot_elevation_profile.png')
    
    if not os.path.exists(gpx_dir):
        return None
    
    # Alle GPX-Dateien finden, neueste zuerst
    gpx_files = sorted(
        [f for f in os.listdir(gpx_dir) if f.endswith('.gpx')],
        key=lambda f: os.path.getmtime(os.path.join(gpx_dir, f)),
        reverse=True
    )
    
    if not gpx_files:
        return None
    
    # Maximal 4 Touren darstellen
    gpx_files = gpx_files[:4]
    
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    fig, axes = plt.subplots(len(gpx_files), 1, figsize=(12, 4 * len(gpx_files)), squeeze=False)
    
    chart_data = []
    for i, gpx_file in enumerate(gpx_files):
        path = os.path.join(gpx_dir, gpx_file)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            points = root.findall('.//gpx:trkpt', ns)
            if not points:
                continue
            
            times = []
            eles = []
            start_time = None
            for p in points:
                time_el = p.find('gpx:time', ns)
                ele_el = p.find('gpx:ele', ns)
                if time_el is not None and ele_el is not None:
                    t = datetime.fromisoformat(time_el.text.replace('Z', '+00:00'))
                    if start_time is None:
                        start_time = t
                    delta_min = (t - start_time).total_seconds() / 60
                    times.append(delta_min)
                    eles.append(float(ele_el.text))
            
            if not eles:
                continue
            
            # Titel aus Dateinamen extrahieren
            name = gpx_file.replace('.gpx', '')
            # Datum und Tour-ID extrahieren
            parts = name.split('_')
            date_part = parts[0] if parts else ''
            tour_type = parts[2] if len(parts) > 2 else ''
            title = f'{date_part} {tour_type.capitalize()}' if tour_type else date_part
            
            # Höhenmeter berechnen
            gain = sum(max(0, eles[j+1]-eles[j]) for j in range(len(eles)-1))
            loss = sum(max(0, eles[j]-eles[j+1]) for j in range(len(eles)-1))
            
            # Chart zeichnen
            color = '#2ecc71' if 'wander' in gpx_file.lower() or 'hike' in gpx_file.lower() else '#3498db'
            axes[i][0].fill_between(times, eles, min(eles) - 5, alpha=0.3, color=color)
            axes[i][0].plot(times, eles, color=color, linewidth=2)
            axes[i][0].set_title(title, fontsize=12, fontweight='bold')
            axes[i][0].set_xlabel('Zeit (Minuten)')
            axes[i][0].set_ylabel('Höhe (m)')
            axes[i][0].grid(True, alpha=0.3)
            axes[i][0].text(0.02, 0.95, f'↑{gain:.0f}m ↓{loss:.0f}m | max {max(eles):.0f}m',
                           transform=axes[i][0].transAxes, fontsize=10, va='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            chart_data.append({
                'file': gpx_file,
                'date': date_part,
                'gain': round(gain),
                'loss': round(loss),
                'max_elev': round(max(eles)),
                'min_elev': round(min(eles)),
            })
        except Exception as e:
            print(f"⚠️ Fehler bei {gpx_file}: {e}")
            continue
    
    if not chart_data:
        return None
    
    plt.suptitle('Komoot Höhenprofile', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Chart generiert: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Komoot Tour Importer')
    parser.add_argument('--full', action='store_true', help='Alle Touren importieren (inkl. bereits vorhandene)')
    parser.add_argument('--dry-run', action='store_true', help='Nur anzeigen, nichts eintragen')
    parser.add_argument('--export-gpx', action='store_true', help='GPX-Dateien herunterladen')
    parser.add_argument('--json', action='store_true', help='JSON-Ausgabe für Cron')
    args = parser.parse_args()
    
    if not KOMOOT_EMAIL or not KOMOOT_PASSWORD:
        print("❌ KOMOOT_EMAIL und KOMOOT_PASSWORD in .env erforderlich!")
        sys.exit(1)
    
    if args.export_gpx:
        export_gpx_files()
        return
    
    conn = get_db()
    
    # Bestehende IDs laden
    existing_ids = get_existing_komoot_ids(conn) if not args.full else set()
    print(f"📊 Bereits importiert: {len(existing_ids)} Touren")
    
    # Touren abrufen (v007 API first, fallback to kompy)
    tours = fetch_tours_api()
    if tours is None:
        tours = []
    # If API returned nothing and we have kompy, try that
    if not tours:
        tours_kompy = fetch_tours_kompy()
        if tours_kompy:
            tours = tours_kompy
    
    if not tours:
        if args.json:
            print(json.dumps({"imported": 0, "skipped": 0, "total": 0}))
        else:
            print("📭 Keine Touren gefunden (Account leer oder Fehler)")
        conn.close()
        return
    
    imported = 0
    skipped = 0
    
    for tour in tours:
        # Geplante Touren überspringen - nur aufgezeichnete importieren
        tour_type = tour.get('type', 'tour_recorded') if isinstance(tour, dict) else getattr(tour, 'type', 'tour_recorded')
        if tour_type and tour_type != 'tour_recorded':
            skipped += 1
            continue
        
        activity = tour_to_activity(tour)
        if not activity:
            skipped += 1
            continue
        
        if activity['komoot_id'] in existing_ids and not args.full:
            skipped += 1
            continue
        
        if import_tour(conn, activity, dry_run=args.dry_run):
            imported += 1
            if not args.dry_run:
                print(f"  ✅ Importiert: {activity['date']} | {activity['category']} | {activity['description']} | {activity['value']} km | ↑{activity['elevation_gain_m']}m ↓{activity['elevation_loss_m']}m | ⌀{activity['avg_speed_kmh']} km/h")
    
    # Nach Import: GPX exportieren + Analysen + Charts generieren
    chart_path = None
    if imported > 0:
        print("\n📁 Exportiere GPX-Dateien für neue Touren...")
        gpx_ok = export_gpx_files()
        if gpx_ok:
            print("📊 Analysiere GPX-Daten + generiere Charts...")
            chart_path = generate_elevation_chart()
            # Detaillierte Analyse pro Tour
            try:
                import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from scripts.gpx_analyzer import analyze_gpx, generate_chart as gen_detail_chart
                import glob
                os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'komoot_charts'), exist_ok=True)
                gpx_files = sorted(glob.glob(os.path.join(GPX_DIR, '*.gpx')))
                for gpx_file in gpx_files:
                    basename = os.path.basename(gpx_file)
                    # Kategorie aus DB holen
                    komoot_id = basename.split('_')[1] if '_' in basename else ''
                    row = conn.execute('SELECT category FROM activities WHERE komoot_id = ?', (komoot_id,)).fetchone() if komoot_id else None
                    cat = row['category'] if row else 'Wandern'
                    analysis = analyze_gpx(gpx_file, category=cat)
                    if analysis:
                        chart_name = basename.replace('.gpx', '_analysis.png')
                        chart_out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'komoot_charts', chart_name)
                        gen_detail_chart(analysis, chart_out)
                        # Kalorien in DB updaten
                        if analysis['total_calories'] > 0:
                            conn.execute('UPDATE activities SET calories = ? WHERE komoot_id = ?', (analysis['total_calories'], komoot_id))
                            conn.execute('UPDATE activities SET avg_speed_kmh = ?, max_speed_kmh = ? WHERE komoot_id = ?', (analysis['avg_speed_kmh'], analysis['max_speed_kmh'], komoot_id))
                            conn.commit()
                        analysis['chart_path'] = chart_out
                        print(f"  📊 {basename}: {analysis['total_dist_km']}km | ⌀{analysis['avg_speed_kmh']}km/h | 🔥{analysis['total_calories']}kcal")
            except Exception as e:
                print(f"⚠️ GPX-Analyse Fehler: {e}")
    
    conn.close()
    
    result = {
        "imported": imported,
        "skipped": skipped,
        "total": len(tours),
        "chart": chart_path,
    }
    
    if args.json:
        print(json.dumps(result))
    else:
        print(f"\n🏁 Import abgeschlossen: {imported} neu, {skipped} übersprungen, {len(tours)} gesamt")
        if chart_path:
            print(f"📊 Höhenprofil: {chart_path}")


if __name__ == '__main__':
    main()