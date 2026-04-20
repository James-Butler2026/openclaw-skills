#!/usr/bin/env python3
"""
WordPress REST API Manager
Erstellt, aktualisiert und löscht WordPress-Beiträge via REST API.

Autor: OpenClaw Assistent
Version: 1.0.0
"""

import argparse
import json
import os
import sys
import ssl
import base64
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# SSL Context (für HTTPS)
ssl_context = ssl.create_default_context()

# Konfiguration aus Umgebungsvariablen laden
WP_URL = os.getenv('WORDPRESS_URL', '')
WP_USERNAME = os.getenv('WORDPRESS_USERNAME', '')
WP_API_KEY = os.getenv('WORDPRESS_API_KEY', '')

# REST API Endpunkte
API_BASE = f"{WP_URL}/wp-json/wp/v2" if WP_URL else None

def make_request(url, method='GET', data=None, headers=None):
    """Führt einen HTTP Request aus."""
    req_headers = headers or {}
    
    # Auth hinzufügen (Basic Auth mit Application Password)
    if WP_USERNAME and WP_API_KEY:
        auth_string = f"{WP_USERNAME}:{WP_API_KEY}"
        auth_str = base64.b64encode(auth_string.encode()).decode()
        req_headers['Authorization'] = f'Basic {auth_str}'
    
    req_headers.setdefault('Content-Type', 'application/json')
    req_headers.setdefault('Accept', 'application/json')
    
    # Cloudflare-Bypass: Realistischer Browser-User-Agent
    req_headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    req_headers.setdefault('Accept-Language', 'de-DE,de;q=0.9,en;q=0.8')
    req_headers.setdefault('Referer', f'{WP_URL}/wp-admin/')
    
    if data and isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    
    req = Request(url, data=data, headers=req_headers, method=method)
    
    try:
        with urlopen(req, context=ssl_context, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            print(f"❌ HTTP Fehler {e.code}: {error_json.get('message', error_body)}")
        except:
            print(f"❌ HTTP Fehler {e.code}: {error_body[:200]}")
        return None
    except URLError as e:
        print(f"❌ Verbindungsfehler: {e.reason}")
        return None

def check_config():
    """Prüft ob die Konfiguration vollständig ist."""
    if not WP_URL:
        print("❌ Fehler: WORDPRESS_URL nicht gesetzt!")
        print("   Füge zu .env hinzu: WORDPRESS_URL=https://deinblog.de")
        return False
    if not WP_USERNAME:
        print("❌ Fehler: WORDPRESS_USERNAME nicht gesetzt!")
        print("   Füge zu .env hinzu: WORDPRESS_USERNAME=dein_benutzername")
        return False
    if not WP_API_KEY:
        print("❌ Fehler: WORDPRESS_API_KEY nicht gesetzt!")
        print("   Füge zu .env hinzu: WORDPRESS_API_KEY=xxxx xxxx xxxx xxxx")
        return False
    return True

def create_page(title, content, status='publish'):
    """Erstellt eine neue Seite."""
    if not check_config():
        return None
    
    url = f"{API_BASE}/pages"
    data = {
        'title': title,
        'content': content,
        'status': status
    }
    
    result = make_request(url, method='POST', data=data)
    if result:
        print(f"✅ **Seite erstellt!**")
        print(f"   ID: {result['id']}")
        print(f"   Titel: {result['title']['rendered']}")
        print(f"   Status: {result['status']}")
        print(f"   Link: {result['link']}")
        return result
    return None

def list_pages(status='publish', per_page=10):
    """Zeigt alle Seiten an."""
    if not check_config():
        return
    
    url = f"{API_BASE}/pages?status={status}&per_page={per_page}&orderby=date&order=desc"
    
    posts = make_request(url)
    if posts is None:
        return
    
    print(f"\n📰 **WordPress Beiträge** ({status})\n")
    print("-" * 80)
    
    if not posts:
        print("Keine Beiträge gefunden.")
        return
    
    for post in posts:
        post_id = post.get('id', 'N/A')
        title = post.get('title', {}).get('rendered', 'Ohne Titel')
        date = post.get('date', 'N/A')
        link = post.get('link', 'N/A')
        status_icon = '🟢' if post.get('status') == 'publish' else '🟡'
        
        print(f"{status_icon} ID: {post_id}")
        print(f"   Titel: {title}")
        print(f"   Datum: {date}")
        print(f"   Link: {link}")
        print("-" * 80)
    
    print(f"\nGesamt: {len(posts)} Beiträge")

def get_post(post_id):
    """Zeigt einen bestimmten Beitrag an."""
    if not check_config():
        return
    
    url = f"{API_BASE}/posts/{post_id}"
    
    post = make_request(url)
    if post is None:
        print(f"❌ Beitrag {post_id} nicht gefunden")
        return
    
    print(f"\n📄 **Beitrag Details**\n")
    print("=" * 80)
    print(f"ID: {post.get('id')}")
    print(f"Titel: {post.get('title', {}).get('rendered', 'N/A')}")
    print(f"Status: {post.get('status', 'N/A')}")
    print(f"Autor: {post.get('author', 'N/A')}")
    print(f"Datum: {post.get('date', 'N/A')}")
    print(f"Link: {post.get('link', 'N/A')}")
    print("-" * 80)
    
    content = post.get('content', {}).get('rendered', 'Kein Inhalt')
    print(f"Inhalt:\n{content[:500]}..." if len(content) > 500 else f"Inhalt:\n{content}")
    print("=" * 80)

def create_post(title, content, status='publish', category_ids=None, tag_ids=None, excerpt=None):
    """Erstellt einen neuen Beitrag."""
    if not check_config():
        return None
    
    url = f"{API_BASE}/posts"
    
    data = {
        'title': title,
        'content': content,
        'status': status,
    }
    
    if excerpt:
        data['excerpt'] = excerpt
    if category_ids:
        data['categories'] = category_ids
    if tag_ids:
        data['tags'] = tag_ids
    
    post = make_request(url, method='POST', data=data)
    if post is None:
        return None
    
    print(f"\n✅ **Beitrag erstellt!**\n")
    print(f"ID: {post.get('id')}")
    print(f"Titel: {post.get('title', {}).get('rendered', 'N/A')}")
    print(f"Status: {post.get('status', 'N/A')}")
    print(f"Link: {post.get('link', 'N/A')}")
    
    return post.get('id')

def update_post(post_id, title=None, content=None, status=None, category_ids=None, tag_ids=None):
    """Aktualisiert einen bestehenden Beitrag."""
    if not check_config():
        return
    
    url = f"{API_BASE}/posts/{post_id}"
    
    data = {}
    if title is not None:
        data['title'] = title
    if content is not None:
        data['content'] = content
    if status is not None:
        data['status'] = status
    if category_ids is not None:
        data['categories'] = category_ids
    if tag_ids is not None:
        data['tags'] = tag_ids
    
    if not data:
        print("❌ Fehler: Keine Änderungen angegeben!")
        return
    
    post = make_request(url, method='POST', data=data)
    if post is None:
        return
    
    print(f"\n✅ **Beitrag aktualisiert!**\n")
    print(f"ID: {post.get('id')}")
    print(f"Titel: {post.get('title', {}).get('rendered', 'N/A')}")
    print(f"Status: {post.get('status', 'N/A')}")
    print(f"Link: {post.get('link', 'N/A')}")

def delete_post(post_id, force=False):
    """Löscht einen Beitrag."""
    if not check_config():
        return
    
    url = f"{API_BASE}/posts/{post_id}"
    if force:
        url += "?force=true"
    
    result = make_request(url, method='DELETE')
    if result is None:
        return
    
    if force:
        print(f"\n🗑️ **Beitrag {post_id} dauerhaft gelöscht!**")
    else:
        print(f"\n🗑️ **Beitrag {post_id} in den Papierkorb verschoben!**")

def list_categories():
    """Zeigt alle Kategorien an."""
    if not check_config():
        return
    
    url = f"{API_BASE}/categories"
    
    categories = make_request(url)
    if categories is None:
        return
    
    print(f"\n📁 **Kategorien**\n")
    print("-" * 50)
    
    for cat in categories:
        print(f"ID {cat.get('id')}: {cat.get('name', 'N/A')}")
    
    print("-" * 50)

def list_tags():
    """Zeigt alle Tags an."""
    if not check_config():
        return
    
    url = f"{API_BASE}/tags"
    
    tags = make_request(url)
    if tags is None:
        return
    
    print(f"\n🏷️ **Tags**\n")
    print("-" * 50)
    
    for tag in tags:
        print(f"ID {tag.get('id')}: {tag.get('name', 'N/A')}")
    
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(
        description='WordPress REST API Manager - Verwaltet WordPress-Beiträge via REST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Beiträge auflisten
  %(prog)s --list
  
  # Neuen Beitrag erstellen
  %(prog)s --create "Mein Titel" "HTML Inhalt hier..."
  
  # Beitrag als Entwurf erstellen
  %(prog)s --create "Titel" "Inhalt" --status draft
  
  # Beitrag bearbeiten
  %(prog)s --update 42 --title "Neuer Titel"
  
  # Beitrag löschen (Papierkorb)
  %(prog)s --delete 42
  
  # Beitrag dauerhaft löschen
  %(prog)s --delete 42 --force
  
  # Seite erstellen
  %(prog)s --create-page "Seitentitel" "HTML Inhalt"
  
  # Kategorien anzeigen
  %(prog)s --list-categories
        """
    )
    
    parser.add_argument('--list', action='store_true', help='Alle Beiträge anzeigen')
    parser.add_argument('--drafts', action='store_true', help='Entwürfe anzeigen')
    parser.add_argument('--get', type=int, metavar='ID', help='Beitrag Details anzeigen')
    parser.add_argument('--create', nargs=2, metavar=('TITEL', 'INHALT'), help='Neuen Beitrag erstellen')
    parser.add_argument('--update', type=int, metavar='ID', help='Beitrag aktualisieren')
    parser.add_argument('--delete', type=int, metavar='ID', help='Beitrag löschen')
    parser.add_argument('--force', action='store_true', help='Dauerhaft löschen (nicht nur Papierkorb)')
    
    # Optionale Parameter
    parser.add_argument('--title', help='Titel für Update')
    parser.add_argument('--content', help='Inhalt für Update')
    parser.add_argument('--status', choices=['publish', 'draft', 'pending', 'private'], help='Status')
    parser.add_argument('--categories', help='Kategorie IDs (kommasepariert)')
    parser.add_argument('--tags', help='Tag IDs (kommasepariert)')
    parser.add_argument('--excerpt', help='Auszug (excerpt)')
    parser.add_argument('--limit', type=int, default=10, help='Anzahl der anzuzeigenden Beiträge')
    
    # Listen
    parser.add_argument('--list-categories', action='store_true', help='Alle Kategorien anzeigen')
    parser.add_argument('--list-tags', action='store_true', help='Alle Tags anzeigen')
    
    # Seiten
    parser.add_argument('--create-page', nargs=2, metavar=('TITEL', 'INHALT'), help='Neue Seite erstellen')
    
    args = parser.parse_args()
    
    if args.list:
        list_posts(per_page=args.limit)
    elif args.drafts:
        list_posts(status='draft', per_page=args.limit)
    elif args.get:
        get_post(args.get)
    elif args.create:
        title, content = args.create
        cats = [int(c) for c in args.categories.split(',')] if args.categories else None
        tags = [int(t) for t in args.tags.split(',')] if args.tags else None
        create_post(title, content, args.status or 'publish', cats, tags, args.excerpt)
    elif args.update:
        cats = [int(c) for c in args.categories.split(',')] if args.categories else None
        tags = [int(t) for t in args.tags.split(',')] if args.tags else None
        update_post(args.update, args.title, args.content, args.status, cats, tags)
    elif args.delete:
        delete_post(args.delete, args.force)
    elif args.list_categories:
        list_categories()
    elif args.list_tags:
        list_tags()
    elif args.create_page:
        title, content = args.create_page
        create_page(title, content, args.status or 'publish')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
