"""
Modelos para el contexto de plataforma y configuración multi-canal.

Este módulo define las estructuras de datos necesarias para soportar
la integración del agente en múltiples puntos de contacto.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """Tipos de plataforma soportados."""
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    EMBEDDED = "embedded"


class SourceType(str, Enum):
    """Tipos de fuente de tráfico."""
    LEAD_MAGNET = "lead-magnet"
    BLOG = "blog"
    LANDING_PAGE = "landing-page"
    MOBILE_APP = "mobile-app"
    DIRECT_API = "direct-api"
    SOCIAL_MEDIA = "social-media"
    EMAIL_CAMPAIGN = "email-campaign"
    REFERRAL = "referral"


class UserIntent(str, Enum):
    """Intención del usuario detectada."""
    EDUCATIONAL = "educational"
    PURCHASING = "purchasing"
    EXPLORING = "exploring"
    SUPPORT = "support"
    CONSULTATION = "consultation"


class ConversationMode(str, Enum):
    """Modo de conversación del agente."""
    EDUCATIONAL = "educational"
    SALES = "sales"
    CONSULTANT = "consultant"
    SUPPORT = "support"
    NURTURE = "nurture"


@dataclass
class PlatformInfo:
    """
    Información sobre la plataforma desde donde se inicia la conversación.
    """
    platform_type: PlatformType
    source: SourceType
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    campaign_id: Optional[str] = None
    content_topic: Optional[str] = None
    user_intent: UserIntent = UserIntent.EXPLORING
    device_info: Optional[Dict[str, Any]] = None
    geo_location: Optional[Dict[str, str]] = None
    session_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationConfig:
    """
    Configuración específica para una conversación basada en el contexto de plataforma.
    """
    mode: ConversationMode
    max_duration_seconds: int = 600
    qualification_threshold: float = 0.5
    tone: str = "professional"
    personality: str = "expert"
    enable_voice: bool = True
    enable_transfer: bool = True
    enable_follow_up: bool = True
    custom_prompts: Dict[str, str] = field(default_factory=dict)
    
    # Configuración de UI específica
    widget_config: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics y tracking
    track_engagement: bool = True
    track_conversion: bool = True
    ab_test_group: Optional[str] = None


@dataclass
class PlatformContext:
    """
    Contexto completo de plataforma para una conversación.
    """
    platform_info: PlatformInfo
    conversation_config: ConversationConfig
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_intent(self, new_intent: UserIntent) -> None:
        """Actualizar la intención del usuario y ajustar configuración."""
        self.platform_info.user_intent = new_intent
        self.updated_at = datetime.now()
        
        # Ajustar configuración basada en nueva intención
        if new_intent == UserIntent.PURCHASING:
            self.conversation_config.mode = ConversationMode.SALES
            self.conversation_config.qualification_threshold = 0.3
        elif new_intent == UserIntent.EDUCATIONAL:
            self.conversation_config.mode = ConversationMode.EDUCATIONAL
            self.conversation_config.max_duration_seconds = 300
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para almacenamiento."""
        return {
            "platform_info": {
                "platform_type": self.platform_info.platform_type.value,
                "source": self.platform_info.source.value,
                "page_url": self.platform_info.page_url,
                "referrer": self.platform_info.referrer,
                "campaign_id": self.platform_info.campaign_id,
                "content_topic": self.platform_info.content_topic,
                "user_intent": self.platform_info.user_intent.value,
                "device_info": self.platform_info.device_info,
                "geo_location": self.platform_info.geo_location,
                "session_metadata": self.platform_info.session_metadata
            },
            "conversation_config": {
                "mode": self.conversation_config.mode.value,
                "max_duration_seconds": self.conversation_config.max_duration_seconds,
                "qualification_threshold": self.conversation_config.qualification_threshold,
                "tone": self.conversation_config.tone,
                "personality": self.conversation_config.personality,
                "enable_voice": self.conversation_config.enable_voice,
                "enable_transfer": self.conversation_config.enable_transfer,
                "enable_follow_up": self.conversation_config.enable_follow_up,
                "custom_prompts": self.conversation_config.custom_prompts,
                "widget_config": self.conversation_config.widget_config,
                "track_engagement": self.conversation_config.track_engagement,
                "track_conversion": self.conversation_config.track_conversion,
                "ab_test_group": self.conversation_config.ab_test_group
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformContext':
        """Crear instancia desde diccionario."""
        platform_info = PlatformInfo(
            platform_type=PlatformType(data["platform_info"]["platform_type"]),
            source=SourceType(data["platform_info"]["source"]),
            page_url=data["platform_info"].get("page_url"),
            referrer=data["platform_info"].get("referrer"),
            campaign_id=data["platform_info"].get("campaign_id"),
            content_topic=data["platform_info"].get("content_topic"),
            user_intent=UserIntent(data["platform_info"]["user_intent"]),
            device_info=data["platform_info"].get("device_info"),
            geo_location=data["platform_info"].get("geo_location"),
            session_metadata=data["platform_info"].get("session_metadata", {})
        )
        
        conversation_config = ConversationConfig(
            mode=ConversationMode(data["conversation_config"]["mode"]),
            max_duration_seconds=data["conversation_config"]["max_duration_seconds"],
            qualification_threshold=data["conversation_config"]["qualification_threshold"],
            tone=data["conversation_config"]["tone"],
            personality=data["conversation_config"]["personality"],
            enable_voice=data["conversation_config"]["enable_voice"],
            enable_transfer=data["conversation_config"]["enable_transfer"],
            enable_follow_up=data["conversation_config"]["enable_follow_up"],
            custom_prompts=data["conversation_config"].get("custom_prompts", {}),
            widget_config=data["conversation_config"].get("widget_config", {}),
            track_engagement=data["conversation_config"]["track_engagement"],
            track_conversion=data["conversation_config"]["track_conversion"],
            ab_test_group=data["conversation_config"].get("ab_test_group")
        )
        
        return cls(
            platform_info=platform_info,
            conversation_config=conversation_config,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )