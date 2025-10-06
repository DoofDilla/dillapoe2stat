"""
Session Data Backup Utility
Creates timestamped backups of runs.jsonl and sessions.jsonl

Usage:
    python backup_session_data.py [--backup-dir DIRECTORY]
"""

import shutil
import argparse
from pathlib import Path
from datetime import datetime


def backup_session_data(backup_dir: Path = None):
    """Create timestamped backups of session data files"""
    
    # Default backup directory
    if backup_dir is None:
        backup_dir = Path(__file__).parent / "backups"
    
    backup_dir.mkdir(exist_ok=True)
    
    # Timestamp for backup files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Files to backup
    files_to_backup = [
        Path(__file__).parent / "runs.jsonl",
        Path(__file__).parent / "sessions.jsonl"
    ]
    
    backed_up_files = []
    
    for file_path in files_to_backup:
        if not file_path.exists():
            print(f"⚠️  {file_path.name} not found, skipping...")
            continue
        
        # Create backup filename
        backup_name = f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        # Get file size for reporting
        size_kb = backup_path.stat().st_size / 1024
        
        print(f"✅ Backed up: {file_path.name} → {backup_name} ({size_kb:.1f} KB)")
        backed_up_files.append(backup_path)
    
    if backed_up_files:
        print(f"\n📁 Backup location: {backup_dir.absolute()}")
        print(f"🎯 Total files backed up: {len(backed_up_files)}")
    else:
        print("❌ No files were backed up")
    
    return backed_up_files


def cleanup_old_backups(backup_dir: Path, keep_count: int = 10):
    """Keep only the N most recent backups of each file type"""
    
    if not backup_dir.exists():
        return
    
    # Group backups by file type
    runs_backups = sorted(backup_dir.glob("runs.backup_*"), reverse=True)
    sessions_backups = sorted(backup_dir.glob("sessions.backup_*"), reverse=True)
    
    deleted_count = 0
    
    # Remove old runs backups
    for old_backup in runs_backups[keep_count:]:
        old_backup.unlink()
        print(f"🗑️  Removed old backup: {old_backup.name}")
        deleted_count += 1
    
    # Remove old sessions backups
    for old_backup in sessions_backups[keep_count:]:
        old_backup.unlink()
        print(f"🗑️  Removed old backup: {old_backup.name}")
        deleted_count += 1
    
    if deleted_count > 0:
        print(f"\n🧹 Cleaned up {deleted_count} old backup(s)")


def main():
    parser = argparse.ArgumentParser(description='Backup session data files')
    parser.add_argument('--backup-dir', type=Path, default=None, 
                       help='Backup directory (default: ./backups)')
    parser.add_argument('--keep', type=int, default=10,
                       help='Number of recent backups to keep (default: 10)')
    parser.add_argument('--cleanup-only', action='store_true',
                       help='Only cleanup old backups, do not create new ones')
    
    args = parser.parse_args()
    
    backup_dir = args.backup_dir or Path(__file__).parent / "backups"
    
    print("🔄 SESSION DATA BACKUP UTILITY")
    print("=" * 50)
    
    if not args.cleanup_only:
        backup_session_data(backup_dir)
        print()
    
    if args.keep > 0:
        cleanup_old_backups(backup_dir, args.keep)


if __name__ == "__main__":
    main()
