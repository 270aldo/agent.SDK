import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from src.models.conversation import ConversationState

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class ConversationEngine:
    """Motor de conversación basado en OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Inicializar el motor de conversación.
        
        Args:
            api_key (Optional[str]): Clave de API de OpenAI. 
                                    Si es None, se usará OPENAI_API_KEY del entorno.
            model (str): Modelo de OpenAI a utilizar.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("Falta variable de entorno OPENAI_API_KEY")
            raise ValueError("Falta API key de OpenAI en variables de entorno")
            
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info(f"Motor de conversación inicializado con modelo {self.model}")
    
    async def get_response(self, state: ConversationState) -> str:
        """
        Obtener respuesta del modelo para una conversación.
        
        Args:
            state (ConversationState): Estado actual de la conversación
            
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            # Preparar mensajes para el modelo
            messages = self._prepare_messages(state)
            
            # Llamar a la API de OpenAI
            logger.info(f"Obteniendo respuesta del modelo para conversación {state.conversation_id}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            
            # Extraer y devolver la respuesta
            response_text = response.choices[0].message.content.strip()
            
            # Analizar la respuesta para detectar la fase
            new_phase = self._detect_phase(state, response_text)
            if new_phase and new_phase != state.phase:
                logger.info(f"Cambiando fase de conversación de {state.phase} a {new_phase}")
                state.phase = new_phase
            
            # Agregar la respuesta al estado
            state.add_message("assistant", response_text)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error al obtener respuesta del modelo: {e}")
            # En caso de error, proporcionar una respuesta de fallback
            fallback = "Lo siento, estoy teniendo problemas para procesar tu solicitud. ¿Podrías reformular tu pregunta o intentarlo más tarde?"
            return fallback
    
    def _prepare_messages(self, state: ConversationState) -> List[Dict[str, str]]:
        """
        Preparar mensajes para enviar al modelo.
        
        Args:
            state (ConversationState): Estado de la conversación
            
        Returns:
            List[Dict[str, str]]: Lista de mensajes formateados para la API
        """
        # Sistema: instrucciones iniciales
        system_prompt = self._generate_system_prompt(state)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Historial: convertir mensajes del estado al formato esperado por OpenAI
        for msg in state.messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    def _generate_system_prompt(self, state: ConversationState) -> str:
        """
        Generar prompt de sistema según el estado actual de la conversación.
        
        Args:
            state (ConversationState): Estado de la conversación
            
        Returns:
            str: Prompt de sistema
        """
        program = state.program_type
        phase = state.phase
        
        # Base del prompt
        prompt = f"""
Eres un agente de ventas especializado para NGX {program}. Tu objetivo es guiar al cliente
a través de una conversación persuasiva y empática que conduzca a la compra del programa.
Tu comunicación debe ser clara, profesional y orientada a resultados.

Información del cliente:
- Nombre: {state.customer_data.get('name', 'Cliente')}
- Edad: {state.customer_data.get('age', 'N/A')}
- Ocupación: {state.customer_data.get('occupation', 'N/A')}
"""
        
        # Objetivos del cliente
        goals = state.customer_data.get('goals', {})
        if goals:
            prompt += "\nObjetivos del cliente:\n"
            if 'primary' in goals:
                prompt += f"- Principal: {goals['primary']}\n"
            if 'secondary' in goals:
                for goal in goals['secondary']:
                    prompt += f"- Secundario: {goal}\n"
        
        # Especificar fase actual
        phases = {
            "greeting": """
FASE: SALUDO INICIAL
- Establece una conexión amigable pero profesional
- Confirma los objetivos del cliente según la evaluación previa
- Escucha activamente y muestra empatía
- No presiones la venta en esta fase, sólo establece confianza
""",
            "exploration": """
FASE: EXPLORACIÓN DE NECESIDADES
- Profundiza en las necesidades específicas del cliente
- Haz preguntas abiertas para descubrir motivaciones y obstáculos
- Toma notas sobre los puntos de dolor mencionados
- Identifica qué aspectos del programa serían más relevantes
""",
            "presentation": """
FASE: PRESENTACIÓN DE SOLUCIÓN
- Explica cómo NGX PRIME se adapta específicamente a las necesidades del cliente
- Destaca 3-4 beneficios clave alineados con sus objetivos
- Presenta un caso de éxito relevante sin exagerar resultados
- Explica la estructura del programa: evaluación inicial, plan personalizado, seguimiento
""",
            "objection_handling": """
FASE: MANEJO DE OBJECIONES
- Aborda las preocupaciones con empatía y sin defensividad
- Proporciona información clara sobre precios y duración
- Ofrece garantías sobre resultados realistas
- Resuelve dudas sobre compromisos de tiempo y esfuerzo
""",
            "closing": """
FASE: CIERRE
- Propón los próximos pasos concretos (agendar sesión inicial)
- Resume los beneficios clave y el valor para el cliente
- Ofrece opciones en lugar de preguntas de sí/no
- Confirma detalles para el seguimiento
- Agradece al cliente por su tiempo e interés
""",
            "follow_up": """
FASE: SEGUIMIENTO
- Confirma los acuerdos alcanzados
- Explica los próximos pasos en detalle
- Responde cualquier pregunta final
- Proporciona información de contacto para asistencia adicional
- Finaliza la conversación de manera positiva y amigable
"""
        }
        
        prompt += "\n" + phases.get(phase, phases["greeting"])
        
        # Agregar instrucciones especiales según el programa
        if program == "PRIME":
            prompt += """
PROGRAMA NGX PRIME:
- Enfoque en rendimiento cerebral, energía física y optimización metabólica
- Beneficios clave: mejor concentración, productividad, gestión del estrés
- Dirigido a profesionales de alto rendimiento
- Incluye: Evaluación bioquímica completa, plan nutricional personalizado, suplementación estratégica, coaching biohacking
"""
        else:  # LONGEVITY
            prompt += """
PROGRAMA NGX LONGEVITY:
- Enfoque en longevidad saludable, prevención y bienestar a largo plazo
- Beneficios clave: vitalidad sostenible, optimización hormonal, mejora de biomarcadores de edad biológica
- Dirigido a adultos interesados en envejecimiento saludable
- Incluye: Evaluación genética y bioquímica, plan nutricional antiinflamatorio, protocolos de optimización hormonal, seguimiento médico
"""
        
        # Indicaciones para respuestas
        prompt += """
DIRECTRICES DE COMUNICACIÓN:
- Mantén un lenguaje claro y profesional, evitando jerga técnica excesiva
- Usa un tono conversacional, cálido pero convincente
- Personaliza tus respuestas incorporando información específica del cliente
- Evita respuestas evasivas o imprecisas
- Da información honesta sobre precios y expectativas de resultados
- Limita tus respuestas a 2-3 párrafos para mantener el ritmo de la conversación
- Habla en primera persona como representante de NGX
"""
        
        return prompt
    
    def _detect_phase(self, state: ConversationState, response_text: str) -> Optional[str]:
        """
        Detectar la fase actual de la conversación basado en la respuesta.
        
        Args:
            state (ConversationState): Estado actual de la conversación
            response_text (str): Texto de respuesta generado
            
        Returns:
            Optional[str]: Nueva fase detectada o None si no hay cambio
        """
        # Lógica simple basada en keywords y la fase actual
        current_phase = state.phase
        
        # Solo avanzamos a la siguiente fase, no retrocedemos
        if current_phase == "greeting" and any(kw in response_text.lower() for kw in ["cuéntame más", "profundicemos", "háblame de tus"]):
            return "exploration"
            
        elif current_phase == "exploration" and any(kw in response_text.lower() for kw in ["ngx prime puede", "nuestro programa", "te ofrecemos", "beneficios"]):
            return "presentation"
            
        elif current_phase == "presentation" and any(kw in response_text.lower() for kw in ["precio", "costo", "inversión", "entiendo tu preocupación", "es normal dudar"]):
            return "objection_handling"
            
        elif current_phase == "objection_handling" and any(kw in response_text.lower() for kw in ["próximos pasos", "agendar", "comenzar", "iniciar"]):
            return "closing"
            
        elif current_phase == "closing" and any(kw in response_text.lower() for kw in ["ha sido un placer", "gracias por tu tiempo", "nos vemos", "hasta pronto"]):
            return "follow_up"
            
        return None 