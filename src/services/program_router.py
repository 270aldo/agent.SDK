"""
Servicio de routing inteligente para detectar automáticamente el programa
NGX más adecuado (PRIME o LONGEVITY) basado en el perfil del cliente.
"""
import logging
import asyncio
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from src.agents.tools.adaptive_tools import analyze_customer_profile, switch_program_focus
from src.conversation.flows.basic_flow import ConversationFlow
from src.utils.program_router_logger import get_program_router_logger, ProgramDecisionLogger, log_system_performance

logger = get_program_router_logger()

@dataclass
class ProgramDecision:
    """Representa una decisión de programa tomada por el router."""
    recommended_program: str
    confidence_score: float
    reasoning: str
    signals_detected: list
    is_hybrid: bool
    timestamp: datetime
    should_ask_clarifying: bool = False

class ProgramRouter:
    """
    Router inteligente que determina automáticamente el programa NGX
    más adecuado para cada cliente basado en múltiples señales.
    """
    
    def __init__(self):
        """Inicializar el router con configuraciones."""
        self.confidence_threshold_high = 0.8  # Decisión automática
        self.confidence_threshold_medium = 0.6  # Zona híbrida
        self.age_weight = 0.4  # Peso de la edad en la decisión
        self.content_weight = 0.6  # Peso del contenido/contexto
        
        # Tracking de decisiones
        self.decision_history = []
        
        # Logger especializado para decisiones
        self.decision_logger = ProgramDecisionLogger(logger)
        
        logger.info(
            f"ROUTER_INITIALIZED: threshold_high={self.confidence_threshold_high} | "
            f"threshold_medium={self.confidence_threshold_medium} | "
            f"age_weight={self.age_weight} | content_weight={self.content_weight}"
        )
    
    async def determine_program(
        self, 
        customer_data: Dict[str, Any], 
        initial_message: str = "",
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> ProgramDecision:
        """
        Determina el programa más adecuado basado en todos los datos disponibles.
        
        Args:
            customer_data: Datos del cliente (edad, intereses, etc.)
            initial_message: Primer mensaje del cliente
            conversation_context: Contexto adicional de la conversación
            
        Returns:
            ProgramDecision: Decisión del programa con detalles
        """
        start_time = time.time()
        
        try:
            customer_id = customer_data.get('id', 'unknown')
            customer_name = customer_data.get('name', 'anónimo')
            customer_age = customer_data.get('age')
            
            # Log inicio de decisión
            self.decision_logger.log_decision_start(customer_id, customer_data)
            
            # Paso 1: Análisis básico por edad
            age_analysis = self._analyze_age_factor(customer_data.get('age'))
            self.decision_logger.log_analysis_step("age_analysis", age_analysis)
            
            # Paso 2: Análisis de contenido si hay mensaje inicial
            content_analysis = None
            if initial_message.strip():
                content_analysis = await self._analyze_content(initial_message, customer_data.get('age'))
                if content_analysis:
                    self.decision_logger.log_analysis_step("content_analysis", content_analysis)
            
            # Paso 3: Análisis de contexto adicional
            context_analysis = self._analyze_context(customer_data, conversation_context)
            self.decision_logger.log_analysis_step("context_analysis", context_analysis)
            
            # Paso 4: Combinar todas las señales
            final_decision = self._combine_analyses(
                age_analysis, 
                content_analysis, 
                context_analysis,
                customer_data
            )
            
            # Paso 5: Logging y tracking
            self._log_decision(final_decision, customer_data)
            self.decision_logger.log_final_decision(final_decision, customer_data)
            self.decision_history.append(final_decision)
            
            # Log performance
            duration_ms = (time.time() - start_time) * 1000
            log_system_performance(
                logger, 
                "determine_program", 
                duration_ms, 
                True,
                {
                    "customer_id": customer_id,
                    "program": final_decision.recommended_program,
                    "confidence": f"{final_decision.confidence_score:.3f}"
                }
            )
            
            return final_decision
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            customer_id = customer_data.get('id', 'unknown')
            
            logger.error(
                f"PROGRAM_DECISION_ERROR: {str(e)} | "
                f"customer_id={customer_id} | "
                f"fallback_activated=true"
            )
            logger.debug(f"ERROR_DETAILS: {type(e).__name__}: {e}")
            
            # Log performance del error
            log_system_performance(
                logger, 
                "determine_program", 
                duration_ms, 
                False,
                {"customer_id": customer_id, "error": str(e)}
            )
            
            # Fallback seguro
            return self._create_fallback_decision(customer_data)
    
    def _analyze_age_factor(self, age: Optional[int]) -> Dict[str, Any]:
        """Analiza el factor edad para la decisión de programa."""
        if not age:
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.0,
                "reasoning": "Edad no especificada"
            }
        
        # Lógica de edad con zona híbrida
        if age < 35:
            # Claramente PRIME
            return {
                "prime_score": 0.9,
                "longevity_score": 0.1,
                "confidence": 0.8,
                "reasoning": f"Edad {age} años - target claro PRIME"
            }
        elif age < 45:
            # Probablemente PRIME
            return {
                "prime_score": 0.7,
                "longevity_score": 0.3,
                "confidence": 0.6,
                "reasoning": f"Edad {age} años - tendencia PRIME"
            }
        elif age < 55:
            # Zona híbrida - necesita más información
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.3,
                "reasoning": f"Edad {age} años - zona híbrida, evaluar estilo de vida"
            }
        elif age < 65:
            # Probablemente LONGEVITY
            return {
                "prime_score": 0.3,
                "longevity_score": 0.7,
                "confidence": 0.6,
                "reasoning": f"Edad {age} años - tendencia LONGEVITY"
            }
        else:
            # Claramente LONGEVITY
            return {
                "prime_score": 0.1,
                "longevity_score": 0.9,
                "confidence": 0.8,
                "reasoning": f"Edad {age} años - target claro LONGEVITY"
            }
    
    async def _analyze_content(self, message: str, age: Optional[int] = None) -> Dict[str, Any]:
        """Analiza el contenido del mensaje usando las herramientas adaptativas."""
        try:
            # Usar la herramienta existente de análisis de perfil
            profile_analysis = await analyze_customer_profile(
                transcript=message,
                customer_age=age
            )
            
            return {
                "prime_score": profile_analysis.get('prime_affinity', 0.5),
                "longevity_score": profile_analysis.get('longevity_affinity', 0.5),
                "confidence": profile_analysis.get('confidence_score', 0.0),
                "reasoning": profile_analysis.get('analysis_summary', 'Análisis de contenido'),
                "signals": profile_analysis.get('detected_signals', [])
            }
            
        except Exception as e:
            logger.error(
                f"CONTENT_ANALYSIS_ERROR: {str(e)} | "
                f"message_length={len(message)} | "
                f"customer_age={age or 'unknown'}"
            )
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.0,
                "reasoning": f"Error en análisis de contenido: {str(e)}",
                "signals": ["content_analysis_error"]
            }
    
    def _analyze_context(
        self, 
        customer_data: Dict[str, Any], 
        conversation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza el contexto adicional del cliente."""
        prime_indicators = 0
        longevity_indicators = 0
        signals = []
        
        # Analizar intereses reportados
        interests = customer_data.get('interests', [])
        for interest in interests:
            interest_lower = interest.lower()
            
            # Indicadores PRIME (rendimiento, productividad)
            prime_keywords = [
                'rendimiento', 'productividad', 'energía', 'foco', 'concentración',
                'trabajo', 'empresa', 'carrera', 'liderazgo', 'éxito', 'eficiencia'
            ]
            
            # Indicadores LONGEVITY (salud, bienestar, prevención)
            longevity_keywords = [
                'salud', 'bienestar', 'vitalidad', 'prevención', 'longevidad',
                'familia', 'nietos', 'independencia', 'movilidad', 'articulaciones'
            ]
            
            for keyword in prime_keywords:
                if keyword in interest_lower:
                    prime_indicators += 1
                    signals.append(f"interés_prime: {interest}")
                    break
            
            for keyword in longevity_keywords:
                if keyword in interest_lower:
                    longevity_indicators += 1
                    signals.append(f"interés_longevity: {interest}")
                    break
        
        # Normalizar scores
        total_indicators = prime_indicators + longevity_indicators
        if total_indicators > 0:
            prime_score = prime_indicators / total_indicators
            longevity_score = longevity_indicators / total_indicators
            confidence = min(total_indicators * 0.2, 0.8)  # Máximo 80% de confianza
        else:
            prime_score = 0.5
            longevity_score = 0.5
            confidence = 0.0
        
        return {
            "prime_score": prime_score,
            "longevity_score": longevity_score,
            "confidence": confidence,
            "reasoning": f"Análisis de {total_indicators} indicadores contextuales",
            "signals": signals
        }
    
    def _combine_analyses(
        self,
        age_analysis: Dict[str, Any],
        content_analysis: Optional[Dict[str, Any]],
        context_analysis: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> ProgramDecision:
        """Combina todos los análisis para tomar la decisión final."""
        
        # Pesos para la combinación
        age_weight = self.age_weight
        content_weight = self.content_weight if content_analysis else 0
        context_weight = 0.3 if not content_analysis else 0.1
        
        # Normalizar pesos si no hay análisis de contenido
        total_weight = age_weight + content_weight + context_weight
        age_weight = age_weight / total_weight
        content_weight = content_weight / total_weight
        context_weight = context_weight / total_weight
        
        # Combinar scores
        final_prime_score = (
            age_analysis["prime_score"] * age_weight +
            (content_analysis["prime_score"] if content_analysis else 0.5) * content_weight +
            context_analysis["prime_score"] * context_weight
        )
        
        final_longevity_score = (
            age_analysis["longevity_score"] * age_weight +
            (content_analysis["longevity_score"] if content_analysis else 0.5) * content_weight +
            context_analysis["longevity_score"] * context_weight
        )
        
        # Combinar confianzas
        final_confidence = (
            age_analysis["confidence"] * age_weight +
            (content_analysis["confidence"] if content_analysis else 0.0) * content_weight +
            context_analysis["confidence"] * context_weight
        )
        
        # Determinar programa recomendado
        if final_prime_score > final_longevity_score * 1.2:  # 20% más alto
            recommended_program = "PRIME"
            confidence_boost = final_prime_score - final_longevity_score
        elif final_longevity_score > final_prime_score * 1.2:
            recommended_program = "LONGEVITY"
            confidence_boost = final_longevity_score - final_prime_score
        else:
            recommended_program = "HYBRID"
            confidence_boost = 0
        
        # Ajustar confianza con el boost de diferencia
        final_confidence = min(final_confidence + confidence_boost * 0.3, 1.0)
        
        # Determinar si es zona híbrida
        is_hybrid = (
            recommended_program == "HYBRID" or 
            final_confidence < self.confidence_threshold_medium
        )
        
        # Determinar si necesita preguntas clarificadoras
        should_ask_clarifying = (
            final_confidence < self.confidence_threshold_high and
            not is_hybrid
        )
        
        # Crear reasoning detallado
        reasoning_parts = []
        reasoning_parts.append(f"Edad: {age_analysis['reasoning']}")
        if content_analysis:
            reasoning_parts.append(f"Contenido: {content_analysis['reasoning']}")
        reasoning_parts.append(f"Contexto: {context_analysis['reasoning']}")
        reasoning_parts.append(f"Confianza final: {final_confidence:.2f}")
        
        # Combinar señales detectadas
        all_signals = []
        if content_analysis and 'signals' in content_analysis:
            all_signals.extend(content_analysis['signals'])
        if 'signals' in context_analysis:
            all_signals.extend(context_analysis['signals'])
        
        return ProgramDecision(
            recommended_program=recommended_program,
            confidence_score=final_confidence,
            reasoning=" | ".join(reasoning_parts),
            signals_detected=all_signals,
            is_hybrid=is_hybrid,
            timestamp=datetime.now(),
            should_ask_clarifying=should_ask_clarifying
        )
    
    def _create_fallback_decision(self, customer_data: Dict[str, Any]) -> ProgramDecision:
        """Crea una decisión de fallback en caso de error."""
        age = customer_data.get('age')
        
        # Fallback simple basado en edad si está disponible
        if age and age < 50:
            program = "PRIME"
            confidence = 0.6
            reasoning = f"Fallback: edad {age} años sugiere PRIME"
        elif age and age >= 50:
            program = "LONGEVITY"
            confidence = 0.6
            reasoning = f"Fallback: edad {age} años sugiere LONGEVITY"
        else:
            program = "HYBRID"
            confidence = 0.3
            reasoning = "Fallback: información insuficiente, modo híbrido"
        
        fallback_decision = ProgramDecision(
            recommended_program=program,
            confidence_score=confidence,
            reasoning=reasoning,
            signals_detected=["fallback_mode"],
            is_hybrid=(program == "HYBRID"),
            timestamp=datetime.now(),
            should_ask_clarifying=True
        )
        
        # Log específico para fallback
        logger.warning(
            f"FALLBACK_DECISION: program={program} | confidence={confidence:.3f} | "
            f"customer_age={age or 'unknown'} | reason=error_recovery"
        )
        
        return fallback_decision
    
    def _log_decision(self, decision: ProgramDecision, customer_data: Dict[str, Any]):
        """Registra la decisión para análisis posterior con logging estructurado."""
        # Log principal con información clave
        logger.info(
            f"PROGRAM_DECISION: {decision.recommended_program} | "
            f"confidence={decision.confidence_score:.2f} | "
            f"customer_age={customer_data.get('age', 'N/A')} | "
            f"is_hybrid={decision.is_hybrid} | "
            f"needs_clarification={decision.should_ask_clarifying}"
        )
        
        # Log detallado del reasoning
        logger.info(f"DECISION_REASONING: {decision.reasoning}")
        
        # Log de señales detectadas
        if decision.signals_detected:
            logger.info(f"DETECTED_SIGNALS: {', '.join(decision.signals_detected)}")
        else:
            logger.info("DETECTED_SIGNALS: none")
        
        # Log estructurado para análisis posterior
        logger.info(
            f"DECISION_METRICS: program={decision.recommended_program} | "
            f"confidence={decision.confidence_score:.3f} | "
            f"timestamp={decision.timestamp.isoformat()} | "
            f"customer_id={customer_data.get('id', 'unknown')} | "
            f"signals_count={len(decision.signals_detected)}"
        )
        
        # Log de categorización de confianza
        if decision.confidence_score >= self.confidence_threshold_high:
            confidence_level = "HIGH"
        elif decision.confidence_score >= self.confidence_threshold_medium:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        logger.info(f"CONFIDENCE_LEVEL: {confidence_level} ({decision.confidence_score:.3f})")
        
        # Log de debug con datos adicionales
        logger.debug(
            f"DECISION_DEBUG: customer_data={customer_data} | "
            f"decision_history_count={len(self.decision_history)}"
        )
    
    async def should_switch_program(
        self, 
        current_program: str, 
        new_information: str,
        conversation_history: list = None
    ) -> Tuple[bool, Optional[ProgramDecision]]:
        """
        Evalúa si se debe cambiar de programa basado en nueva información.
        
        Args:
            current_program: Programa actual (PRIME o LONGEVITY)
            new_information: Nueva información del cliente
            conversation_history: Historial de la conversación
            
        Returns:
            Tuple[bool, ProgramDecision]: (should_switch, new_decision)
        """
        try:
            # Crear transcript combinado para análisis
            full_transcript = new_information
            if conversation_history:
                recent_messages = conversation_history[-3:]  # Últimos 3 mensajes
                full_transcript = " ".join([msg.get('content', '') for msg in recent_messages])
                full_transcript += " " + new_information
            
            # Analizar el nuevo contenido
            new_analysis = await analyze_customer_profile(
                transcript=full_transcript,
                customer_age=None  # No tenemos edad en este contexto
            )
            
            new_program = new_analysis.get('recommended_program', current_program)
            confidence = new_analysis.get('confidence_score', 0.0)
            
            # Solo cambiar si hay alta confianza y el programa es diferente
            should_switch = (
                new_program != current_program and 
                new_program != "HYBRID" and
                confidence > self.confidence_threshold_high
            )
            
            if should_switch:
                new_decision = ProgramDecision(
                    recommended_program=new_program,
                    confidence_score=confidence,
                    reasoning=f"Cambio detectado por nueva información: {new_analysis.get('analysis_summary', '')}",
                    signals_detected=new_analysis.get('detected_signals', []),
                    is_hybrid=False,
                    timestamp=datetime.now(),
                    should_ask_clarifying=False
                )
                
                # Log estructurado del cambio de programa
                logger.info(
                    f"PROGRAM_SWITCH: from={current_program} | to={new_program} | "
                    f"confidence={confidence:.3f} | reason=new_information_analysis"
                )
                logger.info(f"SWITCH_REASONING: {new_analysis.get('analysis_summary', '')}")
                
                return True, new_decision
            else:
                logger.debug(
                    f"PROGRAM_SWITCH_REJECTED: current={current_program} | "
                    f"suggested={new_program} | confidence={confidence:.3f} | "
                    f"threshold_required={self.confidence_threshold_high}"
                )
                return False, None
                
        except Exception as e:
            logger.error(f"Error evaluando cambio de programa: {e}")
            return False, None
    
    def get_decision_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de las decisiones tomadas con logging."""
        if not self.decision_history:
            analytics = {"total_decisions": 0}
            logger.info("ANALYTICS_REQUEST: no_decisions_available")
            return analytics
        
        total = len(self.decision_history)
        prime_count = sum(1 for d in self.decision_history if d.recommended_program == "PRIME")
        longevity_count = sum(1 for d in self.decision_history if d.recommended_program == "LONGEVITY")
        hybrid_count = sum(1 for d in self.decision_history if d.recommended_program == "HYBRID")
        
        avg_confidence = sum(d.confidence_score for d in self.decision_history) / total
        high_confidence_count = sum(1 for d in self.decision_history 
                                   if d.confidence_score > self.confidence_threshold_high)
        
        analytics = {
            "total_decisions": total,
            "program_distribution": {
                "PRIME": prime_count,
                "LONGEVITY": longevity_count,
                "HYBRID": hybrid_count
            },
            "average_confidence": avg_confidence,
            "high_confidence_rate": high_confidence_count / total,
            "confidence_breakdown": {
                "high": high_confidence_count,
                "medium": sum(1 for d in self.decision_history 
                            if self.confidence_threshold_medium <= d.confidence_score < self.confidence_threshold_high),
                "low": sum(1 for d in self.decision_history 
                          if d.confidence_score < self.confidence_threshold_medium)
            }
        }
        
        # Log analytics
        from src.utils.program_router_logger import log_program_analytics
        log_program_analytics(logger, analytics)
        
        return analytics