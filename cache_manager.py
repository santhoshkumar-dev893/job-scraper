"""
Prompt Cache Manager - Manages LLM prompt caching for skill extraction

Handles:
- Cache key generation from skills lists
- Cache hit/miss logic
- Cache invalidation
- Performance metrics
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

log = logging.getLogger(__name__)


class PromptCacheManager:
    """Manages prompt caching for LLM skill extraction calls"""
    
    def __init__(self, enable_caching: bool = False, provider: Optional[str] = None):
        """
        Initialize cache manager
        
        Args:
            enable_caching: Whether to enable caching
            provider: Cache provider ("claude", "openai", "gemini", or None)
        """
        self.enabled = enable_caching
        self.provider = provider
        self.cache: Dict[str, Dict] = {}  # Cache storage
        self.last_revalidation = datetime.now()
        self.jobs_processed = 0
        
        # Metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_cost_saved = 0.0
        self.total_cost_normal = 0.0
        
        log.info(f"PromptCacheManager initialized (enabled={enable_caching}, provider={provider})")
    
    def should_use_cache(self) -> bool:
        """Check if caching should be used"""
        return self.enabled and self.provider is not None
    
    def get_cache_key(self, skills_list: List[str]) -> str:
        """
        Generate a deterministic cache key from skills list
        
        Args:
            skills_list: List of known skills
            
        Returns:
            SHA256 hash of sorted, deduplicated skills
        """
        if not skills_list:
            return hashlib.sha256(b"empty_skills").hexdigest()
        
        # Normalize: sort, deduplicate, lowercase
        normalized = sorted(set(s.lower().strip() for s in skills_list if s))
        skills_str = "|".join(normalized)
        
        # Create hash
        cache_key = hashlib.sha256(skills_str.encode()).hexdigest()
        return cache_key
    
    def should_revalidate_cache(self) -> bool:
        """
        Check if cache should be revalidated
        
        Revalidation triggers:
        - 24 hours elapsed, OR
        - 100 jobs processed
        
        Returns:
            True if revalidation needed
        """
        time_elapsed = datetime.now() - self.last_revalidation
        
        # Check time interval (24 hours)
        if time_elapsed > timedelta(hours=24):
            log.info("Cache revalidation: 24-hour interval reached")
            return True
        
        # Check job count
        if self.jobs_processed % 100 == 0 and self.jobs_processed > 0:
            log.info(f"Cache revalidation: {self.jobs_processed} jobs processed")
            return True
        
        return False
    
    def get_cached_result(self, skills_list: List[str]) -> Optional[Dict]:
        """
        Retrieve cached LLM result if available
        
        Args:
            skills_list: List of known skills to use as cache key
            
        Returns:
            Dict with 'cached': True and 'result' if hit, None if miss
        """
        if not self.should_use_cache():
            return None
        
        cache_key = self.get_cache_key(skills_list)
        
        # Check if in cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            entry['hits'] += 1
            self.cache_hits += 1
            
            # Cost savings depend on provider
            if self.provider == "claude":
                cost_saved = 0.011  # $0.015 normal - $0.004 cached
            elif self.provider == "openai":
                cost_saved = 0.020  # $0.030 normal - $0.010 cached
            elif self.provider == "gemini":
                cost_saved = 0.050  # $0.075 normal - $0.025 cached
            else:
                cost_saved = 0.011
            
            self.total_cost_saved += cost_saved
            
            log.debug(
                f"✅ Cache HIT (key={cache_key[:8]}..., hits={entry['hits']}, "
                f"saved=${cost_saved:.3f})"
            )
            
            return {
                'cached': True,
                'result': entry['result'],
                'cost_saved': cost_saved,
                'cache_key': cache_key
            }
        
        # Cache miss
        self.cache_misses += 1
        self.total_cost_normal += 0.015  # Normal call cost
        
        log.debug(f"❌ Cache MISS (key={cache_key[:8]}...)")
        
        return None
    
    def store_cached_result(
        self, 
        skills_list: List[str], 
        result: Dict, 
        cache_id: Optional[str] = None
    ) -> str:
        """
        Store LLM extraction result in cache
        
        Args:
            skills_list: List of known skills used
            result: Extraction result from LLM
            cache_id: Optional provider-specific cache ID
            
        Returns:
            Cache key that was stored
        """
        if not self.should_use_cache():
            return ""
        
        cache_key = self.get_cache_key(skills_list)
        
        self.cache[cache_key] = {
            'skills_hash': cache_key,
            'result': result,
            'cache_id': cache_id or '',
            'created_at': datetime.now().isoformat(),
            'hits': 0,
            'skills_count': len(set(s.lower().strip() for s in skills_list if s))
        }
        
        log.debug(
            f"💾 Cache STORED (key={cache_key[:8]}..., skills={len(skills_list)}, "
            f"size={len(self.cache)} entries)"
        )
        
        return cache_key
    
    def invalidate_cache(self) -> None:
        """Clear the entire cache"""
        size_before = len(self.cache)
        self.cache.clear()
        self.last_revalidation = datetime.now()
        log.info(f"Cache cleared ({size_before} entries removed)")
    
    def invalidate_on_new_skill(self) -> None:
        """
        Invalidate cache when new skills discovered
        (Called by skill_discovery.py when inserting new skills)
        """
        if len(self.cache) > 0:
            log.info("New skills detected - invalidating cache")
            self.invalidate_cache()
    
    def record_job_processed(self) -> None:
        """Record that a job was processed (for revalidation tracking)"""
        self.jobs_processed += 1
        
        # Check if revalidation needed
        if self.should_revalidate_cache():
            self.invalidate_cache()
    
    def get_stats(self) -> Dict:
        """
        Get current cache statistics
        
        Returns:
            Dictionary with metrics
        """
        total_calls = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_calls * 100) if total_calls > 0 else 0
        cost_reduction = (self.total_cost_saved / self.total_cost_normal * 100) \
                        if self.total_cost_normal > 0 else 0
        
        return {
            'enabled': self.enabled,
            'provider': self.provider,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_calls': total_calls,
            'hit_rate_percent': round(hit_rate, 1),
            'cached_entries': len(self.cache),
            'total_cost_saved': round(self.total_cost_saved, 2),
            'cost_reduction_percent': round(cost_reduction, 1),
            'jobs_processed': self.jobs_processed,
            'last_revalidation': self.last_revalidation.isoformat()
        }
    
    def print_stats(self) -> None:
        """Print formatted cache statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("CACHE STATISTICS")
        print("="*50)
        print(f"Status:              {('✅ ENABLED' if stats['enabled'] else '⚠️  DISABLED')}")
        print(f"Provider:            {stats['provider']}")
        print(f"Cache Hits:          {stats['cache_hits']}")
        print(f"Cache Misses:        {stats['cache_misses']}")
        print(f"Total Calls:         {stats['total_calls']}")
        print(f"Hit Rate:            {stats['hit_rate_percent']}%")
        print(f"Cached Entries:      {stats['cached_entries']}")
        print(f"Cost Saved:          ${stats['total_cost_saved']}")
        print(f"Cost Reduction:      {stats['cost_reduction_percent']}%")
        print(f"Jobs Processed:      {stats['jobs_processed']}")
        print("="*50 + "\n")
