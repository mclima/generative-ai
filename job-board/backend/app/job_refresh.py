from datetime import datetime, timedelta
import threading
import os
import json

class JobRefreshManager:
    def __init__(self):
        self.refresh_lock = threading.Lock()
        self.refresh_interval_hours = 3
        self.state_file = os.path.join(os.path.dirname(__file__), ".refresh_state.json")
        self.last_refresh = self._load_last_refresh()
        self.first_request = True
        
    def _load_last_refresh(self):
        """Load last refresh time from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_refresh'])
        except Exception as e:
            print(f"Could not load refresh state: {e}")
        return None
    
    def _save_last_refresh(self):
        """Save last refresh time to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_refresh': self.last_refresh.isoformat()
                }, f)
        except Exception as e:
            print(f"Could not save refresh state: {e}")
        
    def should_refresh(self) -> bool:
        """Check if jobs should be refreshed:
        - Always on first request after server start
        - Then every 3 hours
        """
        # Always refresh on first request
        if self.first_request:
            return True
            
        # No previous refresh recorded
        if self.last_refresh is None:
            return True
        
        # Check if interval has passed
        time_since_refresh = datetime.now() - self.last_refresh
        return time_since_refresh > timedelta(hours=self.refresh_interval_hours)
    
    def mark_refreshed(self):
        """Mark that jobs have been refreshed"""
        self.last_refresh = datetime.now()
        self.first_request = False
        self._save_last_refresh()
    
    def get_last_refresh_time(self):
        """Get the last refresh timestamp"""
        return self.last_refresh

# Global instance
refresh_manager = JobRefreshManager()
