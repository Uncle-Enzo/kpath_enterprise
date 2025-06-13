"""
Feedback-based ranking system for KPATH Enterprise.

This module enhances search results with feedback-driven ranking,
using historical user interactions to improve relevance.
"""

import logging
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import numpy as np

from backend.models.models import FeedbackLog, Service

logger = logging.getLogger(__name__)


class FeedbackRanker:
    """
    Enhances search results with feedback-based ranking.
    
    Uses click-through rates, selection counts, and other signals
    to boost relevant services in search results.
    """
    
    def __init__(self, 
                 click_weight: float = 0.3,
                 recency_weight: float = 0.2,
                 popularity_weight: float = 0.1):
        """
        Initialize feedback ranker.
        
        Args:
            click_weight: Weight for click-through signal (0-1)
            recency_weight: Weight for recency of interactions (0-1)
            popularity_weight: Weight for overall popularity (0-1)
        """
        self.click_weight = click_weight
        self.recency_weight = recency_weight
        self.popularity_weight = popularity_weight
        
        # Cache for feedback scores
        self._feedback_cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    def apply_feedback_ranking(self, 
                             results: List[Tuple[int, float]], 
                             query: str,
                             db: Session) -> List[Tuple[int, float]]:
        """
        Apply feedback-based ranking to search results.
        
        Args:
            results: List of (service_id, base_score) tuples
            query: Search query text
            db: Database session
            
        Returns:
            Re-ranked list of (service_id, adjusted_score) tuples
        """
        if not results:
            return results
        
        # Get feedback scores for all services
        service_ids = [r[0] for r in results]
        feedback_scores = self._get_feedback_scores(service_ids, query, db)
        
        # Apply feedback to base scores
        adjusted_results = []
        for service_id, base_score in results:
            feedback_score = feedback_scores.get(service_id, 0.0)
            
            # Combine base score with feedback score
            # Base score has higher weight to maintain semantic relevance
            adjusted_score = (0.7 * base_score) + (0.3 * feedback_score)
            
            adjusted_results.append((service_id, adjusted_score))
        
        # Re-sort by adjusted scores
        adjusted_results.sort(key=lambda x: x[1], reverse=True)
        
        # Log ranking changes for analysis
        self._log_ranking_changes(results, adjusted_results)
        
        return adjusted_results
    
    def _get_feedback_scores(self, 
                           service_ids: List[int], 
                           query: str,
                           db: Session) -> Dict[int, float]:
        """
        Calculate feedback scores for services.
        
        Args:
            service_ids: List of service IDs to score
            query: Current search query
            db: Database session
            
        Returns:
            Dictionary mapping service_id to feedback score (0-1)
        """
        # Check cache
        if self._is_cache_valid():
            cached_scores = {sid: self._feedback_cache.get(sid, 0.0) 
                           for sid in service_ids}
            if all(sid in self._feedback_cache for sid in service_ids):
                return cached_scores
        
        scores = {}
        
        # Get click-through rates
        ctr_scores = self._get_ctr_scores(service_ids, db)
        
        # Get recency scores
        recency_scores = self._get_recency_scores(service_ids, db)
        
        # Get popularity scores
        popularity_scores = self._get_popularity_scores(service_ids, db)
        
        # Get query-specific scores
        query_scores = self._get_query_specific_scores(service_ids, query, db)
        
        # Combine all signals
        for service_id in service_ids:
            score = (
                self.click_weight * ctr_scores.get(service_id, 0.0) +
                self.recency_weight * recency_scores.get(service_id, 0.0) +
                self.popularity_weight * popularity_scores.get(service_id, 0.0) +
                0.4 * query_scores.get(service_id, 0.0)  # Query-specific boost
            )
            scores[service_id] = min(1.0, score)  # Cap at 1.0
        
        # Update cache
        self._update_cache(scores)
        
        return scores
    
    def _get_ctr_scores(self, service_ids: List[int], db: Session) -> Dict[int, float]:
        """Calculate click-through rate scores for services."""
        # Get CTR data for last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        ctr_data = db.query(
            FeedbackLog.selected_service_id,
            func.sum(FeedbackLog.click_through.cast(db.Integer)).label('clicks'),
            func.count(FeedbackLog.id).label('impressions')
        ).filter(
            FeedbackLog.selected_service_id.in_(service_ids),
            FeedbackLog.timestamp >= cutoff_date
        ).group_by(
            FeedbackLog.selected_service_id
        ).all()
        
        # Calculate CTR scores
        scores = {}
        max_ctr = 0.0
        
        for row in ctr_data:
            if row.impressions > 0:
                ctr = row.clicks / row.impressions
                scores[row.selected_service_id] = ctr
                max_ctr = max(max_ctr, ctr)
        
        # Normalize to 0-1
        if max_ctr > 0:
            for service_id in scores:
                scores[service_id] = scores[service_id] / max_ctr
        
        return scores
    
    def _get_recency_scores(self, service_ids: List[int], db: Session) -> Dict[int, float]:
        """Calculate recency scores based on recent interactions."""
        # Get latest interaction for each service
        latest_interactions = db.query(
            FeedbackLog.selected_service_id,
            func.max(FeedbackLog.timestamp).label('latest')
        ).filter(
            FeedbackLog.selected_service_id.in_(service_ids)
        ).group_by(
            FeedbackLog.selected_service_id
        ).all()
        
        scores = {}
        now = datetime.utcnow()
        
        for row in latest_interactions:
            # Score based on how recent the interaction was
            days_ago = (now - row.latest).days
            if days_ago <= 1:
                score = 1.0
            elif days_ago <= 7:
                score = 0.8
            elif days_ago <= 30:
                score = 0.5
            else:
                score = 0.2
            
            scores[row.selected_service_id] = score
        
        return scores
    
    def _get_popularity_scores(self, service_ids: List[int], db: Session) -> Dict[int, float]:
        """Calculate popularity scores based on total interactions."""
        # Get interaction counts
        popularity_data = db.query(
            FeedbackLog.selected_service_id,
            func.count(FeedbackLog.id).label('interaction_count')
        ).filter(
            FeedbackLog.selected_service_id.in_(service_ids)
        ).group_by(
            FeedbackLog.selected_service_id
        ).all()
        
        scores = {}
        max_count = 0
        
        for row in popularity_data:
            scores[row.selected_service_id] = row.interaction_count
            max_count = max(max_count, row.interaction_count)
        
        # Normalize using logarithmic scale
        if max_count > 0:
            for service_id in scores:
                # Use log scale to prevent extremely popular services from dominating
                score = np.log1p(scores[service_id]) / np.log1p(max_count)
                scores[service_id] = score
        
        return scores
    
    def _get_query_specific_scores(self, 
                                 service_ids: List[int], 
                                 query: str,
                                 db: Session) -> Dict[int, float]:
        """Calculate scores based on performance for similar queries."""
        import hashlib
        
        # Create query hash for similarity matching
        query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        
        # Find feedback for this exact query
        exact_matches = db.query(
            FeedbackLog.selected_service_id,
            func.count(FeedbackLog.id).label('selection_count')
        ).filter(
            FeedbackLog.selected_service_id.in_(service_ids),
            FeedbackLog.query_embedding_hash == query_hash,
            FeedbackLog.click_through == True
        ).group_by(
            FeedbackLog.selected_service_id
        ).all()
        
        scores = {}
        max_count = 0
        
        for row in exact_matches:
            scores[row.selected_service_id] = row.selection_count
            max_count = max(max_count, row.selection_count)
        
        # Normalize
        if max_count > 0:
            for service_id in scores:
                scores[service_id] = scores[service_id] / max_count
        
        return scores
    
    def _is_cache_valid(self) -> bool:
        """Check if the feedback cache is still valid."""
        if self._cache_timestamp is None:
            return False
        
        age = (datetime.utcnow() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl
    
    def _update_cache(self, scores: Dict[int, float]) -> None:
        """Update the feedback cache."""
        self._feedback_cache.update(scores)
        self._cache_timestamp = datetime.utcnow()
    
    def _log_ranking_changes(self, 
                           original: List[Tuple[int, float]], 
                           adjusted: List[Tuple[int, float]]) -> None:
        """Log significant ranking changes for monitoring."""
        # Create position maps
        orig_positions = {sid: i for i, (sid, _) in enumerate(original)}
        adj_positions = {sid: i for i, (sid, _) in enumerate(adjusted)}
        
        # Find significant movements (3+ positions)
        for service_id in orig_positions:
            if service_id in adj_positions:
                movement = orig_positions[service_id] - adj_positions[service_id]
                if abs(movement) >= 3:
                    logger.debug(
                        f"Service {service_id} moved {movement:+d} positions "
                        f"({orig_positions[service_id]} -> {adj_positions[service_id]})"
                    )


class SearchOptimizer:
    """
    Optimizes search performance through various techniques.
    """
    
    def __init__(self):
        """Initialize search optimizer."""
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000
    
    def optimize_query(self, query: str) -> str:
        """
        Optimize search query for better results.
        
        Args:
            query: Raw search query
            
        Returns:
            Optimized query string
        """
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Expand common abbreviations
        abbreviations = {
            'mgmt': 'management',
            'admin': 'administration administrator',
            'auth': 'authentication authorization',
            'db': 'database',
            'api': 'application programming interface',
            'ui': 'user interface',
            'ux': 'user experience',
            'hr': 'human resources',
            'crm': 'customer relationship management',
            'erp': 'enterprise resource planning'
        }
        
        words = query.lower().split()
        expanded_words = []
        
        for word in words:
            if word in abbreviations:
                expanded_words.append(f"{word} {abbreviations[word]}")
            else:
                expanded_words.append(word)
        
        optimized = ' '.join(expanded_words)
        
        logger.debug(f"Query optimization: '{query}' -> '{optimized}'")
        
        return optimized
    
    def should_use_cache(self, query: str) -> Tuple[bool, Optional[List]]:
        """
        Check if results should be served from cache.
        
        Args:
            query: Search query
            
        Returns:
            Tuple of (should_use_cache, cached_results)
        """
        # Normalize query for cache key
        cache_key = query.lower().strip()
        
        if cache_key in self.query_cache:
            entry = self.query_cache[cache_key]
            age = (datetime.utcnow() - entry['timestamp']).total_seconds()
            
            if age < self.cache_ttl:
                logger.debug(f"Cache hit for query: '{query}'")
                return True, entry['results']
        
        return False, None
    
    def cache_results(self, query: str, results: List) -> None:
        """
        Cache search results.
        
        Args:
            query: Search query
            results: Search results to cache
        """
        # Implement LRU eviction if cache is full
        if len(self.query_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(
                self.query_cache.keys(),
                key=lambda k: self.query_cache[k]['timestamp']
            )
            del self.query_cache[oldest_key]
        
        cache_key = query.lower().strip()
        self.query_cache[cache_key] = {
            'results': results,
            'timestamp': datetime.utcnow()
        }
        
        logger.debug(f"Cached results for query: '{query}'")
