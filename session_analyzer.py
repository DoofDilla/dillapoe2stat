"""
Session Statistics Analyzer
Analyzes all sessions from sessions.jsonl and provides comprehensive statistics
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class SessionStats:
    """Container for session statistics"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: float
    total_value: float
    total_maps: int
    character: str
    maps_per_hour: float
    value_per_hour: float
    avg_map_value: float
    avg_map_time: float


class SessionAnalyzer:
    """Analyzes session data from sessions.jsonl"""
    
    def __init__(self, sessions_file: str = "sessions.jsonl"):
        self.sessions_file = sessions_file
        self.sessions: List[SessionStats] = []
        self._load_sessions()
    
    def _load_sessions(self):
        """Load and parse sessions from jsonl file"""
        if not os.path.exists(self.sessions_file):
            print(f"❌ Sessions file not found: {self.sessions_file}")
            return
        
        # Dictionary to track session starts and ends
        session_data = {}
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = json.loads(line)
                        session_id = event.get('session_id')
                        event_type = event.get('event_type')
                        
                        if event_type == 'session_start':
                            session_data[session_id] = {
                                'start_time': event.get('ts'),
                                'character': event.get('character'),
                                'end_time': None,
                                'duration': 0.0,
                                'total_value': 0.0,
                                'total_maps': 0
                            }
                        elif event_type == 'session_end' and session_id in session_data:
                            session = session_data[session_id]
                            session['end_time'] = event.get('ts')
                            session['duration'] = event.get('session_runtime', 0.0)
                            session['total_value'] = event.get('total_value', 0.0)
                            session['total_maps'] = event.get('total_maps', 0)
                    
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            print(f"❌ Error reading sessions file: {e}")
            return
        
        # Convert to SessionStats objects (only completed sessions)
        for session_id, data in session_data.items():
            if data['end_time'] is not None:  # Only completed sessions
                # Calculate derived statistics
                duration_hours = data['duration'] / 3600 if data['duration'] > 0 else 0
                maps_per_hour = data['total_maps'] / duration_hours if duration_hours > 0 else 0
                value_per_hour = data['total_value'] / duration_hours if duration_hours > 0 else 0
                avg_map_value = data['total_value'] / data['total_maps'] if data['total_maps'] > 0 else 0
                avg_map_time = data['duration'] / data['total_maps'] if data['total_maps'] > 0 else 0
                
                session_stats = SessionStats(
                    session_id=session_id,
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    duration_seconds=data['duration'],
                    total_value=data['total_value'],
                    total_maps=data['total_maps'],
                    character=data['character'],
                    maps_per_hour=maps_per_hour,
                    value_per_hour=value_per_hour,
                    avg_map_value=avg_map_value,
                    avg_map_time=avg_map_time
                )
                self.sessions.append(session_stats)
        
        # Sort by start time
        self.sessions.sort(key=lambda s: s.start_time)
        print(f"✅ Loaded {len(self.sessions)} completed sessions")
    
    def get_total_statistics(self) -> Dict:
        """Calculate overall statistics across all sessions"""
        if not self.sessions:
            return {}
        
        # Basic totals
        total_runtime_seconds = sum(s.duration_seconds for s in self.sessions)
        total_value = sum(s.total_value for s in self.sessions)
        total_maps = sum(s.total_maps for s in self.sessions)
        
        # Convert runtime to human readable
        total_runtime_hours = total_runtime_seconds / 3600
        runtime_td = timedelta(seconds=total_runtime_seconds)
        
        # Average statistics
        sessions_with_maps = [s for s in self.sessions if s.total_maps > 0]
        avg_session_value = statistics.mean([s.total_value for s in self.sessions]) if self.sessions else 0
        avg_session_runtime = statistics.mean([s.duration_seconds for s in self.sessions]) if self.sessions else 0
        avg_session_maps = statistics.mean([s.total_maps for s in self.sessions]) if self.sessions else 0
        
        # Map-specific averages (only sessions with maps)
        avg_map_value = statistics.mean([s.avg_map_value for s in sessions_with_maps]) if sessions_with_maps else 0
        avg_map_time = statistics.mean([s.avg_map_time for s in sessions_with_maps]) if sessions_with_maps else 0
        
        # Efficiency statistics
        maps_per_hour = total_maps / total_runtime_hours if total_runtime_hours > 0 else 0
        value_per_hour = total_value / total_runtime_hours if total_runtime_hours > 0 else 0
        
        # Most productive session
        best_session_by_value = max(self.sessions, key=lambda s: s.total_value) if self.sessions else None
        best_session_by_maps = max(self.sessions, key=lambda s: s.total_maps) if self.sessions else None
        
        # Date range
        first_session = min(self.sessions, key=lambda s: s.start_time) if self.sessions else None
        last_session = max(self.sessions, key=lambda s: s.start_time) if self.sessions else None
        
        return {
            'total_sessions': len(self.sessions),
            'sessions_with_maps': len(sessions_with_maps),
            'total_runtime_seconds': total_runtime_seconds,
            'total_runtime_formatted': str(runtime_td).split('.')[0],  # Remove microseconds
            'total_runtime_hours': total_runtime_hours,
            'total_value': total_value,
            'total_maps': total_maps,
            'avg_session_value': avg_session_value,
            'avg_session_runtime_seconds': avg_session_runtime,
            'avg_session_runtime_formatted': str(timedelta(seconds=avg_session_runtime)).split('.')[0],
            'avg_session_maps': avg_session_maps,
            'avg_map_value': avg_map_value,
            'avg_map_time_seconds': avg_map_time,
            'avg_map_time_formatted': str(timedelta(seconds=avg_map_time)).split('.')[0],
            'maps_per_hour': maps_per_hour,
            'value_per_hour': value_per_hour,
            'best_session_by_value': best_session_by_value,
            'best_session_by_maps': best_session_by_maps,
            'first_session_date': first_session.start_time if first_session else None,
            'last_session_date': last_session.start_time if last_session else None
        }
    
    def get_character_statistics(self) -> Dict[str, Dict]:
        """Get statistics broken down by character"""
        character_stats = {}
        
        # Group sessions by character
        for session in self.sessions:
            char = session.character
            if char not in character_stats:
                character_stats[char] = []
            character_stats[char].append(session)
        
        # Calculate stats for each character
        for char, char_sessions in character_stats.items():
            sessions_with_maps = [s for s in char_sessions if s.total_maps > 0]
            
            total_runtime = sum(s.duration_seconds for s in char_sessions)
            total_value = sum(s.total_value for s in char_sessions)
            total_maps = sum(s.total_maps for s in char_sessions)
            
            runtime_hours = total_runtime / 3600
            
            character_stats[char] = {
                'sessions': len(char_sessions),
                'sessions_with_maps': len(sessions_with_maps),
                'total_runtime_seconds': total_runtime,
                'total_runtime_formatted': str(timedelta(seconds=total_runtime)).split('.')[0],
                'total_value': total_value,
                'total_maps': total_maps,
                'maps_per_hour': total_maps / runtime_hours if runtime_hours > 0 else 0,
                'value_per_hour': total_value / runtime_hours if runtime_hours > 0 else 0,
                'avg_map_value': statistics.mean([s.avg_map_value for s in sessions_with_maps]) if sessions_with_maps else 0,
                'avg_map_time': statistics.mean([s.avg_map_time for s in sessions_with_maps]) if sessions_with_maps else 0
            }
        
        return character_stats
    
    def get_daily_statistics(self) -> Dict[str, Dict]:
        """Get statistics broken down by day"""
        daily_stats = {}
        
        for session in self.sessions:
            # Extract date from timestamp (ISO format: 2025-09-24T01:06:02)
            date_str = session.start_time.split('T')[0]  # Get YYYY-MM-DD
            
            if date_str not in daily_stats:
                daily_stats[date_str] = []
            daily_stats[date_str].append(session)
        
        # Calculate stats for each day
        for date, day_sessions in daily_stats.items():
            sessions_with_maps = [s for s in day_sessions if s.total_maps > 0]
            
            total_runtime = sum(s.duration_seconds for s in day_sessions)
            total_value = sum(s.total_value for s in day_sessions)
            total_maps = sum(s.total_maps for s in day_sessions)
            
            runtime_hours = total_runtime / 3600
            
            daily_stats[date] = {
                'sessions': len(day_sessions),
                'sessions_with_maps': len(sessions_with_maps),
                'total_runtime_seconds': total_runtime,
                'total_runtime_formatted': str(timedelta(seconds=total_runtime)).split('.')[0],
                'total_value': total_value,
                'total_maps': total_maps,
                'maps_per_hour': total_maps / runtime_hours if runtime_hours > 0 else 0,
                'value_per_hour': total_value / runtime_hours if runtime_hours > 0 else 0
            }
        
        return daily_stats
    
    def get_top_sessions(self, limit: int = 10, sort_by: str = 'value') -> List[SessionStats]:
        """Get top sessions sorted by various criteria"""
        if sort_by == 'value':
            return sorted(self.sessions, key=lambda s: s.total_value, reverse=True)[:limit]
        elif sort_by == 'maps':
            return sorted(self.sessions, key=lambda s: s.total_maps, reverse=True)[:limit]
        elif sort_by == 'duration':
            return sorted(self.sessions, key=lambda s: s.duration_seconds, reverse=True)[:limit]
        elif sort_by == 'efficiency':
            return sorted(self.sessions, key=lambda s: s.value_per_hour, reverse=True)[:limit]
        else:
            return self.sessions[:limit]
    
    def get_recent_sessions(self, days: int = 7) -> List[SessionStats]:
        """Get sessions from the last N days"""
        if not self.sessions:
            return []
        
        # Get the most recent session date
        last_session = max(self.sessions, key=lambda s: s.start_time)
        last_date = datetime.fromisoformat(last_session.start_time.replace('T', ' '))
        
        # Calculate cutoff date
        cutoff_date = last_date - timedelta(days=days)
        
        recent_sessions = []
        for session in self.sessions:
            session_date = datetime.fromisoformat(session.start_time.replace('T', ' '))
            if session_date >= cutoff_date:
                recent_sessions.append(session)
        
        return sorted(recent_sessions, key=lambda s: s.start_time, reverse=True)


def main():
    """Example usage of the SessionAnalyzer"""
    analyzer = SessionAnalyzer()
    
    if not analyzer.sessions:
        print("No sessions found!")
        return
    
    # Get overall statistics
    stats = analyzer.get_total_statistics()
    
    print("\n" + "="*60)
    print("📊 PATH OF EXILE 2 - SESSION STATISTICS OVERVIEW")
    print("="*60)
    
    print(f"\n🎯 OVERALL STATISTICS")
    print(f"├─ Total Sessions: {stats['total_sessions']:,}")
    print(f"├─ Sessions with Maps: {stats['sessions_with_maps']:,}")
    print(f"├─ Total Runtime: {stats['total_runtime_formatted']}")
    print(f"├─ Total Value: {stats['total_value']:.2f} exalted")
    print(f"└─ Total Maps: {stats['total_maps']:,}")
    
    print(f"\n⚡ EFFICIENCY METRICS")
    print(f"├─ Maps per Hour: {stats['maps_per_hour']:.2f}")
    print(f"├─ Value per Hour: {stats['value_per_hour']:.2f} exalted")
    print(f"├─ Avg Map Value: {stats['avg_map_value']:.2f} exalted")
    print(f"└─ Avg Map Time: {stats['avg_map_time_formatted']}")
    
    print(f"\n📈 SESSION AVERAGES")
    print(f"├─ Avg Session Value: {stats['avg_session_value']:.2f} exalted")
    print(f"├─ Avg Session Runtime: {stats['avg_session_runtime_formatted']}")
    print(f"└─ Avg Maps per Session: {stats['avg_session_maps']:.2f}")
    
    if stats['best_session_by_value']:
        best = stats['best_session_by_value']
        print(f"\n🏆 BEST SESSION (VALUE)")
        print(f"├─ Date: {best.start_time}")
        print(f"├─ Value: {best.total_value:.2f} exalted")
        print(f"├─ Maps: {best.total_maps}")
        print(f"└─ Runtime: {str(timedelta(seconds=best.duration_seconds)).split('.')[0]}")
    
    print(f"\n📅 DATE RANGE")
    print(f"├─ First Session: {stats['first_session_date']}")
    print(f"└─ Last Session: {stats['last_session_date']}")
    
    # Character breakdown
    char_stats = analyzer.get_character_statistics()
    if char_stats:
        print(f"\n👤 CHARACTER BREAKDOWN")
        for char, cstats in char_stats.items():
            print(f"├─ {char}:")
            print(f"│  ├─ Sessions: {cstats['sessions']} (with maps: {cstats['sessions_with_maps']})")
            print(f"│  ├─ Runtime: {cstats['total_runtime_formatted']}")
            print(f"│  ├─ Value: {cstats['total_value']:.2f} exalted")
            print(f"│  ├─ Maps: {cstats['total_maps']}")
            print(f"│  └─ Efficiency: {cstats['maps_per_hour']:.2f} maps/h, {cstats['value_per_hour']:.2f} exalted/h")
    
    # Top sessions
    print(f"\n🌟 TOP 5 SESSIONS BY VALUE")
    top_sessions = analyzer.get_top_sessions(5, 'value')
    for i, session in enumerate(top_sessions, 1):
        runtime_str = str(timedelta(seconds=session.duration_seconds)).split('.')[0]
        print(f"{i}. {session.start_time} | {session.total_value:.2f} exalted | {session.total_maps} maps | {runtime_str}")


if __name__ == "__main__":
    main()