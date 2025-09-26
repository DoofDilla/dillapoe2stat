"""
Icon Cache Manager for PoE Stats Tracker
Downloads and caches item icons from PoE CDN for analysis
"""

import os
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlparse
import time


class IconCacheManager:
    """Manages downloading and caching of PoE item icons"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = script_dir / "cache" / "icons"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Request session for efficient connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DillaPoE2Stat/1.0 Icon Cache'
        })
        
        # Rate limiting
        self.last_download = 0
        self.min_delay = 0.1  # 100ms between downloads
        
    def _get_cache_filename(self, icon_url):
        """Generate cache filename from icon URL"""
        url_hash = hashlib.md5(icon_url.encode()).hexdigest()
        parsed = urlparse(icon_url)
        extension = os.path.splitext(parsed.path)[1] or '.png'
        return f"{url_hash}{extension}"
    
    def _is_cached(self, icon_url):
        """Check if icon is already cached"""
        cache_file = self.cache_dir / self._get_cache_filename(icon_url)
        return cache_file.exists() and cache_file.stat().st_size > 0
    
    def _rate_limit(self):
        """Enforce rate limiting between downloads"""
        now = time.time()
        elapsed = now - self.last_download
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_download = time.time()
    
    def download_icon(self, icon_url, force_refresh=False):
        """
        Download an icon from PoE CDN and cache it locally
        
        Args:
            icon_url: URL to the icon
            force_refresh: Force re-download even if cached
            
        Returns:
            Path to cached file or None if failed
        """
        if not icon_url or not icon_url.startswith('http'):
            return None
        
        cache_file = self.cache_dir / self._get_cache_filename(icon_url)
        
        # Return cached file if exists and not forcing refresh
        if not force_refresh and self._is_cached(icon_url):
            return cache_file
        
        try:
            # Rate limit downloads
            self._rate_limit()
            
            # Download the icon
            response = self.session.get(icon_url, timeout=10)
            response.raise_for_status()
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            # Only show download message in debug mode
            try:
                from config import Config
                if Config.DEBUG_ENABLED:
                    print(f"[ICON] Downloaded: {os.path.basename(cache_file)}")
            except:
                pass  # Fallback if config not available
            
            return cache_file
            
        except Exception as e:
            print(f"[ICON] Failed to download {icon_url}: {e}")
            return None
    
    def get_cached_icon_path(self, icon_url):
        """Get path to cached icon without downloading"""
        if not icon_url:
            return None
        return self.cache_dir / self._get_cache_filename(icon_url)
    
    def batch_download_icons(self, icon_urls, max_downloads=50):
        """
        Download multiple icons in batch
        
        Args:
            icon_urls: List of icon URLs
            max_downloads: Maximum number of downloads per batch
            
        Returns:
            Dict mapping URLs to cache file paths
        """
        results = {}
        download_count = 0
        
        for url in icon_urls:
            if download_count >= max_downloads:
                try:
                    from config import Config
                    if Config.DEBUG_ENABLED:
                        print(f"[ICON] Batch limit reached ({max_downloads}), stopping downloads")
                except:
                    pass
                break
                
            if self._is_cached(url):
                # Already cached
                results[url] = self.get_cached_icon_path(url)
            else:
                # Need to download
                cache_path = self.download_icon(url)
                results[url] = cache_path
                if cache_path:
                    download_count += 1
        
        # Only show batch complete message in debug mode
        try:
            from config import Config
            if Config.DEBUG_ENABLED:
                print(f"[ICON] Batch complete: {download_count} new downloads, {len(results)} total icons")
        except:
            pass  # Fallback if config not available
        
        return results
    
    def cleanup_cache(self, max_age_days=30):
        """Remove old cached icons"""
        import time
        
        max_age_seconds = max_age_days * 24 * 60 * 60
        current_time = time.time()
        removed_count = 0
        
        for cache_file in self.cache_dir.glob('*'):
            if cache_file.is_file():
                file_age = current_time - cache_file.stat().st_mtime
                if file_age > max_age_seconds:
                    cache_file.unlink()
                    removed_count += 1
        
        print(f"[ICON] Cache cleanup: removed {removed_count} old files")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob('*'))
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        
        return {
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Global cache manager instance
_cache_manager = None

def get_icon_cache_manager():
    """Get the global icon cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = IconCacheManager()
    return _cache_manager