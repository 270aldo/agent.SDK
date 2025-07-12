#!/usr/bin/env python3
"""
NGX ROI Calculator Service
Calculates ROI for NGX AGENTS ACCESS subscriptions and Hybrid Coaching programs
Based on real NGX value propositions and documented benefits
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..services.ngx_master_knowledge import get_ngx_knowledge, NGXArchetype
from ..integrations.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ROIMetric(Enum):
    """Types of ROI metrics for NGX"""
    TIME_SAVINGS = "time_savings"
    PRODUCTIVITY_GAINS = "productivity_gains"
    HEALTH_COST_AVOIDANCE = "health_cost_avoidance"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    LONGEVITY_VALUE = "longevity_value"
    STRESS_REDUCTION_VALUE = "stress_reduction_value"

@dataclass
class NGXROICalculation:
    """NGX-specific ROI calculation result"""
    metric_type: ROIMetric
    monthly_benefit: float
    annual_benefit: float
    calculation_basis: str
    confidence_score: float
    data_source: str

@dataclass
class NGXROIResult:
    """Complete NGX ROI analysis result"""
    total_roi_percentage: float
    annual_value: float
    subscription_cost: float
    net_benefit: float
    payback_period_months: float
    calculations: List[NGXROICalculation]
    archetype: str
    model_type: str
    key_insights: List[str]
    created_at: datetime

class NGXROICalculator:
    """
    ROI calculator specifically for NGX offerings:
    - NGX AGENTS ACCESS (Essential/Pro/Elite)
    - NGX Hybrid Coaching (PRIME/LONGEVITY programs)
    """
    
    def __init__(self):
        self.ngx_knowledge = get_ngx_knowledge()
        self.supabase = get_supabase_client()
        
        # Professional baseline data
        self.profession_baselines = {
            'ceo': {
                'hourly_value': 500,
                'annual_salary': 500000,
                'stress_cost': 15000,
                'productivity_baseline': 0.70  # Room for 30% improvement
            },
            'executive': {
                'hourly_value': 300,
                'annual_salary': 300000,
                'stress_cost': 12000,
                'productivity_baseline': 0.75
            },
            'consultant': {
                'hourly_value': 150,
                'annual_salary': 200000,
                'stress_cost': 8000,
                'productivity_baseline': 0.80
            },
            'entrepreneur': {
                'hourly_value': 200,
                'annual_salary': 150000,
                'stress_cost': 10000,
                'productivity_baseline': 0.65  # High upside potential
            },
            'manager': {
                'hourly_value': 75,
                'annual_salary': 150000,
                'stress_cost': 6000,
                'productivity_baseline': 0.75
            },
            'professional': {  # Default
                'hourly_value': 100,
                'annual_salary': 100000,
                'stress_cost': 5000,
                'productivity_baseline': 0.70
            }
        }
        
        # NGX documented benefits by tier
        self.ngx_benefits = {
            'essential': {
                'energy_increase': 0.15,  # +15% energy daily
                'basic_optimization': 0.10,
                'monthly_cost': 79
            },
            'pro': {
                'energy_increase': 0.15,
                'vitality_increase': 0.20,  # +20% vitality
                'optimization_improvement': 0.15,
                'monthly_cost': 149
            },
            'elite': {
                'energy_increase': 0.15,
                'vitality_increase': 0.20,
                'longevity_increase': 0.25,  # +25% longevity
                'maximum_optimization': 0.20,
                'monthly_cost': 199
            },
            'prime_program': {
                'productivity_increase': 0.25,  # +25% productivity
                'executive_roi': 0.25,
                'one_time_cost': 3997
            },
            'longevity_program': {
                'vitality_increase': 0.25,  # +25% vitalidad sostenible
                'healthspan_extension': 0.20,  # 5-10 years extension
                'one_time_cost': 3997
            }
        }
    
    async def calculate_ngx_roi(
        self,
        user_context: Dict[str, Any],
        ngx_offering: str,  # 'essential', 'pro', 'elite', 'prime_program', 'longevity_program'
        timeframe_months: int = 12
    ) -> NGXROIResult:
        """Calculate ROI for specific NGX offering"""
        
        try:
            # Get user baseline
            profession = user_context.get('profession', 'professional').lower()
            baseline = self.profession_baselines.get(profession, self.profession_baselines['professional'])
            
            # Get NGX context
            ngx_context = self.ngx_knowledge.generate_ngx_context(user_context)
            archetype = ngx_context['suggested_archetype']
            
            # Calculate based on offering type
            if ngx_offering in ['essential', 'pro', 'elite']:
                return await self._calculate_agents_access_roi(
                    baseline, ngx_offering, archetype, timeframe_months, user_context
                )
            else:  # prime_program or longevity_program
                return await self._calculate_hybrid_coaching_roi(
                    baseline, ngx_offering, archetype, timeframe_months, user_context
                )
                
        except Exception as e:
            logger.error(f"Error calculating NGX ROI: {e}")
            raise
    
    async def _calculate_agents_access_roi(
        self,
        baseline: Dict[str, Any],
        tier: str,
        archetype: str,
        timeframe_months: int,
        user_context: Dict[str, Any]
    ) -> NGXROIResult:
        """Calculate ROI for NGX AGENTS ACCESS subscription"""
        
        benefits = self.ngx_benefits[tier]
        monthly_cost = benefits['monthly_cost']
        annual_cost = monthly_cost * 12
        
        calculations = []
        
        # 1. Productivity gains from agents coordination
        if 'vitality_increase' in benefits:
            productivity_gain = baseline['annual_salary'] * benefits['vitality_increase']
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.PRODUCTIVITY_GAINS,
                monthly_benefit=productivity_gain / 12,
                annual_benefit=productivity_gain,
                calculation_basis=f"{benefits['vitality_increase']*100}% vitality increase from NGX agents",
                confidence_score=0.85,
                data_source="NGX official documentation"
            ))
        
        # 2. Time savings from agents automation
        if 'energy_increase' in benefits:
            # Energy increase = more effective hours
            extra_effective_hours = 250 * 2 * benefits['energy_increase']  # 250 working days, 2 hours gained
            time_value = extra_effective_hours * baseline['hourly_value']
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.TIME_SAVINGS,
                monthly_benefit=time_value / 12,
                annual_benefit=time_value,
                calculation_basis=f"{benefits['energy_increase']*100}% energy increase = more effective hours",
                confidence_score=0.80,
                data_source="Energy efficiency calculations"
            ))
        
        # 3. Health cost avoidance (Elite tier)
        if 'longevity_increase' in benefits:
            health_cost_avoided = baseline['stress_cost'] * benefits['longevity_increase']
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.HEALTH_COST_AVOIDANCE,
                monthly_benefit=health_cost_avoided / 12,
                annual_benefit=health_cost_avoided,
                calculation_basis=f"{benefits['longevity_increase']*100}% longevity improvement reduces health costs",
                confidence_score=0.75,
                data_source="Preventive health economics"
            ))
        
        # Calculate totals
        total_annual_benefit = sum(calc.annual_benefit for calc in calculations)
        net_benefit = total_annual_benefit - annual_cost
        roi_percentage = (net_benefit / annual_cost) * 100 if annual_cost > 0 else 0
        payback_months = (annual_cost / (total_annual_benefit / 12)) if total_annual_benefit > 0 else 999
        
        # Generate insights
        key_insights = [
            f"NGX {tier.upper()} delivers {roi_percentage:.0f}% ROI through agents coordination",
            f"Payback achieved in {payback_months:.1f} months",
            f"Primary value: {archetype.upper()} archetype optimization",
            f"Agent ecosystem provides 24/7 personalized guidance"
        ]
        
        return NGXROIResult(
            total_roi_percentage=roi_percentage,
            annual_value=total_annual_benefit,
            subscription_cost=annual_cost,
            net_benefit=net_benefit,
            payback_period_months=payback_months,
            calculations=calculations,
            archetype=archetype,
            model_type=f"NGX AGENTS ACCESS - {tier.upper()}",
            key_insights=key_insights,
            created_at=datetime.utcnow()
        )
    
    async def _calculate_hybrid_coaching_roi(
        self,
        baseline: Dict[str, Any],
        program: str,
        archetype: str,
        timeframe_months: int,
        user_context: Dict[str, Any]
    ) -> NGXROIResult:
        """Calculate ROI for NGX Hybrid Coaching programs"""
        
        benefits = self.ngx_benefits[program]
        program_cost = benefits['one_time_cost']
        
        calculations = []
        
        if program == 'prime_program':
            # PRIME: +25% productivity for executives
            productivity_gain = baseline['annual_salary'] * benefits['productivity_increase']
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.PRODUCTIVITY_GAINS,
                monthly_benefit=productivity_gain / 12,
                annual_benefit=productivity_gain,
                calculation_basis="25% productivity increase from PRIME hybrid coaching",
                confidence_score=0.90,
                data_source="NGX PRIME program documentation"
            ))
            
            # Executive performance premium
            executive_premium = baseline['annual_salary'] * 0.15  # 15% career acceleration
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.PERFORMANCE_IMPROVEMENT,
                monthly_benefit=executive_premium / 12,
                annual_benefit=executive_premium,
                calculation_basis="Executive performance enhancement and career acceleration",
                confidence_score=0.85,
                data_source="Executive coaching ROI studies"
            ))
            
        else:  # longevity_program
            # LONGEVITY: +25% vitalidad sostenible
            vitality_value = baseline['annual_salary'] * benefits['vitality_increase']
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.LONGEVITY_VALUE,
                monthly_benefit=vitality_value / 12,
                annual_benefit=vitality_value,
                calculation_basis="25% sustainable vitality increase",
                confidence_score=0.88,
                data_source="NGX LONGEVITY program documentation"
            ))
            
            # Healthcare cost avoidance
            health_savings = baseline['stress_cost'] * 2  # Preventive approach
            calculations.append(NGXROICalculation(
                metric_type=ROIMetric.HEALTH_COST_AVOIDANCE,
                monthly_benefit=health_savings / 12,
                annual_benefit=health_savings,
                calculation_basis="Healthspan extension reduces long-term healthcare costs",
                confidence_score=0.80,
                data_source="Longevity economics research"
            ))
        
        # Calculate totals
        total_annual_benefit = sum(calc.annual_benefit for calc in calculations)
        net_benefit = total_annual_benefit - program_cost
        roi_percentage = (net_benefit / program_cost) * 100 if program_cost > 0 else 0
        payback_months = (program_cost / (total_annual_benefit / 12)) if total_annual_benefit > 0 else 999
        
        # Generate insights
        program_name = "NGX PRIME" if program == 'prime_program' else "NGX LONGEVITY"
        key_insights = [
            f"{program_name} delivers {roi_percentage:.0f}% ROI through hybrid coaching",
            f"Investment payback in {payback_months:.1f} months",
            f"Combines human coach strategy + AI agents execution",
            f"20-week transformation program with lifetime agent access"
        ]
        
        return NGXROIResult(
            total_roi_percentage=roi_percentage,
            annual_value=total_annual_benefit,
            subscription_cost=program_cost,
            net_benefit=net_benefit,
            payback_period_months=payback_months,
            calculations=calculations,
            archetype=archetype,
            model_type=program_name,
            key_insights=key_insights,
            created_at=datetime.utcnow()
        )
    
    async def compare_ngx_offerings(
        self,
        user_context: Dict[str, Any]
    ) -> Dict[str, NGXROIResult]:
        """Compare ROI across different NGX offerings for user"""
        
        offerings = ['essential', 'pro', 'elite']
        
        # Add hybrid coaching if user profile suggests it
        profession = user_context.get('profession', '').lower()
        if any(exec_term in profession for exec_term in ['ceo', 'executive', 'founder']):
            offerings.append('prime_program')
        
        age = user_context.get('age', 35)
        if age >= 45:
            offerings.append('longevity_program')
        
        results = {}
        for offering in offerings:
            try:
                roi_result = await self.calculate_ngx_roi(user_context, offering)
                results[offering] = roi_result
            except Exception as e:
                logger.warning(f"Could not calculate ROI for {offering}: {e}")
        
        return results
    
    async def get_recommended_ngx_offering(
        self,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get recommended NGX offering based on ROI analysis"""
        
        comparisons = await self.compare_ngx_offerings(user_context)
        
        if not comparisons:
            return {"error": "Could not calculate ROI for any offerings"}
        
        # Find best ROI
        best_offering = max(comparisons.items(), key=lambda x: x[1].total_roi_percentage)
        
        # Find best value (considering cost)
        best_value = min(comparisons.items(), key=lambda x: x[1].payback_period_months)
        
        return {
            "recommended_offering": best_offering[0],
            "recommended_roi": best_offering[1].total_roi_percentage,
            "best_value_offering": best_value[0],
            "best_value_payback": best_value[1].payback_period_months,
            "all_comparisons": {k: {
                "roi_percentage": v.total_roi_percentage,
                "annual_value": v.annual_value,
                "cost": v.subscription_cost,
                "payback_months": v.payback_period_months
            } for k, v in comparisons.items()},
            "recommendation_reasoning": self._generate_recommendation_reasoning(comparisons, user_context)
        }
    
    def _generate_recommendation_reasoning(
        self,
        comparisons: Dict[str, NGXROIResult],
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for recommendation"""
        
        reasoning = []
        profession = user_context.get('profession', 'professional').lower()
        
        # Analyze user context
        if any(exec_term in profession for exec_term in ['ceo', 'executive', 'founder']):
            reasoning.append("Executive-level role suggests high-impact optimization potential")
        
        if user_context.get('age', 35) >= 45:
            reasoning.append("Age profile indicates longevity focus may provide superior long-term value")
        
        # Analyze ROI patterns
        best_roi = max(comparisons.values(), key=lambda x: x.total_roi_percentage)
        if best_roi.total_roi_percentage > 500:
            reasoning.append(f"Exceptional ROI potential ({best_roi.total_roi_percentage:.0f}%) justifies premium investment")
        
        fastest_payback = min(comparisons.values(), key=lambda x: x.payback_period_months)
        if fastest_payback.payback_period_months < 6:
            reasoning.append(f"Rapid payback ({fastest_payback.payback_period_months:.1f} months) reduces financial risk")
        
        return reasoning

# Global instance
_ngx_roi_calculator = None

def get_ngx_roi_calculator() -> NGXROICalculator:
    """Get global NGX ROI calculator instance"""
    global _ngx_roi_calculator
    if _ngx_roi_calculator is None:
        _ngx_roi_calculator = NGXROICalculator()
    return _ngx_roi_calculator

if __name__ == "__main__":
    # Demo NGX ROI calculation
    import asyncio
    
    async def demo():
        calculator = NGXROICalculator()
        
        test_context = {
            'profession': 'CEO',
            'age': 45,
            'budget_sensitivity': 'low'
        }
        
        print("🚀 NGX ROI Calculator Demo")
        print("=" * 40)
        
        # Test Elite tier
        roi_result = await calculator.calculate_ngx_roi(test_context, 'elite')
        print(f"📊 NGX Elite ROI for CEO:")
        print(f"   ROI: {roi_result.total_roi_percentage:.0f}%")
        print(f"   Annual value: ${roi_result.annual_value:,.0f}")
        print(f"   Payback: {roi_result.payback_period_months:.1f} months")
        print()
        
        # Test recommendation
        recommendation = await calculator.get_recommended_ngx_offering(test_context)
        print(f"🎯 Recommendation: {recommendation['recommended_offering']}")
        print(f"   ROI: {recommendation['recommended_roi']:.0f}%")
        print()
        
        print("✅ NGX ROI Calculator ready!")
    
    asyncio.run(demo())