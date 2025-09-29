"""
Session Statistics Display Module
Provides colored and formatted output for session statistics
"""

from typing import Dict, List
from datetime import timedelta
from session_analyzer import SessionAnalyzer, SessionStats


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GOLD = '\033[93m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SessionStatsDisplay:
    """Handles formatted display of session statistics"""
    
    def __init__(self, analyzer: SessionAnalyzer):
        self.analyzer = analyzer
    
    def display_overview(self):
        """Display comprehensive session statistics overview"""
        if not self.analyzer.sessions:
            print(f"{Colors.RED}❌ No sessions found!{Colors.END}")
            return
        
        stats = self.analyzer.get_total_statistics()
        
        # Header
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}📊 PATH OF EXILE 2 - SESSION STATISTICS OVERVIEW{Colors.END}")
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
        
        # Overall Statistics
        self._display_overall_stats(stats)
        
        # Efficiency Metrics
        self._display_efficiency_stats(stats)
        
        # Session Averages
        self._display_averages(stats)
        
        # Best Session
        self._display_best_session(stats)
        
        # Date Range
        self._display_date_range(stats)
        
        # Character Breakdown
        self._display_character_breakdown()
        
        # Top Sessions
        self._display_top_sessions()
        
        # Recent Activity
        self._display_recent_activity()
        
        print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    def _display_overall_stats(self, stats: Dict):
        """Display overall statistics section"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 OVERALL STATISTICS{Colors.END}")
        
        # Format large numbers with thousand separators
        sessions_color = Colors.GREEN if stats['total_sessions'] >= 10 else Colors.YELLOW
        maps_color = Colors.GREEN if stats['total_maps'] >= 50 else Colors.YELLOW
        value_color = Colors.GOLD if stats['total_value'] >= 1000 else Colors.GREEN if stats['total_value'] >= 100 else Colors.YELLOW
        
        print(f"├─ Total Sessions: {sessions_color}{stats['total_sessions']:,}{Colors.END}")
        print(f"├─ Sessions with Maps: {Colors.GREEN}{stats['sessions_with_maps']:,}{Colors.END}")
        print(f"├─ Total Runtime: {Colors.CYAN}{stats['total_runtime_formatted']}{Colors.END}")
        print(f"├─ Total Value: {value_color}{stats['total_value']:.2f} {stats['currency_symbol']}{Colors.END}")
        print(f"└─ Total Maps: {maps_color}{stats['total_maps']:,}{Colors.END}")
    
    def _display_efficiency_stats(self, stats: Dict):
        """Display efficiency metrics section"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}⚡ EFFICIENCY METRICS{Colors.END}")
        
        # Color code efficiency based on performance
        maps_per_hour_color = Colors.GREEN if stats['maps_per_hour'] >= 2.0 else Colors.YELLOW if stats['maps_per_hour'] >= 1.0 else Colors.RED
        value_per_hour_color = Colors.GOLD if stats['value_per_hour'] >= 100 else Colors.GREEN if stats['value_per_hour'] >= 50 else Colors.YELLOW
        
        print(f"├─ Maps per Hour: {maps_per_hour_color}{stats['maps_per_hour']:.2f}{Colors.END}")
        print(f"├─ Value per Hour: {value_per_hour_color}{stats['value_per_hour']:.2f} {stats['currency_symbol']}{Colors.END}")
        print(f"├─ Avg Map Value: {Colors.GOLD}{stats['avg_map_value']:.2f} {stats['currency_symbol']}{Colors.END}")
        print(f"└─ Avg Map Time: {Colors.CYAN}{stats['avg_map_time_formatted']}{Colors.END}")
    
    def _display_averages(self, stats: Dict):
        """Display session averages section"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}📈 SESSION AVERAGES{Colors.END}")
        
        print(f"├─ Avg Session Value: {Colors.GOLD}{stats['avg_session_value']:.2f} {stats['currency_symbol']}{Colors.END}")
        print(f"├─ Avg Session Runtime: {Colors.CYAN}{stats['avg_session_runtime_formatted']}{Colors.END}")
        print(f"└─ Avg Maps per Session: {Colors.GREEN}{stats['avg_session_maps']:.2f}{Colors.END}")
    
    def _display_best_session(self, stats: Dict):
        """Display best session information"""
        if not stats.get('best_session_by_value'):
            return
        
        best = stats['best_session_by_value']
        best_maps = stats['best_session_by_maps']
        
        print(f"\n{Colors.BOLD}{Colors.GOLD}🏆 RECORD SESSIONS{Colors.END}")
        
        # Best by value
        runtime_str = str(timedelta(seconds=best.duration_seconds)).split('.')[0]
        print(f"├─ {Colors.YELLOW}Best Value:{Colors.END}")
        print(f"│  ├─ Date: {Colors.CYAN}{best.start_time.split('T')[0]}{Colors.END}")
        print(f"│  ├─ Value: {Colors.GOLD}{self.analyzer._convert_value(best.total_value):.2f} {stats['currency_symbol']}{Colors.END}")
        print(f"│  ├─ Maps: {Colors.GREEN}{best.total_maps}{Colors.END}")
        print(f"│  └─ Runtime: {Colors.CYAN}{runtime_str}{Colors.END}")
        
        # Best by maps (if different)
        if best_maps.session_id != best.session_id:
            runtime_str_maps = str(timedelta(seconds=best_maps.duration_seconds)).split('.')[0]
            print(f"└─ {Colors.YELLOW}Most Maps:{Colors.END}")
            print(f"   ├─ Date: {Colors.CYAN}{best_maps.start_time.split('T')[0]}{Colors.END}")
            print(f"   ├─ Maps: {Colors.GREEN}{best_maps.total_maps}{Colors.END}")
            print(f"   ├─ Value: {Colors.GOLD}{self.analyzer._convert_value(best_maps.total_value):.2f} {stats['currency_symbol']}{Colors.END}")
            print(f"   └─ Runtime: {Colors.CYAN}{runtime_str_maps}{Colors.END}")
        else:
            print(f"└─ {Colors.GRAY}(Same session holds both records){Colors.END}")
    
    def _display_date_range(self, stats: Dict):
        """Display date range information"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}📅 DATE RANGE{Colors.END}")
        
        first_date = stats['first_session_date'].split('T')[0] if stats.get('first_session_date') else 'Unknown'
        last_date = stats['last_session_date'].split('T')[0] if stats.get('last_session_date') else 'Unknown'
        
        print(f"├─ First Session: {Colors.CYAN}{first_date}{Colors.END}")
        print(f"└─ Last Session: {Colors.CYAN}{last_date}{Colors.END}")
    
    def _display_character_breakdown(self):
        """Display character-specific statistics"""
        char_stats = self.analyzer.get_character_statistics()
        if not char_stats:
            return
        
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}👤 CHARACTER BREAKDOWN{Colors.END}")
        
        for i, (char, cstats) in enumerate(char_stats.items()):
            is_last = i == len(char_stats) - 1
            prefix = "└─" if is_last else "├─"
            sub_prefix = "   " if is_last else "│  "
            
            # Color code character performance
            value_color = Colors.GOLD if cstats['total_value'] >= 500 else Colors.GREEN if cstats['total_value'] >= 100 else Colors.YELLOW
            efficiency_color = Colors.GREEN if cstats['maps_per_hour'] >= 2.0 else Colors.YELLOW
            
            print(f"{prefix} {Colors.BOLD}{Colors.WHITE}{char}:{Colors.END}")
            print(f"{sub_prefix}├─ Sessions: {Colors.CYAN}{cstats['sessions']}{Colors.END} (with maps: {Colors.GREEN}{cstats['sessions_with_maps']}{Colors.END})")
            print(f"{sub_prefix}├─ Runtime: {Colors.CYAN}{cstats['total_runtime_formatted']}{Colors.END}")
            print(f"{sub_prefix}├─ Value: {value_color}{cstats['total_value']:.2f} {self.analyzer._get_currency_symbol()}{Colors.END}")
            print(f"{sub_prefix}├─ Maps: {Colors.GREEN}{cstats['total_maps']}{Colors.END}")
            print(f"{sub_prefix}└─ Efficiency: {efficiency_color}{cstats['maps_per_hour']:.2f} maps/h{Colors.END}, {Colors.GOLD}{cstats['value_per_hour']:.2f} {self.analyzer._get_currency_symbol()}/h{Colors.END}")
    
    def _display_top_sessions(self):
        """Display top sessions by various criteria"""
        print(f"\n{Colors.BOLD}{Colors.GOLD}🌟 TOP 5 SESSIONS{Colors.END}")
        
        # Top by value
        print(f"├─ {Colors.YELLOW}By Value:{Colors.END}")
        top_value = self.analyzer.get_top_sessions(5, 'value')
        for i, session in enumerate(top_value):
            runtime_str = str(timedelta(seconds=session.duration_seconds)).split('.')[0]
            date_str = session.start_time.split('T')[0]
            is_last = i == len(top_value) - 1
            
            if session.total_value >= 500:
                value_color = Colors.GOLD
            elif session.total_value >= 100:
                value_color = Colors.GREEN
            else:
                value_color = Colors.YELLOW
            
            print(f"│  {i+1}. {Colors.CYAN}{date_str}{Colors.END} | {value_color}{self.analyzer._convert_value(session.total_value):.2f} {self.analyzer._get_currency_symbol()}{Colors.END} | {Colors.GREEN}{session.total_maps} maps{Colors.END} | {Colors.GRAY}{runtime_str}{Colors.END}")
        
        # Top by maps
        print(f"└─ {Colors.YELLOW}By Maps:{Colors.END}")
        top_maps = self.analyzer.get_top_sessions(5, 'maps')
        for i, session in enumerate(top_maps):
            runtime_str = str(timedelta(seconds=session.duration_seconds)).split('.')[0]
            date_str = session.start_time.split('T')[0]
            
            maps_color = Colors.GREEN if session.total_maps >= 5 else Colors.YELLOW
            
            print(f"   {i+1}. {Colors.CYAN}{date_str}{Colors.END} | {maps_color}{session.total_maps} maps{Colors.END} | {Colors.GOLD}{self.analyzer._convert_value(session.total_value):.2f} {self.analyzer._get_currency_symbol()}{Colors.END} | {Colors.GRAY}{runtime_str}{Colors.END}")
    
    def _display_recent_activity(self):
        """Display recent activity (last 7 days)"""
        recent_sessions = self.analyzer.get_recent_sessions(7)
        if not recent_sessions:
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 RECENT ACTIVITY (Last 7 Days){Colors.END}")
        
        # Calculate totals for recent period
        total_recent_runtime = sum(s.duration_seconds for s in recent_sessions)
        total_recent_value = sum(s.total_value for s in recent_sessions)
        total_recent_maps = sum(s.total_maps for s in recent_sessions)
        
        recent_runtime_str = str(timedelta(seconds=total_recent_runtime)).split('.')[0]
        
        print(f"├─ Sessions: {Colors.CYAN}{len(recent_sessions)}{Colors.END}")
        print(f"├─ Runtime: {Colors.CYAN}{recent_runtime_str}{Colors.END}")
        print(f"├─ Value: {Colors.GOLD}{self.analyzer._convert_value(total_recent_value):.2f} {self.analyzer._get_currency_symbol()}{Colors.END}")
        print(f"└─ Maps: {Colors.GREEN}{total_recent_maps}{Colors.END}")
    
    def display_daily_breakdown(self, days: int = 7):
        """Display daily breakdown for the last N days"""
        daily_stats = self.analyzer.get_daily_statistics()
        
        if not daily_stats:
            print(f"{Colors.RED}❌ No daily data available{Colors.END}")
            return
        
        # Get recent days
        recent_days = sorted(daily_stats.keys(), reverse=True)[:days]
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📅 DAILY BREAKDOWN (Last {days} Days){Colors.END}")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        
        for day in recent_days:
            stats = daily_stats[day]
            
            # Color code based on activity level
            if stats['total_value'] >= 200:
                day_color = Colors.GOLD
            elif stats['total_value'] >= 50:
                day_color = Colors.GREEN
            elif stats['total_maps'] > 0:
                day_color = Colors.YELLOW
            else:
                day_color = Colors.GRAY
            
            print(f"{day_color}{day}{Colors.END} | "
                  f"{Colors.CYAN}{stats['sessions']} sessions{Colors.END} | "
                  f"{Colors.GREEN}{stats['total_maps']} maps{Colors.END} | "
                  f"{Colors.GOLD}{stats['total_value']:.2f} {self.analyzer._get_currency_symbol()}{Colors.END} | "
                  f"{Colors.GRAY}{stats['total_runtime_formatted']}{Colors.END}")


def main():
    """Enhanced main function with colored output"""
    print(f"{Colors.BOLD}{Colors.WHITE}Loading session data...{Colors.END}")
    
    # Configure currency display here
    # analyzer = SessionAnalyzer(currency_display="divine", divine_rate=400.0)  # For Divine display
    analyzer = SessionAnalyzer()  # Default: Exalted display
    display = SessionStatsDisplay(analyzer)
    
    # Display comprehensive overview
    display.display_overview()
    
    # Display daily breakdown
    display.display_daily_breakdown(10)
    
    print(f"\n{Colors.GREEN}✅ Analysis complete!{Colors.END}")


if __name__ == "__main__":
    main()