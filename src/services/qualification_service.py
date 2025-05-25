"""
Servicio de cualificación de leads para determinar qué usuarios pueden acceder al agente de voz.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from src.integrations.supabase import supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class LeadQualificationService:
    """
    Sistema de puntuación para determinar qué usuarios acceden al agente de voz.
    Implementa criterios de cualificación y límites para optimizar costos y experiencia.
    """
    
    # Criterios de puntuación
    SCORING_CRITERIA = {
        'test_completion_rate': 30,      # Completó >80% del test
        'engagement_time': 20,           # >5 minutos en la app
        'result_interaction': 20,        # Interactuó con resultados
        'demographic_fit': 30            # Fit con audiencia target
    }
    
    # Umbral para acceder al agente de voz
    VOICE_AGENT_THRESHOLD = 75
    
    # Límites de uso
    MAX_CALL_DURATION_SECONDS = 7 * 60   # 7 minutos
    COOLDOWN_PERIOD_HOURS = 48           # 48 horas entre llamadas
    INTENT_DETECTION_TIMEOUT = 3 * 60    # 3 minutos para detectar intención
    
    def __init__(self):
        """Inicializar el servicio de cualificación de leads."""
        logger.info("Servicio de cualificación de leads inicializado")
    
    async def calculate_score(self, user_metrics: Dict[str, Any]) -> Tuple[int, Dict[str, int]]:
        """
        Calcula el score de cualificación para un usuario basado en sus métricas.
        
        Args:
            user_metrics: Diccionario con métricas del usuario
            
        Returns:
            Tuple[int, Dict[str, int]]: Score total y desglose por criterio
        """
        scores = {}
        
        # Criterio 1: Tasa de completación del test
        completion_rate = user_metrics.get('test_completion_rate', 0)
        if completion_rate >= 80:
            scores['test_completion_rate'] = self.SCORING_CRITERIA['test_completion_rate']
        elif completion_rate >= 60:
            scores['test_completion_rate'] = int(self.SCORING_CRITERIA['test_completion_rate'] * 0.7)
        elif completion_rate >= 40:
            scores['test_completion_rate'] = int(self.SCORING_CRITERIA['test_completion_rate'] * 0.4)
        else:
            scores['test_completion_rate'] = 0
            
        # Criterio 2: Tiempo de engagement (en minutos)
        engagement_time = user_metrics.get('engagement_time', 0)
        if engagement_time >= 5:
            scores['engagement_time'] = self.SCORING_CRITERIA['engagement_time']
        elif engagement_time >= 3:
            scores['engagement_time'] = int(self.SCORING_CRITERIA['engagement_time'] * 0.6)
        elif engagement_time >= 1:
            scores['engagement_time'] = int(self.SCORING_CRITERIA['engagement_time'] * 0.3)
        else:
            scores['engagement_time'] = 0
            
        # Criterio 3: Interacción con resultados
        interactions = user_metrics.get('result_interaction', 0)
        if interactions >= 5:
            scores['result_interaction'] = self.SCORING_CRITERIA['result_interaction']
        elif interactions >= 3:
            scores['result_interaction'] = int(self.SCORING_CRITERIA['result_interaction'] * 0.7)
        elif interactions >= 1:
            scores['result_interaction'] = int(self.SCORING_CRITERIA['result_interaction'] * 0.3)
        else:
            scores['result_interaction'] = 0
            
        # Criterio 4: Fit demográfico
        demographic_score = self._calculate_demographic_fit(user_metrics)
        scores['demographic_fit'] = demographic_score
        
        # Calcular score total
        total_score = sum(scores.values())
        
        logger.info(f"Score calculado: {total_score}/100 - Desglose: {scores}")
        return total_score, scores
    
    def _calculate_demographic_fit(self, user_metrics: Dict[str, Any]) -> int:
        """
        Calcula el score de fit demográfico basado en el perfil del usuario.
        
        Args:
            user_metrics: Diccionario con datos demográficos del usuario
            
        Returns:
            int: Score de fit demográfico (0-30)
        """
        score = 0
        max_score = self.SCORING_CRITERIA['demographic_fit']
        
        # Edad (18-65 años es nuestro target principal)
        age = user_metrics.get('age', 0)
        if 25 <= age <= 55:
            score += int(max_score * 0.4)  # 12 puntos
        elif 18 <= age < 25 or 55 < age <= 65:
            score += int(max_score * 0.2)  # 6 puntos
            
        # Ingresos (si están disponibles)
        income = user_metrics.get('income', 0)
        if income >= 80000:
            score += int(max_score * 0.3)  # 9 puntos
        elif income >= 50000:
            score += int(max_score * 0.15)  # 4.5 puntos
            
        # Intereses alineados con nuestro producto
        interests = user_metrics.get('interests', [])
        target_interests = ['fitness', 'salud', 'bienestar', 'nutrición', 'deporte']
        
        matching_interests = sum(1 for interest in interests if interest.lower() in target_interests)
        if matching_interests >= 3:
            score += int(max_score * 0.3)  # 9 puntos
        elif matching_interests >= 1:
            score += int(max_score * 0.15)  # 4.5 puntos
            
        return min(score, max_score)  # Asegurar que no exceda el máximo
    
    async def is_qualified_for_voice(self, user_id: str, user_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determina si un usuario califica para el agente de voz y aplica límites.
        
        Args:
            user_id: ID único del usuario
            user_metrics: Métricas del usuario para calcular score
            
        Returns:
            Dict: Resultado de cualificación con score, elegibilidad y razones
        """
        # Verificar si el usuario ya tuvo una llamada en las últimas 48 horas
        cooldown_status = await self._check_cooldown(user_id)
        if cooldown_status['in_cooldown']:
            return {
                'qualified': False,
                'reason': 'cooldown',
                'score': 0,
                'hours_until_available': cooldown_status['hours_remaining']
            }
        
        # Calcular score de cualificación
        score, score_breakdown = await self.calculate_score(user_metrics)
        
        # Determinar si califica
        qualified = score >= self.VOICE_AGENT_THRESHOLD
        
        # Guardar resultado en la base de datos
        try:
            await self._save_qualification_result(user_id, score, qualified, score_breakdown)
        except Exception as e:
            logger.error(f"Error al guardar resultado de cualificación: {e}")
        
        # Preparar respuesta
        result = {
            'qualified': qualified,
            'score': score,
            'score_breakdown': score_breakdown,
            'threshold': self.VOICE_AGENT_THRESHOLD
        }
        
        if not qualified:
            result['reason'] = 'low_score'
            
        logger.info(f"Resultado de cualificación para usuario {user_id}: {result}")
        return result
    
    async def _check_cooldown(self, user_id: str) -> Dict[str, Any]:
        """
        Verificar si un usuario está en período de enfriamiento (cooldown).
        
        Args:
            user_id: ID del usuario a verificar
            
        Returns:
            Dict con estado de cooldown y horas restantes
        """
        try:
            # Consultar la última sesión del usuario
            result = await supabase_client.table('voice_agent_sessions') \
                .select('created_at, status') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .limit(1) \
                .execute()
            
            if not result.data:
                return {'in_cooldown': False, 'hours_remaining': 0}
            
            last_session = result.data[0]
            last_call_time = datetime.fromisoformat(last_session['created_at'].replace('Z', '+00:00'))
            
            # Calcular tiempo transcurrido desde la última llamada
            now = datetime.now(last_call_time.tzinfo)
            hours_since_last_call = (now - last_call_time).total_seconds() / 3600
            
            # Verificar si está en período de enfriamiento (48 horas)
            if hours_since_last_call < 48:
                return {
                    'in_cooldown': True,
                    'hours_remaining': round(48 - hours_since_last_call, 1)
                }
            
            return {'in_cooldown': False, 'hours_remaining': 0}
            
        except Exception as e:
            logger.error(f"Error al verificar cooldown: {e}")
            # Si hay un error, permitimos la llamada por defecto
            return {'in_cooldown': False, 'hours_remaining': 0}
            
    async def _save_qualification_result(self, user_id: str, score: int, 
                                        qualified: bool, score_breakdown: Dict[str, int]) -> None:
        """
        Guarda el resultado de cualificación en la base de datos.
        
        Args:
            user_id: ID del usuario
            score: Score total calculado
            qualified: Si calificó para el agente de voz
            score_breakdown: Desglose del score por criterio
        """
        try:
            client = supabase_client.get_client()
            
            qualification_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'score': score,
                'qualified': qualified,
                'score_breakdown': score_breakdown,
                'created_at': datetime.now().isoformat()
            }
            
            await client.table("lead_qualifications").insert(qualification_data).execute()
            logger.info(f"Resultado de cualificación guardado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error al guardar resultado de cualificación: {e}")
    
    async def register_voice_agent_session(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Registra una nueva sesión del agente de voz.
        
        Args:
            user_id: ID del usuario
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Datos de la sesión creada
        """
        try:
            client = supabase_client.get_client()
            
            session_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'conversation_id': conversation_id,
                'start_time': datetime.now().isoformat(),
                'max_duration_seconds': self.MAX_CALL_DURATION_SECONDS,
                'intent_detection_timeout': self.INTENT_DETECTION_TIMEOUT,
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            result = await client.table("voice_agent_sessions").insert(session_data).execute()
            
            if result.data:
                logger.info(f"Sesión de agente de voz registrada: {result.data[0]['id']}")
                return result.data[0]
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error al registrar sesión de agente de voz: {e}")
            # Retornamos los datos aunque no se hayan guardado
            return session_data
    
    async def update_session_status(self, session_id: str, status: str, 
                                   end_reason: Optional[str] = None) -> None:
        """
        Actualiza el estado de una sesión del agente de voz.
        
        Args:
            session_id: ID de la sesión
            status: Nuevo estado ('active', 'completed', 'timeout', 'abandoned')
            end_reason: Razón de finalización (opcional)
        """
        try:
            client = supabase_client.get_client()
            
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if status != 'active':
                update_data['end_time'] = datetime.now().isoformat()
                
            if end_reason:
                update_data['end_reason'] = end_reason
                
            await client.table("voice_agent_sessions").update(update_data) \
                .eq("id", session_id).execute()
                
            logger.info(f"Estado de sesión {session_id} actualizado a '{status}'")
            
        except Exception as e:
            logger.error(f"Error al actualizar estado de sesión: {e}")
