"""
Factory para crear agentes según el contexto de plataforma.

Este módulo resuelve el problema de dependencias frágiles mediante
dependency injection y factory patterns.
"""

import logging
from typing import Optional, Dict, Any, Type, Protocol, List
from abc import ABC, abstractmethod

from src.models.platform_context import PlatformContext
from src.models.conversation import CustomerData

logger = logging.getLogger(__name__)


class AgentInterface(Protocol):
    """Protocolo que define la interfaz mínima para agentes."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Procesar un mensaje y retornar respuesta."""
        ...
    
    def get_configuration(self) -> Dict[str, Any]:
        """Obtener configuración del agente."""
        ...


class BaseAgentAdapter(ABC):
    """Adaptador base para diferentes tipos de agentes."""
    
    def __init__(self, platform_context: PlatformContext):
        self.platform_context = platform_context
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    async def create_agent(self, customer_data: CustomerData) -> AgentInterface:
        """Crear instancia del agente."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verificar si el agente está disponible."""
        pass


class OpenAIAgentAdapter(BaseAgentAdapter):
    """Adaptador para agentes de OpenAI Agents SDK."""
    
    def __init__(self, platform_context: PlatformContext):
        super().__init__(platform_context)
        self._agent_module = None
        self._runner_module = None
        self._load_modules()
    
    def _load_modules(self) -> None:
        """Cargar módulos de OpenAI Agents de forma segura."""
        try:
            # Intentar importar el SDK de OpenAI Agents
            import agents
            self._agent_module = agents.Agent
            self._runner_module = agents.Runner
            self.logger.info("OpenAI Agents SDK cargado exitosamente")
        except ImportError as e:
            self.logger.warning(f"OpenAI Agents SDK no disponible: {e}")
            self._agent_module = None
            self._runner_module = None
    
    def is_available(self) -> bool:
        """Verificar si OpenAI Agents SDK está disponible."""
        return self._agent_module is not None and self._runner_module is not None
    
    async def create_agent(self, customer_data: CustomerData) -> AgentInterface:
        """Crear agente de OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI Agents SDK no está disponible")
        
        # Importar el agente unificado
        from src.agents.unified_agent import NGXUnifiedAgent
        
        # Crear contexto inicial basado en platform_context
        initial_context = {
            "platform_type": self.platform_context.platform_info.platform_type.value,
            "source": self.platform_context.platform_info.source.value,
            "mode": self.platform_context.conversation_config.mode.value,
            "customer_data": customer_data.model_dump() if hasattr(customer_data, 'model_dump') else vars(customer_data)
        }
        
        # Crear agente con contexto
        agent = NGXUnifiedAgent(initial_context=initial_context)
        
        return OpenAIAgentWrapper(agent, self._runner_module)


class MockAgentAdapter(BaseAgentAdapter):
    """Adaptador para agente simulado (fallback)."""
    
    def is_available(self) -> bool:
        """El agente mock siempre está disponible."""
        return True
    
    async def create_agent(self, customer_data: CustomerData) -> AgentInterface:
        """Crear agente simulado."""
        from src.agents.mock_agent import MockAgent
        
        # Crear configuración para mock agent
        mock_config = {
            "mode": self.platform_context.conversation_config.mode.value,
            "tone": self.platform_context.conversation_config.tone,
            "personality": self.platform_context.conversation_config.personality,
            "max_duration": self.platform_context.conversation_config.max_duration_seconds
        }
        
        agent = MockAgent(config=mock_config)
        return MockAgentWrapper(agent)


class OpenAIAgentWrapper:
    """Wrapper para agentes de OpenAI que implementa AgentInterface."""
    
    def __init__(self, agent, runner_module):
        self.agent = agent
        self.runner = runner_module
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Procesar mensaje usando OpenAI Agent."""
        try:
            # Preparar mensajes para el agente
            messages = [{"role": "user", "content": message}]
            
            # Ejecutar agente
            result = await self.runner.run(self.agent, messages)
            
            if result and hasattr(result, 'content'):
                return result.content
            elif result:
                return str(result)
            else:
                return "Lo siento, no pude procesar tu mensaje en este momento."
                
        except Exception as e:
            logger.error(f"Error procesando mensaje con OpenAI Agent: {e}")
            return "Lo siento, ocurrió un error procesando tu mensaje."
    
    def get_configuration(self) -> Dict[str, Any]:
        """Obtener configuración del agente."""
        return {
            "type": "openai_agent",
            "model": getattr(self.agent, 'model', 'unknown'),
            "name": getattr(self.agent, 'name', 'NGX Agent')
        }


class MockAgentWrapper:
    """Wrapper para agente simulado que implementa AgentInterface."""
    
    def __init__(self, agent):
        self.agent = agent
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Procesar mensaje usando agente simulado."""
        try:
            return await self.agent.process_message(message, context)
        except Exception as e:
            logger.error(f"Error procesando mensaje con Mock Agent: {e}")
            return "Lo siento, ocurrió un error procesando tu mensaje."
    
    def get_configuration(self) -> Dict[str, Any]:
        """Obtener configuración del agente."""
        return {
            "type": "mock_agent",
            "mode": getattr(self.agent, 'mode', 'unknown'),
            "name": "NGX Mock Agent"
        }


class AgentFactory:
    """
    Factory principal para crear agentes según el contexto de plataforma.
    
    Resuelve el problema de dependencias frágiles mediante un sistema
    de adaptadores que verifica disponibilidad antes de crear agentes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._adapters = [
            OpenAIAgentAdapter,
            MockAgentAdapter  # Siempre último como fallback
        ]
    
    async def create_agent(
        self, 
        platform_context: PlatformContext,
        customer_data: CustomerData
    ) -> AgentInterface:
        """
        Crear agente apropiado según el contexto de plataforma.
        
        Args:
            platform_context: Contexto de la plataforma
            customer_data: Datos del cliente
            
        Returns:
            Instancia de agente que implementa AgentInterface
            
        Raises:
            RuntimeError: Si no se puede crear ningún agente
        """
        last_error = None
        
        for adapter_class in self._adapters:
            try:
                adapter = adapter_class(platform_context)
                
                if adapter.is_available():
                    self.logger.info(f"Usando adaptador: {adapter_class.__name__}")
                    agent = await adapter.create_agent(customer_data)
                    
                    # Verificar que el agente funciona
                    config = agent.get_configuration()
                    self.logger.info(f"Agente creado exitosamente: {config}")
                    
                    return agent
                else:
                    self.logger.debug(f"Adaptador {adapter_class.__name__} no disponible")
                    
            except Exception as e:
                self.logger.warning(f"Error creando agente con {adapter_class.__name__}: {e}")
                last_error = e
                continue
        
        # Si llegamos aquí, ningún adaptador funcionó
        error_msg = f"No se pudo crear ningún agente. Último error: {last_error}"
        self.logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def get_available_adapters(self) -> List[str]:
        """Obtener lista de adaptadores disponibles."""
        available = []
        
        for adapter_class in self._adapters:
            try:
                # Crear contexto dummy para la verificación
                from src.models.platform_context import PlatformInfo, ConversationConfig, PlatformContext
                from src.models.platform_context import PlatformType, SourceType, ConversationMode
                
                dummy_context = PlatformContext(
                    platform_info=PlatformInfo(
                        platform_type=PlatformType.API,
                        source=SourceType.DIRECT_API
                    ),
                    conversation_config=ConversationConfig(
                        mode=ConversationMode.SALES
                    )
                )
                
                adapter = adapter_class(dummy_context)
                if adapter.is_available():
                    available.append(adapter_class.__name__)
                    
            except Exception as e:
                self.logger.debug(f"Error verificando {adapter_class.__name__}: {e}")
        
        return available


# Instancia global del factory
agent_factory = AgentFactory()