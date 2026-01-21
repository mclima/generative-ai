import redis
import json
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class JobCache:
    """Redis cache for job listings with 15-minute TTL"""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            print("✓ Redis cache connected")
        except (redis.ConnectionError, redis.RedisError) as e:
            print(f"⚠ Redis cache disabled: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, role: Optional[str] = None, remote: Optional[bool] = None, 
                  limit: int = 20, offset: int = 0, sort_by: str = "score", order: str = "desc") -> str:
        """Generate cache key from query parameters"""
        return f"jobs:{role}:{remote}:{limit}:{offset}:{sort_by}:{order}"
    
    def get_jobs(self, role: Optional[str] = None, remote: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "score", order: str = "desc") -> Optional[List]:
        """Get cached jobs if available"""
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(role, remote, limit, offset, sort_by, order)
            cached = self.redis_client.get(key)
            
            if cached:
                print(f"✓ Cache HIT: {key}")
                return json.loads(cached)
            else:
                print(f"✗ Cache MISS: {key}")
                return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set_jobs(self, jobs: List, role: Optional[str] = None, remote: Optional[bool] = None,
                 limit: int = 20, offset: int = 0, sort_by: str = "score", order: str = "desc", ttl: int = 900):
        """Cache jobs with TTL (default 15 minutes = 900 seconds)"""
        if not self.enabled:
            return
        
        try:
            key = self._make_key(role, remote, limit, offset, sort_by, order)
            # Convert jobs to JSON-serializable format
            jobs_data = [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "remote": job.remote,
                    "role": job.role,
                    "source": job.source,
                    "url": job.url,
                    "posted_date": job.posted_date,
                    "score": job.score,
                    "description": job.description,
                    "salary": job.salary,
                    "requirements": job.requirements,
                    "responsibilities": job.responsibilities
                }
                for job in jobs
            ]
            
            self.redis_client.setex(key, ttl, json.dumps(jobs_data))
            print(f"✓ Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def invalidate_all(self):
        """Invalidate all job caches (call after refresh)"""
        if not self.enabled:
            return
        
        try:
            # Find all job cache keys
            keys = self.redis_client.keys("jobs:*")
            if keys:
                self.redis_client.delete(*keys)
                print(f"✓ Cache invalidated: {len(keys)} keys deleted")
        except Exception as e:
            print(f"Cache invalidation error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info("stats")
            keys_count = len(self.redis_client.keys("jobs:*"))
            
            return {
                "enabled": True,
                "total_keys": keys_count,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 
                    2
                )
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}

# Global instance
job_cache = JobCache()
