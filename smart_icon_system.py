"""
Smart Icon System for PoE Stats Tracker
Combines icon caching, color analysis, and emoji mapping
"""

import os
from pathlib import Path
import json
from icon_cache_manager import get_icon_cache_manager
from icon_color_analyzer import get_color_analyzer, get_icon_color_mapper


class SmartIconSystem:
    """Main icon system that combines all components"""
    
    def __init__(self):
        self.cache_manager = get_icon_cache_manager()
        self.color_analyzer = get_color_analyzer()
        self.color_mapper = get_icon_color_mapper()
        
        # Cache for analyzed colors to avoid re-processing
        self.color_cache_file = self.cache_manager.cache_dir / "color_analysis.json"
        self.color_cache = self._load_color_cache()
    
    def _load_color_cache(self):
        """Load cached color analysis results"""
        try:
            if self.color_cache_file.exists():
                with open(self.color_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[ICON] Warning: Could not load color cache: {e}")
        return {}
    
    def _save_color_cache(self):
        """Save color analysis cache"""
        try:
            with open(self.color_cache_file, 'w') as f:
                json.dump(self.color_cache, f, indent=2)
        except Exception as e:
            print(f"[ICON] Warning: Could not save color cache: {e}")
    
    def get_item_emoji(self, item_data, enable_downloads=True):
        """
        Get the best emoji for an item
        
        Args:
            item_data: Item data from PoE API
            enable_downloads: Whether to download icons if not cached
            
        Returns:
            str: Emoji representing the item
        """
        icon_url = item_data.get('icon')
        if not icon_url:
            # No icon URL, use type-based fallback
            return self.color_mapper.get_smart_unicode_for_item(item_data, self.color_analyzer, None)
        
        # Check if we have cached color analysis
        if icon_url in self.color_cache:
            color_category = self.color_cache[icon_url]
            return self.color_mapper.get_smart_unicode_for_item(item_data, self.color_analyzer, color_category)
        
        # Try to get cached icon file
        cached_icon = self.cache_manager.get_cached_icon_path(icon_url)
        
        if not cached_icon.exists() and enable_downloads:
            # Download if not cached
            print(f"[ICON] Downloading icon for analysis...")
            cached_icon = self.cache_manager.download_icon(icon_url)
        
        if cached_icon and cached_icon.exists():
            # Analyze color
            dominant_color = self.color_analyzer.get_dominant_color(cached_icon)
            color_category = self.color_analyzer.categorize_color(dominant_color)
            
            # Cache the result
            self.color_cache[icon_url] = color_category
            self._save_color_cache()
            
            return self.color_mapper.get_smart_unicode_for_item(item_data, self.color_analyzer, color_category)
        
        # Fallback to type-based emoji
        return self.color_mapper.get_smart_unicode_for_item(item_data, self.color_analyzer, None)
    
    def batch_analyze_items(self, items_list, max_downloads=20):
        """
        Analyze multiple items in batch for better performance
        
        Args:
            items_list: List of item data dicts
            max_downloads: Maximum number of icons to download
            
        Returns:
            dict: Mapping of item names to emojis
        """
        results = {}
        
        # Collect all icon URLs that need downloading
        urls_to_download = []
        
        for item in items_list:
            item_name = item.get('typeLine') or item.get('name', 'Unknown')
            icon_url = item.get('icon')
            
            if not icon_url:
                # No icon, use type-based
                results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, None)
                continue
            
            if icon_url in self.color_cache:
                # Already analyzed
                color_category = self.color_cache[icon_url]
                results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, color_category)
                continue
            
            cached_path = self.cache_manager.get_cached_icon_path(icon_url)
            if cached_path.exists():
                # Cached but not analyzed
                dominant_color = self.color_analyzer.get_dominant_color(cached_path)
                color_category = self.color_analyzer.categorize_color(dominant_color)
                self.color_cache[icon_url] = color_category
                results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, color_category)
                continue
            
            # Need to download
            if len(urls_to_download) < max_downloads:
                urls_to_download.append((icon_url, item))
            else:
                # Use fallback for items beyond download limit
                results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, None)
        
        # Batch download icons
        if urls_to_download:
            try:
                from config import Config
                if Config.DEBUG_ENABLED:
                    print(f"[ICON] Batch downloading {len(urls_to_download)} icons...")
            except:
                pass
            
            urls = [url for url, _ in urls_to_download]
            downloaded = self.cache_manager.batch_download_icons(urls, max_downloads)
            
            # Analyze downloaded icons
            for icon_url, item in urls_to_download:
                item_name = item.get('typeLine') or item.get('name', 'Unknown')
                cached_path = downloaded.get(icon_url)
                
                if cached_path and cached_path.exists():
                    dominant_color = self.color_analyzer.get_dominant_color(cached_path)
                    color_category = self.color_analyzer.categorize_color(dominant_color)
                    self.color_cache[icon_url] = color_category
                    results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, color_category)
                else:
                    results[item_name] = self.color_mapper.get_smart_unicode_for_item(item, self.color_analyzer, None)
        
        # Save color cache
        self._save_color_cache()
        
        return results
    
    def get_system_stats(self):
        """Get statistics about the icon system"""
        cache_stats = self.cache_manager.get_cache_stats()
        color_cache_size = len(self.color_cache)
        
        return {
            'cached_icons': cache_stats['total_files'],
            'cache_size_mb': cache_stats['total_size_mb'],
            'analyzed_colors': color_cache_size,
            'color_cache_file': str(self.color_cache_file)
        }
    
    def cleanup_system(self, max_age_days=30):
        """Clean up old cache files"""
        self.cache_manager.cleanup_cache(max_age_days)
        
        # Also clean up color cache for non-existent icons
        valid_urls = set()
        for cache_file in self.cache_manager.cache_dir.glob('*.png'):
            # This is a simplified cleanup - in practice you'd want to map filenames back to URLs
            pass
        
        print(f"[ICON] System cleanup completed")


# Global smart icon system instance
_smart_icon_system = None

def get_smart_icon_system():
    """Get the global smart icon system instance"""
    global _smart_icon_system
    if _smart_icon_system is None:
        _smart_icon_system = SmartIconSystem()
    return _smart_icon_system