"""
GitHub Auto-Update System
Checks for new releases and handles updates
"""
import requests
import os
import json
import logging
from datetime import datetime, timedelta
from packaging import version

GITHUB_REPO = "DevSapph1r3/Crystal-Chatbox"  # GitHub repository
VERSION_FILE = "version.txt"
UPDATE_CHECK_CACHE = ".update_cache.json"
UPDATE_CHECK_INTERVAL = 3600  # 1 hour

logger = logging.getLogger(__name__)

def get_current_version():
    """Get current app version"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading version: {e}")
    return "1.0.0"

def get_github_repo():
    """Auto-detect GitHub repo from git remote"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse GitHub URL
            if 'github.com' in url:
                # Handle both HTTPS and SSH URLs
                if url.startswith('https://'):
                    # https://github.com/owner/repo.git
                    parts = url.replace('https://github.com/', '').replace('.git', '').split('/')
                elif url.startswith('git@'):
                    # git@github.com:owner/repo.git
                    parts = url.replace('git@github.com:', '').replace('.git', '').split('/')
                else:
                    return None
                
                if len(parts) >= 2:
                    return f"{parts[0]}/{parts[1]}"
    except Exception as e:
        logger.error(f"Error detecting GitHub repo: {e}")
    return None

def check_for_updates(force=False):
    """
    Check GitHub for new releases
    Returns: dict with update info or None
    """
    try:
        # Check cache
        if not force and os.path.exists(UPDATE_CHECK_CACHE):
            with open(UPDATE_CHECK_CACHE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('checked_at', '2000-01-01'))
                if datetime.now() - cache_time < timedelta(seconds=UPDATE_CHECK_INTERVAL):
                    return cache.get('update_info')
        
        repo = get_github_repo()
        if not repo:
            repo = GITHUB_REPO  # Fallback to hardcoded repo
        
        # Get latest release from GitHub API
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            release = response.json()
            latest_version = release.get('tag_name', '').lstrip('v')
            current_version = get_current_version()
            
            # Use proper semantic version comparison
            try:
                latest_ver = version.parse(latest_version)
                current_ver = version.parse(current_version)
                update_available = latest_ver > current_ver
            except Exception as e:
                logger.error(f"Error parsing versions: {e}")
                # Fallback to string comparison
                update_available = latest_version != current_version and latest_version > current_version
            
            update_info = {
                'current_version': current_version,
                'latest_version': latest_version,
                'update_available': update_available,
                'release_name': release.get('name', ''),
                'release_notes': release.get('body', ''),
                'release_url': release.get('html_url', ''),
                'published_at': release.get('published_at', ''),
                'download_url': release.get('zipball_url', ''),
                'repo': repo
            }
            
            # Cache the result
            with open(UPDATE_CHECK_CACHE, 'w') as f:
                json.dump({
                    'checked_at': datetime.now().isoformat(),
                    'update_info': update_info
                }, f)
            
            return update_info
        
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
    
    return None

def get_update_status():
    """Get cached update status without making new API call"""
    try:
        if os.path.exists(UPDATE_CHECK_CACHE):
            with open(UPDATE_CHECK_CACHE, 'r') as f:
                cache = json.load(f)
                return cache.get('update_info')
    except:
        pass
    
    return {
        'current_version': get_current_version(),
        'latest_version': 'Unknown',
        'update_available': False,
        'repo': get_github_repo()
    }

def apply_update(download_url):
    """
    Download and apply update
    NOTE: This is a simplified version. In production, you'd want:
    - Backup current version
    - Download to temp directory
    - Extract files
    - Replace current files
    - Restart application
    
    For Replit, updates are better handled through git pull
    """
    # For Replit environment, suggest using git pull instead
    return {
        'success': False,
        'message': 'For Replit, please use "git pull" to update, or re-import from GitHub'
    }
