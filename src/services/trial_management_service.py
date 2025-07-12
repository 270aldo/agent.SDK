"""
Trial Management Service
Manages $29 premium trials with automatic conversion optimization.
Handles trial onboarding, engagement tracking, and conversion workflows.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum

from ..models.base import BaseModel
from ..services.tier_detection_service import TierDetectionService
from ..services.real_time_roi_calculator import RealTimeROICalculator
from ..services.pattern_recognition_engine import PatternRecognitionEngine
from ..integrations.supabase_client import get_supabase_client
from ..integrations.openai_client import get_openai_client
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrialStatus(Enum):
    """Trial status states"""
    PENDING = "pending"
    ACTIVE = "active"
    CONVERTED = "converted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ConversionTrigger(Enum):
    """Types of conversion triggers"""
    TIME_BASED = "time_based"
    ENGAGEMENT_BASED = "engagement_based"
    USAGE_BASED = "usage_based"
    ROI_DEMONSTRATED = "roi_demonstrated"
    SUPPORT_INTERACTION = "support_interaction"
    FEATURE_USAGE = "feature_usage"


class TrialTier(Enum):
    """Available trial tiers"""
    ESSENTIAL_TRIAL = "essential_trial"
    PRO_TRIAL = "pro_trial"
    ELITE_TRIAL = "elite_trial"
    PREMIUM_TRIAL = "premium_trial"  # For PRIME/LONGEVITY


@dataclass
class TrialConfiguration:
    """Trial configuration settings"""
    tier: TrialTier
    duration_days: int
    price: float
    features_included: List[str]
    conversion_targets: List[str]
    engagement_milestones: List[Dict[str, Any]]
    auto_conversion_rules: List[Dict[str, Any]]
    success_metrics: Dict[str, float]


@dataclass
class TrialUser:
    """Trial user profile"""
    user_id: str
    trial_id: str
    email: str
    name: str
    profession: str
    detected_tier: str
    trial_tier: TrialTier
    started_at: datetime
    expires_at: datetime
    status: TrialStatus
    payment_method: Optional[str]
    conversion_probability: float
    engagement_score: float
    usage_metrics: Dict[str, Any]
    touchpoints: List[Dict[str, Any]]
    conversion_triggers: List[ConversionTrigger]
    roi_demonstrated: Dict[str, Any]


@dataclass
class ConversionEvent:
    """Conversion event tracking"""
    event_id: str
    trial_id: str
    event_type: ConversionTrigger
    event_data: Dict[str, Any]
    conversion_score: float
    triggered_actions: List[str]
    timestamp: datetime


class TrialManagementService:
    """
    Advanced trial management with intelligent conversion optimization.
    Provides premium trial experiences with automatic conversion workflows.
    """
    
    def __init__(self):
        self.tier_detection = TierDetectionService()
        self.roi_calculator = RealTimeROICalculator()
        self.pattern_recognition = PatternRecognitionEngine()
        self.supabase = get_supabase_client()
        self.openai = get_openai_client()
        
        # Trial configurations
        self.trial_configs = self._initialize_trial_configs()
        
        # Active trials tracking
        self.active_trials: Dict[str, TrialUser] = {}
        
        # Conversion optimization parameters
        self.conversion_weights = {
            'engagement_score': 0.3,
            'usage_frequency': 0.25,
            'roi_demonstration': 0.2,
            'feature_adoption': 0.15,
            'support_interaction': 0.1
        }
        
        # Engagement milestones
        self.engagement_milestones = {
            'first_login': {'weight': 0.1, 'reward': 'welcome_bonus'},
            'feature_exploration': {'weight': 0.15, 'reward': 'feature_unlock'},
            'daily_usage_3days': {'weight': 0.2, 'reward': 'consistency_badge'},
            'roi_calculation': {'weight': 0.25, 'reward': 'personalized_insights'},
            'demo_completion': {'weight': 0.3, 'reward': 'premium_preview'},
            'social_share': {'weight': 0.1, 'reward': 'referral_bonus'},
            'feedback_provided': {'weight': 0.15, 'reward': 'priority_support'}
        }
    
    async def create_trial(
        self,
        user_context: Dict[str, Any],
        payment_method: str,
        trial_tier: Optional[TrialTier] = None
    ) -> TrialUser:
        """
        Create a new premium trial for a user.
        
        Args:
            user_context: User profile and context
            payment_method: Payment method for trial
            trial_tier: Specific trial tier (auto-detect if None)
        
        Returns:
            Created TrialUser instance
        """
        try:
            # Detect optimal trial tier if not specified
            if not trial_tier:
                detected_tier = user_context.get('detected_tier', 'ESSENTIAL')
                trial_tier = self._map_tier_to_trial(detected_tier)
            
            # Get trial configuration
            config = self.trial_configs[trial_tier]
            
            # Create trial user
            trial_id = str(uuid4())
            user_id = user_context.get('user_id', str(uuid4()))
            
            # Calculate trial dates
            started_at = datetime.utcnow()
            expires_at = started_at + timedelta(days=config.duration_days)
            
            # Calculate initial conversion probability
            conversion_probability = await self._calculate_initial_conversion_probability(
                user_context,
                trial_tier
            )
            
            trial_user = TrialUser(
                user_id=user_id,
                trial_id=trial_id,
                email=user_context.get('email', ''),
                name=user_context.get('name', 'Trial User'),
                profession=user_context.get('profession', ''),
                detected_tier=user_context.get('detected_tier', 'ESSENTIAL'),
                trial_tier=trial_tier,
                started_at=started_at,
                expires_at=expires_at,
                status=TrialStatus.ACTIVE,
                payment_method=payment_method,
                conversion_probability=conversion_probability,
                engagement_score=0.1,  # Starting score
                usage_metrics={},
                touchpoints=[],
                conversion_triggers=[],
                roi_demonstrated={}
            )
            
            # Save to database
            await self._save_trial_user(trial_user)
            
            # Add to active trials
            self.active_trials[trial_id] = trial_user
            
            # Initialize trial onboarding
            await self._initialize_trial_onboarding(trial_user)
            
            # Log trial creation
            await self._log_trial_event(trial_id, 'trial_created', {
                'trial_tier': trial_tier.value,
                'user_context': user_context,
                'conversion_probability': conversion_probability
            })
            
            return trial_user
            
        except Exception as e:
            logger.error(f"Error creating trial: {e}")
            raise
    
    async def track_trial_engagement(
        self,
        trial_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track trial user engagement and update metrics"""
        
        trial_user = self.active_trials.get(trial_id)
        if not trial_user:
            trial_user = await self._load_trial_user(trial_id)
            if not trial_user:
                raise ValueError(f"Trial {trial_id} not found")
        
        # Update usage metrics
        await self._update_usage_metrics(trial_user, activity_data)
        
        # Check for milestone achievements
        milestones_achieved = await self._check_milestones(trial_user, activity_data)
        
        # Update engagement score
        new_engagement_score = await self._calculate_engagement_score(trial_user)
        trial_user.engagement_score = new_engagement_score
        
        # Update conversion probability
        new_conversion_probability = await self._update_conversion_probability(trial_user)
        trial_user.conversion_probability = new_conversion_probability
        
        # Check for conversion triggers
        triggered_events = await self._check_conversion_triggers(trial_user, activity_data)
        
        # Save updates
        await self._save_trial_user(trial_user)
        
        # Execute triggered actions
        actions_taken = []
        for event in triggered_events:
            actions = await self._execute_conversion_actions(event)
            actions_taken.extend(actions)
        
        return {
            'trial_id': trial_id,
            'engagement_score': new_engagement_score,
            'conversion_probability': new_conversion_probability,
            'milestones_achieved': milestones_achieved,
            'conversion_events': [e.__dict__ for e in triggered_events],
            'actions_taken': actions_taken,
            'trial_status': trial_user.status.value
        }
    
    async def process_conversion_attempt(
        self,
        trial_id: str,
        conversion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a conversion attempt"""
        
        trial_user = self.active_trials.get(trial_id)
        if not trial_user:
            trial_user = await self._load_trial_user(trial_id)
            if not trial_user:
                raise ValueError(f"Trial {trial_id} not found")
        
        # Analyze conversion readiness
        readiness_analysis = await self._analyze_conversion_readiness(trial_user)
        
        # Generate personalized conversion offer
        conversion_offer = await self._generate_conversion_offer(
            trial_user,
            readiness_analysis,
            conversion_data
        )
        
        # Calculate conversion probability for this attempt
        attempt_probability = await self._calculate_attempt_probability(
            trial_user,
            conversion_data,
            readiness_analysis
        )
        
        # Log conversion attempt
        await self._log_trial_event(trial_id, 'conversion_attempt', {
            'attempt_probability': attempt_probability,
            'readiness_score': readiness_analysis['readiness_score'],
            'conversion_data': conversion_data
        })
        
        return {
            'trial_id': trial_id,
            'conversion_offer': conversion_offer,
            'attempt_probability': attempt_probability,
            'readiness_analysis': readiness_analysis,
            'recommended_timing': readiness_analysis.get('optimal_timing'),
            'personalization': conversion_offer.get('personalization')
        }
    
    async def complete_conversion(
        self,
        trial_id: str,
        selected_plan: str,
        payment_confirmed: bool
    ) -> Dict[str, Any]:
        """Complete trial conversion to paid plan"""
        
        trial_user = self.active_trials.get(trial_id)
        if not trial_user:
            trial_user = await self._load_trial_user(trial_id)
            if not trial_user:
                raise ValueError(f"Trial {trial_id} not found")
        
        if payment_confirmed:
            # Update trial status
            trial_user.status = TrialStatus.CONVERTED
            
            # Calculate conversion metrics
            conversion_metrics = await self._calculate_conversion_metrics(
                trial_user,
                selected_plan
            )
            
            # Generate post-conversion onboarding
            onboarding_plan = await self._generate_post_conversion_onboarding(
                trial_user,
                selected_plan
            )
            
            # Update ML models with successful conversion data
            await self._update_conversion_models(trial_user, selected_plan)
            
            # Clean up trial
            await self._cleanup_converted_trial(trial_user)
            
            await self._log_trial_event(trial_id, 'conversion_completed', {
                'selected_plan': selected_plan,
                'conversion_metrics': conversion_metrics
            })
            
            return {
                'success': True,
                'trial_id': trial_id,
                'converted_plan': selected_plan,
                'conversion_metrics': conversion_metrics,
                'onboarding_plan': onboarding_plan
            }
        else:
            # Handle failed payment
            await self._handle_payment_failure(trial_user)
            
            return {
                'success': False,
                'trial_id': trial_id,
                'message': 'Payment failed - trial extended',
                'recovery_actions': await self._generate_recovery_actions(trial_user)
            }
    
    async def get_trial_insights(
        self,
        trial_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive insights for a trial"""
        
        trial_user = self.active_trials.get(trial_id)
        if not trial_user:
            trial_user = await self._load_trial_user(trial_id)
            if not trial_user:
                raise ValueError(f"Trial {trial_id} not found")
        
        # Generate usage insights
        usage_insights = await self._generate_usage_insights(trial_user)
        
        # Calculate ROI demonstrated
        roi_insights = await self._calculate_trial_roi_insights(trial_user)
        
        # Get behavioral patterns
        behavior_patterns = await self._analyze_behavior_patterns(trial_user)
        
        # Generate recommendations
        recommendations = await self._generate_trial_recommendations(trial_user)
        
        # Calculate time remaining
        time_remaining = (trial_user.expires_at - datetime.utcnow()).total_seconds()
        days_remaining = max(0, time_remaining / 86400)
        
        return {
            'trial_id': trial_id,
            'trial_status': trial_user.status.value,
            'days_remaining': days_remaining,
            'engagement_score': trial_user.engagement_score,
            'conversion_probability': trial_user.conversion_probability,
            'usage_insights': usage_insights,
            'roi_insights': roi_insights,
            'behavior_patterns': behavior_patterns,
            'recommendations': recommendations,
            'milestones_progress': await self._get_milestones_progress(trial_user)
        }
    
    def _initialize_trial_configs(self) -> Dict[TrialTier, TrialConfiguration]:
        """Initialize trial configurations"""
        
        return {
            TrialTier.ESSENTIAL_TRIAL: TrialConfiguration(
                tier=TrialTier.ESSENTIAL_TRIAL,
                duration_days=14,
                price=29.0,
                features_included=[
                    'basic_hie_access',
                    'daily_optimization',
                    'progress_tracking',
                    'mobile_app',
                    'email_support'
                ],
                conversion_targets=['ESSENTIAL', 'PRO'],
                engagement_milestones=[
                    {'milestone': 'first_login', 'day': 1, 'reward': 'welcome_guide'},
                    {'milestone': 'daily_usage_3days', 'day': 3, 'reward': 'consistency_badge'},
                    {'milestone': 'feature_exploration', 'day': 7, 'reward': 'advanced_tips'}
                ],
                auto_conversion_rules=[
                    {'trigger': 'high_engagement', 'threshold': 0.8, 'action': 'offer_discount'},
                    {'trigger': 'roi_demonstrated', 'threshold': 200, 'action': 'emphasize_value'}
                ],
                success_metrics={
                    'daily_usage': 0.7,
                    'feature_adoption': 0.6,
                    'engagement_score': 0.65
                }
            ),
            
            TrialTier.PRO_TRIAL: TrialConfiguration(
                tier=TrialTier.PRO_TRIAL,
                duration_days=14,
                price=29.0,
                features_included=[
                    'advanced_hie_access',
                    'personalized_optimization',
                    'advanced_analytics',
                    'priority_support',
                    'custom_protocols'
                ],
                conversion_targets=['PRO', 'ELITE'],
                engagement_milestones=[
                    {'milestone': 'first_login', 'day': 1, 'reward': 'pro_welcome_package'},
                    {'milestone': 'protocol_customization', 'day': 2, 'reward': 'personalization_boost'},
                    {'milestone': 'analytics_review', 'day': 5, 'reward': 'insights_report'}
                ],
                auto_conversion_rules=[
                    {'trigger': 'protocol_success', 'threshold': 0.75, 'action': 'highlight_results'},
                    {'trigger': 'time_based', 'day': 10, 'action': 'conversion_reminder'}
                ],
                success_metrics={
                    'protocol_completion': 0.8,
                    'analytics_engagement': 0.7,
                    'customization_usage': 0.6
                }
            ),
            
            TrialTier.ELITE_TRIAL: TrialConfiguration(
                tier=TrialTier.ELITE_TRIAL,
                duration_days=14,
                price=29.0,
                features_included=[
                    'elite_hie_access',
                    'ai_coaching',
                    'biometric_integration',
                    'performance_optimization',
                    'concierge_support'
                ],
                conversion_targets=['ELITE', 'PRIME'],
                engagement_milestones=[
                    {'milestone': 'ai_coach_setup', 'day': 1, 'reward': 'elite_onboarding'},
                    {'milestone': 'biometric_sync', 'day': 3, 'reward': 'data_insights'},
                    {'milestone': 'performance_goals', 'day': 7, 'reward': 'goal_tracker'}
                ],
                auto_conversion_rules=[
                    {'trigger': 'performance_improvement', 'threshold': 0.25, 'action': 'showcase_results'},
                    {'trigger': 'ai_engagement', 'threshold': 0.8, 'action': 'highlight_ai_value'}
                ],
                success_metrics={
                    'ai_coach_usage': 0.75,
                    'biometric_sync': 0.8,
                    'performance_gains': 0.2
                }
            ),
            
            TrialTier.PREMIUM_TRIAL: TrialConfiguration(
                tier=TrialTier.PREMIUM_TRIAL,
                duration_days=14,
                price=29.0,
                features_included=[
                    'full_hie_access',
                    'premium_protocols',
                    'expert_consultation',
                    'advanced_biometrics',
                    'custom_development',
                    'white_glove_service'
                ],
                conversion_targets=['PRIME', 'LONGEVITY'],
                engagement_milestones=[
                    {'milestone': 'expert_consultation', 'day': 1, 'reward': 'vip_treatment'},
                    {'milestone': 'custom_protocol', 'day': 3, 'reward': 'personalized_plan'},
                    {'milestone': 'advanced_metrics', 'day': 7, 'reward': 'detailed_analysis'}
                ],
                auto_conversion_rules=[
                    {'trigger': 'expert_recommendation', 'threshold': 1.0, 'action': 'expert_endorsement'},
                    {'trigger': 'premium_results', 'threshold': 0.3, 'action': 'results_showcase'}
                ],
                success_metrics={
                    'expert_engagement': 0.9,
                    'custom_protocol_success': 0.85,
                    'premium_feature_usage': 0.8
                }
            )
        }
    
    def _map_tier_to_trial(self, detected_tier: str) -> TrialTier:
        """Map detected tier to appropriate trial tier"""
        
        mapping = {
            'ESSENTIAL': TrialTier.ESSENTIAL_TRIAL,
            'PRO': TrialTier.PRO_TRIAL,
            'ELITE': TrialTier.ELITE_TRIAL,
            'PRIME': TrialTier.PREMIUM_TRIAL,
            'LONGEVITY': TrialTier.PREMIUM_TRIAL
        }
        
        return mapping.get(detected_tier, TrialTier.ESSENTIAL_TRIAL)
    
    async def _calculate_initial_conversion_probability(
        self,
        user_context: Dict[str, Any],
        trial_tier: TrialTier
    ) -> float:
        """Calculate initial conversion probability"""
        
        # Base probability by tier
        base_probabilities = {
            TrialTier.ESSENTIAL_TRIAL: 0.35,
            TrialTier.PRO_TRIAL: 0.45,
            TrialTier.ELITE_TRIAL: 0.55,
            TrialTier.PREMIUM_TRIAL: 0.65
        }
        
        base_prob = base_probabilities[trial_tier]
        
        # Adjust based on user context
        profession = user_context.get('profession', '').lower()
        if profession in ['ceo', 'executive', 'entrepreneur']:
            base_prob += 0.15
        elif profession in ['consultant', 'doctor', 'lawyer']:
            base_prob += 0.10
        elif profession == 'student':
            base_prob -= 0.10
        
        # Adjust based on touchpoint
        touchpoint = user_context.get('touchpoint', '')
        if touchpoint == 'referral':
            base_prob += 0.20
        elif touchpoint == 'demo_completion':
            base_prob += 0.15
        elif touchpoint == 'roi_calculator':
            base_prob += 0.10
        
        return min(0.95, max(0.05, base_prob))
    
    async def _save_trial_user(self, trial_user: TrialUser) -> None:
        """Save trial user to database"""
        
        try:
            self.supabase.table('trial_users').upsert({
                'trial_id': trial_user.trial_id,
                'user_id': trial_user.user_id,
                'email': trial_user.email,
                'name': trial_user.name,
                'profession': trial_user.profession,
                'detected_tier': trial_user.detected_tier,
                'trial_tier': trial_user.trial_tier.value,
                'started_at': trial_user.started_at.isoformat(),
                'expires_at': trial_user.expires_at.isoformat(),
                'status': trial_user.status.value,
                'payment_method': trial_user.payment_method,
                'conversion_probability': trial_user.conversion_probability,
                'engagement_score': trial_user.engagement_score,
                'usage_metrics': json.dumps(trial_user.usage_metrics),
                'touchpoints': json.dumps([tp.__dict__ if hasattr(tp, '__dict__') else tp for tp in trial_user.touchpoints]),
                'conversion_triggers': json.dumps([ct.value for ct in trial_user.conversion_triggers]),
                'roi_demonstrated': json.dumps(trial_user.roi_demonstrated)
            }).execute()
        except Exception as e:
            logger.error(f"Error saving trial user: {e}")
    
    async def _load_trial_user(self, trial_id: str) -> Optional[TrialUser]:
        """Load trial user from database"""
        
        try:
            response = self.supabase.table('trial_users').select(
                '*'
            ).eq('trial_id', trial_id).execute()
            
            if not response.data:
                return None
            
            data = response.data[0]
            
            return TrialUser(
                user_id=data['user_id'],
                trial_id=data['trial_id'],
                email=data['email'],
                name=data['name'],
                profession=data['profession'],
                detected_tier=data['detected_tier'],
                trial_tier=TrialTier(data['trial_tier']),
                started_at=datetime.fromisoformat(data['started_at']),
                expires_at=datetime.fromisoformat(data['expires_at']),
                status=TrialStatus(data['status']),
                payment_method=data['payment_method'],
                conversion_probability=data['conversion_probability'],
                engagement_score=data['engagement_score'],
                usage_metrics=json.loads(data['usage_metrics']),
                touchpoints=json.loads(data['touchpoints']),
                conversion_triggers=[ConversionTrigger(ct) for ct in json.loads(data['conversion_triggers'])],
                roi_demonstrated=json.loads(data['roi_demonstrated'])
            )
        except Exception as e:
            logger.error(f"Error loading trial user: {e}")
            return None
    
    async def _initialize_trial_onboarding(self, trial_user: TrialUser) -> None:
        """Initialize trial onboarding sequence"""
        
        config = self.trial_configs[trial_user.trial_tier]
        
        # Create onboarding touchpoints
        onboarding_sequence = [
            {
                'type': 'welcome_email',
                'scheduled_at': trial_user.started_at,
                'content': 'trial_welcome',
                'personalization': {
                    'name': trial_user.name,
                    'profession': trial_user.profession,
                    'trial_tier': trial_user.trial_tier.value
                }
            },
            {
                'type': 'feature_introduction',
                'scheduled_at': trial_user.started_at + timedelta(hours=2),
                'content': 'feature_walkthrough',
                'features': config.features_included
            },
            {
                'type': 'engagement_check',
                'scheduled_at': trial_user.started_at + timedelta(days=3),
                'content': 'usage_tips',
                'conditional': {'min_usage': 1}
            },
            {
                'type': 'conversion_prep',
                'scheduled_at': trial_user.started_at + timedelta(days=10),
                'content': 'value_reinforcement',
                'roi_calculation': True
            }
        ]
        
        # Schedule onboarding touchpoints
        for touchpoint in onboarding_sequence:
            await self._schedule_touchpoint(trial_user.trial_id, touchpoint)
    
    async def _update_usage_metrics(
        self,
        trial_user: TrialUser,
        activity_data: Dict[str, Any]
    ) -> None:
        """Update usage metrics for trial user"""
        
        activity_type = activity_data.get('type', 'unknown')
        timestamp = datetime.fromisoformat(activity_data.get('timestamp', datetime.utcnow().isoformat()))
        
        # Initialize metrics if empty
        if not trial_user.usage_metrics:
            trial_user.usage_metrics = {
                'login_count': 0,
                'feature_usage': {},
                'session_duration': [],
                'daily_usage': {},
                'milestones': []
            }
        
        # Update based on activity type
        if activity_type == 'login':
            trial_user.usage_metrics['login_count'] += 1
            
            # Track daily usage
            date_str = timestamp.date().isoformat()
            trial_user.usage_metrics['daily_usage'][date_str] = trial_user.usage_metrics['daily_usage'].get(date_str, 0) + 1
        
        elif activity_type == 'feature_usage':
            feature = activity_data.get('feature', 'unknown')
            trial_user.usage_metrics['feature_usage'][feature] = trial_user.usage_metrics['feature_usage'].get(feature, 0) + 1
        
        elif activity_type == 'session_end':
            duration = activity_data.get('duration_seconds', 0)
            trial_user.usage_metrics['session_duration'].append(duration)
        
        # Add touchpoint
        touchpoint = {
            'type': activity_type,
            'timestamp': timestamp.isoformat(),
            'data': activity_data
        }
        trial_user.touchpoints.append(touchpoint)
    
    async def _check_milestones(
        self,
        trial_user: TrialUser,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Check for achieved milestones"""
        
        milestones_achieved = []
        current_milestones = trial_user.usage_metrics.get('milestones', [])
        
        # Check each milestone
        for milestone, criteria in self.engagement_milestones.items():
            if milestone in current_milestones:
                continue  # Already achieved
            
            achieved = False
            
            if milestone == 'first_login' and trial_user.usage_metrics.get('login_count', 0) >= 1:
                achieved = True
            elif milestone == 'daily_usage_3days':
                daily_usage = trial_user.usage_metrics.get('daily_usage', {})
                if len(daily_usage) >= 3:
                    achieved = True
            elif milestone == 'feature_exploration':
                feature_usage = trial_user.usage_metrics.get('feature_usage', {})
                if len(feature_usage) >= 3:
                    achieved = True
            elif milestone == 'roi_calculation' and activity_data.get('type') == 'roi_calculated':
                achieved = True
            elif milestone == 'demo_completion' and activity_data.get('type') == 'demo_completed':
                achieved = True
            
            if achieved:
                milestones_achieved.append(milestone)
                trial_user.usage_metrics['milestones'].append(milestone)
        
        return milestones_achieved
    
    async def _calculate_engagement_score(self, trial_user: TrialUser) -> float:
        """Calculate engagement score for trial user"""
        
        metrics = trial_user.usage_metrics
        
        # Base engagement factors
        login_frequency = min(1.0, metrics.get('login_count', 0) / 14)  # Normalized to trial duration
        feature_diversity = min(1.0, len(metrics.get('feature_usage', {})) / 5)  # Max 5 main features
        daily_consistency = len(metrics.get('daily_usage', {})) / 14  # Days used out of 14
        
        # Session quality
        session_durations = metrics.get('session_duration', [])
        avg_session = sum(session_durations) / len(session_durations) if session_durations else 0
        session_quality = min(1.0, avg_session / 1800)  # 30 minutes = good session
        
        # Milestone progress
        milestones_achieved = len(metrics.get('milestones', []))
        milestone_score = milestones_achieved / len(self.engagement_milestones)
        
        # Weighted engagement score
        engagement_score = (
            login_frequency * 0.2 +
            feature_diversity * 0.2 +
            daily_consistency * 0.3 +
            session_quality * 0.15 +
            milestone_score * 0.15
        )
        
        return min(1.0, engagement_score)
    
    async def _update_conversion_probability(self, trial_user: TrialUser) -> float:
        """Update conversion probability based on trial progress"""
        
        base_probability = trial_user.conversion_probability
        
        # Engagement impact
        engagement_impact = (trial_user.engagement_score - 0.5) * 0.3
        
        # ROI demonstration impact
        roi_impact = 0
        if trial_user.roi_demonstrated:
            roi_percentage = trial_user.roi_demonstrated.get('total_roi_percentage', 0)
            if roi_percentage > 300:
                roi_impact = 0.2
            elif roi_percentage > 200:
                roi_impact = 0.15
            elif roi_percentage > 100:
                roi_impact = 0.1
        
        # Time decay (urgency increases as trial expires)
        days_remaining = (trial_user.expires_at - datetime.utcnow()).days
        time_urgency = max(0, (14 - days_remaining) / 14 * 0.1)
        
        # Feature adoption impact
        feature_usage = trial_user.usage_metrics.get('feature_usage', {})
        config = self.trial_configs[trial_user.trial_tier]
        features_used = len(feature_usage)
        features_available = len(config.features_included)
        adoption_impact = (features_used / features_available) * 0.15
        
        new_probability = base_probability + engagement_impact + roi_impact + time_urgency + adoption_impact
        
        return min(0.95, max(0.05, new_probability))
    
    async def _check_conversion_triggers(
        self,
        trial_user: TrialUser,
        activity_data: Dict[str, Any]
    ) -> List[ConversionEvent]:
        """Check for conversion triggers"""
        
        events = []
        
        # High engagement trigger
        if (trial_user.engagement_score > 0.8 and 
            ConversionTrigger.ENGAGEMENT_BASED not in trial_user.conversion_triggers):
            
            event = ConversionEvent(
                event_id=str(uuid4()),
                trial_id=trial_user.trial_id,
                event_type=ConversionTrigger.ENGAGEMENT_BASED,
                event_data={'engagement_score': trial_user.engagement_score},
                conversion_score=0.8,
                triggered_actions=['send_high_engagement_offer'],
                timestamp=datetime.utcnow()
            )
            events.append(event)
            trial_user.conversion_triggers.append(ConversionTrigger.ENGAGEMENT_BASED)
        
        # ROI demonstrated trigger
        if (trial_user.roi_demonstrated and 
            trial_user.roi_demonstrated.get('total_roi_percentage', 0) > 200 and
            ConversionTrigger.ROI_DEMONSTRATED not in trial_user.conversion_triggers):
            
            event = ConversionEvent(
                event_id=str(uuid4()),
                trial_id=trial_user.trial_id,
                event_type=ConversionTrigger.ROI_DEMONSTRATED,
                event_data=trial_user.roi_demonstrated,
                conversion_score=0.75,
                triggered_actions=['send_roi_conversion_offer'],
                timestamp=datetime.utcnow()
            )
            events.append(event)
            trial_user.conversion_triggers.append(ConversionTrigger.ROI_DEMONSTRATED)
        
        # Feature usage trigger
        feature_usage = trial_user.usage_metrics.get('feature_usage', {})
        if (len(feature_usage) >= 4 and 
            ConversionTrigger.FEATURE_USAGE not in trial_user.conversion_triggers):
            
            event = ConversionEvent(
                event_id=str(uuid4()),
                trial_id=trial_user.trial_id,
                event_type=ConversionTrigger.FEATURE_USAGE,
                event_data={'features_used': list(feature_usage.keys())},
                conversion_score=0.7,
                triggered_actions=['send_feature_value_message'],
                timestamp=datetime.utcnow()
            )
            events.append(event)
            trial_user.conversion_triggers.append(ConversionTrigger.FEATURE_USAGE)
        
        # Time-based triggers
        days_in_trial = (datetime.utcnow() - trial_user.started_at).days
        if (days_in_trial >= 10 and 
            ConversionTrigger.TIME_BASED not in trial_user.conversion_triggers):
            
            event = ConversionEvent(
                event_id=str(uuid4()),
                trial_id=trial_user.trial_id,
                event_type=ConversionTrigger.TIME_BASED,
                event_data={'days_in_trial': days_in_trial},
                conversion_score=0.6,
                triggered_actions=['send_time_urgency_message'],
                timestamp=datetime.utcnow()
            )
            events.append(event)
            trial_user.conversion_triggers.append(ConversionTrigger.TIME_BASED)
        
        return events
    
    async def _execute_conversion_actions(
        self,
        event: ConversionEvent
    ) -> List[str]:
        """Execute actions triggered by conversion events"""
        
        actions_taken = []
        
        for action in event.triggered_actions:
            try:
                if action == 'send_high_engagement_offer':
                    await self._send_personalized_offer(event.trial_id, 'high_engagement')
                    actions_taken.append('sent_high_engagement_offer')
                
                elif action == 'send_roi_conversion_offer':
                    await self._send_personalized_offer(event.trial_id, 'roi_demonstrated')
                    actions_taken.append('sent_roi_offer')
                
                elif action == 'send_feature_value_message':
                    await self._send_feature_value_message(event.trial_id)
                    actions_taken.append('sent_feature_value_message')
                
                elif action == 'send_time_urgency_message':
                    await self._send_urgency_message(event.trial_id)
                    actions_taken.append('sent_urgency_message')
                
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")
        
        return actions_taken
    
    async def _analyze_conversion_readiness(
        self,
        trial_user: TrialUser
    ) -> Dict[str, Any]:
        """Analyze user's readiness for conversion"""
        
        # Calculate readiness factors
        engagement_readiness = trial_user.engagement_score
        usage_readiness = len(trial_user.usage_metrics.get('feature_usage', {})) / 5  # Normalized
        roi_readiness = 1.0 if trial_user.roi_demonstrated else 0.3
        time_readiness = min(1.0, (datetime.utcnow() - trial_user.started_at).days / 7)  # Week milestone
        
        # Overall readiness score
        readiness_score = (
            engagement_readiness * 0.3 +
            usage_readiness * 0.25 +
            roi_readiness * 0.25 +
            time_readiness * 0.2
        )
        
        # Determine optimal timing
        days_remaining = (trial_user.expires_at - datetime.utcnow()).days
        if readiness_score > 0.8:
            optimal_timing = 'now'
        elif readiness_score > 0.6:
            optimal_timing = 'within_2_days'
        elif days_remaining <= 3:
            optimal_timing = 'urgent'
        else:
            optimal_timing = 'continue_nurturing'
        
        # Identify blockers
        blockers = []
        if engagement_readiness < 0.5:
            blockers.append('low_engagement')
        if not trial_user.roi_demonstrated:
            blockers.append('roi_not_demonstrated')
        if usage_readiness < 0.4:
            blockers.append('limited_feature_usage')
        
        return {
            'readiness_score': readiness_score,
            'optimal_timing': optimal_timing,
            'engagement_readiness': engagement_readiness,
            'usage_readiness': usage_readiness,
            'roi_readiness': roi_readiness,
            'time_readiness': time_readiness,
            'blockers': blockers,
            'conversion_probability': trial_user.conversion_probability
        }
    
    async def _generate_conversion_offer(
        self,
        trial_user: TrialUser,
        readiness_analysis: Dict[str, Any],
        conversion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized conversion offer"""
        
        config = self.trial_configs[trial_user.trial_tier]
        
        # Base offer
        offer = {
            'trial_id': trial_user.trial_id,
            'recommended_plans': config.conversion_targets,
            'discount_percentage': 0,
            'urgency_level': 'medium',
            'personalization': {},
            'value_propositions': [],
            'social_proof': [],
            'guarantees': ['30_day_money_back'],
            'bonuses': []
        }
        
        # Personalize based on readiness
        readiness_score = readiness_analysis['readiness_score']
        
        if readiness_score > 0.8:
            offer['discount_percentage'] = 20
            offer['urgency_level'] = 'high'
            offer['bonuses'].append('early_adopter_bonus')
        elif readiness_score > 0.6:
            offer['discount_percentage'] = 15
            offer['bonuses'].append('trial_completion_bonus')
        elif readiness_score < 0.4:
            offer['discount_percentage'] = 10
            offer['bonuses'].append('extended_trial')
        
        # Add profession-specific value propositions
        profession = trial_user.profession.lower()
        if profession in ['ceo', 'executive']:
            offer['value_propositions'].extend([
                'Enhanced decision-making clarity',
                'Improved leadership stamina',
                'Competitive advantage through optimization'
            ])
        elif profession == 'consultant':
            offer['value_propositions'].extend([
                'Increased billable hour efficiency',
                'Enhanced client problem-solving',
                'ROI delivery for clients'
            ])
        elif profession == 'doctor':
            offer['value_propositions'].extend([
                'Improved patient care quality',
                'Enhanced diagnostic focus',
                'Reduced medical professional burnout'
            ])
        
        # Add ROI-specific messaging
        if trial_user.roi_demonstrated:
            roi_percentage = trial_user.roi_demonstrated.get('total_roi_percentage', 0)
            offer['personalization']['roi_message'] = f"You've already seen {roi_percentage:.0f}% ROI in your trial"
            offer['value_propositions'].append(f'Proven {roi_percentage:.0f}% ROI in your specific use case')
        
        # Add social proof
        offer['social_proof'] = [
            f"Join 10,000+ {profession}s already using HIE",
            "95% of trial users convert to paid plans",
            "Average user sees 300%+ ROI in first month"
        ]
        
        return offer
    
    async def _calculate_attempt_probability(
        self,
        trial_user: TrialUser,
        conversion_data: Dict[str, Any],
        readiness_analysis: Dict[str, Any]
    ) -> float:
        """Calculate probability of successful conversion for this attempt"""
        
        base_probability = trial_user.conversion_probability
        readiness_modifier = readiness_analysis['readiness_score'] * 0.3
        
        # Context modifiers
        urgency_modifier = 0
        if conversion_data.get('triggered_by') == 'expiration_warning':
            urgency_modifier = 0.15
        elif conversion_data.get('triggered_by') == 'high_engagement':
            urgency_modifier = 0.1
        
        # Timing modifier
        time_of_day = datetime.utcnow().hour
        if 9 <= time_of_day <= 17:  # Business hours
            timing_modifier = 0.05
        else:
            timing_modifier = -0.05
        
        attempt_probability = base_probability + readiness_modifier + urgency_modifier + timing_modifier
        
        return min(0.95, max(0.05, attempt_probability))
    
    async def _send_personalized_offer(
        self,
        trial_id: str,
        offer_type: str
    ) -> None:
        """Send personalized conversion offer"""
        
        # Implementation would integrate with email/notification system
        logger.info(f"Sending {offer_type} offer to trial {trial_id}")
    
    async def _send_feature_value_message(self, trial_id: str) -> None:
        """Send feature value reinforcement message"""
        logger.info(f"Sending feature value message to trial {trial_id}")
    
    async def _send_urgency_message(self, trial_id: str) -> None:
        """Send urgency/expiration message"""
        logger.info(f"Sending urgency message to trial {trial_id}")
    
    async def _schedule_touchpoint(
        self,
        trial_id: str,
        touchpoint: Dict[str, Any]
    ) -> None:
        """Schedule a touchpoint for later execution"""
        
        try:
            self.supabase.table('scheduled_touchpoints').insert({
                'trial_id': trial_id,
                'touchpoint_data': json.dumps(touchpoint),
                'scheduled_at': touchpoint['scheduled_at'].isoformat(),
                'status': 'pending'
            }).execute()
        except Exception as e:
            logger.error(f"Error scheduling touchpoint: {e}")
    
    async def _log_trial_event(
        self,
        trial_id: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Log trial event for analytics"""
        
        try:
            self.supabase.table('trial_events').insert({
                'trial_id': trial_id,
                'event_type': event_type,
                'data': json.dumps(data),
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error logging trial event: {e}")
    
    async def get_trial_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get trial analytics"""
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get trial events
        response = self.supabase.table('trial_events').select(
            '*'
        ).gte('created_at', since).execute()
        
        events = response.data
        
        if not events:
            return {"message": "No trial data found"}
        
        # Get trial users
        users_response = self.supabase.table('trial_users').select(
            '*'
        ).gte('started_at', since).execute()
        
        users = users_response.data
        
        # Calculate metrics
        total_trials = len(users)
        converted_trials = len([u for u in users if u['status'] == 'converted'])
        active_trials = len([u for u in users if u['status'] == 'active'])
        
        conversion_rate = converted_trials / total_trials if total_trials > 0 else 0
        
        # Average metrics
        if users:
            avg_engagement = sum(u['engagement_score'] for u in users) / len(users)
            avg_conversion_prob = sum(u['conversion_probability'] for u in users) / len(users)
        else:
            avg_engagement = 0
            avg_conversion_prob = 0
        
        # Trial tier distribution
        tier_distribution = {}
        for user in users:
            tier = user['trial_tier']
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        return {
            "total_trials": total_trials,
            "active_trials": active_trials,
            "converted_trials": converted_trials,
            "conversion_rate": conversion_rate,
            "average_engagement": avg_engagement,
            "average_conversion_probability": avg_conversion_prob,
            "tier_distribution": tier_distribution,
            "timeframe_days": days
        }