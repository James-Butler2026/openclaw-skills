#!/usr/bin/env python3
"""
GitHub Manager - Veröffentlicht Skills zu GitHub
SICHERE VERSION - Keine Tokens im Output!
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib import request, error

# SICHERHEIT: Token niemals im Output zeigen
def load_config():
    """Lädt GitHub Konfiguration aus .env"""
    # .env laden
    env_path = Path.home() / '.openclaw' / 'workspace' / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    token = os.getenv('GITHUB_TOKEN')
    username = os.getenv('GITHUB_USERNAME')
    email = os.getenv('GITHUB_EMAIL', 'j_butler@web.de')
    
    if not token:
        raise ValueError(
            "GITHUB_TOKEN nicht in .env gefunden!\n"
            "1. Erstelle Token unter: https://github.com/settings/tokens\n"
            "2. Füge zu .env hinzu: GITHUB_TOKEN=ghp_xxxx"
        )
    
    if not username:
        raise ValueError(
            "GITHUB_USERNAME nicht in .env gefunden!\n"
            "Füge zu .env hinzu: GITHUB_USERNAME=dein_username"
        )
    
    return {'token': token, 'username': username, 'email': email}


def github_api(endpoint, method='GET', data=None, config=None):
    """Führt GitHub API Request durch"""
    if config is None:
        config = load_config()
    
    url = f"https://api.github.com{endpoint}"
    headers = {
        'Authorization': f"token {config['token']}",
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenClaw-GitHub-Manager'
    }
    
    req = request.Request(url, headers=headers, method=method)
    
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"GitHub API Fehler {e.code}: {error_body}")


def create_repo(name, description="", private=False, config=None):
    """Erstellt ein neues GitHub Repository"""
    print(f"🐙 Erstelle Repository: {name}")
    
    data = {
        'name': name,
        'description': description,
        'private': private,
        'auto_init': True,
        'license_template': 'mit'
    }
    
    result = github_api('/user/repos', method='POST', data=data, config=config)
    
    print(f"✅ Repository erstellt: {result['html_url']}")
    return result


def check_repo_exists(repo_name, config=None):
    """Prüft ob Repository existiert"""
    if config is None:
        config = load_config()
    
    try:
        github_api(f"/repos/{config['username']}/{repo_name}", config=config)
        return True
    except:
        return False


def publish_skill(skill_name, repo_name, description="", config=None):
    """Veröffentlicht einen Skill zu GitHub - JETZT MIT ECHTEM PUSH!"""
    if config is None:
        config = load_config()
    
    print(f"🚀 Veröffentliche Skill: {skill_name}")
    
    # Prüfe/erstelle Repository
    if not check_repo_exists(repo_name, config):
        print(f"   📦 Repository existiert nicht, erstelle...")
        create_repo(repo_name, description, private=False, config=config)
    
    # Erstelle temporäres Verzeichnis für Clone
    temp_clone = Path(tempfile.mkdtemp(prefix='github_clone_'))
    
    try:
        # SICHER: Token in URL nicht im Output zeigen
        repo_url = f"https://{config['username']}:{config['token']}@github.com/{config['username']}/{repo_name}.git"
        
        print(f"   📥 Klone Repository...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, str(temp_clone)],
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Token aus Fehlermeldung entfernen
            safe_error = result.stderr.replace(config['token'], '***HIDDEN***')
            shutil.rmtree(temp_clone, ignore_errors=True)
            raise RuntimeError(f"Git clone fehlgeschlagen: {safe_error}")
        
        # Kopiere lokalen Skill ins geklonte Repo
        skill_source = Path.home() / '.openclaw' / 'workspace' / 'skills' / skill_name
        skill_dest = temp_clone / skill_name
        
        if not skill_source.exists():
            print(f"   ⚠️  Lokaler Skill nicht gefunden: {skill_source}")
            shutil.rmtree(temp_clone, ignore_errors=True)
            return
        
        if skill_dest.exists():
            print(f"   🗑️  Entferne alte Version...")
            shutil.rmtree(skill_dest)
        
        print(f"   📁 Kopiere Skill-Dateien...")
        shutil.copytree(skill_source, skill_dest)
        
        # Erstelle README falls nötig
        readme_path = skill_dest / 'README.md'
        skill_md_path = skill_dest / 'SKILL.md'
        if not readme_path.exists() and skill_md_path.exists():
            print(f"   📝 Generiere README.md...")
            with open(skill_md_path) as f:
                content = f.read()
            with open(readme_path, 'w') as f:
                f.write(f"# {skill_name}\n\n{content}")
        
        # Git add, commit, push
        print(f"   🐙 Committe und pushe...")
        subprocess.run(['git', '-C', str(temp_clone), 'config', 'user.email', config['email']], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(temp_clone), 'config', 'user.name', 'James Butler'], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(temp_clone), 'add', f"{skill_name}/"], check=True, capture_output=True)
        
        # Prüfe ob es etwas zu commiten gibt
        status_result = subprocess.run(
            ['git', '-C', str(temp_clone), 'status', '--porcelain'],
            check=True, capture_output=True, text=True
        )
        
        if status_result.stdout.strip():
            subprocess.run(
                ['git', '-C', str(temp_clone), 'commit', '-m', f'Add {skill_name} skill'],
                check=True, capture_output=True
            )
            subprocess.run(
                ['git', '-C', str(temp_clone), 'push'],
                check=True, capture_output=True
            )
            print(f"   ✅ Erfolgreich gepusht!")
        else:
            print(f"   ⚠️  Nichts zu committen (bereits aktuell?)")
        
        # Cleanup
        shutil.rmtree(temp_clone, ignore_errors=True)
        
    except Exception as e:
        shutil.rmtree(temp_clone, ignore_errors=True)
        raise
    
    print(f"\n🎉 Fertig!")
    print(f"   URL: https://github.com/{config['username']}/{repo_name}/tree/main/{skill_name}")


def publish_all_skills(repo_name, config=None):
    """Veröffentlicht alle Skills"""
    if config is None:
        config = load_config()
    
    skills_dir = Path.home() / '.openclaw' / 'workspace' / 'skills'
    
    if not skills_dir.exists():
        print("❌ Keine Skills gefunden!")
        return
    
    skills = [d.name for d in skills_dir.iterdir() 
              if d.is_dir() and not d.name.startswith('.')]
    
    print(f"📦 Gefundene Skills: {len(skills)}")
    print(f"   {', '.join(skills)}\n")
    
    # Einer nach dem anderen (nicht parallel)
    for skill_name in skills:
        try:
            publish_skill(skill_name, repo_name, config=config)
            print()
        except Exception as e:
            print(f"   ❌ Fehler bei {skill_name}: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description='GitHub Manager - Skills veröffentlichen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --skill image-generation --repo openclaw-skills
  %(prog)s --all --repo openclaw-skills
  %(prog)s --create-repo openclaw-skills --description "Skill Collection"
        """
    )
    
    parser.add_argument('--skill', '-s', help='Skill-Name zu veröffentlichen')
    parser.add_argument('--repo', '-r', default='openclaw-skills', help='Ziel-Repository')
    parser.add_argument('--all', '-a', action='store_true', help='Alle Skills veröffentlichen')
    parser.add_argument('--create-repo', '-c', help='Neues Repository erstellen')
    parser.add_argument('--description', '-d', default='', help='Repository-Beschreibung')
    parser.add_argument('--private', '-p', action='store_true', help='Privates Repository')
    
    args = parser.parse_args()
    
    try:
        config = load_config()
        
        if args.create_repo:
            create_repo(args.create_repo, args.description, args.private, config)
        elif args.all:
            publish_all_skills(args.repo, config)
        elif args.skill:
            publish_skill(args.skill, args.repo, args.description, config)
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
