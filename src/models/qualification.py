"""
Modelos para el sistema de cualificación de leads.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class UserMetrics(BaseModel):
    """Métricas del usuario para calcular el score de cualificación."""
    
    user_id: str = Field(..., description="ID único del usuario")
    test_completion_rate: float = Field(0, description="Porcentaje de completación del test (0-100)")
    engagement_time: float = Field(0, description="Tiempo de engagement en minutos")
    result_interaction: int = Field(0, description="Número de interacciones con resultados")
    age: Optional[int] = Field(None, description="Edad del usuario")
    income: Optional[int] = Field(None, description="Ingresos anuales en USD")
    health_interest: Optional[int] = Field(None, description="Nivel de interés en salud/fitness (1-10)")
    gender: Optional[str] = Field(None, description="Género del usuario")
    occupation: Optional[str] = Field(None, description="Ocupación del usuario")
    goals: Optional[Dict[str, Any]] = Field(None, description="Objetivos del usuario")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "test_completion_rate": 85,
                "engagement_time": 6.5,
                "result_interaction": 4,
                "age": 42,
                "income": 95000,
                "health_interest": 8,
                "gender": "male",
                "occupation": "engineer",
                "goals": {
                    "primary": "improve fitness",
                    "secondary": "increase energy"
                }
            }
        }

class QualificationResult(BaseModel):
    """Resultado de cualificación de un lead."""
    
    qualified: bool = Field(..., description="Si el usuario califica para el agente de voz")
    score: int = Field(..., description="Score total de cualificación (0-100)")
    score_breakdown: Dict[str, int] = Field(..., description="Desglose del score por criterio")
    threshold: int = Field(..., description="Umbral mínimo para cualificar")
    cooldown: Dict[str, Any] = Field(..., description="Estado de cooldown entre llamadas")
    reason: Optional[str] = Field(None, description="Razón de descalificación si aplica")
    
    class Config:
        schema_extra = {
            "example": {
                "qualified": True,
                "score": 82,
                "score_breakdown": {
                    "test_completion_rate": 30,
                    "engagement_time": 20,
                    "result_interaction": 14,
                    "demographic_fit": 18
                },
                "threshold": 75,
                "cooldown": {
                    "in_cooldown": False,
                    "hours_remaining": 0
                }
            }
        }

class VoiceAgentSession(BaseModel):
    """Sesión del agente de voz."""
    
    id: str = Field(..., description="ID único de la sesión")
    user_id: str = Field(..., description="ID del usuario")
    conversation_id: str = Field(..., description="ID de la conversación")
    start_time: datetime = Field(..., description="Hora de inicio de la sesión")
    end_time: Optional[datetime] = Field(None, description="Hora de finalización de la sesión")
    max_duration_seconds: int = Field(..., description="Duración máxima en segundos")
    intent_detection_timeout: int = Field(..., description="Tiempo límite para detectar intención en segundos")
    status: str = Field(..., description="Estado de la sesión")
    end_reason: Optional[str] = Field(None, description="Razón de finalización si aplica")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_time": "2025-05-24T19:30:00Z",
                "max_duration_seconds": 420,
                "intent_detection_timeout": 180,
                "status": "active"
            }
        }
