"""
Servicio para análisis de intención contextual en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Set
import json
from collections import Counter

# Configurar logging
logger = logging.getLogger(__name__)

class ContextualIntentService:
    """
    Servicio para análisis de intención contextual en conversaciones.
    Analiza la intención del usuario considerando el contexto completo de la conversación.
    """
    
    # Categorías principales de intención
    INTENT_CATEGORIES = {
        'información': [
            'consultar', 'preguntar', 'averiguar', 'conocer', 'saber', 'informar', 
            'explicar', 'aclarar', 'detallar', 'describir', 'especificar'
        ],
        'transacción': [
            'comprar', 'adquirir', 'pagar', 'abonar', 'transferir', 'depositar', 
            'retirar', 'cancelar', 'solicitar', 'contratar', 'renovar', 'actualizar'
        ],
        'soporte': [
            'ayudar', 'solucionar', 'resolver', 'arreglar', 'reparar', 'asistir', 
            'apoyar', 'guiar', 'orientar', 'corregir', 'mejorar', 'optimizar'
        ],
        'queja': [
            'reclamar', 'quejar', 'denunciar', 'reportar', 'criticar', 'protestar', 
            'insatisfecho', 'molesto', 'enojado', 'frustrado', 'decepcionado', 'falla'
        ],
        'sugerencia': [
            'sugerir', 'proponer', 'recomendar', 'aconsejar', 'indicar', 'plantear', 
            'idea', 'mejora', 'optimización', 'alternativa', 'opción', 'posibilidad'
        ]
    }
    
    # Patrones de intención específicos
    INTENT_PATTERNS = {
        'información_producto': [
            r'(?:información|detalles|características|especificaciones) (?:sobre|de|del) (?:producto|servicio|plan)',
            r'(?:qué|cuáles) (?:son|es) (?:las|los) (?:características|beneficios|ventajas|funciones)',
            r'(?:cómo|de qué manera) (?:funciona|trabaja|opera)'
        ],
        'información_precio': [
            r'(?:cuánto|qué precio|qué valor|qué costo) (?:cuesta|vale|tiene|es)',
            r'(?:precio|costo|valor|tarifa) (?:de|del|para)',
            r'(?:información|detalles) (?:sobre|de) (?:precios|costos|tarifas)'
        ],
        'información_disponibilidad': [
            r'(?:tienen|hay|existe|disponen de|cuentan con)',
            r'(?:está|se encuentra) (?:disponible|en stock|en inventario)',
            r'(?:cuándo|en qué momento) (?:estará|tendrán|habrá) (?:disponible|en stock)'
        ],
        'transacción_compra': [
            r'(?:quiero|deseo|me gustaría|necesito) (?:comprar|adquirir|obtener)',
            r'(?:cómo|dónde|de qué manera) (?:puedo|podría) (?:comprar|adquirir|obtener)',
            r'(?:proceso|pasos|procedimiento) (?:de|para) (?:compra|adquisición)'
        ],
        'transacción_pago': [
            r'(?:quiero|deseo|necesito) (?:pagar|abonar|liquidar|saldar)',
            r'(?:formas|métodos|opciones) (?:de|para) (?:pago|abono)',
            r'(?:puedo|acepta|aceptan) (?:pagar con|usar) (?:tarjeta|efectivo|transferencia)'
        ],
        'soporte_técnico': [
            r'(?:problema|error|falla|inconveniente|dificultad) (?:con|en|al)',
            r'(?:no|deja de) (?:funciona|responde|sirve|trabaja|opera)',
            r'(?:cómo|qué debo hacer para) (?:solucionar|resolver|arreglar|reparar)'
        ],
        'soporte_cuenta': [
            r'(?:problema|error|inconveniente) (?:con|en) (?:mi|la) (?:cuenta|perfil|usuario)',
            r'(?:no puedo|imposible) (?:acceder|entrar|ingresar|iniciar sesión)',
            r'(?:recuperar|restablecer|cambiar) (?:contraseña|clave|acceso)'
        ],
        'queja_servicio': [
            r'(?:insatisfecho|inconforme|molesto|enojado) (?:con|por) (?:el|su) (?:servicio|atención)',
            r'(?:servicio|atención) (?:pésimo|malo|deficiente|terrible|horrible)',
            r'(?:queja|reclamo|inconformidad) (?:sobre|por|con) (?:el|su) (?:servicio|atención)'
        ],
        'queja_producto': [
            r'(?:producto|artículo|item) (?:defectuoso|dañado|roto|no funciona)',
            r'(?:no cumple|incumple) (?:con|las) (?:expectativas|especificaciones|características)',
            r'(?:decepcionado|inconforme|insatisfecho) (?:con|por) (?:el|mi) (?:producto|compra)'
        ],
        'sugerencia_mejora': [
            r'(?:sugerencia|recomendación|consejo|idea) (?:para|de) (?:mejorar|optimizar)',
            r'(?:deberían|podrían|sería bueno) (?:implementar|añadir|incluir|considerar)',
            r'(?:sería|resultaría) (?:útil|beneficioso|conveniente|práctico) (?:si|que)'
        ]
    }
    
    # Palabras clave para determinar urgencia
    URGENCY_KEYWORDS = [
        'urgente', 'inmediato', 'pronto', 'rápido', 'cuanto antes',
        'emergencia', 'crítico', 'prioritario', 'importante', 'necesito ya',
        'no puede esperar', 'lo antes posible', 'ahora mismo', 'hoy',
        'mañana', 'esta semana', 'plazo', 'fecha límite', 'vencimiento'
    ]
    
    # Palabras clave para determinar importancia
    IMPORTANCE_KEYWORDS = [
        'importante', 'crucial', 'esencial', 'fundamental', 'vital',
        'crítico', 'necesario', 'indispensable', 'prioritario', 'clave',
        'significativo', 'relevante', 'primordial', 'decisivo', 'determinante',
        'imperativo', 'urgente', 'serio', 'grave', 'trascendental'
    ]
    
    def __init__(self):
        """Inicializar el servicio de análisis de intención contextual."""
        logger.info("Servicio de análisis de intención contextual inicializado")
        
        # Compilar patrones para mejor rendimiento
        self.compiled_intent_patterns = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_intent_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            
        # Crear conjuntos de palabras clave para búsqueda eficiente
        self.intent_keyword_sets = {}
        for intent, keywords in self.INTENT_CATEGORIES.items():
            self.intent_keyword_sets[intent] = set(keywords)
            
        # Compilar palabras clave de urgencia e importancia
        self.urgency_pattern = re.compile(r'\b(' + '|'.join(self.URGENCY_KEYWORDS) + r')\b', re.IGNORECASE)
        self.importance_pattern = re.compile(r'\b(' + '|'.join(self.IMPORTANCE_KEYWORDS) + r')\b', re.IGNORECASE)
        
        # Historial de intenciones para análisis contextual
        self.conversation_intents = {}
    
    def detect_intent_from_text(self, text: str) -> Dict[str, float]:
        """
        Detecta intenciones en un texto utilizando patrones y palabras clave.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Diccionario con intenciones y sus puntuaciones (0-1)
        """
        intent_scores = {}
        
        # Detectar intenciones específicas usando patrones
        for intent, patterns in self.compiled_intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = pattern.findall(text.lower())
                if matches:
                    # Incrementar puntuación por cada coincidencia
                    score += len(matches) * 0.3
            
            if score > 0:
                intent_scores[intent] = min(1.0, score)
        
        # Detectar categorías generales de intención usando palabras clave
        words = text.lower().split()
        for word in words:
            # Eliminar signos de puntuación
            word = re.sub(r'[^\w\s]', '', word)
            
            for intent, keyword_set in self.intent_keyword_sets.items():
                if word in keyword_set:
                    # Incrementar puntuación por cada palabra clave
                    intent_scores[intent] = intent_scores.get(intent, 0) + 0.2
        
        # Normalizar puntuaciones (0-1)
        for intent in intent_scores:
            intent_scores[intent] = min(1.0, intent_scores[intent])
            
        return intent_scores
    
    def determine_urgency(self, text: str) -> Dict[str, Any]:
        """
        Determina el nivel de urgencia en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Información sobre la urgencia detectada
        """
        # Buscar palabras clave de urgencia
        matches = self.urgency_pattern.findall(text.lower())
        
        # Calcular nivel de urgencia (0-1)
        urgency_level = min(1.0, len(matches) * 0.2)
        
        # Clasificar nivel de urgencia
        if urgency_level > 0.6:
            urgency_class = "alta"
        elif urgency_level > 0.3:
            urgency_class = "media"
        else:
            urgency_class = "baja"
            
        return {
            "level": urgency_level,
            "class": urgency_class,
            "keywords": matches
        }
    
    def determine_importance(self, text: str) -> Dict[str, Any]:
        """
        Determina el nivel de importancia en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Información sobre la importancia detectada
        """
        # Buscar palabras clave de importancia
        matches = self.importance_pattern.findall(text.lower())
        
        # Calcular nivel de importancia (0-1)
        importance_level = min(1.0, len(matches) * 0.2)
        
        # Clasificar nivel de importancia
        if importance_level > 0.6:
            importance_class = "alta"
        elif importance_level > 0.3:
            importance_class = "media"
        else:
            importance_class = "baja"
            
        return {
            "level": importance_level,
            "class": importance_class,
            "keywords": matches
        }
    
    def update_conversation_intents(self, conversation_id: str, text: str, role: str = 'user'):
        """
        Actualiza el historial de intenciones detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            text: Texto del mensaje
            role: Rol del mensaje (user/assistant)
        """
        # Solo procesar mensajes del usuario
        if role != 'user':
            return
            
        # Inicializar si es la primera vez
        if conversation_id not in self.conversation_intents:
            self.conversation_intents[conversation_id] = []
            
        # Detectar intenciones
        intents = self.detect_intent_from_text(text)
        
        if intents:
            # Determinar urgencia e importancia
            urgency = self.determine_urgency(text)
            importance = self.determine_importance(text)
            
            # Guardar intención con metadatos
            intent_entry = {
                "intents": intents,
                "urgency": urgency,
                "importance": importance,
                "text": text,
                "timestamp": None  # Aquí se podría añadir timestamp si se requiere
            }
            
            self.conversation_intents[conversation_id].append(intent_entry)
    
    def get_conversation_intents(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de intenciones detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            List: Lista de intenciones detectadas con sus metadatos
        """
        return self.conversation_intents.get(conversation_id, [])
    
    def clear_conversation_intents(self, conversation_id: str):
        """
        Limpia el historial de intenciones para una conversación.
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.conversation_intents:
            del self.conversation_intents[conversation_id]
    
    def analyze_intent_evolution(self, conversation_id: str) -> Dict[str, Any]:
        """
        Analiza la evolución de intenciones a lo largo de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Análisis de la evolución de intenciones
        """
        intents_history = self.get_conversation_intents(conversation_id)
        
        if not intents_history:
            return {
                "has_intents": False,
                "message": "No hay historial de intenciones para esta conversación."
            }
            
        # Extraer intenciones principales de cada mensaje
        main_intents = []
        for entry in intents_history:
            intents = entry.get("intents", {})
            if intents:
                # Obtener intención con mayor puntuación
                main_intent = max(intents.items(), key=lambda x: x[1])
                main_intents.append(main_intent[0])
        
        # Contar frecuencia de cada intención
        intent_counts = Counter(main_intents)
        
        # Determinar intención predominante
        predominant_intent = intent_counts.most_common(1)[0][0] if intent_counts else None
        
        # Analizar cambios de intención
        intent_changes = []
        for i in range(1, len(main_intents)):
            if main_intents[i] != main_intents[i-1]:
                intent_changes.append((main_intents[i-1], main_intents[i]))
        
        # Analizar tendencia de urgencia e importancia
        urgency_levels = [entry.get("urgency", {}).get("level", 0) for entry in intents_history]
        importance_levels = [entry.get("importance", {}).get("level", 0) for entry in intents_history]
        
        # Calcular tendencias
        urgency_trend = "estable"
        importance_trend = "estable"
        
        if len(urgency_levels) >= 2:
            if urgency_levels[-1] > urgency_levels[0] + 0.2:
                urgency_trend = "aumentando"
            elif urgency_levels[-1] < urgency_levels[0] - 0.2:
                urgency_trend = "disminuyendo"
                
        if len(importance_levels) >= 2:
            if importance_levels[-1] > importance_levels[0] + 0.2:
                importance_trend = "aumentando"
            elif importance_levels[-1] < importance_levels[0] - 0.2:
                importance_trend = "disminuyendo"
        
        return {
            "has_intents": True,
            "predominant_intent": predominant_intent,
            "intent_counts": dict(intent_counts),
            "intent_changes": intent_changes,
            "urgency_trend": urgency_trend,
            "importance_trend": importance_trend,
            "message_count": len(intents_history)
        }
    
    def analyze_message(self, text: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de intención para un mensaje.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Análisis completo de intención
        """
        # Detectar intenciones
        intents = self.detect_intent_from_text(text)
        
        if not intents:
            return {
                "has_intent": False,
                "message": "No se detectaron intenciones claras en el mensaje."
            }
            
        # Determinar intención principal
        main_intent = max(intents.items(), key=lambda x: x[1])
        
        # Determinar urgencia e importancia
        urgency = self.determine_urgency(text)
        importance = self.determine_importance(text)
        
        # Determinar categoría general
        general_category = None
        for category, specific_intents in self._get_intent_categories().items():
            if main_intent[0] in specific_intents:
                general_category = category
                break
        
        return {
            "has_intent": True,
            "main_intent": {
                "intent": main_intent[0],
                "confidence": main_intent[1]
            },
            "general_category": general_category,
            "all_intents": intents,
            "urgency": urgency,
            "importance": importance
        }
    
    def analyze_conversation(self, messages: List[Dict[str, str]], conversation_id: str = None) -> Dict[str, Any]:
        """
        Analiza intenciones en una conversación completa.
        
        Args:
            messages: Lista de mensajes de la conversación
            conversation_id: ID opcional de la conversación para almacenar intenciones
            
        Returns:
            Dict: Análisis de intenciones en la conversación
        """
        # Extraer solo mensajes del usuario
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                "has_intents": False,
                "message": "No hay mensajes de usuario en la conversación."
            }
            
        # Analizar cada mensaje
        message_analyses = []
        
        for message in user_messages:
            # Actualizar historial de intenciones si se proporciona ID
            if conversation_id:
                self.update_conversation_intents(
                    conversation_id, 
                    message.get('content', ''),
                    message.get('role', 'user')
                )
                
            # Analizar mensaje
            analysis = self.analyze_message(message.get('content', ''))
            message_analyses.append(analysis)
            
        # Contar intenciones principales
        main_intents = [
            analysis.get("main_intent", {}).get("intent")
            for analysis in message_analyses
            if analysis.get("has_intent", False)
        ]
        
        intent_counts = Counter(main_intents)
        
        # Determinar intención predominante
        predominant_intent = intent_counts.most_common(1)[0][0] if intent_counts else None
        
        # Calcular niveles promedio de urgencia e importancia
        urgency_levels = [
            analysis.get("urgency", {}).get("level", 0)
            for analysis in message_analyses
            if analysis.get("has_intent", False)
        ]
        
        importance_levels = [
            analysis.get("importance", {}).get("level", 0)
            for analysis in message_analyses
            if analysis.get("has_intent", False)
        ]
        
        avg_urgency = sum(urgency_levels) / len(urgency_levels) if urgency_levels else 0
        avg_importance = sum(importance_levels) / len(importance_levels) if importance_levels else 0
        
        # Clasificar niveles promedio
        urgency_class = "alta" if avg_urgency > 0.6 else "media" if avg_urgency > 0.3 else "baja"
        importance_class = "alta" if avg_importance > 0.6 else "media" if avg_importance > 0.3 else "baja"
        
        # Analizar evolución de intenciones si se proporciona ID
        intent_evolution = None
        if conversation_id:
            intent_evolution = self.analyze_intent_evolution(conversation_id)
            
        return {
            "has_intents": bool(main_intents),
            "message_count": len(user_messages),
            "intent_count": len(main_intents),
            "predominant_intent": predominant_intent,
            "intent_counts": dict(intent_counts),
            "avg_urgency": {
                "level": avg_urgency,
                "class": urgency_class
            },
            "avg_importance": {
                "level": avg_importance,
                "class": importance_class
            },
            "message_analyses": message_analyses,
            "intent_evolution": intent_evolution
        }
    
    def get_intent_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Genera un resumen conciso de las intenciones detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Resumen de intenciones
        """
        # Analizar evolución de intenciones
        evolution = self.analyze_intent_evolution(conversation_id)
        
        if not evolution.get("has_intents", False):
            return {
                "has_intents": False,
                "summary": "No se han detectado intenciones claras en esta conversación."
            }
            
        # Crear resumen
        predominant_intent = evolution.get("predominant_intent", "desconocida")
        message_count = evolution.get("message_count", 0)
        intent_changes = evolution.get("intent_changes", [])
        urgency_trend = evolution.get("urgency_trend", "estable")
        importance_trend = evolution.get("importance_trend", "estable")
        
        # Mapear intenciones a descripciones más amigables
        intent_display = {
            "información_producto": "información sobre productos",
            "información_precio": "información sobre precios",
            "información_disponibilidad": "consulta de disponibilidad",
            "transacción_compra": "intención de compra",
            "transacción_pago": "gestión de pagos",
            "soporte_técnico": "soporte técnico",
            "soporte_cuenta": "soporte de cuenta",
            "queja_servicio": "queja sobre el servicio",
            "queja_producto": "queja sobre producto",
            "sugerencia_mejora": "sugerencia de mejora"
        }
        
        # Generar resumen textual
        intent_text = intent_display.get(predominant_intent, predominant_intent)
        
        summary = f"Intención predominante: {intent_text} "
        summary += f"en {message_count} mensajes. "
        
        if intent_changes:
            summary += f"La intención ha cambiado {len(intent_changes)} veces. "
            
        if urgency_trend != "estable":
            summary += f"Nivel de urgencia {urgency_trend}. "
            
        if importance_trend != "estable":
            summary += f"Nivel de importancia {importance_trend}."
            
        return {
            "has_intents": True,
            "predominant_intent": predominant_intent,
            "message_count": message_count,
            "intent_changes": len(intent_changes),
            "urgency_trend": urgency_trend,
            "importance_trend": importance_trend,
            "summary": summary
        }
    
    def _get_intent_categories(self) -> Dict[str, List[str]]:
        """
        Obtiene un mapeo de categorías generales a intenciones específicas.
        
        Returns:
            Dict: Mapeo de categorías a intenciones específicas
        """
        categories = {
            "información": [
                "información_producto", 
                "información_precio", 
                "información_disponibilidad"
            ],
            "transacción": [
                "transacción_compra", 
                "transacción_pago"
            ],
            "soporte": [
                "soporte_técnico", 
                "soporte_cuenta"
            ],
            "queja": [
                "queja_servicio", 
                "queja_producto"
            ],
            "sugerencia": [
                "sugerencia_mejora"
            ]
        }
        
        return categories
