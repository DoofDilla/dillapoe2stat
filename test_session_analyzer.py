#!/usr/bin/env python3
"""
Test Script for Session Analyzer
Demonstrates the functionality of the session analysis modules
"""

import os
import sys
from session_analyzer import SessionAnalyzer
from session_display import SessionStatsDisplay, Colors


def test_basic_functionality():
    """Test basic analyzer functionality"""
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 Testing Basic Functionality{Colors.END}")
    
    # Check if sessions.jsonl exists
    if not os.path.exists("sessions.jsonl"):
        print(f"{Colors.RED}❌ sessions.jsonl not found in current directory{Colors.END}")
        print(f"{Colors.YELLOW}💡 Make sure to run this script from the directory containing sessions.jsonl{Colors.END}")
        return False
    
    # Initialize analyzer
    analyzer = SessionAnalyzer()
    
    if not analyzer.sessions:
        print(f"{Colors.RED}❌ No sessions loaded{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✅ Successfully loaded {len(analyzer.sessions)} sessions{Colors.END}")
    
    # Test statistics calculation
    try:
        stats = analyzer.get_total_statistics()
        print(f"{Colors.GREEN}✅ Statistics calculation successful{Colors.END}")
        print(f"   📊 {stats['total_sessions']} sessions, {stats['total_maps']} maps, {stats['total_value']:.2f} {stats['currency_symbol']}")
    except Exception as e:
        print(f"{Colors.RED}❌ Statistics calculation failed: {e}{Colors.END}")
        return False
    
    # Test character breakdown
    try:
        char_stats = analyzer.get_character_statistics()
        print(f"{Colors.GREEN}✅ Character breakdown successful{Colors.END}")
        print(f"   👤 {len(char_stats)} characters found")
    except Exception as e:
        print(f"{Colors.RED}❌ Character breakdown failed: {e}{Colors.END}")
        return False
    
    # Test daily statistics
    try:
        daily_stats = analyzer.get_daily_statistics()
        print(f"{Colors.GREEN}✅ Daily statistics successful{Colors.END}")
        print(f"   📅 {len(daily_stats)} days with activity")
    except Exception as e:
        print(f"{Colors.RED}❌ Daily statistics failed: {e}{Colors.END}")
        return False
    
    return True


def demo_different_views():
    """Demonstrate different analysis views"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}🎭 Demo: Different Analysis Views{Colors.END}")
    
    analyzer = SessionAnalyzer()
    
    if not analyzer.sessions:
        print(f"{Colors.RED}❌ No data to demonstrate{Colors.END}")
        return
    
    # Top sessions by value
    print(f"\n{Colors.YELLOW}🏆 Top 3 Sessions by Value:{Colors.END}")
    top_value = analyzer.get_top_sessions(3, 'value')
    for i, session in enumerate(top_value, 1):
        date = session.start_time.split('T')[0]
        print(f"  {i}. {date}: {Colors.GOLD}{analyzer._convert_value(session.total_value):.2f} {analyzer._get_currency_symbol()}{Colors.END} ({session.total_maps} maps)")
    
    # Top sessions by maps
    print(f"\n{Colors.YELLOW}🗺️  Top 3 Sessions by Maps:{Colors.END}")
    top_maps = analyzer.get_top_sessions(3, 'maps')
    for i, session in enumerate(top_maps, 1):
        date = session.start_time.split('T')[0]
        print(f"  {i}. {date}: {Colors.GREEN}{session.total_maps} maps{Colors.END} ({analyzer._convert_value(session.total_value):.2f} {analyzer._get_currency_symbol()})")
    
    # Recent activity
    print(f"\n{Colors.YELLOW}📊 Recent Activity (Last 5 Days):{Colors.END}")
    recent = analyzer.get_recent_sessions(5)
    if recent:
        total_value = sum(s.total_value for s in recent)
        total_maps = sum(s.total_maps for s in recent)
        print(f"  Sessions: {len(recent)}, Maps: {total_maps}, Value: {analyzer._convert_value(total_value):.2f} {analyzer._get_currency_symbol()}")
    else:
        print(f"  {Colors.GRAY}No recent activity found{Colors.END}")


def performance_comparison():
    """Show performance comparison between different periods"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}⚔️  Performance Comparison{Colors.END}")
    
    analyzer = SessionAnalyzer()
    
    if len(analyzer.sessions) < 2:
        print(f"{Colors.YELLOW}⚠️  Need at least 2 sessions for comparison{Colors.END}")
        return
    
    # Split sessions into two halves (earlier vs later)
    mid_point = len(analyzer.sessions) // 2
    early_sessions = analyzer.sessions[:mid_point]
    recent_sessions = analyzer.sessions[mid_point:]
    
    def calc_stats(sessions):
        """Calculate basic stats for a session list"""
        if not sessions:
            return {'maps': 0, 'value': 0, 'runtime': 0, 'efficiency': 0}
        
        total_maps = sum(s.total_maps for s in sessions)
        total_value = sum(s.total_value for s in sessions)
        total_runtime = sum(s.duration_seconds for s in sessions)
        
        runtime_hours = total_runtime / 3600 if total_runtime > 0 else 0
        efficiency = total_value / runtime_hours if runtime_hours > 0 else 0
        
        return {
            'sessions': len(sessions),
            'maps': total_maps,
            'value': total_value,
            'runtime': total_runtime,
            'efficiency': efficiency,
            'maps_per_hour': total_maps / runtime_hours if runtime_hours > 0 else 0
        }
    
    early_stats = calc_stats(early_sessions)
    recent_stats = calc_stats(recent_sessions)
    
    print(f"\n{Colors.BLUE}📈 Early Period:{Colors.END} {early_stats['sessions']} sessions")
    print(f"  Maps: {early_stats['maps']}, Value: {analyzer._convert_value(early_stats['value']):.2f} {analyzer._get_currency_symbol()}")
    print(f"  Efficiency: {early_stats['maps_per_hour']:.2f} maps/h, {analyzer._convert_value(early_stats['efficiency']):.2f} {analyzer._get_currency_symbol()}/h")
    
    print(f"\n{Colors.GREEN}📊 Recent Period:{Colors.END} {recent_stats['sessions']} sessions")
    print(f"  Maps: {recent_stats['maps']}, Value: {analyzer._convert_value(recent_stats['value']):.2f} {analyzer._get_currency_symbol()}")
    print(f"  Efficiency: {recent_stats['maps_per_hour']:.2f} maps/h, {analyzer._convert_value(recent_stats['efficiency']):.2f} {analyzer._get_currency_symbol()}/h")
    
    # Calculate improvements
    if early_stats['efficiency'] > 0:
        efficiency_change = ((recent_stats['efficiency'] - early_stats['efficiency']) / early_stats['efficiency']) * 100
        maps_change = ((recent_stats['maps_per_hour'] - early_stats['maps_per_hour']) / early_stats['maps_per_hour']) * 100 if early_stats['maps_per_hour'] > 0 else 0
        
        print(f"\n{Colors.BOLD}🔄 Performance Change:{Colors.END}")
        
        if efficiency_change > 5:
            print(f"  💰 Value Efficiency: {Colors.GREEN}+{efficiency_change:.1f}%{Colors.END} (improved)")
        elif efficiency_change < -5:
            print(f"  💰 Value Efficiency: {Colors.RED}{efficiency_change:.1f}%{Colors.END} (declined)")
        else:
            print(f"  💰 Value Efficiency: {Colors.YELLOW}{efficiency_change:.1f}%{Colors.END} (stable)")
        
        if maps_change > 5:
            print(f"  🗺️  Map Speed: {Colors.GREEN}+{maps_change:.1f}%{Colors.END} (faster)")
        elif maps_change < -5:
            print(f"  🗺️  Map Speed: {Colors.RED}{maps_change:.1f}%{Colors.END} (slower)")
        else:
            print(f"  🗺️  Map Speed: {Colors.YELLOW}{maps_change:.1f}%{Colors.END} (stable)")


def demo_currency_switching():
    """Demonstrate currency switching between exalted and divine"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}💰 Demo: Currency Switching{Colors.END}")
    
    # Show both currency modes
    print(f"\n{Colors.YELLOW}🪙 Exalted Mode (1:1):{Colors.END}")
    analyzer_ex = SessionAnalyzer(currency_display="exalted")
    if analyzer_ex.sessions:
        stats_ex = analyzer_ex.get_total_statistics()
        print(f"  Total Value: {stats_ex['total_value']:.2f} {stats_ex['currency_symbol']}")
        print(f"  Avg Map Value: {stats_ex['avg_map_value']:.2f} {stats_ex['currency_symbol']}")
    
    print(f"\n{Colors.YELLOW}💎 Divine Mode (1:400):{Colors.END}")
    analyzer_div = SessionAnalyzer(currency_display="divine", divine_rate=400.0)
    if analyzer_div.sessions:
        stats_div = analyzer_div.get_total_statistics()
        print(f"  Total Value: {stats_div['total_value']:.2f} {stats_div['currency_symbol']}")
        print(f"  Avg Map Value: {stats_div['avg_map_value']:.2f} {stats_div['currency_symbol']}")
        print(f"  {Colors.GRAY}(Conversion rate: 1 divine = {analyzer_div.divine_rate} exalted){Colors.END}")


def main():
    """Run all tests and demonstrations"""
    print(f"{Colors.BOLD}{Colors.WHITE}🔍 Session Analyzer - Test & Demo Suite{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    # Test basic functionality
    success = test_basic_functionality()
    
    if not success:
        print(f"\n{Colors.RED}❌ Basic tests failed. Cannot proceed with demos.{Colors.END}")
        return 1
    
    # Run demonstrations
    demo_different_views()
    performance_comparison()
    demo_currency_switching()
    
    # Show full analysis
    print(f"\n{Colors.BOLD}{Colors.WHITE}📊 Full Session Analysis{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    try:
        analyzer = SessionAnalyzer()
        display = SessionStatsDisplay(analyzer)
        display.display_overview()
    except Exception as e:
        print(f"{Colors.RED}❌ Full analysis failed: {e}{Colors.END}")
        return 1
    
    print(f"\n{Colors.GREEN}✅ All tests and demos completed successfully!{Colors.END}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)