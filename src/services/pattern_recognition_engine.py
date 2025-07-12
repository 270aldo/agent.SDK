"""
Pattern Recognition Engine
Advanced ML engine for identifying success patterns, user archetypes, and behavioral signals.
Uses clustering, neural networks, and statistical analysis for deep insights.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from uuid import uuid4
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum

from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats
import pandas as pd

from ..models.base import BaseModel
from ..models.learning_models import PatternAnalysis, UserArchetype, ConversationPattern
from ..services.adaptive_learning_service import AdaptiveLearningService
from ..services.conversation_outcome_tracker import ConversationOutcomeTracker
from ..integrations.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PatternType(Enum):
    """Types of patterns to recognize"""
    CONVERSION_PATTERN = "conversion"
    ENGAGEMENT_PATTERN = "engagement" 
    OBJECTION_PATTERN = "objection"
    ARCHETYPE_PATTERN = "archetype"
    TIMING_PATTERN = "timing"
    EMOTIONAL_PATTERN = "emotional"
    LINGUISTIC_PATTERN = "linguistic"


class SuccessIndicator(Enum):
    """Indicators of conversation success"""
    CONVERSION = "conversion"
    HIGH_ENGAGEMENT = "high_engagement"
    TIER_UPGRADE = "tier_upgrade"
    EARLY_ADOPTER_SIGNUP = "early_adopter"
    POSITIVE_SENTIMENT = "positive_sentiment"
    REFERRAL_INTENT = "referral_intent"


@dataclass
class PatternSignature:
    """Unique signature representing a behavioral pattern"""
    pattern_id: str
    pattern_type: PatternType
    features: Dict[str, float]
    success_indicators: List[SuccessIndicator]
    confidence_score: float
    occurrence_count: int
    success_rate: float
    discovered_at: datetime


@dataclass
class UserBehaviorProfile:
    """Comprehensive user behavior profile"""
    user_id: str
    archetype: str
    confidence: float
    behavior_features: Dict[str, float]
    conversation_patterns: List[str]
    success_probability: float
    optimal_tier: str
    preferred_touchpoints: List[str]
    emotional_triggers: List[str]
    objection_predictors: List[str]


class PatternRecognitionEngine:
    """
    Advanced pattern recognition for conversation optimization.
    Identifies success patterns, user archetypes, and behavioral signals.
    """
    
    def __init__(self):
        self.adaptive_learning = AdaptiveLearningService()
        self.outcome_tracker = ConversationOutcomeTracker()
        self.supabase = get_supabase_client()
        
        # ML models
        self.archetype_model = None
        self.conversion_model = None
        self.engagement_model = None
        
        # Pattern storage
        self.discovered_patterns: Dict[str, PatternSignature] = {}
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        
        # Feature extractors
        self.feature_extractors = {
            'linguistic': self._extract_linguistic_features,
            'temporal': self._extract_temporal_features,
            'emotional': self._extract_emotional_features,
            'behavioral': self._extract_behavioral_features,
            'contextual': self._extract_contextual_features
        }
        
        # Known archetypes
        self.base_archetypes = {
            'optimizer': {
                'traits': ['efficiency', 'data_driven', 'roi_focused'],
                'triggers': ['performance', 'metrics', 'optimization'],
                'preferred_tier': 'PRIME'
            },
            'architect': {
                'traits': ['long_term', 'strategic', 'holistic'],
                'triggers': ['longevity', 'lifestyle', 'transformation'],
                'preferred_tier': 'LONGEVITY'
            },
            'explorer': {
                'traits': ['curious', 'experimental', 'early_adopter'],
                'triggers': ['innovation', 'cutting_edge', 'beta'],
                'preferred_tier': 'PRO'
            },
            'pragmatist': {
                'traits': ['practical', 'cost_conscious', 'gradual'],
                'triggers': ['value', 'proven', 'reliable'],
                'preferred_tier': 'ESSENTIAL'
            },
            'maximizer': {
                'traits': ['ambitious', 'premium_seeker', 'status'],
                'triggers': ['elite', 'exclusive', 'premium'],
                'preferred_tier': 'ELITE'
            }
        }
    
    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> PatternAnalysis:
        """
        Analyze conversation for patterns and generate insights.
        
        Args:
            conversation_data: Full conversation history and metadata
            user_context: User profile and context information
        
        Returns:
            PatternAnalysis with discovered patterns and recommendations
        """
        try:
            # Extract features from conversation
            features = await self._extract_all_features(
                conversation_data,
                user_context
            )
            
            # Identify patterns
            patterns = await self._identify_patterns(features, conversation_data)
            
            # Classify user archetype
            archetype = await self._classify_archetype(features, user_context)
            
            # Predict success probability
            success_probability = await self._predict_success(features, patterns)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                patterns,
                archetype,
                features
            )
            
            # Update pattern database
            await self._update_pattern_database(patterns, conversation_data)
            
            return PatternAnalysis(
                conversation_id=conversation_data.get('id'),
                patterns=patterns,
                archetype=archetype,
                success_probability=success_probability,
                recommendations=recommendations,
                features=features,
                analyzed_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {e}")
            return PatternAnalysis(
                conversation_id=conversation_data.get('id'),
                patterns=[],
                archetype=UserArchetype(name="unknown", confidence=0.0),
                success_probability=0.5,
                recommendations=[],
                features={},
                analyzed_at=datetime.utcnow()
            )
    
    async def _extract_all_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract comprehensive feature set from conversation"""
        
        features = {}
        
        # Extract features using all extractors
        for extractor_name, extractor_func in self.feature_extractors.items():
            try:
                extracted = await extractor_func(conversation_data, user_context)
                features[extractor_name] = extracted
            except Exception as e:
                logger.warning(f"Feature extraction failed for {extractor_name}: {e}")
                features[extractor_name] = {}
        
        return features
    
    async def _extract_linguistic_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract linguistic patterns from conversation"""
        
        messages = conversation_data.get('messages', [])
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        if not user_messages:
            return {}
        
        # Combine all user text
        user_text = ' '.join([m.get('content', '') for m in user_messages])
        words = user_text.lower().split()
        
        features = {
            'message_count': len(user_messages),
            'avg_message_length': np.mean([len(m.get('content', '')) for m in user_messages]),
            'total_word_count': len(words),
            'unique_word_ratio': len(set(words)) / len(words) if words else 0,
            'question_ratio': sum(1 for m in user_messages if '?' in m.get('content', '')) / len(user_messages),
            'exclamation_ratio': sum(1 for m in user_messages if '!' in m.get('content', '')) / len(user_messages),
            'technical_terms': self._count_technical_terms(user_text),
            'urgency_indicators': self._count_urgency_words(user_text),
            'sentiment_words': self._count_sentiment_words(user_text),
            'decision_words': self._count_decision_words(user_text)
        }
        
        return features
    
    async def _extract_temporal_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract timing and temporal patterns"""
        
        messages = conversation_data.get('messages', [])
        timestamps = [
            datetime.fromisoformat(m.get('timestamp', datetime.utcnow().isoformat()))
            for m in messages
        ]
        
        if len(timestamps) < 2:
            return {}
        
        # Calculate time intervals
        intervals = [
            (timestamps[i+1] - timestamps[i]).total_seconds()
            for i in range(len(timestamps)-1)
        ]
        
        features = {
            'conversation_duration': (timestamps[-1] - timestamps[0]).total_seconds(),
            'avg_response_time': np.mean(intervals),
            'response_time_variance': np.var(intervals),
            'fastest_response': min(intervals),
            'slowest_response': max(intervals),
            'response_acceleration': self._calculate_acceleration(intervals),
            'engagement_consistency': 1 / (1 + np.var(intervals)),
            'time_of_day': timestamps[0].hour,
            'day_of_week': timestamps[0].weekday()
        }
        
        return features
    
    async def _extract_emotional_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract emotional patterns and sentiment progression"""
        
        messages = conversation_data.get('messages', [])
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        # Get sentiment scores (assuming they're tracked)
        sentiment_scores = [
            m.get('sentiment_score', 0.5) for m in user_messages
        ]
        
        if not sentiment_scores:
            return {}
        
        features = {
            'initial_sentiment': sentiment_scores[0] if sentiment_scores else 0.5,
            'final_sentiment': sentiment_scores[-1] if sentiment_scores else 0.5,
            'sentiment_trajectory': sentiment_scores[-1] - sentiment_scores[0] if len(sentiment_scores) > 1 else 0,
            'avg_sentiment': np.mean(sentiment_scores),
            'sentiment_variance': np.var(sentiment_scores),
            'positive_peaks': sum(1 for s in sentiment_scores if s > 0.7),
            'negative_dips': sum(1 for s in sentiment_scores if s < 0.3),
            'emotional_stability': 1 / (1 + np.var(sentiment_scores)),
            'enthusiasm_indicators': self._count_enthusiasm_markers(user_messages),
            'concern_indicators': self._count_concern_markers(user_messages)
        }
        
        return features
    
    async def _extract_behavioral_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract behavioral patterns and engagement signals"""
        
        messages = conversation_data.get('messages', [])
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        features = {
            'proactive_questions': self._count_proactive_questions(user_messages),
            'objection_patterns': self._identify_objection_patterns(user_messages),
            'interest_escalation': self._measure_interest_escalation(user_messages),
            'decision_readiness': self._assess_decision_readiness(user_messages),
            'information_seeking': self._measure_information_seeking(user_messages),
            'price_sensitivity': self._assess_price_sensitivity(user_messages),
            'authority_indicators': self._identify_authority_level(user_messages),
            'urgency_level': self._assess_urgency_level(user_messages),
            'technical_sophistication': self._assess_technical_level(user_messages),
            'relationship_building': self._measure_relationship_signals(user_messages)
        }
        
        return features
    
    async def _extract_contextual_features(
        self,
        conversation_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract contextual and demographic features"""
        
        features = {
            'detected_tier': self._encode_tier(user_context.get('detected_tier', 'ESSENTIAL')),
            'profession_category': self._encode_profession(user_context.get('profession', 'unknown')),
            'company_size': self._encode_company_size(user_context.get('company_size', 'unknown')),
            'industry_category': self._encode_industry(user_context.get('industry', 'unknown')),
            'touchpoint_source': self._encode_touchpoint(conversation_data.get('source', 'unknown')),
            'previous_interactions': user_context.get('interaction_count', 0),
            'referral_source': self._encode_referral(user_context.get('referral_source', 'direct')),
            'geographic_region': self._encode_region(user_context.get('region', 'unknown'))
        }
        
        return features
    
    async def _identify_patterns(
        self,
        features: Dict[str, Any],
        conversation_data: Dict[str, Any]
    ) -> List[ConversationPattern]:
        """Identify specific patterns in the conversation"""
        
        patterns = []
        
        # Check for known pattern signatures
        for pattern_id, signature in self.discovered_patterns.items():
            similarity = self._calculate_pattern_similarity(features, signature)
            
            if similarity > 0.7:  # High similarity threshold
                patterns.append(ConversationPattern(
                    pattern_id=pattern_id,
                    pattern_type=signature.pattern_type.value,
                    confidence=similarity,
                    indicators=signature.success_indicators,
                    description=f"Detected {signature.pattern_type.value} pattern"
                ))
        
        # Discover new patterns using clustering
        new_patterns = await self._discover_new_patterns(features, conversation_data)
        patterns.extend(new_patterns)
        
        return patterns
    
    async def _classify_archetype(
        self,
        features: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> UserArchetype:
        """Classify user into archetype using ML and rule-based approach"""
        
        # Extract archetype-relevant features
        archetype_features = self._prepare_archetype_features(features, user_context)
        
        # Rule-based classification for known archetypes
        rule_based_result = self._rule_based_archetype_classification(
            archetype_features
        )
        
        # ML-based classification (if model is trained)
        ml_result = await self._ml_archetype_classification(archetype_features)
        
        # Combine results
        if rule_based_result['confidence'] > 0.7:
            return UserArchetype(
                name=rule_based_result['archetype'],
                confidence=rule_based_result['confidence'],
                traits=rule_based_result['traits'],
                optimal_tier=rule_based_result['optimal_tier']
            )
        elif ml_result and ml_result['confidence'] > 0.6:
            return ml_result
        else:
            # Default to pragmatist with low confidence
            return UserArchetype(
                name='pragmatist',
                confidence=0.3,
                traits=['practical', 'cautious'],
                optimal_tier='ESSENTIAL'
            )
    
    async def _predict_success(
        self,
        features: Dict[str, Any],
        patterns: List[ConversationPattern]
    ) -> float:
        """Predict conversation success probability"""
        
        # Base probability from features
        base_probability = self._calculate_base_success_probability(features)
        
        # Adjust based on patterns
        pattern_adjustment = self._calculate_pattern_adjustment(patterns)
        
        # Combine with historical data
        historical_adjustment = await self._get_historical_success_rate(features)
        
        # Weighted combination
        success_probability = (
            base_probability * 0.4 +
            pattern_adjustment * 0.4 +
            historical_adjustment * 0.2
        )
        
        return max(0.0, min(1.0, success_probability))
    
    async def _generate_recommendations(
        self,
        patterns: List[ConversationPattern],
        archetype: UserArchetype,
        features: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Archetype-based recommendations
        archetype_recs = self._get_archetype_recommendations(archetype)
        recommendations.extend(archetype_recs)
        
        # Pattern-based recommendations
        pattern_recs = self._get_pattern_recommendations(patterns)
        recommendations.extend(pattern_recs)
        
        # Feature-based recommendations
        feature_recs = self._get_feature_recommendations(features)
        recommendations.extend(feature_recs)
        
        # Remove duplicates and prioritize
        unique_recs = list(set(recommendations))
        prioritized_recs = self._prioritize_recommendations(unique_recs, features)
        
        return prioritized_recs[:5]  # Top 5 recommendations
    
    def _count_technical_terms(self, text: str) -> float:
        """Count technical/professional terms in text"""
        technical_terms = [
            'optimization', 'performance', 'efficiency', 'metrics',
            'analytics', 'roi', 'productivity', 'workflow', 'system',
            'algorithm', 'data', 'analysis', 'strategy'
        ]
        
        words = text.lower().split()
        count = sum(1 for word in words if any(term in word for term in technical_terms))
        return count / len(words) if words else 0
    
    def _count_urgency_words(self, text: str) -> float:
        """Count urgency indicators in text"""
        urgency_words = [
            'urgent', 'quickly', 'asap', 'immediately', 'rush',
            'deadline', 'soon', 'fast', 'hurry', 'critical'
        ]
        
        words = text.lower().split()
        count = sum(1 for word in words if word in urgency_words)
        return count / len(words) if words else 0
    
    def _count_sentiment_words(self, text: str) -> float:
        """Count positive/negative sentiment words"""
        positive_words = [
            'great', 'excellent', 'amazing', 'perfect', 'love',
            'fantastic', 'wonderful', 'impressive', 'outstanding'
        ]
        negative_words = [
            'terrible', 'awful', 'bad', 'hate', 'disappointed',
            'frustrated', 'annoying', 'useless', 'horrible'
        ]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment = positive_count + negative_count
        return (positive_count - negative_count) / len(words) if words else 0
    
    def _count_decision_words(self, text: str) -> float:
        """Count decision-related words"""
        decision_words = [
            'decide', 'choose', 'option', 'consider', 'think',
            'evaluate', 'compare', 'purchase', 'buy', 'invest'
        ]
        
        words = text.lower().split()
        count = sum(1 for word in words if any(dw in word for dw in decision_words))
        return count / len(words) if words else 0
    
    def _calculate_acceleration(self, intervals: List[float]) -> float:
        """Calculate response time acceleration/deceleration"""
        if len(intervals) < 3:
            return 0.0
        
        # Simple acceleration calculation
        first_half_avg = np.mean(intervals[:len(intervals)//2])
        second_half_avg = np.mean(intervals[len(intervals)//2:])
        
        return (first_half_avg - second_half_avg) / first_half_avg if first_half_avg > 0 else 0
    
    def _count_enthusiasm_markers(self, messages: List[Dict]) -> float:
        """Count enthusiasm indicators"""
        enthusiasm_markers = ['!', 'awesome', 'great', 'excited', 'wow', 'amazing']
        
        total_markers = 0
        total_messages = len(messages)
        
        for message in messages:
            content = message.get('content', '').lower()
            total_markers += sum(1 for marker in enthusiasm_markers if marker in content)
        
        return total_markers / total_messages if total_messages > 0 else 0
    
    def _count_concern_markers(self, messages: List[Dict]) -> float:
        """Count concern/hesitation indicators"""
        concern_markers = ['but', 'however', 'concerned', 'worry', 'unsure', 'hesitant']
        
        total_markers = 0
        total_messages = len(messages)
        
        for message in messages:
            content = message.get('content', '').lower()
            total_markers += sum(1 for marker in concern_markers if marker in content)
        
        return total_markers / total_messages if total_messages > 0 else 0
    
    def _count_proactive_questions(self, messages: List[Dict]) -> float:
        """Count proactive questions asked by user"""
        question_starters = ['how', 'what', 'when', 'where', 'why', 'can', 'would', 'could']
        
        proactive_questions = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            if '?' in content and any(content.startswith(q) for q in question_starters):
                proactive_questions += 1
        
        return proactive_questions / len(messages) if messages else 0
    
    def _identify_objection_patterns(self, messages: List[Dict]) -> float:
        """Identify objection patterns"""
        objection_indicators = [
            'expensive', 'cost', 'price', 'but', 'however',
            'not sure', 'think about', 'consider', 'maybe later'
        ]
        
        objection_count = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            if any(indicator in content for indicator in objection_indicators):
                objection_count += 1
        
        return objection_count / len(messages) if messages else 0
    
    def _measure_interest_escalation(self, messages: List[Dict]) -> float:
        """Measure how interest escalates throughout conversation"""
        interest_words = ['interested', 'tell me more', 'sounds good', 'how much', 'when can']
        
        escalation_score = 0
        
        for i, message in enumerate(messages):
            content = message.get('content', '').lower()
            weight = (i + 1) / len(messages)  # Later messages weighted more
            
            interest_indicators = sum(1 for word in interest_words if word in content)
            escalation_score += interest_indicators * weight
        
        return escalation_score / len(messages) if messages else 0
    
    def _assess_decision_readiness(self, messages: List[Dict]) -> float:
        """Assess how ready the user is to make a decision"""
        decision_indicators = [
            'ready', 'let\'s do it', 'sign up', 'start', 'proceed',
            'yes', 'sounds good', 'when can we', 'how do i'
        ]
        
        readiness_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            readiness_score += sum(1 for indicator in decision_indicators if indicator in content)
        
        return min(1.0, readiness_score / 3)  # Normalize to 0-1
    
    def _measure_information_seeking(self, messages: List[Dict]) -> float:
        """Measure information-seeking behavior"""
        info_seeking_words = [
            'how', 'what', 'explain', 'details', 'more info',
            'tell me', 'show me', 'example', 'case study'
        ]
        
        info_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            info_score += sum(1 for word in info_seeking_words if word in content)
        
        return info_score / len(messages) if messages else 0
    
    def _assess_price_sensitivity(self, messages: List[Dict]) -> float:
        """Assess price sensitivity level"""
        price_sensitive_words = [
            'expensive', 'cost', 'price', 'budget', 'afford',
            'cheap', 'discount', 'deal', 'value', 'worth'
        ]
        
        sensitivity_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            sensitivity_score += sum(1 for word in price_sensitive_words if word in content)
        
        return sensitivity_score / len(messages) if messages else 0
    
    def _identify_authority_level(self, messages: List[Dict]) -> float:
        """Identify decision-making authority level"""
        authority_indicators = [
            'i decide', 'my company', 'my team', 'i manage',
            'i\'m responsible', 'i choose', 'my budget'
        ]
        
        authority_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            authority_score += sum(1 for indicator in authority_indicators if indicator in content)
        
        return min(1.0, authority_score / 2)  # Normalize
    
    def _assess_urgency_level(self, messages: List[Dict]) -> float:
        """Assess urgency level"""
        urgency_indicators = [
            'urgent', 'asap', 'quickly', 'soon', 'immediate',
            'deadline', 'rush', 'critical', 'time sensitive'
        ]
        
        urgency_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            urgency_score += sum(1 for indicator in urgency_indicators if indicator in content)
        
        return min(1.0, urgency_score / 2)  # Normalize
    
    def _assess_technical_level(self, messages: List[Dict]) -> float:
        """Assess technical sophistication"""
        technical_indicators = [
            'api', 'integration', 'system', 'platform', 'algorithm',
            'data', 'analytics', 'metrics', 'optimization', 'architecture'
        ]
        
        technical_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            technical_score += sum(1 for indicator in technical_indicators if indicator in content)
        
        return technical_score / len(messages) if messages else 0
    
    def _measure_relationship_signals(self, messages: List[Dict]) -> float:
        """Measure relationship-building signals"""
        relationship_indicators = [
            'thanks', 'appreciate', 'helpful', 'great', 'understand',
            'makes sense', 'i see', 'good point', 'that helps'
        ]
        
        relationship_score = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            relationship_score += sum(1 for indicator in relationship_indicators if indicator in content)
        
        return relationship_score / len(messages) if messages else 0
    
    def _encode_tier(self, tier: str) -> float:
        """Encode tier to numeric value"""
        tier_values = {
            'ESSENTIAL': 0.2,
            'PRO': 0.4,
            'ELITE': 0.6,
            'PRIME': 0.8,
            'LONGEVITY': 1.0
        }
        return tier_values.get(tier.upper(), 0.2)
    
    def _encode_profession(self, profession: str) -> float:
        """Encode profession category"""
        profession_categories = {
            'executive': 1.0,
            'manager': 0.8,
            'consultant': 0.9,
            'entrepreneur': 0.95,
            'engineer': 0.7,
            'doctor': 0.85,
            'lawyer': 0.85,
            'student': 0.3,
            'unknown': 0.5
        }
        
        profession_lower = profession.lower()
        for category, value in profession_categories.items():
            if category in profession_lower:
                return value
        
        return 0.5
    
    def _encode_company_size(self, company_size: str) -> float:
        """Encode company size"""
        size_mapping = {
            'startup': 0.3,
            'small': 0.4,
            'medium': 0.6,
            'large': 0.8,
            'enterprise': 1.0,
            'unknown': 0.5
        }
        return size_mapping.get(company_size.lower(), 0.5)
    
    def _encode_industry(self, industry: str) -> float:
        """Encode industry category"""
        high_value_industries = [
            'technology', 'finance', 'consulting', 'healthcare',
            'pharmaceuticals', 'aerospace', 'telecommunications'
        ]
        
        industry_lower = industry.lower()
        if any(hvi in industry_lower for hvi in high_value_industries):
            return 0.8
        elif industry_lower != 'unknown':
            return 0.6
        else:
            return 0.5
    
    def _encode_touchpoint(self, touchpoint: str) -> float:
        """Encode touchpoint source"""
        touchpoint_values = {
            'landing_page': 0.6,
            'lead_magnet': 0.8,
            'referral': 0.9,
            'direct': 0.5,
            'social_media': 0.4,
            'unknown': 0.3
        }
        return touchpoint_values.get(touchpoint.lower(), 0.3)
    
    def _encode_referral(self, referral_source: str) -> float:
        """Encode referral source"""
        referral_values = {
            'customer': 1.0,
            'partner': 0.8,
            'employee': 0.7,
            'organic': 0.5,
            'paid': 0.4,
            'direct': 0.3
        }
        return referral_values.get(referral_source.lower(), 0.3)
    
    def _encode_region(self, region: str) -> float:
        """Encode geographic region"""
        region_values = {
            'north_america': 0.8,
            'europe': 0.7,
            'asia_pacific': 0.6,
            'latin_america': 0.5,
            'middle_east': 0.6,
            'africa': 0.4,
            'unknown': 0.5
        }
        return region_values.get(region.lower(), 0.5)
    
    def _calculate_pattern_similarity(
        self,
        features: Dict[str, Any],
        signature: PatternSignature
    ) -> float:
        """Calculate similarity between current features and pattern signature"""
        
        # Flatten feature dictionary
        current_features = self._flatten_features(features)
        signature_features = signature.features
        
        # Calculate cosine similarity
        common_keys = set(current_features.keys()) & set(signature_features.keys())
        
        if not common_keys:
            return 0.0
        
        vector1 = np.array([current_features[key] for key in common_keys])
        vector2 = np.array([signature_features[key] for key in common_keys])
        
        return cosine_similarity([vector1], [vector2])[0][0]
    
    def _flatten_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Flatten nested feature dictionary"""
        flattened = {}
        
        for category, category_features in features.items():
            if isinstance(category_features, dict):
                for key, value in category_features.items():
                    if isinstance(value, (int, float)):
                        flattened[f"{category}_{key}"] = float(value)
        
        return flattened
    
    async def _discover_new_patterns(
        self,
        features: Dict[str, Any],
        conversation_data: Dict[str, Any]
    ) -> List[ConversationPattern]:
        """Discover new patterns using unsupervised learning"""
        
        # This would require a larger dataset to be effective
        # For now, return empty list
        return []
    
    def _prepare_archetype_features(
        self,
        features: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Prepare features specifically for archetype classification"""
        
        archetype_features = {}
        
        # Extract key archetype indicators
        if 'linguistic' in features:
            archetype_features.update({
                'technical_sophistication': features['linguistic'].get('technical_terms', 0),
                'decision_orientation': features['linguistic'].get('decision_words', 0),
                'urgency_level': features['linguistic'].get('urgency_indicators', 0)
            })
        
        if 'behavioral' in features:
            archetype_features.update({
                'proactive_engagement': features['behavioral'].get('proactive_questions', 0),
                'information_seeking': features['behavioral'].get('information_seeking', 0),
                'decision_readiness': features['behavioral'].get('decision_readiness', 0),
                'price_sensitivity': features['behavioral'].get('price_sensitivity', 0)
            })
        
        if 'contextual' in features:
            archetype_features.update({
                'professional_level': features['contextual'].get('profession_category', 0.5),
                'company_influence': features['contextual'].get('company_size', 0.5),
                'industry_sophistication': features['contextual'].get('industry_category', 0.5)
            })
        
        return archetype_features
    
    def _rule_based_archetype_classification(
        self,
        features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Classify archetype using rules"""
        
        # Optimizer archetype
        if (features.get('technical_sophistication', 0) > 0.6 and 
            features.get('decision_orientation', 0) > 0.5 and
            features.get('professional_level', 0) > 0.7):
            return {
                'archetype': 'optimizer',
                'confidence': 0.8,
                'traits': ['efficiency', 'data_driven', 'roi_focused'],
                'optimal_tier': 'PRIME'
            }
        
        # Architect archetype
        elif (features.get('information_seeking', 0) > 0.6 and
              features.get('decision_readiness', 0) < 0.4 and
              features.get('professional_level', 0) > 0.6):
            return {
                'archetype': 'architect',
                'confidence': 0.75,
                'traits': ['long_term', 'strategic', 'holistic'],
                'optimal_tier': 'LONGEVITY'
            }
        
        # Explorer archetype
        elif (features.get('proactive_engagement', 0) > 0.7 and
              features.get('urgency_level', 0) > 0.5):
            return {
                'archetype': 'explorer',
                'confidence': 0.7,
                'traits': ['curious', 'experimental', 'early_adopter'],
                'optimal_tier': 'PRO'
            }
        
        # Pragmatist archetype
        elif features.get('price_sensitivity', 0) > 0.5:
            return {
                'archetype': 'pragmatist',
                'confidence': 0.65,
                'traits': ['practical', 'cost_conscious', 'gradual'],
                'optimal_tier': 'ESSENTIAL'
            }
        
        # Default
        else:
            return {
                'archetype': 'pragmatist',
                'confidence': 0.3,
                'traits': ['practical'],
                'optimal_tier': 'ESSENTIAL'
            }
    
    async def _ml_archetype_classification(
        self,
        features: Dict[str, float]
    ) -> Optional[UserArchetype]:
        """ML-based archetype classification (placeholder for future implementation)"""
        
        # Would require trained model
        return None
    
    def _calculate_base_success_probability(
        self,
        features: Dict[str, Any]
    ) -> float:
        """Calculate base success probability from features"""
        
        success_factors = []
        
        # Extract success indicators
        if 'behavioral' in features:
            behavioral = features['behavioral']
            success_factors.extend([
                behavioral.get('decision_readiness', 0),
                behavioral.get('interest_escalation', 0),
                behavioral.get('proactive_questions', 0),
                1 - behavioral.get('objection_patterns', 0)  # Fewer objections = better
            ])
        
        if 'emotional' in features:
            emotional = features['emotional']
            success_factors.extend([
                emotional.get('sentiment_trajectory', 0),
                emotional.get('enthusiasm_indicators', 0),
                1 - emotional.get('concern_indicators', 0)  # Fewer concerns = better
            ])
        
        if 'contextual' in features:
            contextual = features['contextual']
            success_factors.extend([
                contextual.get('profession_category', 0.5),
                contextual.get('company_size', 0.5),
                contextual.get('touchpoint_source', 0.5)
            ])
        
        return np.mean(success_factors) if success_factors else 0.5
    
    def _calculate_pattern_adjustment(
        self,
        patterns: List[ConversationPattern]
    ) -> float:
        """Calculate adjustment based on identified patterns"""
        
        if not patterns:
            return 0.5
        
        # Weight patterns by confidence and historical success rate
        weighted_success = 0
        total_weight = 0
        
        for pattern in patterns:
            # Get pattern from discovered patterns
            if pattern.pattern_id in self.discovered_patterns:
                signature = self.discovered_patterns[pattern.pattern_id]
                weight = pattern.confidence
                success_rate = signature.success_rate
                
                weighted_success += success_rate * weight
                total_weight += weight
        
        return weighted_success / total_weight if total_weight > 0 else 0.5
    
    async def _get_historical_success_rate(
        self,
        features: Dict[str, Any]
    ) -> float:
        """Get historical success rate for similar feature combinations"""
        
        # Query similar conversations from database
        # This is a simplified implementation
        return 0.5  # Placeholder
    
    def _get_archetype_recommendations(
        self,
        archetype: UserArchetype
    ) -> List[str]:
        """Get recommendations based on user archetype"""
        
        recommendations = {
            'optimizer': [
                "Focus on performance metrics and ROI calculations",
                "Emphasize efficiency gains and time savings",
                "Present data-driven evidence and case studies"
            ],
            'architect': [
                "Discuss long-term benefits and lifestyle transformation",
                "Emphasize holistic wellness and longevity aspects",
                "Allow time for thorough consideration"
            ],
            'explorer': [
                "Highlight cutting-edge features and innovations",
                "Offer early adopter benefits and exclusive access",
                "Create urgency with limited availability"
            ],
            'pragmatist': [
                "Emphasize value and cost-effectiveness",
                "Provide gradual adoption options",
                "Focus on proven results and reliability"
            ],
            'maximizer': [
                "Present premium features and exclusive benefits",
                "Emphasize status and elite access",
                "Focus on maximum results and optimization"
            ]
        }
        
        return recommendations.get(archetype.name, [])
    
    def _get_pattern_recommendations(
        self,
        patterns: List[ConversationPattern]
    ) -> List[str]:
        """Get recommendations based on identified patterns"""
        
        recommendations = []
        
        for pattern in patterns:
            if pattern.pattern_type == PatternType.CONVERSION_PATTERN.value:
                recommendations.append("Continue current conversation approach - strong conversion signals detected")
            elif pattern.pattern_type == PatternType.OBJECTION_PATTERN.value:
                recommendations.append("Address price objections with value-focused messaging")
            elif pattern.pattern_type == PatternType.ENGAGEMENT_PATTERN.value:
                recommendations.append("Maintain engagement with interactive elements and questions")
        
        return recommendations
    
    def _get_feature_recommendations(
        self,
        features: Dict[str, Any]
    ) -> List[str]:
        """Get recommendations based on specific features"""
        
        recommendations = []
        
        # Behavioral recommendations
        if 'behavioral' in features:
            behavioral = features['behavioral']
            
            if behavioral.get('price_sensitivity', 0) > 0.6:
                recommendations.append("Focus on value proposition and ROI rather than features")
            
            if behavioral.get('decision_readiness', 0) > 0.7:
                recommendations.append("Present clear call-to-action and next steps")
            
            if behavioral.get('information_seeking', 0) > 0.6:
                recommendations.append("Provide detailed information and case studies")
        
        # Emotional recommendations
        if 'emotional' in features:
            emotional = features['emotional']
            
            if emotional.get('concern_indicators', 0) > 0.5:
                recommendations.append("Address concerns proactively with reassurance")
            
            if emotional.get('enthusiasm_indicators', 0) > 0.6:
                recommendations.append("Capitalize on enthusiasm with urgency elements")
        
        return recommendations
    
    def _prioritize_recommendations(
        self,
        recommendations: List[str],
        features: Dict[str, Any]
    ) -> List[str]:
        """Prioritize recommendations based on current context"""
        
        # Simple prioritization - would be more sophisticated in practice
        priority_keywords = {
            'conversion': 10,
            'objection': 9,
            'value': 8,
            'engagement': 7,
            'roi': 6
        }
        
        scored_recs = []
        for rec in recommendations:
            score = 0
            for keyword, weight in priority_keywords.items():
                if keyword in rec.lower():
                    score += weight
            scored_recs.append((rec, score))
        
        # Sort by score and return
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        return [rec for rec, score in scored_recs]
    
    async def _update_pattern_database(
        self,
        patterns: List[ConversationPattern],
        conversation_data: Dict[str, Any]
    ) -> None:
        """Update pattern database with new observations"""
        
        try:
            # Save patterns to database
            for pattern in patterns:
                self.supabase.table('conversation_patterns').upsert({
                    'pattern_id': pattern.pattern_id,
                    'pattern_type': pattern.pattern_type,
                    'confidence': pattern.confidence,
                    'conversation_id': conversation_data.get('id'),
                    'discovered_at': datetime.utcnow().isoformat()
                }).execute()
            
        except Exception as e:
            logger.error(f"Error updating pattern database: {e}")
    
    async def get_pattern_insights(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get insights about discovered patterns"""
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Query pattern data
        response = self.supabase.table('conversation_patterns').select(
            '*'
        ).gte(
            'discovered_at', since
        ).execute()
        
        patterns = response.data
        
        if not patterns:
            return {"message": "No patterns found in the specified timeframe"}
        
        # Analyze patterns
        pattern_types = Counter([p['pattern_type'] for p in patterns])
        avg_confidence = np.mean([p['confidence'] for p in patterns])
        
        # Top patterns by frequency
        top_patterns = pattern_types.most_common(5)
        
        return {
            "total_patterns": len(patterns),
            "average_confidence": avg_confidence,
            "pattern_distribution": dict(pattern_types),
            "top_patterns": top_patterns,
            "discovered_patterns": len(self.discovered_patterns),
            "timeframe_days": days
        }