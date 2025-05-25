"""
Agente simulado para pruebas sin necesidad de API key de OpenAI.
"""

import logging
import random
from typing import List, Dict, Any, Optional

# Configurar logging
logger = logging.getLogger(__name__)

class MockAgentResult:
    """Resultado simulado de una ejecución del agente."""
    
    def __init__(self, final_output: str):
        self.final_output = final_output

class MockAgent:
    """
    Agente simulado para pruebas sin necesidad de API key de OpenAI.
    Genera respuestas predefinidas según el contexto de la conversación.
    """
    
    def __init__(self, program_type: str = "PRIME"):
        """
        Inicializar el agente simulado.
        
        Args:
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
        """
        self.program_type = program_type
        logger.info(f"Agente simulado inicializado para programa {program_type}")
        
        # Respuestas predefinidas para diferentes fases de la conversación
        self.responses = {
            "greeting": [
                "¡Gracias por tu interés en nuestro programa! Estoy aquí para ayudarte a entender cómo NGX puede mejorar tu rendimiento físico y cognitivo.",
                "Me alegra que quieras saber más sobre NGX. Nuestro programa está diseñado para optimizar tu biología y ayudarte a alcanzar tus objetivos de rendimiento."
            ],
            "exploration": [
                "Basado en tus objetivos de mejorar tu condición física y aumentar masa muscular, nuestro programa PRIME sería perfecto para ti. Combina suplementos de alta calidad con un plan personalizado.",
                "Veo que tienes un estilo de vida activo. NGX PRIME puede ayudarte a optimizar tu recuperación y maximizar tus resultados de entrenamiento."
            ],
            "objection": [
                "Entiendo tu preocupación sobre el precio. Sin embargo, NGX es una inversión en tu salud y rendimiento a largo plazo. Muchos de nuestros clientes ven resultados significativos en las primeras semanas.",
                "Es normal tener dudas. Lo que hace único a NGX es nuestra formulación basada en ciencia y nuestro enfoque personalizado. No es solo otro suplemento más."
            ],
            "closing": [
                "¿Te gustaría comenzar con NGX PRIME hoy? Podemos procesar tu pedido ahora y tendrás tu primer kit en unos días.",
                "Basado en nuestra conversación, creo que NGX PRIME es la mejor opción para ti. ¿Quieres que te guíe a través del proceso de registro?"
            ],
            "fallback": [
                "Esa es una excelente pregunta. NGX se basa en la ciencia más avanzada de optimización biológica para ayudarte a alcanzar tu máximo potencial.",
                "Gracias por compartir eso. En NGX, creemos que cada persona es única, por eso nuestros programas están diseñados para adaptarse a tus necesidades específicas."
            ]
        }
    
    async def run(self, messages: List[Dict[str, str]]) -> MockAgentResult:
        """
        Simular una ejecución del agente.
        
        Args:
            messages (List[Dict[str, str]]): Historial de mensajes
            
        Returns:
            MockAgentResult: Resultado simulado con la respuesta
        """
        # Determinar la fase de la conversación basada en el número de mensajes
        num_messages = len([m for m in messages if m["role"] == "user"])
        
        if num_messages <= 1:
            phase = "greeting"
        elif num_messages <= 3:
            phase = "exploration"
        elif num_messages <= 5:
            phase = "objection"
        else:
            phase = "closing"
        
        # Obtener el último mensaje del usuario para análisis básico
        last_user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"].lower()
                break
        
        # Detectar si hay una objeción
        objection_keywords = ["caro", "precio", "costoso", "no puedo pagar", "demasiado", "dudas", "no estoy seguro"]
        if any(keyword in last_user_message for keyword in objection_keywords):
            phase = "objection"
        
        # Seleccionar una respuesta aleatoria para la fase actual
        responses = self.responses.get(phase, self.responses["fallback"])
        response = random.choice(responses)
        
        # Personalizar la respuesta con el tipo de programa
        response = response.replace("NGX", f"NGX {self.program_type}")
        
        logger.info(f"Agente simulado generó respuesta para fase {phase}: {response[:50]}...")
        return MockAgentResult(final_output=response)

# Clase simulada para el Runner
class MockRunner:
    """Simulador del Runner de OpenAI Agents."""
    
    @staticmethod
    async def run(agent: MockAgent, messages: List[Dict[str, str]]) -> MockAgentResult:
        """
        Simular la ejecución de un agente.
        
        Args:
            agent (MockAgent): Agente a ejecutar
            messages (List[Dict[str, str]]): Historial de mensajes
            
        Returns:
            MockAgentResult: Resultado de la ejecución
        """
        return await agent.run(messages)
