"""
Agente unificado NGX con detección dinámica de programa.
Implementa la estrategia de un solo agente inteligente que se adapta al cliente.
"""
from agents import Agent, ModelSettings
from src.conversation.prompts.unified_prompts import UNIFIED_SYSTEM_PROMPT
from src.agents.tools import (
    get_program_details, 
    handle_price_objection,
    analyze_customer_profile,
    switch_program_focus,
    get_adaptive_responses,
    track_conversation_metrics
)
from typing import Optional, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

class NGXUnifiedAgent(Agent):
    """
    Agente unificado que detecta dinámicamente el programa más adecuado
    para cada cliente y adapta su enfoque durante la conversación.
    
    Características mejoradas:
    - Detección inteligente en primeros 60 segundos
    - Transiciones suaves entre programas
    - Modo híbrido para zona 45-55 años
    - Tracking de métricas para optimización continua
    """
    
    def __init__(self, initial_context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Inicializa el agente unificado NGX con capacidades mejoradas.
        
        Args:
            initial_context: Contexto inicial del cliente (edad estimada, score, etc.)
        """
        self.current_mode = "DISCOVERY"  # Inicia siempre en modo discovery
        self.detected_program = None
        self.confidence_score = 0.0
        self.adaptation_history = []
        self.conversation_start_time = time.time()
        self.detection_completed = False
        self.mode_changes_count = 0
        
        # Preparar contexto inicial mejorado
        context_info = self._prepare_initial_context(initial_context or {})
        
        # Herramientas disponibles para este agente (incluyendo las nuevas)
        available_tools = [
            get_program_details,
            handle_price_objection,
            analyze_customer_profile,      # Nueva herramienta de análisis
            switch_program_focus,          # Nueva herramienta de cambio
            get_adaptive_responses,        # Nueva herramienta de respuestas
            track_conversation_metrics     # Nueva herramienta de tracking
        ]
        
        # Configuración del modelo optimizada
        model_settings = ModelSettings(
            model="gpt-4o",
            temperature=0.7,  # Balance entre creatividad y consistencia
            max_tokens=500,
            frequency_penalty=0.3,  # Reduce repetición
            presence_penalty=0.1   # Fomenta variedad
        )
        
        super().__init__(
            name="NGX Unified Sales Agent v2.0",
            instructions=UNIFIED_SYSTEM_PROMPT.format(**context_info),
            tools=available_tools,
            model_settings=model_settings,
            **kwargs
        )
        
        # Configuración de detección automática
        self.detection_config = {
            "min_confidence_threshold": 0.7,  # Umbral para considerar detección completa
            "detection_timeout_seconds": 90,   # Máximo tiempo para detectar
            "hybrid_age_range": (45, 55),     # Rango de edad híbrida
            "quick_detection_signals": 3       # Señales mínimas para detección rápida
        }
        
        logger.info(f"Agente unificado NGX v2.0 inicializado en modo {self.current_mode}")
        logger.info(f"Configuración de detección: {self.detection_config}")
    
    def _prepare_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara el contexto inicial mejorado para el prompt del sistema.
        """
        # Estimar grupo de edad si está disponible
        age = initial_context.get("age")
        age_range = "no especificada"
        if age:
            if age < 35:
                age_range = "30-35 años"
            elif age < 45:
                age_range = "35-45 años"
            elif age < 55:
                age_range = "45-55 años (zona híbrida)"
            elif age < 65:
                age_range = "55-65 años"
            else:
                age_range = "65+ años"
        
        return {
            "initial_score": initial_context.get("score", "no especificado"),
            "age_range": age_range,
            "initial_interests": ", ".join(initial_context.get("interests", ["general"])),
            "lead_source": initial_context.get("lead_source", "lead magnet premium"),
            "test_results_summary": initial_context.get("test_results_summary", "pendiente de análisis")
        }
    
    def update_detection_confidence(self, program: str, confidence: float, reason: str = None):
        """
        Actualiza la confianza en la detección del programa con tracking mejorado.
        """
        previous_program = self.detected_program
        self.detected_program = program
        self.confidence_score = confidence
        
        # Registrar en historial
        detection_entry = {
            "timestamp": self._get_timestamp(),
            "elapsed_seconds": self._get_elapsed_seconds(),
            "program": program,
            "confidence": confidence,
            "mode": self.current_mode,
            "reason": reason or "actualización automática"
        }
        self.adaptation_history.append(detection_entry)
        
        # Cambiar modo según confianza y programa
        if confidence >= self.detection_config["min_confidence_threshold"]:
            if program == "HYBRID":
                self.current_mode = "HYBRID"
            else:
                self.current_mode = f"{program}_FOCUSED"
            self.detection_completed = True
        elif confidence >= 0.3:
            self.current_mode = "HYBRID"
        else:
            self.current_mode = "DISCOVERY"
        
        # Contar cambios de modo
        if previous_program and previous_program != program:
            self.mode_changes_count += 1
        
        logger.info(
            f"Detección actualizada: {program} (confianza: {confidence:.2f}), "
            f"modo: {self.current_mode}, razón: {reason}"
        )
        
        # Auto-tracking si la detección está completa
        if self.detection_completed and not previous_program:
            self._auto_track_detection()
    
    def get_adaptive_context(self) -> Dict[str, Any]:
        """
        Obtiene el contexto adaptativo actual mejorado del agente.
        """
        elapsed_seconds = self._get_elapsed_seconds()
        
        return {
            "current_mode": self.current_mode,
            "detected_program": self.detected_program,
            "confidence_score": self.confidence_score,
            "detection_completed": self.detection_completed,
            "elapsed_seconds": elapsed_seconds,
            "detection_speed": self._get_detection_speed(),
            "adaptation_count": len(self.adaptation_history),
            "mode_changes": self.mode_changes_count,
            "is_hybrid_candidate": self.current_mode == "HYBRID",
            "should_close": elapsed_seconds > 300 and self.detection_completed,  # 5+ minutos
            "conversation_stage": self._determine_conversation_stage()
        }
    
    def get_detection_insights(self) -> Dict[str, Any]:
        """
        Obtiene insights sobre el proceso de detección para optimización.
        """
        if not self.adaptation_history:
            return {"status": "no_data"}
        
        first_detection = next(
            (h for h in self.adaptation_history if h["confidence"] >= 0.5), 
            None
        )
        
        final_detection = self.adaptation_history[-1] if self.adaptation_history else None
        
        return {
            "first_detection_time": first_detection["elapsed_seconds"] if first_detection else None,
            "final_program": final_detection["program"] if final_detection else None,
            "final_confidence": final_detection["confidence"] if final_detection else 0,
            "total_adaptations": len(self.adaptation_history),
            "mode_changes": self.mode_changes_count,
            "detection_stability": self._calculate_detection_stability(),
            "recommendation_quality": self._assess_recommendation_quality()
        }
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual para tracking."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_elapsed_seconds(self) -> int:
        """Calcula segundos transcurridos desde el inicio."""
        return int(time.time() - self.conversation_start_time)
    
    def _determine_conversation_stage(self) -> str:
        """Determina la etapa actual de la conversación."""
        elapsed = self._get_elapsed_seconds()
        
        if elapsed < 60:
            return "opening"
        elif elapsed < 180 and not self.detection_completed:
            return "discovery"
        elif elapsed < 300:
            return "presentation"
        else:
            return "closing"
    
    def _get_detection_speed(self) -> str:
        """Evalúa la velocidad de detección."""
        if not self.detection_completed:
            return "en_proceso"
        
        detection_time = next(
            (h["elapsed_seconds"] for h in self.adaptation_history 
             if h["confidence"] >= self.detection_config["min_confidence_threshold"]),
            None
        )
        
        if detection_time:
            if detection_time <= 30:
                return "muy_rápida"
            elif detection_time <= 60:
                return "rápida"
            elif detection_time <= 90:
                return "normal"
            else:
                return "lenta"
        return "no_detectado"
    
    def _calculate_detection_stability(self) -> float:
        """Calcula qué tan estable fue la detección (menos cambios = más estable)."""
        if len(self.adaptation_history) <= 1:
            return 1.0
        
        # Contar cambios de programa
        program_changes = 0
        for i in range(1, len(self.adaptation_history)):
            if self.adaptation_history[i]["program"] != self.adaptation_history[i-1]["program"]:
                program_changes += 1
        
        # Estabilidad = 1 - (cambios / adaptaciones)
        stability = 1 - (program_changes / len(self.adaptation_history))
        return round(stability, 2)
    
    def _assess_recommendation_quality(self) -> str:
        """Evalúa la calidad de la recomendación basada en métricas."""
        if not self.detection_completed:
            return "pendiente"
        
        stability = self._calculate_detection_stability()
        speed = self._get_detection_speed()
        confidence = self.confidence_score
        
        # Scoring simple
        quality_score = 0
        
        # Confianza alta
        if confidence >= 0.8:
            quality_score += 3
        elif confidence >= 0.7:
            quality_score += 2
        else:
            quality_score += 1
        
        # Estabilidad alta
        if stability >= 0.8:
            quality_score += 2
        elif stability >= 0.6:
            quality_score += 1
        
        # Velocidad adecuada
        if speed in ["rápida", "normal"]:
            quality_score += 1
        
        # Evaluación final
        if quality_score >= 5:
            return "excelente"
        elif quality_score >= 3:
            return "buena"
        else:
            return "mejorable"
    
    def _auto_track_detection(self):
        """Auto-tracking cuando se completa la detección."""
        try:
            # En una implementación real, esto llamaría a track_conversation_metrics
            logger.info(
                f"Auto-tracking: Programa {self.detected_program} detectado "
                f"en {self._get_elapsed_seconds()}s con confianza {self.confidence_score:.2f}"
            )
        except Exception as e:
            logger.error(f"Error en auto-tracking: {e}")
