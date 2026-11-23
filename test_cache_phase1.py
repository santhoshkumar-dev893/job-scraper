"""
Test Phase 1 cache implementation
"""

import logging
from cache_manager import PromptCacheManager

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_cache_manager():
    """Test basic cache manager functionality"""
    
    # Test 1: Create manager
    print("\n=== Test 1: Initialize Cache Manager ===")
    manager = PromptCacheManager(enable_caching=True, provider="claude")
    assert manager.enabled == True
    assert manager.provider == "claude"
    print("✅ Manager initialized")
    
    # Test 2: Cache key generation
    print("\n=== Test 2: Cache Key Generation ===")
    skills1 = ["Python", "JavaScript", "AWS"]
    skills2 = ["JavaScript", "Python", "AWS"]  # Different order, same content
    
    key1 = manager.get_cache_key(skills1)
    key2 = manager.get_cache_key(skills2)
    
    assert key1 == key2, "Same skills should produce same key"
    print(f"✅ Cache keys match: {key1[:16]}...")
    
    # Test 3: Cache miss
    print("\n=== Test 3: Cache Miss ===")
    result = manager.get_cached_result(skills1)
    assert result is None
    assert manager.cache_misses == 1
    print("✅ Cache miss recorded")
    
    # Test 4: Store result
    print("\n=== Test 4: Store Cached Result ===")
    dummy_result = {
        'status': 'ok',
        'skills': [{'name': 'Python', 'level': 'mandatory'}],
        'warnings': []
    }
    manager.store_cached_result(skills1, dummy_result, cache_id="test_123")
    assert len(manager.cache) == 1
    print("✅ Result stored in cache")
    
    # Test 5: Cache hit
    print("\n=== Test 5: Cache Hit ===")
    cached = manager.get_cached_result(skills1)
    assert cached is not None
    assert cached['cached'] == True
    assert manager.cache_hits == 1
    print("✅ Cache hit retrieved")
    
    # Test 6: Stats
    print("\n=== Test 6: Get Statistics ===")
    stats = manager.get_stats()
    assert stats['cache_hits'] == 1
    assert stats['cache_misses'] == 1
    assert stats['hit_rate_percent'] == 50.0
    print(f"✅ Stats: {stats}")
    
    # Test 7: Print stats
    print("\n=== Test 7: Print Formatted Stats ===")
    manager.print_stats()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_cache_manager()
