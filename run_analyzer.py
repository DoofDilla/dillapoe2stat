"""
Run Analyzer - Advanced analysis of individual runs from runs.jsonl
Focuses on Waystone modifier impact, map efficiency, and drop patterns
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import statistics


@dataclass
class RunData:
    """Container for processed run data"""
    run_id: str
    session_id: Optional[str]
    timestamp: str
    character: str
    map_name: str
    map_level: int
    map_value: float
    map_runtime: float
    gear_rarity: Optional[int]
    
    # Waystone attributes
    waystone_tier: int
    magic_monsters: int
    rare_monsters: int
    item_rarity: int
    item_quantity: int
    waystone_drop_chance: int
    pack_size: int
    
    # Items
    added_items: List[Dict]
    removed_items: List[Dict]
    added_count: int
    removed_count: int
    
    # Derived metrics
    value_per_minute: float
    runtime_minutes: float


class RunAnalyzer:
    """Advanced analyzer for individual run data"""
    
    def __init__(self, runs_file: str = "runs.jsonl", 
                 currency_display: str = "exalted",
                 divine_rate: float = 400.0):
        self.runs_file = runs_file
        self.currency_display = currency_display.lower()
        self.divine_rate = divine_rate
        self.runs: List[RunData] = []
        self._load_runs()
    
    def _convert_value(self, exalted_value: float) -> float:
        """Convert exalted value to display currency"""
        if self.currency_display == "divine":
            return exalted_value / self.divine_rate
        return exalted_value
    
    def _get_currency_symbol(self) -> str:
        """Get currency symbol for display"""
        return "divine" if self.currency_display == "divine" else "exalted"
    
    def _load_runs(self):
        """Load and process runs from jsonl file"""
        if not os.path.exists(self.runs_file):
            print(f"❌ Runs file not found: {self.runs_file}")
            return
        
        raw_runs = []
        try:
            with open(self.runs_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        run = json.loads(line)
                        raw_runs.append(run)
                    except json.JSONDecodeError as e:
                        if line_num <= 10:  # Only show first 10 errors
                            print(f"⚠️  JSON decode error on line {line_num}: {e}")
                        
        except Exception as e:
            print(f"❌ Error reading runs file: {e}")
            return
        
        # Filter to recent, complete runs (with modern data structure)
        processed_runs = []
        for run in raw_runs:
            # Only process runs with complete modern data
            if not self._is_complete_run(run):
                continue
                
            try:
                processed_run = self._process_run(run)
                if processed_run:
                    processed_runs.append(processed_run)
            except Exception as e:
                # Skip problematic runs silently
                continue
        
        self.runs = processed_runs
        print(f"✅ Loaded {len(self.runs)} complete runs for analysis")
    
    def _is_complete_run(self, run: Dict) -> bool:
        """Check if run has all required modern fields"""
        required_fields = ['run_id', 'ts', 'map', 'map_value', 'map_runtime', 'added', 'removed']
        
        if not all(field in run for field in required_fields):
            return False
        
        # Check for waystone attributes
        map_data = run.get('map', {})
        waystone_attrs = map_data.get('waystone_attributes', {})
        
        if not waystone_attrs.get('hasAttributeInfo', False):
            return False
        
        # Must have valid map value and runtime
        if run.get('map_value') is None or run.get('map_runtime', 0) <= 0:
            return False
        
        return True
    
    def _process_run(self, run: Dict) -> Optional[RunData]:
        """Convert raw run data to processed RunData object"""
        try:
            map_data = run['map']
            waystone_attrs = map_data.get('waystone_attributes', {})
            
            runtime_seconds = run['map_runtime']
            runtime_minutes = runtime_seconds / 60
            map_value = run['map_value'] or 0
            value_per_minute = map_value / runtime_minutes if runtime_minutes > 0 else 0
            
            return RunData(
                run_id=run['run_id'],
                session_id=run.get('session_id'),
                timestamp=run['ts'],
                character=run['character'],
                map_name=map_data['name'],
                map_level=map_data['level'],
                map_value=map_value,
                map_runtime=runtime_seconds,
                gear_rarity=run.get('gear_rarity'),
                
                waystone_tier=waystone_attrs.get('tier', 0),
                magic_monsters=waystone_attrs.get('magic_monsters', 0),
                rare_monsters=waystone_attrs.get('rare_monsters', 0),
                item_rarity=waystone_attrs.get('item_rarity', 0),
                item_quantity=waystone_attrs.get('item_quantity', 0),
                waystone_drop_chance=waystone_attrs.get('waystone_drop_chance', 0),
                pack_size=waystone_attrs.get('pack_size', 0),
                
                added_items=run.get('added', []),
                removed_items=run.get('removed', []),
                added_count=run.get('added_count', 0),
                removed_count=run.get('removed_count', 0),
                
                value_per_minute=value_per_minute,
                runtime_minutes=runtime_minutes
            )
        
        except Exception as e:
            return None
    
    def analyze_waystone_impact(self) -> Dict:
        """Analyze impact of waystone modifiers on map value and efficiency"""
        if not self.runs:
            return {}
        
        print(f"\n🪄 WAYSTONE MODIFIER IMPACT ANALYSIS")
        print("="*60)
        
        # Group runs by modifier ranges for statistical analysis
        modifier_buckets = {
            'item_rarity': [(0, 20), (20, 40), (40, 60), (60, 80), (80, 120)],
            'magic_monsters': [(0, 1), (1, 30), (30, 50), (50, 70), (70, 100)],
            'rare_monsters': [(0, 1), (1, 20), (20, 40), (40, 60), (60, 100)],
            'waystone_drop_chance': [(0, 80), (80, 95), (95, 110), (110, 130), (130, 200)]
        }
        
        results = {}
        currency_symbol = self._get_currency_symbol()
        
        for modifier, buckets in modifier_buckets.items():
            print(f"\n📊 {modifier.replace('_', ' ').title()} Impact:")
            
            bucket_stats = []
            
            for min_val, max_val in buckets:
                # Find runs in this bucket
                bucket_runs = [
                    run for run in self.runs 
                    if min_val <= getattr(run, modifier) < max_val
                ]
                
                if len(bucket_runs) < 3:  # Need minimum sample size
                    continue
                
                # Calculate statistics
                avg_value = statistics.mean([self._convert_value(run.map_value) for run in bucket_runs])
                avg_runtime = statistics.mean([run.runtime_minutes for run in bucket_runs])
                avg_efficiency = statistics.mean([self._convert_value(run.value_per_minute) for run in bucket_runs])
                
                bucket_stats.append({
                    'range': f"{min_val}-{max_val-1}%",
                    'count': len(bucket_runs),
                    'avg_value': avg_value,
                    'avg_runtime': avg_runtime,
                    'avg_efficiency': avg_efficiency,
                    'runs': bucket_runs
                })
                
                # Color code based on efficiency
                if avg_efficiency >= 20:
                    color = "🟢"
                elif avg_efficiency >= 10:
                    color = "🟡"
                else:
                    color = "🔴"
                
                print(f"  {color} {min_val:3d}-{max_val-1:3d}%: "
                      f"{len(bucket_runs):2d} runs, "
                      f"{avg_value:6.1f} {currency_symbol}, "
                      f"{avg_efficiency:5.1f} {currency_symbol}/min")
            
            results[modifier] = bucket_stats
        
        return results
    
    def analyze_map_efficiency(self) -> Dict:
        """Analyze efficiency by map type"""
        print(f"\n🗺️  MAP EFFICIENCY ANALYSIS")
        print("="*60)
        
        # Group by map name
        map_stats = defaultdict(list)
        for run in self.runs:
            map_stats[run.map_name].append(run)
        
        # Calculate statistics for each map
        map_analysis = []
        currency_symbol = self._get_currency_symbol()
        
        for map_name, runs in map_stats.items():
            if len(runs) < 2:  # Need minimum sample size
                continue
            
            avg_value = statistics.mean([self._convert_value(run.map_value) for run in runs])
            avg_runtime = statistics.mean([run.runtime_minutes for run in runs])
            avg_efficiency = statistics.mean([self._convert_value(run.value_per_minute) for run in runs])
            
            # Calculate consistency (lower std dev = more consistent)
            value_std = statistics.stdev([self._convert_value(run.map_value) for run in runs]) if len(runs) > 1 else 0
            
            map_analysis.append({
                'name': map_name,
                'count': len(runs),
                'avg_value': avg_value,
                'avg_runtime': avg_runtime,
                'avg_efficiency': avg_efficiency,
                'value_std': value_std,
                'consistency': 1 / (value_std + 1),  # Higher = more consistent
                'runs': runs
            })
        
        # Sort by efficiency
        map_analysis.sort(key=lambda x: x['avg_efficiency'], reverse=True)
        
        print(f"📈 Top Maps by Efficiency ({currency_symbol}/min):")
        for i, map_data in enumerate(map_analysis[:10], 1):
            consistency_icon = "🎯" if map_data['consistency'] > 0.5 else "📊"
            
            print(f"{i:2d}. {map_data['name']:<20} "
                  f"{map_data['avg_efficiency']:6.1f} {currency_symbol}/min "
                  f"({map_data['count']} runs) "
                  f"{consistency_icon}")
        
        print(f"\n💰 Top Maps by Total Value:")
        map_analysis_by_value = sorted(map_analysis, key=lambda x: x['avg_value'], reverse=True)
        for i, map_data in enumerate(map_analysis_by_value[:10], 1):
            print(f"{i:2d}. {map_data['name']:<20} "
                  f"{map_data['avg_value']:6.1f} {currency_symbol} avg "
                  f"({map_data['avg_runtime']:.1f}min avg)")
        
        return map_analysis
    
    def analyze_drop_patterns(self) -> Dict:
        """Analyze currency and item drop patterns"""
        print(f"\n💎 DROP PATTERN ANALYSIS")
        print("="*60)
        
        # Count currency drops
        currency_drops = Counter()
        valuable_items = Counter()
        
        for run in self.runs:
            for item in run.added_items:
                name = item.get('name', '')
                stack = item.get('stack', 1)
                
                # Count currency
                if 'orb' in name.lower():
                    currency_drops[name] += stack
                
                # Count valuable items
                if any(term in name.lower() for term in ['divine', 'exalted', 'greater', 'perfect']):
                    valuable_items[name] += stack
        
        print("🪙 Most Common Currency Drops:")
        for i, (currency, count) in enumerate(currency_drops.most_common(10), 1):
            avg_per_run = count / len(self.runs)
            print(f"{i:2d}. {currency:<30} {count:4d} total ({avg_per_run:.2f}/run)")
        
        print(f"\n💰 Most Valuable Items:")
        for i, (item, count) in enumerate(valuable_items.most_common(10), 1):
            avg_per_run = count / len(self.runs)
            print(f"{i:2d}. {item:<35} {count:3d} total ({avg_per_run:.2f}/run)")
        
        return {
            'currency_drops': dict(currency_drops),
            'valuable_items': dict(valuable_items)
        }
    
    def find_optimal_strategies(self) -> Dict:
        """Find optimal waystone modifier combinations"""
        print(f"\n🎯 OPTIMAL STRATEGY RECOMMENDATIONS")
        print("="*60)
        
        currency_symbol = self._get_currency_symbol()
        
        # Find highest efficiency runs
        top_runs = sorted(self.runs, key=lambda r: r.value_per_minute, reverse=True)[:20]
        
        print("🏆 Top 10 Most Efficient Runs:")
        for i, run in enumerate(top_runs[:10], 1):
            efficiency = self._convert_value(run.value_per_minute)
            value = self._convert_value(run.map_value)
            
            print(f"{i:2d}. {run.map_name:<15} "
                  f"{efficiency:6.1f} {currency_symbol}/min "
                  f"({value:6.1f} {currency_symbol} in {run.runtime_minutes:.1f}min)")
            print(f"    Modifiers: Magic+{run.magic_monsters}%, Rare+{run.rare_monsters}%, "
                  f"Rarity+{run.item_rarity}%, Drops+{run.waystone_drop_chance}%")
        
        # Analyze common patterns in top runs
        print(f"\n📊 Common Patterns in Top Runs:")
        
        # Average modifiers in top runs vs all runs
        top_20_runs = top_runs[:20]
        
        avg_magic_top = statistics.mean([r.magic_monsters for r in top_20_runs])
        avg_magic_all = statistics.mean([r.magic_monsters for r in self.runs])
        
        avg_rare_top = statistics.mean([r.rare_monsters for r in top_20_runs])
        avg_rare_all = statistics.mean([r.rare_monsters for r in self.runs])
        
        avg_rarity_top = statistics.mean([r.item_rarity for r in top_20_runs])
        avg_rarity_all = statistics.mean([r.item_rarity for r in self.runs])
        
        avg_drops_top = statistics.mean([r.waystone_drop_chance for r in top_20_runs])
        avg_drops_all = statistics.mean([r.waystone_drop_chance for r in self.runs])
        
        print(f"Magic Monsters:      Top 20 avg: {avg_magic_top:5.1f}%  vs  All runs: {avg_magic_all:5.1f}%")
        print(f"Rare Monsters:       Top 20 avg: {avg_rare_top:5.1f}%  vs  All runs: {avg_rare_all:5.1f}%")
        print(f"Item Rarity:         Top 20 avg: {avg_rarity_top:5.1f}%  vs  All runs: {avg_rarity_all:5.1f}%")
        print(f"Waystone Drop:       Top 20 avg: {avg_drops_top:5.1f}%  vs  All runs: {avg_drops_all:5.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if avg_rarity_top > avg_rarity_all + 10:
            print(f"🎯 Prioritize HIGH Item Rarity waystones ({avg_rarity_top:.0f}%+ is optimal)")
        
        if avg_magic_top > avg_magic_all + 10:
            print(f"🎯 Magic Monster bonus is valuable ({avg_magic_top:.0f}%+ recommended)")
        
        if avg_rare_top > avg_rare_all + 10:
            print(f"🎯 Rare Monster bonus shows good returns ({avg_rare_top:.0f}%+ recommended)")
        
        if avg_drops_top > avg_drops_all + 10:
            print(f"🎯 Waystone Drop Chance pays off ({avg_drops_top:.0f}%+ recommended)")
        
        return {
            'top_runs': top_runs[:10],
            'avg_modifiers_top': {
                'magic_monsters': avg_magic_top,
                'rare_monsters': avg_rare_top,
                'item_rarity': avg_rarity_top,
                'waystone_drop_chance': avg_drops_top
            },
            'avg_modifiers_all': {
                'magic_monsters': avg_magic_all,
                'rare_monsters': avg_rare_all,
                'item_rarity': avg_rarity_all,
                'waystone_drop_chance': avg_drops_all
            }
        }
    
    def get_summary_stats(self) -> Dict:
        """Get overall summary statistics"""
        if not self.runs:
            return {}
        
        currency_symbol = self._get_currency_symbol()
        
        total_value = sum(self._convert_value(run.map_value) for run in self.runs)
        total_runtime = sum(run.runtime_minutes for run in self.runs)
        avg_efficiency = statistics.mean([self._convert_value(run.value_per_minute) for run in self.runs])
        
        return {
            'total_runs': len(self.runs),
            'total_value': total_value,
            'total_runtime_minutes': total_runtime,
            'total_runtime_formatted': f"{int(total_runtime//60)}h {int(total_runtime%60)}m",
            'avg_efficiency': avg_efficiency,
            'currency_symbol': currency_symbol,
            'date_range': {
                'first': min(run.timestamp for run in self.runs).split('T')[0],
                'last': max(run.timestamp for run in self.runs).split('T')[0]
            }
        }


def main():
    """Example usage of the RunAnalyzer"""
    print("🔬 ADVANCED RUN ANALYSIS")
    print("="*50)
    
    # You can configure currency display here
    # analyzer = RunAnalyzer(currency_display="divine", divine_rate=400.0)
    analyzer = RunAnalyzer(currency_display="exalted")
    
    if not analyzer.runs:
        print("No complete runs found for analysis!")
        return
    
    # Display summary
    summary = analyzer.get_summary_stats()
    print(f"📊 Analyzing {summary['total_runs']} runs from {summary['date_range']['first']} to {summary['date_range']['last']}")
    print(f"💰 Total Value: {summary['total_value']:.1f} {summary['currency_symbol']}")
    print(f"⏱️  Total Runtime: {summary['total_runtime_formatted']}")
    print(f"⚡ Average Efficiency: {summary['avg_efficiency']:.1f} {summary['currency_symbol']}/min")
    
    # Run all analyses
    analyzer.analyze_waystone_impact()
    analyzer.analyze_map_efficiency()
    analyzer.analyze_drop_patterns()
    analyzer.find_optimal_strategies()
    
    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    main()