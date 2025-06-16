"""
Modelos de datos para la API predictiva.

Este módulo define los modelos de datos utilizados en la API predictiva,
proporcionando validación y documentación para las entradas y salidas.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import json

# Modelos comunes
class Message(BaseModel):
    """Modelo para un mensaje en una conversación."""
    role: str = Field(..., description="Rol del emisor del mensaje (user | assistant)")
    content: str = Field(..., description="Contenido del mensaje")
    timestamp: str = Field(..., description="Timestamp en formato ISO-8601")
    
    @validator("role")
    def validate_role(cls, v):
        """Valida que el rol sea válido."""
        if v not in ["user", "assistant"]:
            raise ValueError("El rol debe ser 'user' o 'assistant'")
        return v
    
    @validator("timestamp")
    def validate_timestamp(cls, v):
        """Valida que el timestamp tenga formato ISO-8601."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("El timestamp debe tener formato ISO-8601")
        return v

class CustomerProfile(BaseModel):
    """Modelo para el perfil de un cliente."""
    id: Optional[str] = Field(None, description="ID del cliente")
    demographics: Optional[Dict[str, Any]] = Field(None, description="Datos demográficos del cliente")
    purchase_history: Optional[List[Dict[str, Any]]] = Field(None, description="Historial de compras del cliente")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferencias del cliente")

# Modelos para predicción de objeciones
class ObjectionPredictionRequest(BaseModel):
    """Modelo para solicitud de predicción de objeciones."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v

class ObjectionRecord(BaseModel):
    """Modelo para registro de objeciones reales."""
    conversation_id: str = Field(..., description="ID de la conversación")
    objection_type: str = Field(..., description="Tipo de objeción detectada")
    objection_text: str = Field(..., description="Texto de la objeción")
    
    @validator("objection_type")
    def validate_objection_type(cls, v):
        """Valida que el tipo de objeción sea válido."""
        valid_types = ["price", "features", "competition", "timing", "trust", "need", "other"]
        if v not in valid_types:
            raise ValueError(f"Tipo de objeción no válido. Debe ser uno de: {', '.join(valid_types)}")
        return v

# Modelos para predicción de necesidades
class NeedsPredictionRequest(BaseModel):
    """Modelo para solicitud de predicción de necesidades."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v

class NeedRecord(BaseModel):
    """Modelo para registro de necesidades reales."""
    conversation_id: str = Field(..., description="ID de la conversación")
    need_category: str = Field(..., description="Categoría de necesidad detectada")
    need_description: str = Field(..., description="Descripción de la necesidad")
    
    @validator("need_category")
    def validate_need_category(cls, v):
        """Valida que la categoría de necesidad sea válida."""
        valid_categories = ["pricing", "features", "support", "integration", "customization", "security", "performance", "other"]
        if v not in valid_categories:
            raise ValueError(f"Categoría de necesidad no válida. Debe ser una de: {', '.join(valid_categories)}")
        return v

# Modelos para predicción de conversión
class ConversionPredictionRequest(BaseModel):
    """Modelo para solicitud de predicción de conversión."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    product_id: Optional[str] = Field(None, description="ID del producto")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v

class ConversionRecord(BaseModel):
    """Modelo para registro de conversiones reales."""
    conversation_id: str = Field(..., description="ID de la conversación")
    did_convert: bool = Field(..., description="Indica si el cliente realmente se convirtió")
    conversion_details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales de la conversión")

# Modelos para motor de decisiones
class OptimizeFlowRequest(BaseModel):
    """Modelo para solicitud de optimización de flujo de conversación."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    current_objectives: Optional[Dict[str, float]] = Field(None, description="Objetivos actuales con sus pesos")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_objectives(cls, values):
        """Valida que los pesos de los objetivos sumen aproximadamente 1."""
        objectives = values.get("current_objectives")
        if objectives:
            total = sum(objectives.values())
            if not (0.99 <= total <= 1.01):
                raise ValueError("La suma de los pesos de los objetivos debe ser aproximadamente 1")
        return values

class AdaptStrategyRequest(BaseModel):
    """Modelo para solicitud de adaptación de estrategia en tiempo real."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    current_strategy: Dict[str, Any] = Field(..., description="Estrategia actual")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback del usuario")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v

class EvaluatePathRequest(BaseModel):
    """Modelo para solicitud de evaluación de ruta de conversación."""
    conversation_id: str = Field(..., description="ID de la conversación")
    messages: List[Message] = Field(..., description="Lista de mensajes de la conversación")
    path_actions: List[Dict[str, Any]] = Field(..., description="Acciones tomadas en la ruta a evaluar")
    customer_profile: Optional[CustomerProfile] = Field(None, description="Perfil del cliente")
    
    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        """Valida que el ID de conversación tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El ID de conversación contiene caracteres no válidos")
        return v
    
    @validator("path_actions")
    def validate_path_actions(cls, v):
        """Valida que las acciones de ruta tengan una estructura válida."""
        if len(v) == 0:
            raise ValueError("Debe proporcionar al menos una acción de ruta")
        
        for action in v:
            if "type" not in action:
                raise ValueError("Cada acción debe tener un tipo")
            if "id" not in action:
                raise ValueError("Cada acción debe tener un ID")
        
        return v

# Modelos para gestión de modelos predictivos
class ModelUpdate(BaseModel):
    """Modelo para actualización de un modelo predictivo."""
    model_params: Optional[Dict[str, Any]] = Field(None, description="Nuevos parámetros del modelo")
    status: Optional[str] = Field(None, description="Nuevo estado del modelo")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Nueva precisión del modelo")
    
    @validator("status")
    def validate_status(cls, v):
        """Valida que el estado sea válido."""
        valid_statuses = ["active", "inactive", "training", "deprecated"]
        if v not in valid_statuses:
            raise ValueError(f"Estado no válido. Debe ser uno de: {', '.join(valid_statuses)}")
        return v
    
    @validator("model_params")
    def validate_model_params(cls, v):
        """Valida que los parámetros del modelo sean serializables."""
        if v:
            try:
                json.dumps(v)
            except (TypeError, OverflowError):
                raise ValueError("Los parámetros del modelo deben ser serializables a JSON")
        return v

# Modelos para retroalimentación
class FeedbackRequest(BaseModel):
    """Modelo para solicitud de retroalimentación sobre una predicción."""
    conversation_id: str = Field(..., description="ID de la conversación")
    model_type: str = Field(..., description="Tipo de modelo (objection, needs, conversion, decision_engine)")
    prediction_id: str = Field(..., description="ID de la predicción")
    feedback_rating: float = Field(..., ge=0, le=1, description="Valoración de 0 a 1 sobre la precisión")
    feedback_details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales sobre la retroalimentación")
    
    @validator("model_type")
    def validate_model_type(cls, v):
        """Valida que el tipo de modelo sea válido."""
        valid_types = ["objection", "needs", "conversion", "decision_engine"]
        if v not in valid_types:
            raise ValueError(f"Tipo de modelo no válido. Debe ser uno de: {', '.join(valid_types)}")
        return v

# Modelos para entrenamiento de modelos
class TrainingRequest(BaseModel):
    """Modelo para solicitud de entrenamiento de modelo."""
    model_name: str = Field(..., description="Nombre del modelo a entrenar")
    force_training: bool = Field(False, description="Si es True, fuerza el entrenamiento aunque no se cumplan los criterios")
    training_config: Optional[Dict[str, Any]] = Field(None, description="Configuración específica para el entrenamiento")
    
    @validator("model_name")
    def validate_model_name(cls, v):
        """Valida que el nombre del modelo tenga un formato válido."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("El nombre del modelo contiene caracteres no válidos")
        return v
    
    @validator("training_config")
    def validate_training_config(cls, v):
        """Valida que la configuración de entrenamiento sea serializable."""
        if v:
            try:
                json.dumps(v)
            except (TypeError, OverflowError):
                raise ValueError("La configuración de entrenamiento debe ser serializable a JSON")
        return v
