#!/usr/bin/env python3
"""
Runs.jsonl Analyzer - Analyze individual run data structure and extract information
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

class RunsAnalyzer:
    """Analyzes individual runs from runs.jsonl"""
    
    def __init__(self, runs_file: str = "runs.jsonl"):
        self.runs_file = runs_file
        self.runs: List[Dict] = []
        self._load_runs()
    
    def _load_runs(self):
        """Load runs from jsonl file"""
        if not os.path.exists(self.runs_file):
            print(f"❌ Runs file not found: {self.runs_file}")
            return
        
        try:
            with open(self.runs_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        run = json.loads(line)
                        self.runs.append(run)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON decode error on line {line_num}: {e}")
                        
        except Exception as e:
            print(f"❌ Error reading runs file: {e}")
            return
        
        print(f"✅ Loaded {len(self.runs)} runs")
    
    def analyze_data_evolution(self):
        """Analyze how the data structure has evolved over time"""
        print("\n📊 DATA STRUCTURE EVOLUTION ANALYSIS")
        print("="*60)
        
        # Group by date to see changes over time
        by_date = defaultdict(list)
        for run in self.runs:
            date = run.get('ts', '').split('T')[0]
            by_date[date].append(run)
        
        # Analyze field presence over time
        field_evolution = defaultdict(dict)
        
        for date in sorted(by_date.keys()):
            runs_on_date = by_date[date]
            
            # Count field presence
            field_counts = defaultdict(int)
            total_runs = len(runs_on_date)
            
            for run in runs_on_date:
                for field in run.keys():
                    field_counts[field] += 1
            
            field_evolution[date] = {
                'total_runs': total_runs,
                'fields': {field: count/total_runs for field, count in field_counts.items()}
            }
        
        # Find the "cleanest" data blocks
        print("📅 Field presence by date:")
        best_dates = []
        
        for date in sorted(field_evolution.keys())[-10:]:  # Last 10 dates
            data = field_evolution[date]
            print(f"\n{date} ({data['total_runs']} runs):")
            
            # Sort fields by presence percentage
            sorted_fields = sorted(data['fields'].items(), key=lambda x: x[1], reverse=True)
            
            # Count "modern" fields (added later)
            modern_fields = ['session_id', 'gear_rarity', 'map_runtime', 'waystone_tier', 
                           'area_modifiers', 'waystone_attributes', 'modifier_count']
            modern_field_count = sum(1 for field, pct in sorted_fields if field in modern_fields and pct > 0.8)
            
            for field, percentage in sorted_fields:
                if percentage >= 0.8:  # Present in 80%+ of runs
                    color = "🟢" if field in modern_fields else "🔵"
                    print(f"  {color} {field}: {percentage:.1%}")
                elif percentage >= 0.5:
                    print(f"  🟡 {field}: {percentage:.1%}")
                else:
                    print(f"  🔴 {field}: {percentage:.1%}")
            
            # Rate this date's data quality
            if modern_field_count >= 5 and data['total_runs'] >= 5:
                best_dates.append((date, modern_field_count, data['total_runs']))
        
        # Recommend best data blocks
        print(f"\n🏆 BEST DATA BLOCKS (most complete recent data):")
        best_dates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        for i, (date, modern_count, run_count) in enumerate(best_dates[:3], 1):
            print(f"{i}. {date}: {modern_count} modern fields, {run_count} runs")
        
        return best_dates[0][0] if best_dates else None
    
    def analyze_recent_runs(self, limit: int = 20):
        """Analyze the most recent runs in detail"""
        print(f"\n🔍 RECENT RUNS ANALYSIS (Last {limit})")
        print("="*60)
        
        recent_runs = self.runs[-limit:] if len(self.runs) >= limit else self.runs
        
        for i, run in enumerate(recent_runs, 1):
            print(f"\n{i}. Run {run.get('run_id', 'Unknown')[:8]}... ({run.get('ts', 'No timestamp')})")
            
            # Basic info
            character = run.get('character', 'Unknown')
            map_info = run.get('map', {})
            map_name = map_info.get('name', 'Unknown')
            map_level = map_info.get('level', 0)
            
            print(f"   👤 Character: {character}")
            print(f"   🗺️  Map: {map_name} (Level {map_level})")
            
            # Session info
            if 'session_id' in run:
                session_id = run['session_id'][:8] + "..."
                print(f"   📊 Session: {session_id}")
            
            # Gear rarity
            if 'gear_rarity' in run:
                print(f"   ✨ Gear Rarity: {run['gear_rarity']}%")
            
            # Map value and runtime
            map_value = run.get('map_value')
            map_runtime = run.get('map_runtime')
            
            if map_value is not None:
                print(f"   💰 Value: {map_value:.2f} exalted")
            
            if map_runtime is not None:
                minutes = int(map_runtime // 60)
                seconds = int(map_runtime % 60)
                print(f"   ⏱️  Runtime: {minutes}m {seconds}s")
            
            # Items
            added_count = run.get('added_count', 0)
            removed_count = run.get('removed_count', 0)
            print(f"   📦 Items: +{added_count}, -{removed_count}")
            
            # Waystone info (if available)
            waystone_info = map_info.get('waystone_attributes', {})
            if waystone_info.get('hasAttributeInfo'):
                tier = waystone_info.get('tier', 0)
                magic_monsters = waystone_info.get('magic_monsters', 0)
                rare_monsters = waystone_info.get('rare_monsters', 0)
                item_rarity = waystone_info.get('item_rarity', 0)
                
                print(f"   🪄 Waystone: T{tier}, Magic+{magic_monsters}%, Rare+{rare_monsters}%, Rarity+{item_rarity}%")
            
            # Notable items (high value currency)
            added_items = run.get('added', [])
            notable_items = []
            
            for item in added_items:
                name = item.get('name', '')
                stack = item.get('stack', 1)
                
                if any(currency in name.lower() for currency in ['divine', 'exalted', 'perfect exalted']):
                    if stack > 1:
                        notable_items.append(f"{name} x{stack}")
                    else:
                        notable_items.append(name)
                elif 'greater' in name.lower() and 'orb' in name.lower():
                    notable_items.append(name)
            
            if notable_items:
                print(f"   💎 Notable: {', '.join(notable_items[:3])}")
                if len(notable_items) > 3:
                    print(f"        ... and {len(notable_items)-3} more")
    
    def extract_available_fields(self):
        """Extract all available fields and their types from recent runs"""
        print(f"\n📋 AVAILABLE FIELDS ANALYSIS")
        print("="*60)
        
        # Analyze recent runs (last 50 or all if less)
        recent_runs = self.runs[-50:] if len(self.runs) >= 50 else self.runs
        
        field_info = defaultdict(lambda: {'count': 0, 'types': set(), 'examples': []})
        
        def analyze_dict(obj, prefix=""):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                field_info[full_key]['count'] += 1
                field_info[full_key]['types'].add(type(value).__name__)
                
                # Store example (first 3)
                if len(field_info[full_key]['examples']) < 3:
                    if isinstance(value, (str, int, float, bool)):
                        field_info[full_key]['examples'].append(value)
                    elif isinstance(value, list) and value:
                        field_info[full_key]['examples'].append(f"[{len(value)} items]")
                    elif isinstance(value, dict):
                        field_info[full_key]['examples'].append(f"{{dict with {len(value)} keys}}")
                
                # Recurse into nested dicts
                if isinstance(value, dict):
                    analyze_dict(value, full_key)
        
        for run in recent_runs:
            analyze_dict(run)
        
        # Sort by count (most common first)
        sorted_fields = sorted(field_info.items(), key=lambda x: x[1]['count'], reverse=True)
        
        print(f"Fields found in recent {len(recent_runs)} runs:\n")
        
        for field, info in sorted_fields:
            percentage = info['count'] / len(recent_runs) * 100
            types = ', '.join(info['types'])
            examples = info['examples'][:2]  # Show max 2 examples
            
            if percentage >= 80:
                status = "🟢"
            elif percentage >= 50:
                status = "🟡"
            else:
                status = "🔴"
            
            print(f"{status} {field:<35} {percentage:5.1f}% ({types})")
            if examples:
                example_str = ', '.join(str(ex) for ex in examples)
                if len(example_str) > 60:
                    example_str = example_str[:57] + "..."
                print(f"    └─ Examples: {example_str}")
        
        return field_info
    
    def suggest_analysis_possibilities(self):
        """Suggest what kind of analysis we can do with this data"""
        print(f"\n🔮 ANALYSIS POSSIBILITIES")
        print("="*60)
        
        recent_runs = self.runs[-100:] if len(self.runs) >= 100 else self.runs
        
        # Check what analysis we can do
        has_session_id = any('session_id' in run for run in recent_runs)
        has_gear_rarity = any('gear_rarity' in run for run in recent_runs)
        has_map_value = any('map_value' in run for run in recent_runs)
        has_map_runtime = any('map_runtime' in run for run in recent_runs)
        has_waystone_info = any(run.get('map', {}).get('waystone_attributes', {}).get('hasAttributeInfo') for run in recent_runs)
        has_items = any(run.get('added') for run in recent_runs)
        
        print("Based on available data, we can analyze:")
        print()
        
        if has_session_id:
            print("📊 SESSION-BASED ANALYSIS:")
            print("  • Group runs by session")
            print("  • Calculate session efficiency")
            print("  • Track session progression")
            print()
        
        if has_map_value and has_map_runtime:
            print("💰 VALUE & EFFICIENCY ANALYSIS:")
            print("  • Value per minute/hour")
            print("  • Most/least profitable maps")
            print("  • Runtime vs value correlation")
            print()
        
        if has_gear_rarity:
            print("✨ GEAR RARITY IMPACT:")
            print("  • Correlation between gear rarity and loot value")
            print("  • Track gear progression impact")
            print()
        
        if has_waystone_info:
            print("🪄 WAYSTONE MODIFIER ANALYSIS:")
            print("  • Impact of waystone modifiers on loot")
            print("  • Best modifier combinations")
            print("  • Tier vs reward correlation")
            print()
        
        if has_items:
            print("📦 ITEM DROP ANALYSIS:")
            print("  • Most common drops")
            print("  • Currency drop rates")
            print("  • Item rarity distribution")
            print()
        
        print("🗺️  MAP ANALYSIS:")
        print("  • Best/worst maps by value")
        print("  • Map completion times")
        print("  • Map level efficiency")
        print()
        
        print("📈 PROGRESSION TRACKING:")
        print("  • Performance over time")
        print("  • Learning curve analysis")
        print("  • Consistency metrics")


def main():
    """Main analysis function"""
    print("🔍 RUNS.JSONL ANALYZER")
    print("="*50)
    
    analyzer = RunsAnalyzer()
    
    if not analyzer.runs:
        print("No runs data found!")
        return
    
    # 1. Analyze data structure evolution
    best_date = analyzer.analyze_data_evolution()
    
    # 2. Analyze recent runs in detail
    analyzer.analyze_recent_runs(10)
    
    # 3. Extract available fields
    field_info = analyzer.extract_available_fields()
    
    # 4. Suggest analysis possibilities
    analyzer.suggest_analysis_possibilities()
    
    print(f"\n✅ Analysis complete!")
    if best_date:
        print(f"💡 Recommended: Focus on data from {best_date} onwards for most complete information")


if __name__ == "__main__":
    main()