"""
Definición del flujo básico de conversación de ventas para los programas NGX.
Estructura las etapas y transiciones del proceso de venta.
"""

from enum import Enum
from typing import Dict, Any, List

class ConversationPhase(str, Enum):
    """Fases de la conversación de ventas."""
    GREETING = "greeting"            # Saludo inicial
    EXPLORATION = "exploration"      # Exploración de necesidades
    PRESENTATION = "presentation"    # Presentación de la solución
    OBJECTION_HANDLING = "objection_handling"  # Manejo de objeciones
    CLOSING = "closing"              # Cierre
    FOLLOW_UP = "follow_up"          # Seguimiento

class Objection(str, Enum):
    """Tipos comunes de objeciones durante la venta."""
    PRICE = "price"                  # "Es muy caro"
    TIME = "time"                    # "No tengo tiempo"
    VALUE = "value"                  # "No estoy seguro si vale la pena"
    RESULTS = "results"              # "¿Realmente funciona?"
    COMPETITION = "competition"      # "Estoy considerando otra opción"
    DECISION_MAKER = "decision_maker"  # "Necesito consultarlo"
    TIMING = "timing"                # "No es el momento adecuado"

class ConversationFlow:
    """
    Define el flujo de la conversación de ventas, incluyendo transiciones 
    entre fases y manejo de eventos específicos.
    """
    
    def __init__(self, program_type: str = "PRIME"):
        """
        Inicializar el flujo de conversación.
        
        Args:
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
        """
        self.program_type = program_type
        self.current_phase = ConversationPhase.GREETING
        self.detected_objections = set()
        self.phase_history = [self.current_phase]
        
        # Configuración específica según el programa
        self.program_config = self._get_program_config(program_type)
    
    def _get_program_config(self, program_type: str) -> Dict[str, Any]:
        """
        Obtener la configuración específica del programa.
        
        Args:
            program_type (str): Tipo de programa
            
        Returns:
            Dict[str, Any]: Configuración del programa
        """
        if program_type == "PRIME":
            return {
                "price_full": 1997,
                "price_monthly": 697,
                "months": 3,
                "key_benefits": [
                    "rendimiento cognitivo optimizado",
                    "energía sostenible durante el día",
                    "mayor capacidad de foco y concentración",
                    "mejor manejo del estrés"
                ],
                "target_audience": "profesionales de alto rendimiento",
                "main_pain_points": [
                    "fatiga mental",
                    "caída de energía durante el día",
                    "dificultad para concentrarse",
                    "estrés crónico",
                    "problemas de sueño"
                ]
            }
        else:  # LONGEVITY
            return {
                "price_full": 2497,
                "price_monthly": 647,
                "months": 4,
                "key_benefits": [
                    "mayor vitalidad diaria",
                    "mejor función cognitiva",
                    "mantenimiento de masa muscular",
                    "optimización metabólica",
                    "mejora en marcadores de salud"
                ],
                "target_audience": "adultos interesados en envejecimiento saludable",
                "main_pain_points": [
                    "pérdida de energía",
                    "disminución de fuerza física",
                    "problemas de memoria",
                    "recuperación lenta",
                    "preocupación por independencia futura"
                ]
            }
    
    def transition_to(self, new_phase: ConversationPhase) -> bool:
        """
        Transicionar a una nueva fase de la conversación.
        
        Args:
            new_phase (ConversationPhase): Nueva fase de la conversación
            
        Returns:
            bool: True si la transición fue exitosa, False si no
        """
        # Validar que la transición sea lógica
        if not self._is_valid_transition(self.current_phase, new_phase):
            return False
        
        # Actualizar fase actual
        self.current_phase = new_phase
        self.phase_history.append(new_phase)
        
        return True
    
    def _is_valid_transition(self, current: ConversationPhase, target: ConversationPhase) -> bool:
        """
        Verificar si una transición entre fases es válida.
        
        Args:
            current (ConversationPhase): Fase actual
            target (ConversationPhase): Fase objetivo
            
        Returns:
            bool: True si la transición es válida, False si no
        """
        # Definir transiciones válidas para cada fase
        valid_transitions = {
            ConversationPhase.GREETING: [
                ConversationPhase.EXPLORATION,
                ConversationPhase.OBJECTION_HANDLING
            ],
            ConversationPhase.EXPLORATION: [
                ConversationPhase.PRESENTATION,
                ConversationPhase.OBJECTION_HANDLING
            ],
            ConversationPhase.PRESENTATION: [
                ConversationPhase.OBJECTION_HANDLING,
                ConversationPhase.CLOSING
            ],
            ConversationPhase.OBJECTION_HANDLING: [
                ConversationPhase.PRESENTATION,
                ConversationPhase.CLOSING,
                ConversationPhase.FOLLOW_UP
            ],
            ConversationPhase.CLOSING: [
                ConversationPhase.OBJECTION_HANDLING,
                ConversationPhase.FOLLOW_UP
            ],
            ConversationPhase.FOLLOW_UP: []  # No hay transiciones desde FOLLOW_UP (fase final)
        }
        
        return target in valid_transitions[current]
    
    def detect_phase_from_text(self, text: str) -> ConversationPhase:
        """
        Detectar la fase de la conversación a partir del texto.
        
        Args:
            text (str): Texto de la respuesta del agente
            
        Returns:
            ConversationPhase: Fase detectada
        """
        # Palabras clave que indican cada fase
        phase_keywords = {
            ConversationPhase.GREETING: [
                "hola", "bienvenido", "gusto conocerte", "gracias por completar", 
                "evaluación", "¿cómo estás?", "¿qué tal tu día?"
            ],
            ConversationPhase.EXPLORATION: [
                "cuéntame más", "¿qué buscas?", "objetivos", "¿qué es importante para ti?",
                "¿qué te gustaría mejorar?", "prioridades", "¿qué te motivó?"
            ],
            ConversationPhase.PRESENTATION: [
                "nuestro programa", "te ofrecemos", "beneficios", "incluye", 
                "está diseñado para", "funciona así", "consiste en"
            ],
            ConversationPhase.OBJECTION_HANDLING: [
                "entiendo tu preocupación", "es un punto válido", "muchos se preguntan",
                "respecto al precio", "en cuanto al tiempo", "garantía"
            ],
            ConversationPhase.CLOSING: [
                "próximos pasos", "empezar", "iniciar", "agendar", "sesión inicial",
                "reservar tu lugar", "proceso de inscripción"
            ],
            ConversationPhase.FOLLOW_UP: [
                "ha sido un placer", "estaremos en contacto", "nos vemos pronto",
                "te enviaré un correo", "hasta pronto", "cualquier duda"
            ]
        }
        
        # Contar ocurrencias de palabras clave por fase
        text_lower = text.lower()
        phase_scores = {phase: 0 for phase in ConversationPhase}
        
        for phase, keywords in phase_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    phase_scores[phase] += 1
        
        # Determinar la fase con mayor puntuación
        detected_phase = max(phase_scores.items(), key=lambda x: x[1])[0]
        
        # Si no hay una clara detección, mantener la fase actual
        if phase_scores[detected_phase] == 0:
            return self.current_phase
            
        return detected_phase
    
    def detect_objections(self, text: str) -> List[Objection]:
        """
        Detectar objeciones en el texto del cliente.
        
        Args:
            text (str): Texto del mensaje del cliente
            
        Returns:
            List[Objection]: Lista de objeciones detectadas
        """
        text_lower = text.lower()
        detected = []
        
        # Palabras clave que indican cada tipo de objeción
        objection_keywords = {
            Objection.PRICE: [
                "caro", "costoso", "precio", "inversión", "pago", "presupuesto", "gasto"
            ],
            Objection.TIME: [
                "tiempo", "ocupado", "agenda", "horario", "compromisos", "disponibilidad"
            ],
            Objection.VALUE: [
                "vale la pena", "beneficio", "retorno", "inversión", "valor"
            ],
            Objection.RESULTS: [
                "funciona", "resultados", "efectivo", "evidencia", "pruebas", "estudios"
            ],
            Objection.COMPETITION: [
                "otra opción", "alternativa", "comparado", "diferencia", "competencia"
            ],
            Objection.DECISION_MAKER: [
                "consultar", "esposo", "esposa", "pareja", "jefe", "pensar", "decidir"
            ],
            Objection.TIMING: [
                "ahora no", "más adelante", "futuro", "momento", "después", "luego"
            ]
        }
        
        for objection_type, keywords in objection_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(objection_type)
                    self.detected_objections.add(objection_type)
                    break  # Una coincidencia es suficiente por tipo
        
        return detected
    
    def get_phase_duration(self) -> Dict[ConversationPhase, int]:
        """
        Obtener la duración (en número de mensajes) de cada fase.
        
        Returns:
            Dict[ConversationPhase, int]: Duración de cada fase
        """
        phase_counts = {phase: 0 for phase in ConversationPhase}
        
        for phase in self.phase_history:
            phase_counts[phase] += 1
            
        return phase_counts
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """
        Obtener insights sobre la conversación.
        
        Returns:
            Dict[str, Any]: Insights de la conversación
        """
        return {
            "program_type": self.program_type,
            "current_phase": self.current_phase,
            "phase_history": self.phase_history,
            "phase_duration": self.get_phase_duration(),
            "detected_objections": list(self.detected_objections),
            "is_completed": self.current_phase == ConversationPhase.FOLLOW_UP,
            "total_phases_visited": len(set(self.phase_history)),
            "conversation_path": [p.value for p in self.phase_history]
        } 