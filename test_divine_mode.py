#!/usr/bin/env python3
"""
Quick test to demonstrate Divine Orb display mode
"""

from session_analyzer import SessionAnalyzer
from session_display import SessionStatsDisplay, Colors

def main():
    print(f"{Colors.BOLD}{Colors.WHITE}🧪 Testing Divine Orb Display Mode{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    # Test Divine mode with 1 Divine = 400 Exalted
    print(f"\n{Colors.MAGENTA}💎 DIVINE MODE (1 Divine = 400 Exalted){Colors.END}")
    analyzer = SessionAnalyzer(currency_display="divine", divine_rate=400.0)
    
    if not analyzer.sessions:
        print(f"{Colors.RED}❌ No sessions found{Colors.END}")
        return
    
    # Get and display basic stats
    stats = analyzer.get_total_statistics()
    
    print(f"\n{Colors.YELLOW}📊 Quick Stats Comparison:{Colors.END}")
    print(f"├─ Total Value: {Colors.GOLD}{stats['total_value']:.2f} {stats['currency_symbol']}{Colors.END}")
    print(f"├─ Avg Map Value: {Colors.GOLD}{stats['avg_map_value']:.3f} {stats['currency_symbol']}{Colors.END}")
    print(f"├─ Value per Hour: {Colors.GOLD}{stats['value_per_hour']:.2f} {stats['currency_symbol']}{Colors.END}")
    print(f"└─ Conversion Rate: {Colors.GRAY}1 divine = {stats['divine_rate']} exalted{Colors.END}")
    
    # Show top sessions in Divine
    print(f"\n{Colors.YELLOW}🏆 Top 3 Sessions (Divine):{Colors.END}")
    top_sessions = analyzer.get_top_sessions(3, 'value')
    for i, session in enumerate(top_sessions, 1):
        date = session.start_time.split('T')[0]
        converted_value = analyzer._convert_value(session.total_value)
        print(f"  {i}. {date}: {Colors.GOLD}{converted_value:.3f} divine{Colors.END} ({session.total_maps} maps)")
    
    # Show what the same values would be in Exalted
    print(f"\n{Colors.GRAY}💰 For comparison - same values in Exalted:{Colors.END}")
    analyzer_ex = SessionAnalyzer(currency_display="exalted")
    stats_ex = analyzer_ex.get_total_statistics()
    print(f"├─ Total Value: {stats_ex['total_value']:.2f} exalted")
    print(f"├─ Avg Map Value: {stats_ex['avg_map_value']:.2f} exalted")
    print(f"└─ Value per Hour: {stats_ex['value_per_hour']:.2f} exalted")

if __name__ == "__main__":
    main()