"""
Gestor de configuraciones por plataforma.

Este módulo centraliza todas las configuraciones específicas para diferentes
puntos de contacto y contextos de conversación.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from src.models.platform_context import (
    PlatformType, SourceType, UserIntent, ConversationMode,
    PlatformInfo, ConversationConfig, PlatformContext
)

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfigTemplate:
    """Template de configuración para una plataforma específica."""
    name: str
    description: str
    default_mode: ConversationMode
    default_config: Dict[str, Any] = field(default_factory=dict)
    ui_config: Dict[str, Any] = field(default_factory=dict)
    triggers: Dict[str, Any] = field(default_factory=dict)


class PlatformConfigManager:
    """
    Gestor central de configuraciones por plataforma.
    
    Proporciona configuraciones optimizadas para diferentes puntos de contacto
    como lead magnets, landing pages, blogs, etc.
    """
    
    # Configuraciones predefinidas por fuente
    PLATFORM_CONFIGS = {
        SourceType.LEAD_MAGNET: PlatformConfigTemplate(
            name="Lead Magnet",
            description="Widget para lead magnets premium con enfoque educativo",
            default_mode=ConversationMode.NURTURE,
            default_config={
                "max_duration_seconds": 300,
                "qualification_threshold": 0.7,
                "tone": "educational",
                "personality": "helpful_expert",
                "enable_voice": True,
                "enable_transfer": False,  # Más sutil en lead magnets
                "enable_follow_up": True,
                "track_engagement": True,
                "track_conversion": True
            },
            ui_config={
                "size": "compact",
                "position": "bottom-right",
                "theme": "professional",
                "auto_open": False,
                "delay_ms": 5000,
                "show_branding": True
            },
            triggers={
                "post_download": True,
                "exit_intent": False,
                "time_based": True,
                "scroll_based": False
            }
        ),
        
        SourceType.LANDING_PAGE: PlatformConfigTemplate(
            name="Landing Page",
            description="Widget optimizado para conversión en landing pages",
            default_mode=ConversationMode.SALES,
            default_config={
                "max_duration_seconds": 600,
                "qualification_threshold": 0.5,
                "tone": "confident",
                "personality": "sales_expert",
                "enable_voice": True,
                "enable_transfer": True,
                "enable_follow_up": True,
                "track_engagement": True,
                "track_conversion": True
            },
            ui_config={
                "size": "large",
                "position": "center",
                "theme": "branded",
                "auto_open": False,
                "delay_ms": 0,
                "show_branding": False,
                "fullscreen_option": True
            },
            triggers={
                "exit_intent": True,
                "cta_click": True,
                "time_based": True,
                "scroll_based": True
            }
        ),
        
        SourceType.BLOG: PlatformConfigTemplate(
            name="Blog/Educational",
            description="Widget contextual para contenido educativo",
            default_mode=ConversationMode.CONSULTANT,
            default_config={
                "max_duration_seconds": 240,
                "qualification_threshold": 0.6,
                "tone": "friendly",
                "personality": "knowledgeable_advisor",
                "enable_voice": True,
                "enable_transfer": True,
                "enable_follow_up": True,
                "track_engagement": True,
                "track_conversion": False  # Menos agresivo en contenido educativo
            },
            ui_config={
                "size": "medium",
                "position": "sidebar",
                "theme": "minimal",
                "auto_open": False,
                "delay_ms": 30000,  # Más tiempo para leer
                "show_branding": True,
                "context_aware": True
            },
            triggers={
                "scroll_percentage": 75,
                "reading_time": 120,
                "exit_intent": True,
                "content_completion": True
            }
        ),
        
        SourceType.MOBILE_APP: PlatformConfigTemplate(
            name="Mobile App",
            description="Configuración optimizada para aplicaciones móviles",
            default_mode=ConversationMode.SUPPORT,
            default_config={
                "max_duration_seconds": 180,  # Más corto en móvil
                "qualification_threshold": 0.5,
                "tone": "casual",
                "personality": "mobile_friendly",
                "enable_voice": True,
                "enable_transfer": True,
                "enable_follow_up": True,
                "track_engagement": True,
                "track_conversion": True
            },
            ui_config={
                "size": "fullscreen",
                "position": "overlay",
                "theme": "mobile_optimized",
                "auto_open": False,
                "gesture_support": True,
                "voice_priority": True
            },
            triggers={
                "app_event": True,
                "push_notification": True,
                "in_app_action": True
            }
        ),
        
        SourceType.DIRECT_API: PlatformConfigTemplate(
            name="Direct API",
            description="Configuración para integraciones directas via API",
            default_mode=ConversationMode.SALES,
            default_config={
                "max_duration_seconds": 900,  # Más tiempo para integraciones custom
                "qualification_threshold": 0.4,
                "tone": "professional",
                "personality": "adaptive",
                "enable_voice": True,
                "enable_transfer": True,
                "enable_follow_up": True,
                "track_engagement": True,
                "track_conversion": True
            },
            ui_config={
                "customizable": True,
                "headless_mode": True,
                "webhook_support": True
            },
            triggers={
                "custom_event": True,
                "api_trigger": True,
                "scheduled": True
            }
        )
    }
    
    @classmethod
    def get_platform_config(
        cls, 
        source: SourceType, 
        custom_overrides: Optional[Dict[str, Any]] = None
    ) -> PlatformContext:
        """
        Obtener configuración completa para una plataforma específica.
        
        Args:
            source: Tipo de fuente/plataforma
            custom_overrides: Configuraciones personalizadas para sobrescribir defaults
            
        Returns:
            PlatformContext configurado para la plataforma
        """
        if source not in cls.PLATFORM_CONFIGS:
            logger.warning(f"Configuración no encontrada para {source}, usando default")
            source = SourceType.DIRECT_API
        
        template = cls.PLATFORM_CONFIGS[source]
        
        # Crear configuración base
        platform_info = PlatformInfo(
            platform_type=cls._detect_platform_type(source),
            source=source,
            user_intent=cls._detect_default_intent(source)
        )
        
        # Crear configuración de conversación
        config_dict = template.default_config.copy()
        if custom_overrides:
            config_dict.update(custom_overrides)
        
        conversation_config = ConversationConfig(
            mode=template.default_mode,
            **config_dict
        )
        
        # Añadir configuración de UI
        conversation_config.widget_config = template.ui_config.copy()
        
        return PlatformContext(
            platform_info=platform_info,
            conversation_config=conversation_config
        )
    
    @classmethod
    def _detect_platform_type(cls, source: SourceType) -> PlatformType:
        """Detectar tipo de plataforma basado en la fuente."""
        mobile_sources = {SourceType.MOBILE_APP}
        api_sources = {SourceType.DIRECT_API}
        
        if source in mobile_sources:
            return PlatformType.MOBILE
        elif source in api_sources:
            return PlatformType.API
        else:
            return PlatformType.WEB
    
    @classmethod
    def _detect_default_intent(cls, source: SourceType) -> UserIntent:
        """Detectar intención por defecto basada en la fuente."""
        intent_mapping = {
            SourceType.LEAD_MAGNET: UserIntent.EDUCATIONAL,
            SourceType.BLOG: UserIntent.EDUCATIONAL,
            SourceType.LANDING_PAGE: UserIntent.PURCHASING,
            SourceType.MOBILE_APP: UserIntent.SUPPORT,
            SourceType.DIRECT_API: UserIntent.EXPLORING,
            SourceType.SOCIAL_MEDIA: UserIntent.EXPLORING,
            SourceType.EMAIL_CAMPAIGN: UserIntent.PURCHASING,
            SourceType.REFERRAL: UserIntent.PURCHASING
        }
        
        return intent_mapping.get(source, UserIntent.EXPLORING)
    
    @classmethod
    def create_custom_config(
        cls,
        platform_type: PlatformType,
        source: SourceType,
        mode: ConversationMode,
        custom_settings: Dict[str, Any]
    ) -> PlatformContext:
        """
        Crear configuración completamente personalizada.
        
        Args:
            platform_type: Tipo de plataforma
            source: Fuente de tráfico
            mode: Modo de conversación
            custom_settings: Configuraciones personalizadas
            
        Returns:
            PlatformContext personalizado
        """
        platform_info = PlatformInfo(
            platform_type=platform_type,
            source=source,
            user_intent=cls._detect_default_intent(source),
            **custom_settings.get("platform_info", {})
        )
        
        conversation_config = ConversationConfig(
            mode=mode,
            **custom_settings.get("conversation_config", {})
        )
        
        return PlatformContext(
            platform_info=platform_info,
            conversation_config=conversation_config
        )
    
    @classmethod
    def get_available_sources(cls) -> List[SourceType]:
        """Obtener lista de fuentes soportadas."""
        return list(cls.PLATFORM_CONFIGS.keys())
    
    @classmethod
    def get_config_template(cls, source: SourceType) -> Optional[PlatformConfigTemplate]:
        """Obtener template de configuración para una fuente."""
        return cls.PLATFORM_CONFIGS.get(source)