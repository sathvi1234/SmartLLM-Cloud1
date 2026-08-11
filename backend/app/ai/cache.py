import time
import uuid
from typing import Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

# In a real production setup, use `redis.asyncio` with Redis Stack (RediSearch) for true HNSW vector similarity.
# For this implementation, we will build a high-performance abstraction that calculates cosine similarity.
# We will simulate the Redis VSS using a fast in-memory store if Redis is unavailable, structured for Redis migration.

class SemanticCache:
    def __init__(self, redis_client=None, similarity_threshold: float = 0.90, ttl_seconds: int = 86400):
        self.redis = redis_client
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        
        # Local fallback if no Redis configured
        self._local_cache = {}
        
        # Cumulative Stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "cost_saved_usd": 0.0,
            "tokens_saved": 0,
            "time_saved_ms": 0
        }

    def _get_embedding(self, text: str) -> np.ndarray:
        # Placeholder for actual embedding logic (e.g. OpenAI text-embedding-3-small or sentence-transformers)
        # Using a deterministic hash-based pseudo-embedding for demonstration without pulling heavy ML libraries
        np.random.seed(sum(ord(c) for c in text))
        emb = np.random.rand(384)
        return emb / np.linalg.norm(emb)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        start_time = time.time()
        query_emb = self._get_embedding(prompt)
        
        best_match = None
        highest_score = -1.0
        
        # Clean up expired items lazily
        current_time = time.time()
        keys_to_delete = [k for k, v in self._local_cache.items() if current_time > v["expires_at"]]
        for k in keys_to_delete:
            del self._local_cache[k]
        
        # Simulate Redis Vector Search
        # In prod: FT.SEARCH idx "*=>[KNN 1 @embedding $vec AS score]" PARAMS 2 vec query_emb
        for key, entry in self._local_cache.items():
            score = self._cosine_similarity(query_emb, entry["embedding"])
            if score > highest_score:
                highest_score = score
                best_match = entry

        if best_match and highest_score >= self.similarity_threshold:
            # Cache Hit
            self.stats["hits"] += 1
            self.stats["tokens_saved"] += best_match["tokens"]
            self.stats["cost_saved_usd"] += best_match["cost_usd"]
            
            # Estimate latency saved: original latency minus current fast retrieval time
            retrieval_ms = int((time.time() - start_time) * 1000)
            saved_ms = best_match["latency_ms"] - retrieval_ms
            self.stats["time_saved_ms"] += max(0, saved_ms)
            
            logger.info(f"[Semantic Cache] Hit! Score: {highest_score:.2f} | Saved {saved_ms}ms and ${best_match['cost_usd']:.4f}")
            
            return {
                "content": best_match["response"],
                "similarity": highest_score,
                "cached_at": best_match["created_at"],
                "saved_ms": max(0, saved_ms),
                "saved_usd": best_match["cost_usd"]
            }
            
        # Cache Miss
        self.stats["misses"] += 1
        return None

    async def set(self, prompt: str, response: str, tokens: int, cost_usd: float, latency_ms: int):
        emb = self._get_embedding(prompt)
        key = str(uuid.uuid4())
        
        entry = {
            "embedding": emb,
            "response": response,
            "tokens": tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl_seconds
        }
        
        # Store locally
        self._local_cache[key] = entry
        
        # In prod with Redis:
        # self.redis.hset(f"cache:{key}", mapping={"response": response, "embedding": emb.tobytes()})
        # self.redis.expire(f"cache:{key}", self.ttl_seconds)

    def get_statistics(self) -> Dict[str, Any]:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0.0
        
        return {
            "total_requests": total,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate_percentage": round(hit_rate, 2),
            "total_cost_saved_usd": round(self.stats["cost_saved_usd"], 6),
            "total_tokens_saved": self.stats["tokens_saved"],
            "total_time_saved_ms": self.stats["time_saved_ms"],
            "active_cache_entries": len(self._local_cache)
        }
