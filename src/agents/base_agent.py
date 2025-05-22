"""
Define el agente base para las conversaciones de ventas NGX utilizando el SDK de OpenAI Agents.
"""
from agents import Agent, ModelSettings
from src.conversation.prompts import PRIME_SYSTEM_PROMPT, LONGEVITY_SYSTEM_PROMPT
from src.agents.tools import get_program_details, handle_price_objection # Importamos nuestras herramientas

class NGXBaseAgent(Agent):
    def __init__(self, program_type: str = "PRIME", **kwargs):
        """
        Inicializa el agente base NGX.

        Args:
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY").
                                Determina el system prompt y la configuración base.
        """
        self.program_type = program_type.upper()
        
        if self.program_type == "PRIME":
            system_instructions = PRIME_SYSTEM_PROMPT
        elif self.program_type == "LONGEVITY":
            system_instructions = LONGEVITY_SYSTEM_PROMPT
        else:
            raise ValueError("Tipo de programa no válido. Debe ser 'PRIME' o 'LONGEVITY'.")

        # Herramientas disponibles para este agente
        available_tools = [
            get_program_details,
            handle_price_objection # Añadida nueva herramienta
        ]

        super().__init__(
            name=f"NGX {self.program_type} Sales Agent",
            instructions=system_instructions,
            tools=available_tools,
            # Podríamos configurar model_settings si queremos especificar el modelo de OpenAI, temperatura, etc.
            # model_settings=ModelSettings(model="gpt-4o", temperature=0.7),
            **kwargs
        ) 