"""
Prompt Optimizer Service
Optimizes conversation prompts automatically based on ML tracking results.
Uses A/B testing and genetic algorithms to evolve better prompts.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

from ..models.base import BaseModel
from ..models.learning_models import (
    ExperimentResult,
    ModelType,
    PromptVariant,
    PerformanceMetrics
)
from ..services.ab_testing_framework import ABTestingFramework
from ..services.adaptive_learning_service import AdaptiveLearningService
from ..services.conversation_outcome_tracker import ConversationOutcomeTracker
from ..services.ngx_master_knowledge import get_ngx_knowledge, NGXArchetype
from ..integrations.supabase_client import get_supabase_client
from ..integrations.openai_client import get_openai_client
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PromptTemplate(BaseModel):
    """Template for generating prompt variations"""
    id: str
    name: str
    base_template: str
    variables: List[str]
    constraints: Dict[str, Any]
    performance_history: List[Dict[str, float]]


class PromptOptimizerService:
    """
    Automatically optimizes prompts based on performance data.
    Uses genetic algorithms and ML to evolve better prompts.
    """
    
    def __init__(self):
        self.ab_testing = ABTestingFramework()
        self.adaptive_learning = AdaptiveLearningService()
        self.outcome_tracker = ConversationOutcomeTracker()
        self.ngx_knowledge = get_ngx_knowledge()
        self.supabase = get_supabase_client()
        self.openai = get_openai_client()
        
        # Optimization parameters
        self.mutation_rate = 0.15
        self.crossover_rate = 0.7
        self.population_size = 20
        self.elite_size = 5
        self.generation_limit = 10
        
        # Prompt components for genetic algorithm
        self.prompt_genes = {
            "tone": ["consultative", "friendly", "professional", "empathetic", "confident"],
            "structure": ["question-first", "benefit-first", "story-first", "data-first"],
            "urgency": ["subtle", "moderate", "strong", "time-sensitive"],
            "personalization": ["role-based", "industry-based", "goal-based", "challenge-based"],
            "hie_emphasis": ["technical", "lifestyle", "performance", "longevity", "optimization"],
            "call_to_action": ["soft", "direct", "question-based", "value-based", "scarcity-based"]
        }
    
    async def optimize_prompt(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        target_metric: str = "conversion_rate"
    ) -> str:
        """
        Optimize a prompt for a specific context and metric.
        
        Args:
            prompt_type: Type of prompt (greeting, objection_handler, closer, etc.)
            context: Current conversation context
            target_metric: Metric to optimize for
        
        Returns:
            Optimized prompt string
        """
        try:
            # Get current best performing variant
            best_variant = await self._get_best_variant(prompt_type, context)
            
            # Check if we should explore new variants
            should_explore = await self._should_explore(prompt_type, best_variant)
            
            if should_explore:
                # Generate new variant using genetic algorithm
                new_variant = await self._generate_variant(
                    prompt_type,
                    context,
                    best_variant,
                    target_metric
                )
                
                # Register variant for A/B testing
                await self._register_variant(prompt_type, new_variant)
                
                # Decide which variant to use (exploration vs exploitation)
                selected_variant = await self.ab_testing.select_variant(
                    f"prompt_{prompt_type}",
                    context
                )
                
                return selected_variant.content
            else:
                # Use best known variant
                return best_variant.content
                
        except Exception as e:
            logger.error(f"Error optimizing prompt: {e}")
            return await self._get_fallback_prompt(prompt_type, context)
    
    async def _get_best_variant(
        self,
        prompt_type: str,
        context: Dict[str, Any]
    ) -> PromptVariant:
        """Get the best performing prompt variant for the context"""
        
        # Query performance data from Supabase
        response = self.supabase.table('prompt_variants').select(
            '*'
        ).eq(
            'prompt_type', prompt_type
        ).eq(
            'is_active', True
        ).order(
            'performance_score', desc=True
        ).limit(1).execute()
        
        if response.data:
            return PromptVariant(**response.data[0])
        
        # Create default variant if none exists
        return await self._create_default_variant(prompt_type, context)
    
    async def _should_explore(
        self,
        prompt_type: str,
        current_best: PromptVariant
    ) -> bool:
        """Determine if we should explore new variants"""
        
        # Check exploration criteria
        if not current_best:
            return True
            
        # Get recent performance metrics
        recent_performance = await self._get_recent_performance(
            prompt_type,
            current_best.id
        )
        
        # Explore if performance is declining or insufficient data
        if len(recent_performance) < 10:
            return True
            
        # Calculate performance trend
        trend = self._calculate_trend(recent_performance)
        
        # Explore if negative trend or below target
        return trend < -0.05 or current_best.performance_score < 0.7
    
    async def _generate_variant(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        parent: Optional[PromptVariant],
        target_metric: str
    ) -> PromptVariant:
        """Generate new prompt variant using genetic algorithm"""
        
        # Generate population
        population = await self._generate_population(
            prompt_type,
            context,
            parent
        )
        
        # Evolve through generations
        for generation in range(self.generation_limit):
            # Evaluate fitness
            population = await self._evaluate_fitness(
                population,
                context,
                target_metric
            )
            
            # Select best performers
            elite = self._select_elite(population)
            
            # Create next generation
            population = await self._create_next_generation(
                elite,
                context
            )
        
        # Return best variant from final generation
        return max(population, key=lambda v: v.fitness_score)
    
    async def _generate_population(
        self,
        prompt_type: str,
        context: Dict[str, Any],
        parent: Optional[PromptVariant]
    ) -> List[PromptVariant]:
        """Generate initial population of prompt variants"""
        
        population = []
        
        # Include parent if exists
        if parent:
            population.append(parent)
        
        # Generate variants
        while len(population) < self.population_size:
            genes = self._generate_random_genes()
            prompt = await self._genes_to_prompt(
                prompt_type,
                genes,
                context
            )
            
            variant = PromptVariant(
                id=str(uuid4()),
                prompt_type=prompt_type,
                content=prompt,
                genes=genes,
                created_at=datetime.utcnow()
            )
            
            population.append(variant)
        
        return population
    
    def _generate_random_genes(self) -> Dict[str, str]:
        """Generate random genetic combination"""
        return {
            gene: random.choice(values)
            for gene, values in self.prompt_genes.items()
        }
    
    async def _genes_to_prompt(
        self,
        prompt_type: str,
        genes: Dict[str, str],
        context: Dict[str, Any]
    ) -> str:
        """Convert genetic representation to actual prompt"""
        
        # Use GPT-4 to generate prompt based on genes
        system_prompt = f"""
        You are an expert prompt engineer for a conversational AI sales system.
        Generate a {prompt_type} prompt with these characteristics:
        
        - Tone: {genes['tone']}
        - Structure: {genes['structure']}
        - Urgency: {genes['urgency']}
        - Personalization: {genes['personalization']}
        - HIE Emphasis: {genes['hie_emphasis']}
        - Call to Action: {genes['call_to_action']}
        
        Context:
        - User Tier: {context.get('detected_tier', 'unknown')}
        - Conversation Stage: {context.get('stage', 'unknown')}
        - User Profession: {context.get('profession', 'unknown')}
        
        The prompt should be natural, persuasive, and focused on the NGX HIE system benefits.
        Keep it concise (2-3 sentences max).
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a {prompt_type} prompt"}
            ],
            temperature=0.8,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    async def _evaluate_fitness(
        self,
        population: List[PromptVariant],
        context: Dict[str, Any],
        target_metric: str
    ) -> List[PromptVariant]:
        """Evaluate fitness of each variant using historical data and predictions"""
        
        for variant in population:
            # Get predicted performance using ML model
            prediction = await self.adaptive_learning.predict_performance(
                ModelType.PROMPT_OPTIMIZER,
                {
                    "prompt_content": variant.content,
                    "prompt_genes": variant.genes,
                    "context": context
                }
            )
            
            # Adjust based on similar prompts' historical performance
            historical_adjustment = await self._get_historical_adjustment(
                variant,
                target_metric
            )
            
            # Calculate fitness score
            variant.fitness_score = (
                prediction.get(target_metric, 0.5) * 0.7 +
                historical_adjustment * 0.3
            )
        
        return population
    
    def _select_elite(self, population: List[PromptVariant]) -> List[PromptVariant]:
        """Select top performing variants"""
        sorted_population = sorted(
            population,
            key=lambda v: v.fitness_score,
            reverse=True
        )
        return sorted_population[:self.elite_size]
    
    async def _create_next_generation(
        self,
        elite: List[PromptVariant],
        context: Dict[str, Any]
    ) -> List[PromptVariant]:
        """Create next generation through crossover and mutation"""
        
        next_generation = elite.copy()
        
        while len(next_generation) < self.population_size:
            # Select parents
            parent1, parent2 = random.sample(elite, 2)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child_genes = self._crossover(parent1.genes, parent2.genes)
            else:
                child_genes = parent1.genes.copy()
            
            # Mutation
            if random.random() < self.mutation_rate:
                child_genes = self._mutate(child_genes)
            
            # Create child variant
            child_prompt = await self._genes_to_prompt(
                parent1.prompt_type,
                child_genes,
                context
            )
            
            child = PromptVariant(
                id=str(uuid4()),
                prompt_type=parent1.prompt_type,
                content=child_prompt,
                genes=child_genes,
                created_at=datetime.utcnow()
            )
            
            next_generation.append(child)
        
        return next_generation
    
    def _crossover(
        self,
        genes1: Dict[str, str],
        genes2: Dict[str, str]
    ) -> Dict[str, str]:
        """Perform genetic crossover"""
        child_genes = {}
        
        for gene in self.prompt_genes.keys():
            # Randomly select from either parent
            child_genes[gene] = random.choice([genes1[gene], genes2[gene]])
        
        return child_genes
    
    def _mutate(self, genes: Dict[str, str]) -> Dict[str, str]:
        """Perform genetic mutation"""
        mutated_genes = genes.copy()
        
        # Randomly mutate one gene
        gene_to_mutate = random.choice(list(self.prompt_genes.keys()))
        mutated_genes[gene_to_mutate] = random.choice(
            self.prompt_genes[gene_to_mutate]
        )
        
        return mutated_genes
    
    async def _register_variant(
        self,
        prompt_type: str,
        variant: PromptVariant
    ) -> None:
        """Register new variant for A/B testing"""
        
        # Save to database
        self.supabase.table('prompt_variants').insert({
            'id': variant.id,
            'prompt_type': prompt_type,
            'content': variant.content,
            'genes': json.dumps(variant.genes),
            'fitness_score': variant.fitness_score,
            'is_active': True,
            'created_at': variant.created_at.isoformat()
        }).execute()
        
        # Register with A/B testing framework
        await self.ab_testing.create_experiment(
            name=f"prompt_{prompt_type}_{variant.id[:8]}",
            variants=[
                {"id": "control", "content": variant.content},
                {"id": "variant", "content": variant.content}
            ],
            target_metrics=[
                "conversion_rate",
                "engagement_score",
                "satisfaction_rating"
            ]
        )
    
    async def update_performance(
        self,
        prompt_id: str,
        outcome: Dict[str, Any]
    ) -> None:
        """Update prompt performance based on conversation outcome"""
        
        try:
            # Calculate performance metrics
            metrics = self._calculate_performance_metrics(outcome)
            
            # Update variant performance
            self.supabase.table('prompt_variants').update({
                'performance_score': metrics['overall_score'],
                'conversion_rate': metrics['conversion_rate'],
                'engagement_score': metrics['engagement_score'],
                'usage_count': self.supabase.raw(
                    'usage_count + 1'
                ),
                'last_used': datetime.utcnow().isoformat()
            }).eq('id', prompt_id).execute()
            
            # Update ML model
            await self.adaptive_learning.update_model(
                ModelType.PROMPT_OPTIMIZER,
                {
                    'prompt_id': prompt_id,
                    'outcome': outcome,
                    'metrics': metrics
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating prompt performance: {e}")
    
    def _calculate_performance_metrics(
        self,
        outcome: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate performance metrics from outcome data"""
        
        # Base metrics
        converted = outcome.get('converted', False)
        engagement_time = outcome.get('engagement_time', 0)
        message_count = outcome.get('message_count', 0)
        sentiment_score = outcome.get('sentiment_score', 0)
        
        # Calculate composite metrics
        conversion_rate = 1.0 if converted else 0.0
        engagement_score = min(1.0, engagement_time / 600)  # 10 min max
        interaction_score = min(1.0, message_count / 20)  # 20 messages max
        
        # Overall score weighted average
        overall_score = (
            conversion_rate * 0.5 +
            engagement_score * 0.3 +
            sentiment_score * 0.1 +
            interaction_score * 0.1
        )
        
        return {
            'overall_score': overall_score,
            'conversion_rate': conversion_rate,
            'engagement_score': engagement_score,
            'sentiment_score': sentiment_score,
            'interaction_score': interaction_score
        }
    
    async def _get_recent_performance(
        self,
        prompt_type: str,
        variant_id: str,
        days: int = 7
    ) -> List[float]:
        """Get recent performance scores"""
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        response = self.supabase.table('conversation_outcomes').select(
            'performance_score'
        ).eq(
            'prompt_variant_id', variant_id
        ).gte(
            'created_at', since
        ).execute()
        
        return [r['performance_score'] for r in response.data]
    
    def _calculate_trend(self, performance_scores: List[float]) -> float:
        """Calculate performance trend (positive or negative)"""
        
        if len(performance_scores) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(performance_scores)
        x = list(range(n))
        y = performance_scores
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    async def _get_historical_adjustment(
        self,
        variant: PromptVariant,
        target_metric: str
    ) -> float:
        """Get historical performance adjustment based on similar prompts"""
        
        # Find similar prompts based on genes
        similar_prompts = await self._find_similar_prompts(variant.genes)
        
        if not similar_prompts:
            return 0.5  # Neutral adjustment
        
        # Average performance of similar prompts
        performances = [p.get(target_metric, 0.5) for p in similar_prompts]
        return sum(performances) / len(performances)
    
    async def _find_similar_prompts(
        self,
        genes: Dict[str, str],
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find historically similar prompts based on genetic similarity"""
        
        response = self.supabase.table('prompt_variants').select(
            '*'
        ).execute()
        
        similar_prompts = []
        
        for variant in response.data:
            variant_genes = json.loads(variant.get('genes', '{}'))
            similarity = self._calculate_gene_similarity(genes, variant_genes)
            
            if similarity >= similarity_threshold:
                similar_prompts.append(variant)
        
        return similar_prompts
    
    def _calculate_gene_similarity(
        self,
        genes1: Dict[str, str],
        genes2: Dict[str, str]
    ) -> float:
        """Calculate similarity between two gene sets"""
        
        if not genes1 or not genes2:
            return 0.0
        
        matches = sum(
            1 for gene in genes1
            if gene in genes2 and genes1[gene] == genes2[gene]
        )
        
        return matches / len(self.prompt_genes)
    
    async def _create_default_variant(
        self,
        prompt_type: str,
        context: Dict[str, Any]
    ) -> PromptVariant:
        """Create default variant for a prompt type"""
        
        default_prompts = {
            "greeting": "Hi! I noticed you're interested in optimizing your performance. I'm here to help you discover how the NGX HIE system can transform your daily energy and focus. What's your biggest challenge right now?",
            "objection_handler": "I completely understand your concern. Many of our most successful users had similar thoughts before experiencing the HIE difference. Would you like to hear how someone in your field achieved remarkable results?",
            "closer": "Based on everything we've discussed, the {tier} plan would be perfect for your goals. As an early adopter, you'll lock in exclusive pricing and be part of our founding member community. Shall we secure your spot?",
            "value_reinforcement": "Imagine having {benefit} every single day. That's exactly what the HIE system delivers. Our {profession} users report an average ROI of {roi}%. This isn't just an investment in a product—it's an investment in your future performance.",
            "engagement": "That's a great question! It shows you're really thinking about how this could work for you. Let me share something specific about the HIE that addresses exactly that..."
        }
        
        genes = {
            "tone": "consultative",
            "structure": "question-first",
            "urgency": "moderate",
            "personalization": "role-based",
            "hie_emphasis": "performance",
            "call_to_action": "value-based"
        }
        
        content = default_prompts.get(
            prompt_type,
            "How can I help you achieve your performance goals today?"
        )
        
        # Personalize default prompt
        if context.get('detected_tier'):
            content = content.replace('{tier}', context['detected_tier'])
        if context.get('profession'):
            content = content.replace('{profession}', context['profession'])
        if context.get('roi'):
            content = content.replace('{roi}', str(context['roi']))
        if context.get('benefit'):
            content = content.replace('{benefit}', context['benefit'])
        
        variant = PromptVariant(
            id=str(uuid4()),
            prompt_type=prompt_type,
            content=content,
            genes=genes,
            performance_score=0.5,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        await self._register_variant(prompt_type, variant)
        
        return variant
    
    async def _get_fallback_prompt(
        self,
        prompt_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Get fallback prompt in case of errors"""
        
        fallback_prompts = {
            "greeting": "Welcome! I'm here to help you explore how NGX can enhance your performance. What brings you here today?",
            "objection_handler": "I understand your perspective. Let's explore this together and see if there's a solution that fits your needs.",
            "closer": "Based on our conversation, I believe NGX could really benefit you. Would you like to take the next step?",
            "value_reinforcement": "The value you'll receive from NGX goes beyond the investment—it's about transforming your daily performance.",
            "engagement": "That's interesting! Tell me more about your thoughts on this."
        }
        
        return fallback_prompts.get(
            prompt_type,
            "How can I assist you with your performance goals?"
        )
    
    async def get_prompt_insights(
        self,
        prompt_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get insights about prompt performance"""
        
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Build query
        query = self.supabase.table('prompt_variants').select('*')
        
        if prompt_type:
            query = query.eq('prompt_type', prompt_type)
        
        response = query.gte('created_at', since).execute()
        
        if not response.data:
            return {
                "total_variants": 0,
                "average_performance": 0,
                "best_genes": {},
                "improvement_rate": 0
            }
        
        variants = response.data
        
        # Analyze gene performance
        gene_performance = {}
        for variant in variants:
            genes = json.loads(variant.get('genes', '{}'))
            performance = variant.get('performance_score', 0)
            
            for gene, value in genes.items():
                if gene not in gene_performance:
                    gene_performance[gene] = {}
                if value not in gene_performance[gene]:
                    gene_performance[gene][value] = []
                gene_performance[gene][value].append(performance)
        
        # Find best performing gene values
        best_genes = {}
        for gene, values in gene_performance.items():
            best_value = max(
                values.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0
            )
            best_genes[gene] = {
                "value": best_value[0],
                "avg_performance": sum(best_value[1]) / len(best_value[1])
            }
        
        # Calculate improvement rate
        early_variants = [v for v in variants if v['created_at'] < (datetime.utcnow() - timedelta(days=days/2)).isoformat()]
        recent_variants = [v for v in variants if v['created_at'] >= (datetime.utcnow() - timedelta(days=days/2)).isoformat()]
        
        early_avg = sum(v['performance_score'] for v in early_variants) / len(early_variants) if early_variants else 0
        recent_avg = sum(v['performance_score'] for v in recent_variants) / len(recent_variants) if recent_variants else 0
        
        improvement_rate = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        
        return {
            "total_variants": len(variants),
            "average_performance": sum(v['performance_score'] for v in variants) / len(variants),
            "best_genes": best_genes,
            "improvement_rate": improvement_rate,
            "top_variant": max(variants, key=lambda v: v['performance_score']),
            "gene_insights": gene_performance
        }
    
    async def optimize_hie_prompt(
        self,
        prompt_type: str,
        user_context: Dict[str, Any],
        target_metric: str = 'hie_conversion_rate'
    ) -> str:
        """Optimize prompts specifically for HIE conversion"""
        
        try:
            # Get user profession and archetype
            profession = user_context.get('profession', 'Professional')
            archetype = ArchetypeType(user_context.get('detected_tier', 'optimizer').lower())
            
            # Get HIE context for this user
            hie_context = self.hie_knowledge.generate_hie_context(user_context, 'optimization_phase')
            
            # Generate HIE-focused prompt variants
            variants = await self._generate_hie_focused_variants(
                prompt_type, 
                profession, 
                archetype, 
                hie_context
            )
            
            # Test variants for HIE conversion
            best_variant = await self._test_hie_variants(variants, user_context, target_metric)
            
            # Learn from results
            await self._learn_from_hie_optimization(best_variant, user_context, target_metric)
            
            return best_variant['prompt']
            
        except Exception as e:
            logger.error(f"HIE prompt optimization failed: {e}")
            return await self._get_fallback_hie_prompt(prompt_type, user_context)
    
    async def _generate_hie_focused_variants(
        self,
        prompt_type: str,
        profession: str,
        archetype: ArchetypeType,
        hie_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate prompt variants specifically focused on NGX benefits"""
        
        # NGX-specific genetic material
        ngx_genes = {
            "ngx_benefit_focus": [
                "performance optimization", 
                "energy amplification",
                "stress mastery",
                "focus enhancement",
                "longevity support",
                "vitality optimization"
            ],
            "evidence_type": [
                "scientific_research",
                "customer_success_story",
                "measurable_results",
                "roi_data",
                "peer_reviewed_studies"
            ],
            "urgency_mechanism": [
                "limited_early_access",
                "optimization_timeline",
                "competitive_advantage",
                "compounding_benefits",
                "immediate_results"
            ],
            "social_proof": [
                "ceo_testimonial",
                "professional_peer",
                "industry_leader",
                "similar_challenge",
                "measurable_outcomes"
            ],
            "hie_language": [
                "scientifically_validated",
                "measurably_superior",
                "optimization_protocol",
                "enhancement_system",
                "performance_acceleration"
            ],
            "benefit_framing": [
                "multiplication_not_addition",
                "systemic_optimization",
                "compound_improvements",
                "exponential_returns",
                "permanent_enhancement"
            ]
        }
        
        # Get base HIE templates by prompt type
        base_templates = self._get_hie_base_templates(prompt_type, profession, archetype)
        
        variants = []
        
        # Generate variants using genetic combinations
        for i in range(8):  # Generate 8 variants
            # Select random genes
            selected_genes = {}
            for gene_type, options in ngx_genes.items():
                selected_genes[gene_type] = random.choice(options)
            
            # Build prompt from template and genes
            base_template = random.choice(base_templates)
            
            # Replace variables with NGX-specific content
            prompt = await self._build_hie_prompt_from_genes(
                base_template,
                selected_genes,
                hie_context,
                profession,
                archetype
            )
            
            variants.append({
                'id': str(uuid4()),
                'prompt': prompt,
                'genes': selected_genes,
                'template': base_template,
                'ngx_focus': selected_genes['ngx_benefit_focus'],
                'evidence_type': selected_genes['evidence_type']
            })
        
        return variants
    
    def _get_hie_base_templates(
        self,
        prompt_type: str,
        profession: str,
        archetype: ArchetypeType
    ) -> List[str]:
        """Get HIE-focused base templates by prompt type and user profile"""
        
        templates = {
            'greeting': {
                'ceo': [
                    "As a {profession}, you understand the value of optimization. NGX represents the next evolution in {ngx_benefit_focus} - with {evidence_type} showing {measurable_result}% improvement. {social_proof_example} achieved {roi_result}% ROI. Ready to explore what's possible?",
                    "Executive performance optimization through {ngx_benefit_focus} - scientifically validated with {evidence_type}. {social_proof_example} transformed their {specific_challenge} with {measurable_result}% improvement. Shall we discuss your optimization potential?"
                ],
                'consultant': [
                    "Your clients expect peak performance. NGX delivers {ngx_benefit_focus} with measurable {evidence_type} - {social_proof_example} improved client satisfaction by {measurable_result}%. Ready to become their competitive advantage?",
                    "Transform your consulting impact with {ngx_benefit_focus}. {evidence_type} proves {measurable_result}% improvement in {specific_metric}. {social_proof_example} achieved {roi_result}% ROI. Let's optimize your client outcomes."
                ],
                'doctor': [
                    "Patient outcomes improve when providers operate at peak capacity. NGX enhances {ngx_benefit_focus} with {evidence_type} showing {measurable_result}% improvement. {social_proof_example} enhanced patient care through optimization. Interested in learning more?",
                    "Medical precision requires optimal cognitive function. NGX provides {ngx_benefit_focus} with validated {evidence_type}. {social_proof_example} achieved {measurable_result}% improvement in {specific_metric}. Ready to explore enhanced performance?"
                ],
                'entrepreneur': [
                    "Innovation requires peak cognitive performance. NGX delivers {ngx_benefit_focus} with {evidence_type} proving {measurable_result}% improvement. {social_proof_example} closed their Series C after NGX optimization. Ready to accelerate your success?",
                    "Entrepreneurial edge through {ngx_benefit_focus}. {evidence_type} demonstrates {measurable_result}% improvement in {specific_metric}. {social_proof_example} achieved {roi_result}% ROI. Let's discuss your competitive advantage."
                ]
            },
            'objection_handling': {
                'price_concern': [
                    "{social_proof_example} had the same concern - then achieved {roi_result}% ROI in {timeframe} months. With {evidence_type} proving {measurable_result}% improvement in {ngx_benefit_focus}, the question isn't cost - it's what NOT optimizing costs you daily.",
                    "Investment perspective: {evidence_type} shows {measurable_result}% improvement in {ngx_benefit_focus}. {social_proof_example} calculated their NGX investment paid for itself in {payback_period} through enhanced {specific_benefit}. What's your current performance worth?"
                ],
                'skepticism': [
                    "Healthy skepticism is smart. That's why we have {evidence_type} with {sample_size}+ participants proving {measurable_result}% improvement. {social_proof_example} was skeptical too - until they experienced {specific_result}. Ready for a demonstration?",
                    "Science-based skepticism? Perfect. {evidence_type} from {institution} with {sample_size} participants proves {measurable_result}% improvement in {ngx_benefit_focus}. {social_proof_example} transformed from skeptic to advocate after experiencing {specific_result}."
                ]
            },
            'closing': [
                "Based on {evidence_type} and {social_proof_example}'s {roi_result}% ROI, NGX optimization in {ngx_benefit_focus} offers measurable {specific_benefit}. With {urgency_factor}, shall we begin your transformation?",
                "The data is clear: {evidence_type} proves {measurable_result}% improvement. {social_proof_example} achieved {specific_result} in {timeframe}. With NGX's {ngx_benefit_focus}, you're not just improving - you're evolving. Ready to start?"
            ]
        }
        
        # Get profession-specific templates or fallback to generic
        profession_key = profession.lower()
        prompt_templates = templates.get(prompt_type, {})
        
        if isinstance(prompt_templates, dict):
            return prompt_templates.get(profession_key, prompt_templates.get('entrepreneur', list(prompt_templates.values())[0] if prompt_templates else []))
        else:
            return prompt_templates
    
    async def _build_hie_prompt_from_genes(
        self,
        template: str,
        genes: Dict[str, str],
        hie_context: Dict[str, Any],
        profession: str,
        archetype: ArchetypeType
    ) -> str:
        """Build final HIE prompt by replacing variables with gene-selected content"""
        
        # Get relevant HIE data
        success_story = hie_context.get('success_story')
        evidence = hie_context.get('scientific_evidence', [])
        
        # Build replacement dictionary
        replacements = {
            'profession': profession,
            'ngx_benefit_focus': genes['ngx_benefit_focus'],
            'evidence_type': self._get_evidence_content(genes['evidence_type'], evidence),
            'measurable_result': self._get_measurable_result(genes['ngx_benefit_focus'], success_story),
            'social_proof_example': self._get_social_proof(genes['social_proof'], success_story, profession),
            'roi_result': str(int(success_story.get('roi_achieved', 4500))) if success_story else "4,500",
            'specific_challenge': success_story.get('initial_challenge', 'performance optimization') if success_story else 'performance optimization',
            'specific_metric': self._get_specific_metric(genes['ngx_benefit_focus']),
            'timeframe': str(success_story.get('timeframe_months', 6)) if success_story else "6",
            'urgency_factor': self._get_urgency_content(genes['urgency_mechanism']),
            'specific_benefit': self._get_specific_benefit(genes['ngx_benefit_focus']),
            'specific_result': self._get_specific_result(genes['ngx_benefit_focus'], success_story),
            'institution': 'Stanford' if evidence else 'leading research institutions',
            'sample_size': str(evidence[0].get('sample_size', 1247)) if evidence else '1,247',
            'payback_period': '3.2 weeks'
        }
        
        # Replace variables in template
        prompt = template
        for variable, content in replacements.items():
            prompt = prompt.replace(f'{{{variable}}}', str(content))
        
        return prompt
    
    def _get_evidence_content(self, evidence_type: str, evidence_list: List[Dict]) -> str:
        """Get evidence content based on selected gene"""
        if not evidence_list:
            return "peer-reviewed research"
        
        evidence = evidence_list[0]
        
        if evidence_type == "scientific_research":
            return f"research from {evidence.get('institution', 'MIT')}"
        elif evidence_type == "peer_reviewed_studies":
            return f"peer-reviewed studies with {evidence.get('sample_size', 1247)} participants"
        elif evidence_type == "measurable_results":
            return f"clinical data showing {evidence.get('improvement_percentage', 34.7):.1f}% improvement"
        else:
            return "validated research"
    
    def _get_measurable_result(self, benefit_focus: str, success_story: Dict) -> str:
        """Get measurable result based on benefit focus and success story"""
        if not success_story:
            return "35"
        
        results = success_story.get('measurable_results', {})
        
        mapping = {
            'performance optimization': results.get('performance_improvement', results.get('productivity', 47)),
            'energy amplification': results.get('energy_consistency', results.get('personal_energy', 67)),
            'stress mastery': results.get('stress_reduction', results.get('stress_management', 48)),
            'focus enhancement': results.get('focus_improvement', results.get('concentration', 78)),
            'longevity support': results.get('health_markers', results.get('vitality', 29)),
            'vitality optimization': results.get('vitality_improvement', results.get('vitality', 42))
        }
        
        return str(int(mapping.get(benefit_focus, 35)))
    
    def _get_social_proof(self, social_proof_type: str, success_story: Dict, profession: str) -> str:
        """Get social proof content based on selected gene"""
        if not success_story:
            return f"A fellow {profession}"
        
        name = success_story.get('anonymized_name', 'Michael R.')
        prof = success_story.get('profession', profession)
        
        if social_proof_type == "ceo_testimonial":
            return f"{name}, {prof}"
        elif social_proof_type == "similar_challenge":
            return f"{name} ({prof}) with similar challenges"
        elif social_proof_type == "industry_leader":
            return f"{name}, industry leader in {prof.lower()}"
        else:
            return f"{name}, {prof}"
    
    def _get_specific_metric(self, benefit_focus: str) -> str:
        """Get specific metric based on benefit focus"""
        mapping = {
            'performance optimization': 'overall productivity',
            'energy amplification': 'sustained energy',
            'stress mastery': 'stress resilience',
            'focus enhancement': 'attention span',
            'longevity support': 'biological markers',
            'vitality optimization': 'daily energy levels'
        }
        return mapping.get(benefit_focus, 'performance metrics')
    
    def _get_urgency_content(self, urgency_mechanism: str) -> str:
        """Get urgency content based on selected gene"""
        mapping = {
            'limited_early_access': 'limited early access program',
            'optimization_timeline': 'optimization compounding over time',
            'competitive_advantage': 'your competitive advantage window',
            'compounding_benefits': 'benefits that compound daily',
            'immediate_results': 'immediate results protocol'
        }
        return mapping.get(urgency_mechanism, 'optimization opportunity')
    
    def _get_specific_benefit(self, benefit_focus: str) -> str:
        """Get specific benefit based on focus"""
        mapping = {
            'performance optimization': 'professional output',
            'energy amplification': 'sustained performance',
            'stress mastery': 'pressure handling',
            'focus enhancement': 'deep work capacity',
            'longevity support': 'long-term optimization',
            'vitality optimization': 'daily wellness'
        }
        return mapping.get(benefit_focus, 'professional performance')
    
    def _get_specific_result(self, benefit_focus: str, success_story: Dict) -> str:
        """Get specific result based on focus and success story"""
        if not success_story:
            return "measurable performance improvements"
        
        quote = success_story.get('testimonial_quote', '')
        if len(quote) > 50:
            return quote[:47] + "..."
        
        return "transformational results"
    
    async def _test_hie_variants(
        self,
        variants: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        target_metric: str
    ) -> Dict[str, Any]:
        """Test HIE prompt variants and return best performer"""
        
        # For now, simulate testing with heuristic scoring
        # In production, this would integrate with actual A/B testing
        
        scored_variants = []
        
        for variant in variants:
            score = await self._score_hie_variant(variant, user_context, target_metric)
            variant['score'] = score
            scored_variants.append(variant)
        
        # Return best scoring variant
        best_variant = max(scored_variants, key=lambda v: v['score'])
        
        return best_variant
    
    async def _score_hie_variant(
        self,
        variant: Dict[str, Any],
        user_context: Dict[str, Any],
        target_metric: str
    ) -> float:
        """Score HIE variant based on conversion factors"""
        
        score = 0.5  # Base score
        
        genes = variant['genes']
        profession = user_context.get('profession', '').lower()
        
        # Score based on NGX-specific factors
        
        # 1. Benefit focus alignment with profession
        benefit_profession_mapping = {
            'ceo': ['performance optimization', 'vitality optimization'],
            'consultant': ['performance optimization', 'energy amplification'],
            'doctor': ['focus enhancement', 'stress mastery'],
            'entrepreneur': ['energy amplification', 'performance optimization']
        }
        
        if genes['ngx_benefit_focus'] in benefit_profession_mapping.get(profession, []):
            score += 0.2
        
        # 2. Evidence type credibility
        if genes['evidence_type'] in ['scientific_research', 'peer_reviewed_studies']:
            score += 0.15
        
        # 3. Social proof relevance
        if genes['social_proof'] in ['similar_challenge', 'professional_peer']:
            score += 0.1
        
        # 4. Language sophistication
        if genes['hie_language'] in ['scientifically_validated', 'optimization_protocol']:
            score += 0.1
        
        # 5. Benefit framing impact
        if genes['benefit_framing'] in ['exponential_returns', 'compound_improvements']:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _learn_from_hie_optimization(
        self,
        best_variant: Dict[str, Any],
        user_context: Dict[str, Any],
        target_metric: str
    ) -> None:
        """Learn from HIE optimization results for future improvement"""
        
        try:
            # Store optimization result
            await self.supabase.table('hie_prompt_optimizations').insert({
                'variant_id': best_variant['id'],
                'genes': json.dumps(best_variant['genes']),
                'prompt': best_variant['prompt'],
                'score': best_variant['score'],
                'profession': user_context.get('profession'),
                'archetype': user_context.get('detected_tier'),
                'target_metric': target_metric,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            # Update genetic algorithm learning
            await self._update_hie_genetic_weights(best_variant, user_context)
            
        except Exception as e:
            logger.error(f"Error learning from HIE optimization: {e}")
    
    async def _update_hie_genetic_weights(
        self,
        best_variant: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> None:
        """Update genetic algorithm weights based on HIE optimization success"""
        
        # Update gene weights for better future combinations
        profession = user_context.get('profession', '').lower()
        genes = best_variant['genes']
        score = best_variant['score']
        
        # Store gene performance data
        for gene_type, gene_value in genes.items():
            await self.supabase.table('hie_gene_performance').upsert({
                'gene_type': gene_type,
                'gene_value': gene_value,
                'profession': profession,
                'performance_score': score,
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
    
    async def _get_fallback_hie_prompt(
        self,
        prompt_type: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Get fallback HIE prompt if optimization fails"""
        
        profession = user_context.get('profession', 'Professional')
        
        fallback_prompts = {
            'greeting': f"As a {profession}, you understand the importance of optimization. HIE represents scientifically-validated human performance enhancement with measurable results. Studies show 35% improvement in cognitive performance. Ready to explore your potential?",
            'objection_handling': "I understand your concern. That's why HIE is backed by peer-reviewed research with over 1,200 participants showing measurable improvements. Real customers achieve an average 4,500% ROI. What specific questions can I answer?",
            'closing': "Based on scientific evidence and proven customer results, HIE offers measurable performance optimization. With limited early access available, shall we discuss your implementation timeline?"
        }
        
        return fallback_prompts.get(prompt_type, fallback_prompts['greeting'])
    
    async def get_hie_optimization_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics on HIE prompt optimization performance"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get HIE optimization data
        response = await self.supabase.table('hie_prompt_optimizations').select(
            '*'
        ).gte(
            'created_at', since.isoformat()
        ).execute()
        
        if not response.data:
            return {"message": "No HIE optimization data found"}
        
        optimizations = response.data
        
        # Analytics
        avg_score = sum(opt['score'] for opt in optimizations) / len(optimizations)
        
        # By profession
        by_profession = {}
        for opt in optimizations:
            prof = opt['profession']
            if prof not in by_profession:
                by_profession[prof] = []
            by_profession[prof].append(opt['score'])
        
        profession_performance = {
            prof: {
                'avg_score': sum(scores) / len(scores),
                'count': len(scores)
            }
            for prof, scores in by_profession.items()
        }
        
        # Gene performance
        gene_response = await self.supabase.table('hie_gene_performance').select(
            '*'
        ).gte(
            'updated_at', since.isoformat()
        ).execute()
        
        gene_performance = {}
        if gene_response.data:
            for gene_data in gene_response.data:
                gene_type = gene_data['gene_type']
                if gene_type not in gene_performance:
                    gene_performance[gene_type] = {}
                
                gene_value = gene_data['gene_value']
                if gene_value not in gene_performance[gene_type]:
                    gene_performance[gene_type][gene_value] = []
                
                gene_performance[gene_type][gene_value].append(gene_data['performance_score'])
        
        # Best performing genes
        best_genes = {}
        for gene_type, values in gene_performance.items():
            if values:
                best_value = max(
                    values.items(),
                    key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0
                )
                best_genes[gene_type] = {
                    'value': best_value[0],
                    'avg_score': sum(best_value[1]) / len(best_value[1])
                }
        
        return {
            "total_optimizations": len(optimizations),
            "average_score": avg_score,
            "profession_performance": profession_performance,
            "best_performing_genes": best_genes,
            "improvement_trends": self._calculate_hie_improvement_trends(optimizations),
            "timeframe_days": days
        }
    
    def _calculate_hie_improvement_trends(self, optimizations: List[Dict]) -> Dict[str, Any]:
        """Calculate improvement trends in HIE optimization"""
        
        if len(optimizations) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by creation date
        sorted_opts = sorted(optimizations, key=lambda x: x['created_at'])
        
        # Calculate trend
        early_half = sorted_opts[:len(sorted_opts)//2]
        later_half = sorted_opts[len(sorted_opts)//2:]
        
        early_avg = sum(opt['score'] for opt in early_half) / len(early_half)
        later_avg = sum(opt['score'] for opt in later_half) / len(later_half)
        
        improvement = ((later_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        
        return {
            "improvement_percentage": improvement,
            "early_period_avg": early_avg,
            "later_period_avg": later_avg,
            "trend": "improving" if improvement > 5 else "stable" if improvement > -5 else "declining"
        }