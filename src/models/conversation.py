from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import uuid

class Message(BaseModel):
    """Modelo para un mensaje en la conversación."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system"] = "user"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class CustomerData(BaseModel):
    """Datos del cliente y su interacción."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr # Usamos EmailStr para validación
    age: int
    gender: Optional[str] = None
    occupation: Optional[str] = None
    goals: Dict[str, Any] = Field(default_factory=dict)
    fitness_metrics: Dict[str, Any] = Field(default_factory=dict)
    lifestyle: Dict[str, Any] = Field(default_factory=dict)
    interaction_history: Dict[str, Any] = Field(default_factory=dict) # De la segunda definición
    created_at: datetime = Field(default_factory=datetime.now) # De la segunda definición
    updated_at: datetime = Field(default_factory=datetime.now) # De la segunda definición

    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 120:
            raise ValueError('La edad debe estar entre 18 y 120 años')
        return v

class ConversationState(BaseModel):
    """Estado de una conversación entre el agente y un cliente."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None  # Añadido para compatibilidad con Supabase
    customer_id: Optional[str] = None
    program_type: Literal["PRIME", "LONGEVITY"] = "PRIME"
    phase: Literal[
        "greeting", 
        "exploration", 
        "presentation", 
        "objection_handling", 
        "closing", 
        "follow_up",
        "completed"
    ] = "greeting"
    messages: List[Message] = Field(default_factory=list)
    customer_data: Dict[str, Any] = Field(default_factory=dict)
    session_insights: Dict[str, Any] = Field(default_factory=dict)
    objections_raised: List[str] = Field(default_factory=list)
    
    # Campos para la sesión del agente de voz
    session_id: Optional[str] = None
    session_start_time: Optional[datetime] = None
    max_duration_seconds: Optional[int] = None
    intent_detection_timeout: Optional[int] = None
    next_steps_agreed: bool = False
    call_duration_seconds: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def __init__(self, **data):
        # Gestionar la compatibilidad conversation_id e id
        if 'id' in data and 'conversation_id' not in data:
            data['conversation_id'] = data['id']
        elif 'conversation_id' in data and 'id' not in data:
            data['id'] = data['conversation_id']
        super().__init__(**data)
    
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Asegurar que conversation_id siempre está presente y coincide con id
        if 'id' in data and ('conversation_id' not in data or data['conversation_id'] is None):
            data['conversation_id'] = data['id']
        return data
    
    def add_message(self, role: Literal["user", "assistant", "system"], content: str) -> None:
        """
        Añadir un mensaje a la conversación.
        
        Args:
            role (str): Rol del mensaje (user, assistant, system)
            content (str): Contenido del mensaje
        """
        message = Message(role=role, content=content)
        self.messages.append(message) # Almacenamos el objeto Message directamente
        self.updated_at = datetime.now()
    
    def get_formatted_message_history(self) -> List[Dict[str, str]]:
        """Devuelve el historial de mensajes formateado para el SDK de OpenAI Agents."""
        history = []
        for msg in self.messages:
            if msg.role in ["user", "assistant"]:
                history.append({"role": msg.role, "content": msg.content})
        return history
    
    def update_phase(self, new_phase: str) -> None:
        """
        Actualizar la fase actual de la conversación.
        
        Args:
            new_phase (str): Nueva fase de la conversación
        """
        self.phase = new_phase
        self.updated_at = datetime.now()
    
    def add_objection(self, objection: str) -> None:
        """
        Añadir una objeción planteada por el cliente.
        
        Args:
            objection (str): Objeción planteada
        """
        if objection not in self.objections_raised:
            self.objections_raised.append(objection)
            self.updated_at = datetime.now()
    
    def update_insights(self, key: str, value: Any) -> None:
        """
        Actualizar los insights de la sesión.
        
        Args:
            key (str): Clave del insight
            value (Any): Valor del insight
        """
        self.session_insights[key] = value
        self.updated_at = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 