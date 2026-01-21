from datetime import datetime, timedelta
import os
import json
from typing import Optional

class SourceTracker:
    """Track last refresh time per job source for incremental updates"""
    
    def __init__(self):
        self.state_file = os.path.join(os.path.dirname(__file__), ".source_state.json")
        self.sources = self._load_state()
    
    def _load_state(self) -> dict:
        """Load source tracking state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Convert ISO strings back to datetime objects
                    for source in data:
                        if data[source].get('last_refresh'):
                            data[source]['last_refresh'] = datetime.fromisoformat(data[source]['last_refresh'])
                    return data
        except Exception as e:
            print(f"Could not load source state: {e}")
        return {}
    
    def _save_state(self):
        """Save source tracking state to file"""
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            data = {}
            for source, info in self.sources.items():
                data[source] = {
                    'last_refresh': info['last_refresh'].isoformat() if info.get('last_refresh') else None,
                    'jobs_fetched': info.get('jobs_fetched', 0)
                }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save source state: {e}")
    
    def get_last_refresh(self, source: str) -> Optional[datetime]:
        """Get last refresh time for a specific source"""
        return self.sources.get(source, {}).get('last_refresh')
    
    def should_refresh_source(self, source: str, interval_hours: int = 3) -> bool:
        """Check if a specific source should be refreshed based on its interval"""
        last_refresh = self.get_last_refresh(source)
        
        if last_refresh is None:
            return True
        
        time_since_refresh = datetime.now() - last_refresh
        return time_since_refresh > timedelta(hours=interval_hours)
    
    def mark_refreshed(self, source: str, jobs_count: int = 0):
        """Mark that a source has been refreshed"""
        if source not in self.sources:
            self.sources[source] = {}
        
        self.sources[source]['last_refresh'] = datetime.now()
        self.sources[source]['jobs_fetched'] = jobs_count
        self._save_state()
    
    def get_all_sources_status(self) -> dict:
        """Get status of all tracked sources"""
        status = {}
        for source, info in self.sources.items():
            last_refresh = info.get('last_refresh')
            status[source] = {
                'last_refresh': last_refresh.isoformat() if last_refresh else None,
                'jobs_fetched': info.get('jobs_fetched', 0),
                'should_refresh': self.should_refresh_source(source)
            }
        return status

# Global instance
source_tracker = SourceTracker()
