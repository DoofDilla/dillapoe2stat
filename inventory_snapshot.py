"""
Inventory Snapshot Service and Data Objects
Handles API calls, rate limiting, and snapshot data management
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any
from poe_api import snapshot_inventory


@dataclass(frozen=True)
class InventorySnapshot:
    """Immutable inventory snapshot data
    
    Attributes:
        items: List of inventory items from API
        snapshot_type: Type of snapshot (PRE, POST, CHECK, WAYSTONE)
        timestamp: Unix timestamp when snapshot was taken
        item_count: Number of items in snapshot
    """
    items: List[Dict[str, Any]]
    snapshot_type: str
    timestamp: float
    
    @property
    def item_count(self) -> int:
        """Get number of items in snapshot"""
        return len(self.items)
    
    def __repr__(self):
        return f"InventorySnapshot({self.snapshot_type}, {self.item_count} items, {time.strftime('%H:%M:%S', time.localtime(self.timestamp))})"


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, min_gap_seconds: float = 1.0):
        """Initialize rate limiter
        
        Args:
            min_gap_seconds: Minimum time gap between API calls
        """
        self.min_gap = min_gap_seconds
        self.last_call_time = 0.0
    
    def wait_if_needed(self):
        """Wait if necessary to maintain rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.min_gap:
            wait_time = self.min_gap - time_since_last
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def reset(self):
        """Reset rate limiter (useful for testing)"""
        self.last_call_time = 0.0


class InventorySnapshotService:
    """Handles all inventory snapshot API calls with rate limiting
    
    This service encapsulates:
    - API authentication and calls
    - Rate limiting between requests
    - Snapshot data object creation
    - Error handling for API failures
    """
    
    def __init__(self, token: str, min_gap_seconds: float = 1.0):
        """Initialize snapshot service
        
        Args:
            token: PoE API authentication token
            min_gap_seconds: Minimum time gap between API calls
        """
        self.token = token
        self.rate_limiter = RateLimiter(min_gap_seconds)
    
    def take_snapshot(self, character_name: str, snapshot_type: str = "GENERIC") -> InventorySnapshot:
        """Take an inventory snapshot with rate limiting
        
        Args:
            character_name: Name of the character to snapshot
            snapshot_type: Type of snapshot (PRE, POST, CHECK, WAYSTONE)
            
        Returns:
            InventorySnapshot object with snapshot data
            
        Raises:
            Exception: If API call fails
        """
        # Rate limit
        self.rate_limiter.wait_if_needed()
        
        # Take snapshot
        timestamp = time.time()
        items = snapshot_inventory(self.token, character_name)
        
        # Create snapshot object
        return InventorySnapshot(
            items=items,
            snapshot_type=snapshot_type,
            timestamp=timestamp
        )
    
    def update_token(self, new_token: str):
        """Update API token (for re-authentication)"""
        self.token = new_token
