"""
Runs.jsonl Data Upgrade Tool
============================
Upgrades existing runs.jsonl entries to the enhanced format with individual item values.

This tool:
1. Creates a backup of the original runs.jsonl
2. Processes each run to calculate individual item values using the existing pricing system
3. Upgrades the format to include detailed value information per item
4. Maintains backwards compatibility

Usage:
    python upgrade_runs_data.py [--dry-run] [--backup-suffix=.backup]
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import argparse
import sys

def backup_runs_file(runs_file: Path, backup_suffix: str = None) -> Path:
    """Create a backup of the runs.jsonl file"""
    if backup_suffix is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_suffix = f".backup_{timestamp}"
    
    backup_file = runs_file.with_suffix(runs_file.suffix + backup_suffix)
    shutil.copy2(runs_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def is_enhanced_format(run_data: Dict) -> bool:
    """Check if a run is already in enhanced format"""
    return run_data.get('format_version') == '2.0' or run_data.get('enhanced_items') == True

def upgrade_items_with_values(items: List[Dict]) -> List[Dict]:
    """Upgrade item list to include individual values using the pricing system"""
    if not items:
        return items
    
    try:
        from price_check_poe2 import valuate_items_raw
        
        # Convert old format to pricing system format
        pricing_items = []
        for item in items:
            pricing_item = {
                "name": item.get("name", "Unknown"),
                "stackSize": item.get("stack", 1)
            }
            pricing_items.append(pricing_item)
        
        # Get detailed value information
        valued_items, _ = valuate_items_raw(pricing_items)
        
        # Convert to enhanced format
        enhanced_items = []
        for item_data in valued_items:
            enhanced_item = {
                "name": item_data["name"],
                "stack": item_data["qty"],
                "category": item_data.get("category", "Unknown")
            }
            
            # Add value information if available
            if item_data.get("ex_each") is not None:
                enhanced_item["value_each_exalted"] = round(item_data["ex_each"], 6)
                enhanced_item["total_value_exalted"] = round(item_data["ex_total"], 6)
            
            if item_data.get("chaos_each") is not None:
                enhanced_item["value_each_chaos"] = round(item_data["chaos_each"], 2)
                enhanced_item["total_value_chaos"] = round(item_data["chaos_total"], 2)
            
            enhanced_items.append(enhanced_item)
        
        return enhanced_items
        
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate values for items, keeping original format: {e}")
        return items

def upgrade_run(run_data: Dict) -> Dict:
    """Upgrade a single run to enhanced format"""
    if is_enhanced_format(run_data):
        return run_data  # Already upgraded
    
    # Create a copy to avoid modifying original
    upgraded_run = run_data.copy()
    
    # Upgrade added items
    if 'added' in upgraded_run:
        upgraded_run['added'] = upgrade_items_with_values(upgraded_run['added'])
    
    # Upgrade removed items
    if 'removed' in upgraded_run:
        upgraded_run['removed'] = upgrade_items_with_values(upgraded_run['removed'])
    
    # Add format metadata
    upgraded_run['format_version'] = '2.0'
    upgraded_run['enhanced_items'] = True
    upgraded_run['upgraded_at'] = datetime.now().isoformat(timespec="seconds")
    
    return upgraded_run

def upgrade_runs_file(runs_file: Path, dry_run: bool = False) -> Dict[str, int]:
    """Upgrade an entire runs.jsonl file"""
    if not runs_file.exists():
        raise FileNotFoundError(f"Runs file not found: {runs_file}")
    
    stats = {
        'total_runs': 0,
        'upgraded_runs': 0,
        'already_enhanced': 0,
        'failed_runs': 0
    }
    
    # Read all runs
    runs = []
    print(f"📖 Reading runs from {runs_file}...")
    
    with open(runs_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                run_data = json.loads(line.strip())
                runs.append(run_data)
                stats['total_runs'] += 1
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Skipping invalid JSON on line {line_num}: {e}")
                stats['failed_runs'] += 1
    
    print(f"📊 Found {stats['total_runs']} runs to process")
    
    # Process each run
    upgraded_runs = []
    for i, run_data in enumerate(runs):
        try:
            if is_enhanced_format(run_data):
                upgraded_runs.append(run_data)
                stats['already_enhanced'] += 1
            else:
                print(f"🔄 Upgrading run {i+1}/{len(runs)}: {run_data.get('run_id', 'unknown')[:8]}...")
                upgraded_run = upgrade_run(run_data)
                upgraded_runs.append(upgraded_run)
                stats['upgraded_runs'] += 1
                
                # Show progress every 10 runs
                if (i + 1) % 10 == 0:
                    print(f"   Progress: {i+1}/{len(runs)} runs processed")
                    
        except Exception as e:
            print(f"❌ Failed to upgrade run {i+1}: {e}")
            upgraded_runs.append(run_data)  # Keep original on failure
            stats['failed_runs'] += 1
    
    # Write upgraded data
    if not dry_run:
        print(f"💾 Writing upgraded data to {runs_file}...")
        with open(runs_file, 'w', encoding='utf-8') as f:
            for run_data in upgraded_runs:
                f.write(json.dumps(run_data, ensure_ascii=False) + '\n')
        print(f"✅ Successfully upgraded {runs_file}")
    else:
        print(f"🔍 DRY RUN: Would upgrade {stats['upgraded_runs']} runs")
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='Upgrade runs.jsonl to enhanced format with item values')
    parser.add_argument('--runs-file', default='runs.jsonl', help='Path to runs.jsonl file (default: runs.jsonl)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--backup-suffix', default=None, help='Backup file suffix (default: .backup_TIMESTAMP)')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup (not recommended)')
    
    args = parser.parse_args()
    
    runs_file = Path(args.runs_file)
    
    print("🔧 RUNS.JSONL DATA UPGRADE TOOL")
    print("=" * 50)
    print(f"📁 Target file: {runs_file}")
    print(f"🔍 Dry run: {'Yes' if args.dry_run else 'No'}")
    
    if not runs_file.exists():
        print(f"❌ Error: Runs file not found: {runs_file}")
        sys.exit(1)
    
    try:
        # Create backup unless explicitly disabled
        if not args.no_backup and not args.dry_run:
            backup_file = backup_runs_file(runs_file, args.backup_suffix)
        
        # Upgrade the file
        stats = upgrade_runs_file(runs_file, args.dry_run)
        
        # Show results
        print("\n📈 UPGRADE RESULTS")
        print("=" * 30)
        print(f"📊 Total runs processed: {stats['total_runs']}")
        print(f"✅ Runs upgraded: {stats['upgraded_runs']}")
        print(f"🔄 Already enhanced: {stats['already_enhanced']}")
        print(f"❌ Failed upgrades: {stats['failed_runs']}")
        
        if stats['upgraded_runs'] > 0:
            print(f"\n🎉 Successfully upgraded {stats['upgraded_runs']} runs!")
            print("💡 New runs will now include:")
            print("   • Individual item values (exalted & chaos)")
            print("   • Item categories")
            print("   • Enhanced analysis capabilities")
        
        if stats['already_enhanced'] > 0:
            print(f"\n✅ {stats['already_enhanced']} runs were already in enhanced format")
            
        if not args.dry_run and not args.no_backup:
            print(f"\n💾 Original data backed up to: {backup_file}")
            
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()