"""
NGX AGENTS ACCESS Live Demonstration Service
Interactive demonstration system for showcasing NGX agents capabilities during conversations.
Provides real-time mini-demos, interactive experiences, and compelling showcases.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum

from ..models.base import BaseModel
from ..services.tier_detection_service import TierDetectionService
from ..services.ngx_master_knowledge import get_ngx_knowledge, NGXArchetype, AgentType
from ..integrations.supabase_client import get_supabase_client
from ..integrations.openai_client import get_openai_client
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DemoType(Enum):
    """Types of NGX AGENTS ACCESS demonstrations"""
    FOCUS_ENHANCEMENT = "focus_enhancement"
    ENERGY_OPTIMIZATION = "energy_optimization"
    STRESS_REDUCTION = "stress_reduction"
    COGNITIVE_BOOST = "cognitive_boost"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    PERSONALIZED_INSIGHTS = "personalized_insights"
    REAL_TIME_BIOMETRICS = "real_time_biometrics"
    PRODUCTIVITY_SIMULATION = "productivity_simulation"


class InteractionMode(Enum):
    """Modes of user interaction"""
    PASSIVE_WATCH = "passive_watch"
    ACTIVE_PARTICIPATION = "active_participation"
    GUIDED_EXPERIENCE = "guided_experience"
    SELF_ASSESSMENT = "self_assessment"


@dataclass
class DemoStep:
    """Individual step in a demonstration"""
    step_id: str
    title: str
    description: str
    duration_seconds: int
    interaction_type: str
    user_prompt: Optional[str]
    expected_response: Optional[str]
    visual_elements: List[Dict[str, Any]]
    audio_cues: List[str]
    biometric_simulation: Optional[Dict[str, Any]]
    success_criteria: Dict[str, Any]


@dataclass
class DemoSession:
    """Complete demonstration session"""
    session_id: str
    demo_type: DemoType
    user_id: str
    user_context: Dict[str, Any]
    steps: List[DemoStep]
    interaction_mode: InteractionMode
    personalization: Dict[str, Any]
    expected_outcomes: List[str]
    success_metrics: Dict[str, float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: Optional[Dict[str, Any]]


@dataclass
class DemoResult:
    """Results from a completed demonstration"""
    session_id: str
    demo_type: DemoType
    user_engagement: float
    completion_rate: float
    success_score: float
    user_feedback: Dict[str, Any]
    biometric_improvements: Dict[str, float]
    conversion_impact: float
    insights_generated: List[str]
    next_recommendations: List[str]


class LiveDemoService:
    """
    Service for creating and managing live NGX AGENTS ACCESS demonstrations.
    Provides interactive, personalized experiences that showcase NGX agents benefits.
    """
    
    def __init__(self):
        self.tier_detection = TierDetectionService()
        self.supabase = get_supabase_client()
        self.openai = get_openai_client()
        
        # Demo templates
        self.demo_templates = self._initialize_demo_templates()
        
        # Active sessions
        self.active_sessions: Dict[str, DemoSession] = {}
        
        # Biometric simulation parameters
        self.baseline_metrics = {
            'heart_rate': 72,
            'stress_level': 0.6,
            'focus_score': 0.5,
            'energy_level': 0.6,
            'cognitive_load': 0.7,
            'reaction_time': 450,  # milliseconds
            'attention_span': 300,  # seconds
        }
        
        # HIE improvement factors
        self.hie_multipliers = {
            'heart_rate_variability': 1.25,
            'stress_reduction': 0.4,  # 40% reduction
            'focus_improvement': 1.35,  # 35% improvement
            'energy_boost': 1.3,
            'cognitive_enhancement': 1.4,
            'reaction_time_improvement': 0.85,  # 15% faster
            'attention_extension': 1.6,  # 60% longer
        }
    
    async def create_personalized_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode = InteractionMode.GUIDED_EXPERIENCE
    ) -> DemoSession:
        """Create personalized demo for NGX AGENTS ACCESS"""
        
        try:
            return await self._create_ngx_agents_demo(user_context, demo_type, interaction_mode)
        except Exception as e:
            logger.warning(f"NGX agents demo failed, falling back to standard: {e}")
            return await self._create_standard_demo(user_context, demo_type, interaction_mode)
    
    async def _create_ngx_agents_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode
    ) -> DemoSession:
        """Create NGX AGENTS ACCESS demonstration"""
        
        # Get NGX knowledge system
        ngx_knowledge = get_ngx_knowledge()
        
        # Generate NGX context for this user
        ngx_context = ngx_knowledge.generate_ngx_context(user_context)
        
        # Create NGX-specific demo
        demo_session = await self._build_ngx_agents_demo(
            user_context,
            demo_type,
            interaction_mode,
            ngx_context
        )
        
        return demo_session
    
    async def _build_ngx_agents_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        ngx_context: Dict[str, Any]
    ) -> DemoSession:
        """Build NGX AGENTS ACCESS demonstration"""
        
        suggested_archetype = ngx_context['suggested_archetype']
        suggested_model = ngx_context['suggested_model']
        
        # Determine demo focus based on NGX archetype
        if suggested_archetype == 'prime':
            return await self._build_prime_agents_demo(user_context, demo_type, interaction_mode, ngx_context)
        else:  # longevity
            return await self._build_longevity_agents_demo(user_context, demo_type, interaction_mode, ngx_context)
    
    async def _build_prime_agents_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        ngx_context: Dict[str, Any]
    ) -> DemoSession:
        """Build NGX PRIME archetype agents demonstration"""
        
        session_id = str(uuid4())
        
        # PRIME archetype focuses on performance optimization
        steps = [
            DemoStep(
                step_id="prime_nexus_coordination",
                title="NEXUS: Your Executive Command Center",
                description="Experience how NEXUS coordinates your entire performance optimization ecosystem",
                instructions="See NEXUS analyze your executive profile and coordinate BLAZE, SAGE, and WAVE for peak performance",
                expected_outcome="Coordinated optimization across all performance dimensions",
                duration_seconds=180,
                interaction_type="agent_coordination",
                success_criteria={"coordination": 0.8, "personalization": 0.7, "efficiency": 0.6}
            ),
            DemoStep(
                step_id="prime_blaze_workout",
                title="BLAZE: Executive Fitness Optimization",
                description="Experience BLAZE designing high-impact workouts for busy executives",
                instructions="BLAZE creates a 30-minute power session adaptable to your office/hotel",
                expected_outcome="Maximum results in minimum time for executive schedules",
                duration_seconds=240,
                interaction_type="fitness_optimization",
                success_criteria={"efficiency": 0.8, "adaptability": 0.7, "results": 0.6}
            ),
            DemoStep(
                step_id="prime_sage_nutrition",
                title="SAGE: Performance Nutrition Intelligence",
                description="Watch SAGE analyze your meals and optimize for cognitive performance", 
                instructions="Take a photo of your lunch and see SAGE provide instant optimization recommendations",
                expected_outcome="Nutrition protocols that enhance decision-making and sustained energy",
                duration_seconds=200,
                interaction_type="nutrition_analysis",
                success_criteria={"analysis_speed": 0.9, "accuracy": 0.8, "actionability": 0.7}
            )
        ]
        
        # PRIME-specific personalization
        prime_personalization = {
            'archetype': 'PRIME - El Optimizador',
            'focus': 'Performance ejecutivo y productividad',
            'key_agents': ['NEXUS', 'BLAZE', 'SAGE', 'WAVE', 'SPARK'],
            'benefits': [
                'Coordination inteligente de todos los agentes',
                'Optimización para schedules ejecutivos',
                'Performance sostenido en jornadas largas',
                'Recovery optimization para consistency'
            ],
            'demo_value': 'Experiencia directa del ecosistema NGX AGENTS ACCESS',
            'next_step': 'Subscription tier recommendation based on needs'
        }
        
        return DemoSession(
            session_id=session_id,
            user_context=user_context,
            demo_type=demo_type,
            interaction_mode=interaction_mode,
            steps=steps,
            personalization=prime_personalization,
            estimated_impact=0.85,
            created_at=datetime.utcnow()
        )
    
    async def _build_consultant_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        hie_context: Dict[str, Any],
        archetype: ArchetypeType
    ) -> DemoSession:
        """Build consultant-specific NGX AGENTS ACCESS demonstration"""
        
        session_id = str(uuid4())
        
        steps = [
            DemoStep(
                step_id="consultant_client_presentation",
                title="Client Presentation Mastery",
                description="Transform your presentation confidence and client connection ability",
                instructions="Practice delivering a complex recommendation to a skeptical client while monitoring anxiety and clarity",
                expected_outcome="89% presentation confidence with 43% client satisfaction improvement",
                duration_seconds=210,
                interaction_type="client_simulation",
                success_criteria={"presentation_confidence": 0.5, "client_connection": 0.4, "clarity": 0.3}
            ),
            DemoStep(
                step_id="consultant_problem_solving",
                title="Rapid Problem-Solving Enhancement",
                description="Experience accelerated analytical thinking and solution generation",
                instructions="Tackle a complex business challenge with optimized cognitive processing",
                expected_outcome="56% improvement in solution quality and speed",
                duration_seconds=180,
                interaction_type="problem_solving",
                success_criteria={"analytical_speed": 0.4, "solution_quality": 0.3, "creativity": 0.3}
            ),
            DemoStep(
                step_id="consultant_billable_optimization",
                title="Billable Hour Quality Maximization",
                description="See how HIE maximizes the value and impact of every billable hour",
                instructions="Work through client deliverables with enhanced focus and efficiency",
                expected_outcome="2,840% ROI through higher-value client outcomes",
                duration_seconds=240,
                interaction_type="work_simulation",
                success_criteria={"work_quality": 0.4, "efficiency": 0.3, "client_value": 0.3}
            )
        ]
        
        success_story = hie_context.get('success_story')
        consultant_personalization = {
            'profession_focus': 'client success and analytical excellence',
            'key_benefits': ['89% presentation confidence', '2,840% ROI', '56% solution quality'],
            'success_story': success_story,
            'competitive_edge': 'Analytical clarity and client confidence that wins deals',
            'implementation_timeline': '4 weeks to transformation',
            'specific_metrics': {
                'presentation_confidence': 89,
                'client_satisfaction': 43,
                'solution_quality': 56,
                'roi_percentage': 2840
            }
        }
        
        return DemoSession(
            session_id=session_id,
            user_context=user_context,
            demo_type=demo_type,
            interaction_mode=interaction_mode,
            steps=steps,
            personalization=consultant_personalization,
            estimated_impact=0.78,
            created_at=datetime.utcnow()
        )
    
    async def _build_doctor_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        hie_context: Dict[str, Any],
        archetype: ArchetypeType
    ) -> DemoSession:
        """Build doctor/surgeon-specific NGX AGENTS ACCESS demonstration"""
        
        session_id = str(uuid4())
        
        steps = [
            DemoStep(
                step_id="doctor_precision_enhancement",
                title="Surgical Precision Amplification",
                description="Experience enhanced hand-eye coordination and precision under pressure",
                instructions="Perform precision tasks simulating surgical procedures with HIE enhancement",
                expected_outcome="78% improvement in precision with 23% faster completion",
                duration_seconds=300,
                interaction_type="precision_task",
                success_criteria={"precision": 0.5, "speed": 0.2, "consistency": 0.3}
            ),
            DemoStep(
                step_id="doctor_diagnostic_clarity",
                title="Diagnostic Accuracy Enhancement",
                description="Experience improved pattern recognition and diagnostic confidence",
                instructions="Analyze complex patient cases with optimized cognitive processing",
                expected_outcome="34% better patient outcomes through enhanced diagnosis",
                duration_seconds=240,
                interaction_type="diagnostic_challenge",
                success_criteria={"pattern_recognition": 0.4, "diagnostic_confidence": 0.3, "accuracy": 0.3}
            ),
            DemoStep(
                step_id="doctor_fatigue_resistance",
                title="Sustained Performance Under Fatigue",
                description="Maintain peak performance during long procedures without energy decline",
                instructions="Simulate extended procedure while monitoring energy and precision maintenance",
                expected_outcome="67% energy maintenance with sustained precision",
                duration_seconds=360,
                interaction_type="endurance_simulation",
                success_criteria={"energy_maintenance": 0.4, "precision_consistency": 0.3, "fatigue_resistance": 0.3}
            )
        ]
        
        success_story = hie_context.get('success_story')
        doctor_personalization = {
            'profession_focus': 'patient outcomes and surgical excellence',
            'key_benefits': ['78% precision improvement', '34% better outcomes', '15,600% ROI'],
            'success_story': success_story,
            'competitive_edge': 'Precision and endurance that saves lives',
            'implementation_timeline': '8 weeks to mastery',
            'specific_metrics': {
                'surgical_precision': 78,
                'patient_outcomes': 34,
                'energy_maintenance': 67,
                'roi_percentage': 15600
            }
        }
        
        return DemoSession(
            session_id=session_id,
            user_context=user_context,
            demo_type=demo_type,
            interaction_mode=interaction_mode,
            steps=steps,
            personalization=doctor_personalization,
            estimated_impact=0.92,
            created_at=datetime.utcnow()
        )
    
    async def _build_entrepreneur_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        hie_context: Dict[str, Any],
        archetype: ArchetypeType
    ) -> DemoSession:
        """Build entrepreneur-specific NGX AGENTS ACCESS demonstration"""
        
        session_id = str(uuid4())
        
        steps = [
            DemoStep(
                step_id="entrepreneur_pitch_mastery",
                title="Investor Pitch Optimization",
                description="Transform your pitch delivery with enhanced confidence and clarity",
                instructions="Deliver your startup pitch while monitoring confidence, clarity, and persuasion metrics",
                expected_outcome="156% pitch success rate improvement",
                duration_seconds=270,
                interaction_type="pitch_simulation",
                success_criteria={"pitch_confidence": 0.5, "clarity": 0.3, "persuasion": 0.2}
            ),
            DemoStep(
                step_id="entrepreneur_creative_breakthrough",
                title="Innovation and Creative Enhancement",
                description="Experience accelerated creative thinking and breakthrough ideation",
                instructions="Generate innovative solutions to business challenges with enhanced creative processing",
                expected_outcome="78% increase in creative output and solution quality",
                duration_seconds=180,
                interaction_type="creative_challenge",
                success_criteria={"creative_output": 0.4, "innovation_quality": 0.3, "ideation_speed": 0.3}
            ),
            DemoStep(
                step_id="entrepreneur_decision_confidence",
                title="Strategic Decision Confidence",
                description="Make complex business decisions with enhanced clarity and confidence",
                instructions="Navigate strategic business decisions while monitoring confidence and decision quality",
                expected_outcome="84% decision confidence with 12,400% ROI achievement",
                duration_seconds=240,
                interaction_type="decision_simulation",
                success_criteria={"decision_confidence": 0.4, "strategic_thinking": 0.3, "execution_clarity": 0.3}
            )
        ]
        
        success_story = hie_context.get('success_story')
        entrepreneur_personalization = {
            'profession_focus': 'innovation and investor confidence',
            'key_benefits': ['156% pitch success', '78% creative output', '12,400% ROI'],
            'success_story': success_story,
            'competitive_edge': 'Creative clarity and pitch confidence that closes funding',
            'implementation_timeline': '3 weeks to breakthrough',
            'specific_metrics': {
                'pitch_success_rate': 156,
                'creative_output': 78,
                'decision_confidence': 84,
                'roi_percentage': 12400
            }
        }
        
        return DemoSession(
            session_id=session_id,
            user_context=user_context,
            demo_type=demo_type,
            interaction_mode=interaction_mode,
            steps=steps,
            personalization=entrepreneur_personalization,
            estimated_impact=0.88,
            created_at=datetime.utcnow()
        )
    
    async def _build_generic_professional_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode,
        hie_context: Dict[str, Any],
        archetype: ArchetypeType
    ) -> DemoSession:
        """Build generic professional NGX AGENTS ACCESS demonstration"""
        
        session_id = str(uuid4())
        
        # Fallback to existing demo creation logic
        return await self._create_standard_demo(user_context, demo_type, interaction_mode)
    
    async def _create_standard_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        interaction_mode: InteractionMode
    ) -> DemoSession:
        """
        Create a personalized demonstration session.
        
        Args:
            user_context: User profile and preferences
            demo_type: Type of demonstration to create
            interaction_mode: How the user will interact with the demo
        
        Returns:
            Configured DemoSession ready to start
        """
        try:
            session_id = str(uuid4())
            
            # Get base template
            template = self.demo_templates.get(demo_type)
            if not template:
                raise ValueError(f"Unknown demo type: {demo_type}")
            
            # Personalize the demo
            personalized_steps = await self._personalize_demo_steps(
                template['steps'],
                user_context,
                demo_type
            )
            
            # Create personalization context
            personalization = await self._create_personalization_context(
                user_context,
                demo_type
            )
            
            # Generate expected outcomes
            expected_outcomes = await self._generate_expected_outcomes(
                user_context,
                demo_type,
                personalization
            )
            
            session = DemoSession(
                session_id=session_id,
                demo_type=demo_type,
                user_id=user_context.get('user_id', 'anonymous'),
                user_context=user_context,
                steps=personalized_steps,
                interaction_mode=interaction_mode,
                personalization=personalization,
                expected_outcomes=expected_outcomes,
                success_metrics=template['success_metrics'],
                started_at=None,
                completed_at=None,
                results=None
            )
            
            self.active_sessions[session_id] = session
            
            # Log demo creation
            await self._log_demo_event(session_id, 'demo_created', {
                'demo_type': demo_type.value,
                'interaction_mode': interaction_mode.value,
                'user_context': user_context
            })
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating personalized demo: {e}")
            return await self._create_fallback_demo(user_context, demo_type)
    
    async def start_demo_session(self, session_id: str) -> Dict[str, Any]:
        """Start a demonstration session"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.started_at = datetime.utcnow()
        
        # Initialize biometric baseline
        baseline = await self._simulate_user_baseline(session.user_context)
        
        # Prepare first step
        first_step = session.steps[0] if session.steps else None
        
        await self._log_demo_event(session_id, 'demo_started', {
            'baseline_metrics': baseline,
            'first_step': first_step.step_id if first_step else None
        })
        
        return {
            'session_id': session_id,
            'demo_type': session.demo_type.value,
            'total_steps': len(session.steps),
            'estimated_duration': sum(step.duration_seconds for step in session.steps),
            'baseline_metrics': baseline,
            'first_step': self._format_demo_step(first_step, 0) if first_step else None,
            'personalization': session.personalization
        }
    
    async def execute_demo_step(
        self,
        session_id: str,
        step_index: int,
        user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a specific demo step"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if step_index >= len(session.steps):
            raise ValueError(f"Step {step_index} out of range")
        
        step = session.steps[step_index]
        
        # Simulate HIE effects for this step
        hie_effects = await self._simulate_hie_effects(
            step,
            session.user_context,
            user_input
        )
        
        # Generate real-time insights
        insights = await self._generate_real_time_insights(
            step,
            hie_effects,
            session.personalization
        )
        
        # Calculate step success
        step_success = await self._evaluate_step_success(
            step,
            user_input,
            hie_effects
        )
        
        # Prepare next step
        next_step = None
        if step_index + 1 < len(session.steps):
            next_step = self._format_demo_step(
                session.steps[step_index + 1],
                step_index + 1
            )
        
        await self._log_demo_event(session_id, 'step_completed', {
            'step_index': step_index,
            'step_id': step.step_id,
            'success_score': step_success,
            'hie_effects': hie_effects,
            'user_input': user_input
        })
        
        return {
            'step_index': step_index,
            'step_completed': True,
            'success_score': step_success,
            'hie_effects': hie_effects,
            'insights': insights,
            'next_step': next_step,
            'is_final_step': step_index + 1 >= len(session.steps),
            'session_progress': (step_index + 1) / len(session.steps)
        }
    
    async def complete_demo_session(
        self,
        session_id: str,
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> DemoResult:
        """Complete a demonstration session and generate results"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.completed_at = datetime.utcnow()
        
        # Calculate overall results
        demo_result = await self._calculate_demo_results(session, user_feedback)
        
        # Generate conversion insights
        conversion_insights = await self._generate_conversion_insights(
            demo_result,
            session.user_context
        )
        
        # Save results
        session.results = {
            'demo_result': demo_result.__dict__,
            'conversion_insights': conversion_insights
        }
        
        # Clean up session
        del self.active_sessions[session_id]
        
        await self._log_demo_event(session_id, 'demo_completed', {
            'completion_rate': demo_result.completion_rate,
            'success_score': demo_result.success_score,
            'conversion_impact': demo_result.conversion_impact
        })
        
        return demo_result
    
    async def get_available_demos(
        self,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get list of available demos personalized for user"""
        
        demos = []
        
        for demo_type, template in self.demo_templates.items():
            # Check if demo is suitable for user
            suitability = await self._assess_demo_suitability(
                demo_type,
                user_context
            )
            
            if suitability['suitable']:
                demos.append({
                    'demo_type': demo_type.value,
                    'title': template['title'],
                    'description': template['description'],
                    'duration_minutes': template['duration_minutes'],
                    'difficulty_level': template['difficulty_level'],
                    'expected_benefits': template['expected_benefits'],
                    'suitability_score': suitability['score'],
                    'personalization_preview': suitability['preview']
                })
        
        # Sort by suitability score
        demos.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return demos
    
    def _initialize_demo_templates(self) -> Dict[DemoType, Dict[str, Any]]:
        """Initialize demo templates"""
        
        return {
            DemoType.FOCUS_ENHANCEMENT: {
                'title': 'Focus Enhancement Experience',
                'description': 'Experience immediate focus improvement with HIE technology',
                'duration_minutes': 5,
                'difficulty_level': 'beginner',
                'expected_benefits': ['Increased concentration', 'Reduced distractions', 'Mental clarity'],
                'steps': [
                    {
                        'title': 'Baseline Assessment',
                        'description': 'Measure your current focus level',
                        'duration_seconds': 60,
                        'interaction_type': 'assessment',
                        'user_prompt': 'Please count backwards from 100 by 7s as quickly as possible',
                        'visual_elements': [{'type': 'timer', 'duration': 60}],
                        'biometric_simulation': {'focus_score': 'baseline'}
                    },
                    {
                        'title': 'HIE Activation',
                        'description': 'Experience HIE focus enhancement',
                        'duration_seconds': 120,
                        'interaction_type': 'guided',
                        'user_prompt': 'Focus on the pulsing light and breathe deeply',
                        'visual_elements': [{'type': 'focus_light', 'pattern': 'alpha_wave'}],
                        'biometric_simulation': {'focus_score': 'enhanced'}
                    },
                    {
                        'title': 'Enhanced Performance',
                        'description': 'Test your enhanced focus',
                        'duration_seconds': 60,
                        'interaction_type': 'assessment',
                        'user_prompt': 'Repeat the counting exercise from step 1',
                        'visual_elements': [{'type': 'timer', 'duration': 60}],
                        'biometric_simulation': {'focus_score': 'peak'}
                    }
                ],
                'success_metrics': {
                    'focus_improvement': 0.35,
                    'task_completion': 0.9,
                    'user_satisfaction': 0.8
                }
            },
            
            DemoType.ENERGY_OPTIMIZATION: {
                'title': 'Energy Optimization Demo',
                'description': 'Feel the immediate energy boost from HIE',
                'duration_minutes': 7,
                'difficulty_level': 'beginner',
                'expected_benefits': ['Increased energy', 'Reduced fatigue', 'Enhanced vitality'],
                'steps': [
                    {
                        'title': 'Energy Assessment',
                        'description': 'Rate your current energy level',
                        'duration_seconds': 30,
                        'interaction_type': 'self_report',
                        'user_prompt': 'Rate your energy level from 1-10',
                        'visual_elements': [{'type': 'energy_meter', 'scale': '1-10'}],
                        'biometric_simulation': {'energy_level': 'baseline'}
                    },
                    {
                        'title': 'Cellular Optimization',
                        'description': 'HIE optimizes cellular energy production',
                        'duration_seconds': 180,
                        'interaction_type': 'visualization',
                        'visual_elements': [
                            {'type': 'cellular_animation', 'theme': 'mitochondria'},
                            {'type': 'energy_graph', 'trend': 'increasing'}
                        ],
                        'biometric_simulation': {'energy_level': 'optimizing'}
                    },
                    {
                        'title': 'Peak Energy State',
                        'description': 'Experience your optimized energy',
                        'duration_seconds': 60,
                        'interaction_type': 'activity',
                        'user_prompt': 'Do 10 jumping jacks and notice the difference',
                        'visual_elements': [{'type': 'activity_tracker'}],
                        'biometric_simulation': {'energy_level': 'peak'}
                    }
                ],
                'success_metrics': {
                    'energy_increase': 0.4,
                    'fatigue_reduction': 0.3,
                    'vitality_boost': 0.35
                }
            },
            
            DemoType.STRESS_REDUCTION: {
                'title': 'Stress Reduction Experience',
                'description': 'Experience immediate stress relief with HIE',
                'duration_minutes': 6,
                'difficulty_level': 'beginner',
                'expected_benefits': ['Reduced stress', 'Improved calm', 'Better mood'],
                'steps': [
                    {
                        'title': 'Stress Level Check',
                        'description': 'Assess your current stress',
                        'duration_seconds': 45,
                        'interaction_type': 'biometric',
                        'visual_elements': [{'type': 'stress_meter'}],
                        'biometric_simulation': {'stress_level': 'baseline'}
                    },
                    {
                        'title': 'HIE Stress Relief',
                        'description': 'HIE technology reduces cortisol levels',
                        'duration_seconds': 240,
                        'interaction_type': 'relaxation',
                        'user_prompt': 'Close your eyes and breathe naturally',
                        'visual_elements': [
                            {'type': 'breathing_guide'},
                            {'type': 'calming_colors'}
                        ],
                        'biometric_simulation': {'stress_level': 'reducing'}
                    },
                    {
                        'title': 'Optimized State',
                        'description': 'Notice your improved state',
                        'duration_seconds': 75,
                        'interaction_type': 'reflection',
                        'user_prompt': 'Rate your stress level now',
                        'visual_elements': [{'type': 'stress_meter'}],
                        'biometric_simulation': {'stress_level': 'optimized'}
                    }
                ],
                'success_metrics': {
                    'stress_reduction': 0.45,
                    'mood_improvement': 0.3,
                    'relaxation_depth': 0.4
                }
            },
            
            DemoType.COGNITIVE_BOOST: {
                'title': 'Cognitive Enhancement Demo',
                'description': 'Experience enhanced mental performance',
                'duration_minutes': 8,
                'difficulty_level': 'intermediate',
                'expected_benefits': ['Faster thinking', 'Better memory', 'Enhanced creativity'],
                'steps': [
                    {
                        'title': 'Cognitive Baseline',
                        'description': 'Test your cognitive performance',
                        'duration_seconds': 120,
                        'interaction_type': 'cognitive_test',
                        'user_prompt': 'Complete these mental math problems',
                        'visual_elements': [{'type': 'math_problems'}],
                        'biometric_simulation': {'cognitive_load': 'baseline'}
                    },
                    {
                        'title': 'Neural Optimization',
                        'description': 'HIE enhances neural connectivity',
                        'duration_seconds': 180,
                        'interaction_type': 'visualization',
                        'visual_elements': [
                            {'type': 'brain_network', 'activity': 'enhanced'},
                            {'type': 'neural_firing', 'speed': 'accelerated'}
                        ],
                        'biometric_simulation': {'cognitive_load': 'optimizing'}
                    },
                    {
                        'title': 'Enhanced Performance',
                        'description': 'Test your enhanced cognitive abilities',
                        'duration_seconds': 120,
                        'interaction_type': 'cognitive_test',
                        'user_prompt': 'Complete the same type of problems',
                        'visual_elements': [{'type': 'math_problems'}],
                        'biometric_simulation': {'cognitive_load': 'enhanced'}
                    }
                ],
                'success_metrics': {
                    'processing_speed': 0.25,
                    'accuracy_improvement': 0.2,
                    'mental_clarity': 0.35
                }
            }
        }
    
    async def _personalize_demo_steps(
        self,
        base_steps: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        demo_type: DemoType
    ) -> List[DemoStep]:
        """Personalize demo steps for specific user"""
        
        personalized_steps = []
        
        profession = user_context.get('profession', '').lower()
        detected_tier = user_context.get('detected_tier', 'ESSENTIAL')
        
        for i, step_data in enumerate(base_steps):
            # Personalize prompts based on profession
            user_prompt = step_data.get('user_prompt', '')
            if profession and user_prompt:
                user_prompt = await self._personalize_prompt(
                    user_prompt,
                    profession,
                    demo_type
                )
            
            # Adjust visual elements based on tier
            visual_elements = step_data.get('visual_elements', [])
            if detected_tier in ['PRIME', 'LONGEVITY']:
                visual_elements = await self._enhance_visuals_for_premium(visual_elements)
            
            # Create personalized step
            step = DemoStep(
                step_id=f"{demo_type.value}_step_{i}",
                title=step_data['title'],
                description=step_data['description'],
                duration_seconds=step_data['duration_seconds'],
                interaction_type=step_data['interaction_type'],
                user_prompt=user_prompt,
                expected_response=step_data.get('expected_response'),
                visual_elements=visual_elements,
                audio_cues=step_data.get('audio_cues', []),
                biometric_simulation=step_data.get('biometric_simulation'),
                success_criteria=step_data.get('success_criteria', {})
            )
            
            personalized_steps.append(step)
        
        return personalized_steps
    
    async def _create_personalization_context(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType
    ) -> Dict[str, Any]:
        """Create personalization context for demo"""
        
        profession = user_context.get('profession', '').lower()
        tier = user_context.get('detected_tier', 'ESSENTIAL')
        
        # Professional personalization
        professional_context = {
            'ceo': {
                'focus_areas': ['decision_making', 'leadership', 'strategic_thinking'],
                'language_style': 'executive',
                'examples': 'board_meetings',
                'benefits_emphasis': 'competitive_advantage'
            },
            'consultant': {
                'focus_areas': ['client_performance', 'billable_hours', 'expertise'],
                'language_style': 'analytical',
                'examples': 'client_projects',
                'benefits_emphasis': 'roi_delivery'
            },
            'doctor': {
                'focus_areas': ['patient_care', 'diagnostic_accuracy', 'stamina'],
                'language_style': 'clinical',
                'examples': 'patient_consultations',
                'benefits_emphasis': 'care_quality'
            },
            'engineer': {
                'focus_areas': ['problem_solving', 'innovation', 'technical_focus'],
                'language_style': 'technical',
                'examples': 'complex_projects',
                'benefits_emphasis': 'performance_optimization'
            }
        }
        
        context = professional_context.get(profession, {
            'focus_areas': ['productivity', 'energy', 'focus'],
            'language_style': 'general',
            'examples': 'daily_tasks',
            'benefits_emphasis': 'life_improvement'
        })
        
        # Add tier-specific context
        context['tier'] = tier
        context['demo_type'] = demo_type.value
        context['user_profession'] = profession
        
        return context
    
    async def _generate_expected_outcomes(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType,
        personalization: Dict[str, Any]
    ) -> List[str]:
        """Generate expected outcomes for the demo"""
        
        base_outcomes = {
            DemoType.FOCUS_ENHANCEMENT: [
                "Experience 35% improvement in focus within minutes",
                "Reduce mental distractions significantly",
                "Feel enhanced mental clarity and concentration"
            ],
            DemoType.ENERGY_OPTIMIZATION: [
                "Feel immediate energy boost",
                "Experience reduced fatigue",
                "Notice improved vitality and alertness"
            ],
            DemoType.STRESS_REDUCTION: [
                "Experience 40% stress reduction",
                "Feel increased calm and relaxation",
                "Notice improved mood and emotional balance"
            ],
            DemoType.COGNITIVE_BOOST: [
                "Experience faster mental processing",
                "Notice improved memory recall",
                "Feel enhanced creative thinking"
            ]
        }
        
        outcomes = base_outcomes.get(demo_type, [])
        
        # Personalize outcomes based on profession
        profession = personalization.get('user_profession', '')
        if profession == 'ceo':
            outcomes.append("Enhanced strategic decision-making clarity")
        elif profession == 'consultant':
            outcomes.append("Improved client problem-solving abilities")
        elif profession == 'doctor':
            outcomes.append("Enhanced diagnostic focus and stamina")
        elif profession == 'engineer':
            outcomes.append("Improved technical problem-solving speed")
        
        return outcomes
    
    async def _simulate_user_baseline(
        self,
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Simulate user's baseline biometric data"""
        
        # Base baseline metrics
        baseline = self.baseline_metrics.copy()
        
        # Adjust based on profession (some professions have different baselines)
        profession = user_context.get('profession', '').lower()
        
        if profession in ['ceo', 'executive']:
            baseline['stress_level'] = 0.75  # Higher baseline stress
            baseline['heart_rate'] = 78
        elif profession == 'doctor':
            baseline['stress_level'] = 0.7
            baseline['focus_score'] = 0.65  # Better baseline focus
        elif profession == 'student':
            baseline['energy_level'] = 0.5  # Lower energy
            baseline['stress_level'] = 0.8  # Higher stress
        
        # Add some realistic variation
        for metric in baseline:
            if isinstance(baseline[metric], float):
                variation = random.uniform(-0.1, 0.1)
                baseline[metric] = max(0.1, min(1.0, baseline[metric] + variation))
            elif isinstance(baseline[metric], int):
                variation = random.uniform(-0.1, 0.1)
                baseline[metric] = int(baseline[metric] * (1 + variation))
        
        return baseline
    
    async def _simulate_hie_effects(
        self,
        step: DemoStep,
        user_context: Dict[str, Any],
        user_input: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate HIE effects for a demo step"""
        
        effects = {}
        
        if not step.biometric_simulation:
            return effects
        
        baseline = await self._simulate_user_baseline(user_context)
        
        for metric, effect_type in step.biometric_simulation.items():
            if effect_type == 'baseline':
                effects[metric] = baseline[metric]
            elif effect_type == 'enhanced':
                if metric in self.hie_multipliers:
                    if 'reduction' in metric or metric == 'stress_level':
                        effects[metric] = baseline[metric] * self.hie_multipliers.get(f'{metric}_reduction', 0.7)
                    else:
                        effects[metric] = baseline[metric] * self.hie_multipliers.get(f'{metric}_improvement', 1.3)
                else:
                    effects[metric] = baseline[metric] * 1.25  # Default 25% improvement
            elif effect_type == 'peak':
                peak_multiplier = 1.5 if metric != 'stress_level' else 0.5
                effects[metric] = baseline[metric] * peak_multiplier
            elif effect_type == 'optimizing':
                # Gradual improvement
                improvement_factor = 1.15 if metric != 'stress_level' else 0.85
                effects[metric] = baseline[metric] * improvement_factor
        
        # Add progression indicators
        effects['improvement_trend'] = 'increasing'
        effects['stability'] = 'stable'
        effects['optimization_level'] = random.uniform(0.7, 0.95)
        
        return effects
    
    async def _generate_real_time_insights(
        self,
        step: DemoStep,
        hie_effects: Dict[str, Any],
        personalization: Dict[str, Any]
    ) -> List[str]:
        """Generate real-time insights during demo step"""
        
        insights = []
        
        # Analyze effects and generate insights
        for metric, value in hie_effects.items():
            if metric in ['focus_score', 'energy_level', 'cognitive_load']:
                if isinstance(value, (int, float)) and value > 0.7:
                    insight = self._generate_metric_insight(metric, value, personalization)
                    if insight:
                        insights.append(insight)
        
        # Add step-specific insights
        if 'focus' in step.step_id:
            insights.append("Notice how your ability to concentrate has sharpened")
        elif 'energy' in step.step_id:
            insights.append("Feel the cellular energy optimization taking effect")
        elif 'stress' in step.step_id:
            insights.append("Your stress response is being naturally regulated")
        elif 'cognitive' in step.step_id:
            insights.append("Your neural processing speed is increasing")
        
        return insights[:3]  # Limit to top 3 insights
    
    def _generate_metric_insight(
        self,
        metric: str,
        value: float,
        personalization: Dict[str, Any]
    ) -> Optional[str]:
        """Generate insight for a specific metric"""
        
        profession = personalization.get('user_profession', '')
        
        metric_insights = {
            'focus_score': {
                'general': f"Your focus has improved to {value*100:.0f}% of optimal",
                'ceo': f"Strategic thinking clarity enhanced to {value*100:.0f}%",
                'consultant': f"Client problem-solving focus at {value*100:.0f}%",
                'doctor': f"Diagnostic focus enhanced to {value*100:.0f}%"
            },
            'energy_level': {
                'general': f"Energy optimization at {value*100:.0f}% of peak capacity",
                'ceo': f"Leadership stamina enhanced to {value*100:.0f}%",
                'consultant': f"Billable hour performance at {value*100:.0f}%",
                'doctor': f"Patient care stamina at {value*100:.0f}%"
            },
            'cognitive_load': {
                'general': f"Mental processing efficiency at {value*100:.0f}%",
                'ceo': f"Decision-making speed enhanced {value*100:.0f}%",
                'consultant': f"Analytical capability at {value*100:.0f}%",
                'engineer': f"Technical problem-solving at {value*100:.0f}%"
            }
        }
        
        insights = metric_insights.get(metric, {})
        return insights.get(profession, insights.get('general'))
    
    async def _evaluate_step_success(
        self,
        step: DemoStep,
        user_input: Optional[Dict[str, Any]],
        hie_effects: Dict[str, Any]
    ) -> float:
        """Evaluate success of a demo step"""
        
        success_score = 0.0
        
        # Base success from biometric improvements
        for metric, value in hie_effects.items():
            if isinstance(value, (int, float)) and metric in ['focus_score', 'energy_level']:
                if value > 0.7:
                    success_score += 0.3
                elif value > 0.6:
                    success_score += 0.2
                elif value > 0.5:
                    success_score += 0.1
        
        # Success from user interaction
        if user_input:
            engagement = user_input.get('engagement_level', 0.5)
            satisfaction = user_input.get('satisfaction', 0.5)
            success_score += (engagement + satisfaction) * 0.25
        
        # Success from step completion
        if step.success_criteria:
            for criterion, threshold in step.success_criteria.items():
                if criterion in hie_effects and hie_effects[criterion] >= threshold:
                    success_score += 0.15
        
        return min(1.0, success_score)
    
    def _format_demo_step(self, step: DemoStep, step_index: int) -> Dict[str, Any]:
        """Format demo step for client consumption"""
        
        return {
            'step_index': step_index,
            'step_id': step.step_id,
            'title': step.title,
            'description': step.description,
            'duration_seconds': step.duration_seconds,
            'interaction_type': step.interaction_type,
            'user_prompt': step.user_prompt,
            'visual_elements': step.visual_elements,
            'audio_cues': step.audio_cues
        }
    
    async def _calculate_demo_results(
        self,
        session: DemoSession,
        user_feedback: Optional[Dict[str, Any]]
    ) -> DemoResult:
        """Calculate overall demo results"""
        
        # Get demo events from logs
        demo_events = await self._get_demo_events(session.session_id)
        
        # Calculate completion rate
        completed_steps = len([e for e in demo_events if e.get('event_type') == 'step_completed'])
        completion_rate = completed_steps / len(session.steps) if session.steps else 0
        
        # Calculate average success score
        step_successes = [
            e.get('data', {}).get('success_score', 0)
            for e in demo_events
            if e.get('event_type') == 'step_completed'
        ]
        success_score = sum(step_successes) / len(step_successes) if step_successes else 0
        
        # Calculate user engagement
        user_engagement = 0.8  # Default high engagement for demos
        if user_feedback:
            user_engagement = user_feedback.get('engagement', user_engagement)
        
        # Calculate biometric improvements
        biometric_improvements = {}
        for event in demo_events:
            if event.get('event_type') == 'step_completed':
                hie_effects = event.get('data', {}).get('hie_effects', {})
                for metric, value in hie_effects.items():
                    if isinstance(value, (int, float)) and metric not in ['improvement_trend', 'stability']:
                        if metric not in biometric_improvements:
                            biometric_improvements[metric] = []
                        biometric_improvements[metric].append(value)
        
        # Average improvements
        avg_improvements = {}
        for metric, values in biometric_improvements.items():
            if values:
                baseline = values[0] if values else 0.5
                peak = max(values) if values else baseline
                improvement = (peak - baseline) / baseline if baseline > 0 else 0
                avg_improvements[metric] = improvement
        
        # Estimate conversion impact
        conversion_impact = self._estimate_conversion_impact(
            success_score,
            completion_rate,
            user_engagement,
            session.demo_type
        )
        
        # Generate insights
        insights = self._generate_demo_insights(
            session,
            success_score,
            avg_improvements
        )
        
        # Generate recommendations
        recommendations = self._generate_next_recommendations(
            session.user_context,
            session.demo_type,
            success_score
        )
        
        return DemoResult(
            session_id=session.session_id,
            demo_type=session.demo_type,
            user_engagement=user_engagement,
            completion_rate=completion_rate,
            success_score=success_score,
            user_feedback=user_feedback or {},
            biometric_improvements=avg_improvements,
            conversion_impact=conversion_impact,
            insights_generated=insights,
            next_recommendations=recommendations
        )
    
    def _estimate_conversion_impact(
        self,
        success_score: float,
        completion_rate: float,
        engagement: float,
        demo_type: DemoType
    ) -> float:
        """Estimate impact on conversion probability"""
        
        # Base conversion impact by demo type
        base_impact = {
            DemoType.FOCUS_ENHANCEMENT: 0.25,
            DemoType.ENERGY_OPTIMIZATION: 0.30,
            DemoType.STRESS_REDUCTION: 0.20,
            DemoType.COGNITIVE_BOOST: 0.35,
            DemoType.PERFORMANCE_ANALYSIS: 0.40,
            DemoType.PERSONALIZED_INSIGHTS: 0.45
        }
        
        base = base_impact.get(demo_type, 0.25)
        
        # Adjust based on performance metrics
        performance_multiplier = (success_score + completion_rate + engagement) / 3
        
        return base * performance_multiplier
    
    def _generate_demo_insights(
        self,
        session: DemoSession,
        success_score: float,
        improvements: Dict[str, float]
    ) -> List[str]:
        """Generate insights from demo performance"""
        
        insights = []
        
        if success_score > 0.8:
            insights.append("Exceptional response to HIE technology - you're an ideal candidate")
        elif success_score > 0.6:
            insights.append("Strong positive response to HIE - significant benefits observed")
        else:
            insights.append("Positive initial response - full benefits increase with consistent use")
        
        # Add improvement-specific insights
        if 'focus_score' in improvements and improvements['focus_score'] > 0.3:
            insights.append("Your focus improvement exceeded typical first-time results")
        
        if 'energy_level' in improvements and improvements['energy_level'] > 0.25:
            insights.append("Energy optimization shows excellent cellular responsiveness")
        
        if 'stress_level' in improvements and improvements['stress_level'] > 0.3:
            insights.append("Stress reduction indicates strong nervous system compatibility")
        
        return insights
    
    def _generate_next_recommendations(
        self,
        user_context: Dict[str, Any],
        completed_demo: DemoType,
        success_score: float
    ) -> List[str]:
        """Generate recommendations for next steps"""
        
        recommendations = []
        
        if success_score > 0.7:
            recommendations.append("Consider starting with a 7-day trial to experience sustained benefits")
            tier = user_context.get('detected_tier', 'ESSENTIAL')
            recommendations.append(f"The {tier} plan is optimized for your profile and needs")
        
        # Suggest complementary demos
        if completed_demo == DemoType.FOCUS_ENHANCEMENT:
            recommendations.append("Try the Energy Optimization demo to see full performance potential")
        elif completed_demo == DemoType.ENERGY_OPTIMIZATION:
            recommendations.append("Experience the Stress Reduction demo for complete wellness")
        elif completed_demo == DemoType.STRESS_REDUCTION:
            recommendations.append("The Cognitive Boost demo will show enhanced mental performance")
        
        recommendations.append("Schedule a personalized consultation to discuss your specific goals")
        
        return recommendations
    
    async def _personalize_prompt(
        self,
        base_prompt: str,
        profession: str,
        demo_type: DemoType
    ) -> str:
        """Personalize prompts for specific professions"""
        
        profession_contexts = {
            'ceo': 'Imagine you\'re in an important board meeting',
            'consultant': 'Think about your most challenging client project',
            'doctor': 'Consider a complex patient diagnosis',
            'engineer': 'Think about solving a technical problem',
            'student': 'Imagine you\'re studying for an important exam'
        }
        
        if profession in profession_contexts:
            context = profession_contexts[profession]
            return f"{context}. {base_prompt}"
        
        return base_prompt
    
    async def _enhance_visuals_for_premium(
        self,
        base_visuals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance visuals for premium tier users"""
        
        enhanced = []
        
        for visual in base_visuals:
            enhanced_visual = visual.copy()
            
            # Add premium effects
            enhanced_visual['enhanced'] = True
            enhanced_visual['resolution'] = 'high'
            enhanced_visual['animations'] = 'smooth'
            
            if visual.get('type') == 'focus_light':
                enhanced_visual['pattern'] = 'premium_alpha_wave'
                enhanced_visual['colors'] = ['gold', 'purple']
            elif visual.get('type') == 'energy_meter':
                enhanced_visual['style'] = '3d'
                enhanced_visual['effects'] = ['glow', 'pulse']
            
            enhanced.append(enhanced_visual)
        
        return enhanced
    
    async def _assess_demo_suitability(
        self,
        demo_type: DemoType,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess how suitable a demo is for a user"""
        
        profession = user_context.get('profession', '').lower()
        tier = user_context.get('detected_tier', 'ESSENTIAL')
        
        # Demo suitability by profession
        suitability_matrix = {
            DemoType.FOCUS_ENHANCEMENT: {
                'ceo': 0.9, 'executive': 0.9, 'consultant': 0.85,
                'doctor': 0.8, 'engineer': 0.85, 'student': 0.7
            },
            DemoType.ENERGY_OPTIMIZATION: {
                'ceo': 0.85, 'executive': 0.8, 'entrepreneur': 0.9,
                'doctor': 0.9, 'consultant': 0.75, 'student': 0.6
            },
            DemoType.STRESS_REDUCTION: {
                'ceo': 0.95, 'executive': 0.9, 'doctor': 0.85,
                'lawyer': 0.85, 'student': 0.8, 'manager': 0.75
            },
            DemoType.COGNITIVE_BOOST: {
                'engineer': 0.9, 'consultant': 0.85, 'doctor': 0.8,
                'ceo': 0.8, 'student': 0.9, 'lawyer': 0.8
            }
        }
        
        base_score = suitability_matrix.get(demo_type, {}).get(profession, 0.6)
        
        # Adjust for tier
        if tier in ['PRIME', 'LONGEVITY']:
            base_score += 0.1
        elif tier in ['ELITE', 'PRO']:
            base_score += 0.05
        
        suitable = base_score >= 0.6
        
        # Generate preview
        preview = f"Optimized for {profession}s" if profession else "General optimization"
        if tier in ['PRIME', 'LONGEVITY']:
            preview += " with premium features"
        
        return {
            'suitable': suitable,
            'score': min(1.0, base_score),
            'preview': preview
        }
    
    async def _create_fallback_demo(
        self,
        user_context: Dict[str, Any],
        demo_type: DemoType
    ) -> DemoSession:
        """Create a basic fallback demo"""
        
        return DemoSession(
            session_id=str(uuid4()),
            demo_type=demo_type,
            user_id=user_context.get('user_id', 'fallback'),
            user_context=user_context,
            steps=[],
            interaction_mode=InteractionMode.PASSIVE_WATCH,
            personalization={},
            expected_outcomes=["Experience HIE benefits"],
            success_metrics={'basic_completion': 0.5},
            started_at=None,
            completed_at=None,
            results=None
        )
    
    async def _log_demo_event(
        self,
        session_id: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Log demo events for analytics"""
        
        try:
            self.supabase.table('demo_events').insert({
                'session_id': session_id,
                'event_type': event_type,
                'data': json.dumps(data),
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error logging demo event: {e}")
    
    async def _get_demo_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get demo events for a session"""
        
        try:
            response = self.supabase.table('demo_events').select(
                '*'
            ).eq(
                'session_id', session_id
            ).order('created_at').execute()
            
            events = []
            for event in response.data:
                event_data = event.copy()
                if event_data.get('data'):
                    event_data['data'] = json.loads(event_data['data'])
                events.append(event_data)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting demo events: {e}")
            return []
    
    async def get_demo_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get demo analytics"""
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        try:
            # Get demo events
            response = self.supabase.table('demo_events').select(
                '*'
            ).gte(
                'created_at', since
            ).execute()
            
            events = response.data
            
            if not events:
                return {"message": "No demo data found"}
            
            # Analyze events
            sessions = {}
            for event in events:
                session_id = event['session_id']
                if session_id not in sessions:
                    sessions[session_id] = []
                sessions[session_id].append(event)
            
            # Calculate metrics
            total_sessions = len(sessions)
            completed_sessions = sum(
                1 for session_events in sessions.values()
                if any(e['event_type'] == 'demo_completed' for e in session_events)
            )
            
            avg_completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0
            
            # Demo type distribution
            demo_types = {}
            for session_events in sessions.values():
                started_event = next(
                    (e for e in session_events if e['event_type'] == 'demo_started'),
                    None
                )
                if started_event:
                    demo_type = started_event.get('data', {}).get('demo_type', 'unknown')
                    demo_types[demo_type] = demo_types.get(demo_type, 0) + 1
            
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": avg_completion_rate,
                "demo_type_distribution": demo_types,
                "timeframe_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting demo analytics: {e}")
            return {"error": "Unable to retrieve analytics"}