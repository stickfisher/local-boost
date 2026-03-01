"""
Local Boost - Backup & Recovery System
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path(__file__).parent.parent / 'backups'

def create_backup():
    """Create full backup"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'backup_{timestamp}.zip'
    
    # Backup database
    db_file = Path(__file__).parent.parent / 'data' / 'customers.db'
    config_file = Path(__file__).parent.parent / 'data' / 'ad_config.json'
    
    # Create backup
    import zipfile
    with zipfile.ZipFile(backup_file, 'w') as zf:
        if db_file.exists():
            zf.write(db_file, 'customers.db')
        if config_file.exists():
            zf.write(config_file, 'ad_config.json')
    
    return str(backup_file)

def restore_backup(backup_file):
    """Restore from backup"""
    import zipfile
    
    with zipfile.ZipFile(backup_file, 'r') as zf:
        zf.extractall(Path(__file__).parent.parent / 'data')
    
    return True

def list_backups():
    """List all backups"""
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for f in BACKUP_DIR.glob('backup_*.zip'):
        backups.append({
            'file': str(f),
            'size': f.stat().st_size,
            'created': datetime.fromtimestamp(f.stat().st_ctime).isoformat()
        })
    
    return sorted(backups, key=lambda x: x['created'], reverse=True)

if __name__ == '__main__':
    print("Backup system ready")
    backup = create_backup()
    print(f"Backup created: {backup}")
    print(f"Available: {len(list_backups())}")
