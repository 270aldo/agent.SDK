"""
Servicio para clasificación de preguntas en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Set
import json

# Configurar logging
logger = logging.getLogger(__name__)

class QuestionClassificationService:
    """
    Servicio para clasificación de preguntas en conversaciones.
    Identifica tipos de preguntas, intención y complejidad.
    """
    
    # Patrones para tipos de preguntas
    QUESTION_PATTERNS = {
        'factual': [
            r'(?:qué|cuál|cuáles|quién|quiénes|dónde|cuándo|cuánto|cuánta|cuántos|cuántas) (?:es|son|está|están|fue|fueron|hay|tiene|tienen)',
            r'(?:me puedes|puedes|podrías|me podrías) (?:decir|indicar|informar) (?:qué|cuál|cuáles|quién|quiénes|dónde|cuándo|cuánto|cuánta|cuántos|cuántas)',
            r'(?:sabes|conoces) (?:qué|cuál|cuáles|quién|quiénes|dónde|cuándo)'
        ],
        'procedural': [
            r'(?:cómo|de qué manera|de qué forma) (?:puedo|podría|se puede|se podría|hago|haría|funciona|funcionaría)',
            r'(?:me puedes|puedes|podrías|me podrías) (?:explicar|mostrar|enseñar) (?:cómo|de qué manera|de qué forma)',
            r'(?:cuál es|cuáles son) (?:el|los) (?:proceso|procedimiento|paso|pasos|método|métodos) (?:para|de)'
        ],
        'comparative': [
            r'(?:qué|cuál) (?:es|sería) (?:mejor|peor|más recomendable|más adecuado|más conveniente|la diferencia)',
            r'(?:en qué|cómo) se (?:diferencia|diferencian|distingue|distinguen|compara|comparan)',
            r'(?:ventajas|desventajas|beneficios|pros|contras) (?:de|entre)'
        ],
        'causal': [
            r'(?:por qué|debido a qué|a qué se debe|cuál es la razón|cuáles son las razones)',
            r'(?:qué causa|qué provoca|qué origina|qué genera|qué produce)',
            r'(?:cuál es|cuáles son) (?:el|los) (?:motivo|motivos|causa|causas|origen|orígenes) (?:de|para|por)'
        ],
        'hypothetical': [
            r'(?:qué pasaría|qué ocurriría|qué sucedería|qué ocurre|qué pasa) (?:si|cuando)',
            r'(?:en caso de|suponiendo que|si) (?:yo|nosotros|se)',
            r'(?:sería posible|es posible|podría|habría) (?:que|si)'
        ],
        'verification': [
            r'(?:es|son|está|están|fue|fueron|hay|tiene|tienen|puede|pueden|debe|deben|va|van) (?:cierto|verdad|correcto|posible|necesario|obligatorio|requerido)',
            r'(?:se puede|se pueden|se debe|se deben|se podría|se podrían) (?:hacer|usar|utilizar|aplicar)',
            r'^(?:es|son|está|están|fue|fueron|hay|tiene|tienen|puede|pueden|debe|deben|va|van) '
        ],
        'opinion': [
            r'(?:qué|cuál) (?:opinas|piensas|crees|consideras|te parece|recomiendas|sugieres)',
            r'(?:crees|consideras|piensas|opinas) (?:que|si)',
            r'(?:me puedes|puedes|podrías|me podrías) (?:recomendar|sugerir|aconsejar|dar tu opinión)'
        ],
        'clarification': [
            r'(?:qué quieres|qué quisiste|qué querías) (?:decir|expresar)',
            r'(?:no entiendo|no comprendo|no me queda claro|podrías aclarar|puedes aclarar)',
            r'(?:a qué te refieres|qué significa|qué quiere decir)'
        ]
    }
    
    # Patrones para detectar preguntas
    QUESTION_INDICATORS = [
        r'\?',
        r'^(?:qué|cuál|cuáles|quién|quiénes|dónde|cuándo|cuánto|cuánta|cuántos|cuántas|cómo|por qué)',
        r'(?:me puedes|puedes|podrías|me podrías|sabes|conoces|dime|explícame|cuéntame)'
    ]
    
    # Palabras clave para determinar complejidad
    COMPLEXITY_KEYWORDS = {
        'alta': [
            'complejo', 'complicado', 'difícil', 'avanzado', 'detallado', 'profundo',
            'técnico', 'especializado', 'exhaustivo', 'minucioso', 'elaborado',
            'específico', 'preciso', 'exacto', 'riguroso', 'meticuloso',
            'paso a paso', 'procedimiento', 'metodología', 'algoritmo', 'fórmula',
            'comparación', 'diferencia', 'análisis', 'evaluación', 'criterio',
            'requisito', 'condición', 'restricción', 'limitación', 'excepción'
        ],
        'media': [
            'explicar', 'describir', 'detallar', 'elaborar', 'especificar',
            'proceso', 'método', 'sistema', 'mecanismo', 'funcionamiento',
            'característica', 'propiedad', 'atributo', 'cualidad', 'aspecto',
            'ventaja', 'desventaja', 'beneficio', 'perjuicio', 'inconveniente',
            'causa', 'efecto', 'consecuencia', 'resultado', 'impacto',
            'relación', 'conexión', 'vínculo', 'asociación', 'correlación'
        ],
        'baja': [
            'qué', 'cuál', 'quién', 'dónde', 'cuándo', 'cuánto',
            'simple', 'sencillo', 'básico', 'elemental', 'fundamental',
            'general', 'común', 'usual', 'normal', 'típico',
            'ejemplo', 'muestra', 'caso', 'instancia', 'ilustración',
            'sí', 'no', 'verdadero', 'falso', 'correcto', 'incorrecto',
            'bueno', 'malo', 'mejor', 'peor', 'recomendable', 'desaconsejable'
        ]
    }
    
    # Categorías de intención de preguntas
    INTENT_CATEGORIES = {
        'información': [
            'factual', 'procedural', 'causal'
        ],
        'comparación': [
            'comparative'
        ],
        'validación': [
            'verification', 'clarification'
        ],
        'opinión': [
            'opinion'
        ],
        'exploración': [
            'hypothetical'
        ]
    }
    
    def __init__(self):
        """Inicializar el servicio de clasificación de preguntas."""
        logger.info("Servicio de clasificación de preguntas inicializado")
        
        # Compilar patrones para mejor rendimiento
        self.compiled_question_patterns = {}
        for question_type, patterns in self.QUESTION_PATTERNS.items():
            self.compiled_question_patterns[question_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            
        # Compilar indicadores de preguntas
        self.compiled_question_indicators = [re.compile(pattern, re.IGNORECASE) for pattern in self.QUESTION_INDICATORS]
        
        # Crear conjuntos de palabras clave para búsqueda eficiente
        self.complexity_keyword_sets = {}
        for complexity, keywords in self.COMPLEXITY_KEYWORDS.items():
            self.complexity_keyword_sets[complexity] = set(keywords)
    
    def is_question(self, text: str) -> bool:
        """
        Determina si un texto contiene una pregunta.
        
        Args:
            text: Texto a analizar
            
        Returns:
            bool: True si el texto contiene una pregunta, False en caso contrario
        """
        # Verificar indicadores de preguntas
        for pattern in self.compiled_question_indicators:
            if pattern.search(text):
                return True
                
        return False
    
    def extract_questions(self, text: str) -> List[str]:
        """
        Extrae preguntas de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            List[str]: Lista de preguntas encontradas
        """
        questions = []
        
        # Dividir por signos de interrogación
        if '?' in text:
            # Extraer preguntas con signos de interrogación
            question_pattern = re.compile(r'[^.!?]*\?')
            questions.extend(question_pattern.findall(text))
        
        # Si no hay preguntas con signos de interrogación, buscar por patrones
        if not questions:
            # Dividir por oraciones
            sentences = re.split(r'[.!;]', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Verificar si la oración es una pregunta
                if self.is_question(sentence):
                    questions.append(sentence)
        
        return questions
    
    def classify_question_type(self, question: str) -> Dict[str, float]:
        """
        Clasifica el tipo de una pregunta.
        
        Args:
            question: Pregunta a clasificar
            
        Returns:
            Dict[str, float]: Diccionario con tipos de pregunta y sus puntuaciones (0-1)
        """
        results = {}
        
        # Verificar cada tipo de pregunta
        for question_type, patterns in self.compiled_question_patterns.items():
            # Contar coincidencias para cada patrón
            matches = 0
            for pattern in patterns:
                if pattern.search(question.lower()):
                    matches += 1
                    
            # Calcular puntuación (0-1)
            if matches > 0:
                score = min(1.0, matches / len(patterns))
                results[question_type] = score
        
        # Si no se encontró ningún tipo, asignar "otro"
        if not results:
            results["otro"] = 1.0
            
        return results
    
    def determine_question_complexity(self, question: str) -> Dict[str, Any]:
        """
        Determina la complejidad de una pregunta.
        
        Args:
            question: Pregunta a analizar
            
        Returns:
            Dict: Información sobre la complejidad de la pregunta
        """
        # Inicializar contadores
        complexity_counts = {
            'alta': 0,
            'media': 0,
            'baja': 0
        }
        
        # Contar palabras clave de complejidad
        words = question.lower().split()
        for word in words:
            # Eliminar signos de puntuación
            word = re.sub(r'[^\w\s]', '', word)
            
            for complexity, keyword_set in self.complexity_keyword_sets.items():
                if word in keyword_set:
                    complexity_counts[complexity] += 1
        
        # Determinar complejidad predominante
        total_keywords = sum(complexity_counts.values())
        
        if total_keywords == 0:
            # Si no hay palabras clave, asignar complejidad baja por defecto
            complexity = "baja"
            confidence = 0.5
        else:
            # Calcular proporciones
            proportions = {
                complexity: count / total_keywords
                for complexity, count in complexity_counts.items()
            }
            
            # Determinar complejidad predominante
            max_complexity = max(proportions.items(), key=lambda x: x[1])
            complexity = max_complexity[0]
            confidence = max_complexity[1]
        
        # Calcular longitud de la pregunta (indicador adicional de complejidad)
        word_count = len(words)
        
        # Ajustar complejidad según longitud
        if word_count > 20 and complexity != "alta":
            complexity = "alta"
            confidence = max(confidence, 0.6)
        elif word_count < 5 and complexity != "baja":
            complexity = "baja"
            confidence = max(confidence, 0.6)
            
        return {
            "complexity": complexity,
            "confidence": confidence,
            "word_count": word_count,
            "keyword_counts": complexity_counts
        }
    
    def determine_question_intent(self, question_types: Dict[str, float]) -> Dict[str, Any]:
        """
        Determina la intención general de una pregunta basada en sus tipos.
        
        Args:
            question_types: Diccionario con tipos de pregunta y sus puntuaciones
            
        Returns:
            Dict: Información sobre la intención de la pregunta
        """
        intent_scores = {}
        
        # Calcular puntuación para cada categoría de intención
        for intent, types in self.INTENT_CATEGORIES.items():
            score = 0.0
            count = 0
            
            for question_type in types:
                if question_type in question_types:
                    score += question_types[question_type]
                    count += 1
            
            if count > 0:
                intent_scores[intent] = score / count
        
        # Si no se encontró ninguna intención, asignar "otro"
        if not intent_scores:
            intent_scores["otro"] = 1.0
            
        # Determinar intención predominante
        max_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent = max_intent[0]
        confidence = max_intent[1]
            
        return {
            "intent": intent,
            "confidence": confidence,
            "intent_scores": intent_scores
        }
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de una pregunta.
        
        Args:
            question: Pregunta a analizar
            
        Returns:
            Dict: Resultados del análisis
        """
        # Verificar si es una pregunta
        if not self.is_question(question):
            return {
                "is_question": False,
                "message": "El texto no contiene una pregunta."
            }
            
        # Clasificar tipo de pregunta
        question_types = self.classify_question_type(question)
        
        # Determinar tipo predominante
        predominant_type = max(question_types.items(), key=lambda x: x[1])
        
        # Determinar complejidad
        complexity_info = self.determine_question_complexity(question)
        
        # Determinar intención
        intent_info = self.determine_question_intent(question_types)
        
        return {
            "is_question": True,
            "question": question,
            "predominant_type": {
                "type": predominant_type[0],
                "confidence": predominant_type[1]
            },
            "types": question_types,
            "complexity": complexity_info,
            "intent": intent_info
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analiza un texto completo para identificar y clasificar preguntas.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Resultados del análisis
        """
        # Extraer preguntas
        questions = self.extract_questions(text)
        
        if not questions:
            return {
                "has_questions": False,
                "message": "No se detectaron preguntas en el texto.",
                "question_count": 0
            }
            
        # Analizar cada pregunta
        question_analyses = []
        for question in questions:
            analysis = self.analyze_question(question)
            question_analyses.append(analysis)
            
        # Determinar intención predominante del texto
        intent_counts = {}
        for analysis in question_analyses:
            if analysis.get("is_question", False):
                intent = analysis.get("intent", {}).get("intent", "otro")
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
        predominant_intent = max(intent_counts.items(), key=lambda x: x[1]) if intent_counts else ("otro", 0)
        
        # Determinar complejidad predominante del texto
        complexity_counts = {}
        for analysis in question_analyses:
            if analysis.get("is_question", False):
                complexity = analysis.get("complexity", {}).get("complexity", "baja")
                complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
                
        predominant_complexity = max(complexity_counts.items(), key=lambda x: x[1]) if complexity_counts else ("baja", 0)
        
        return {
            "has_questions": True,
            "question_count": len(questions),
            "questions": questions,
            "analyses": question_analyses,
            "predominant_intent": predominant_intent[0],
            "predominant_complexity": predominant_complexity[0]
        }
    
    def analyze_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analiza preguntas en una conversación completa.
        
        Args:
            messages: Lista de mensajes de la conversación
            
        Returns:
            Dict: Análisis de preguntas en la conversación
        """
        # Extraer solo mensajes del usuario
        user_messages = [msg['content'] for msg in messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                "has_questions": False,
                "message": "No hay mensajes de usuario en la conversación.",
                "question_count": 0
            }
            
        # Analizar cada mensaje
        message_analyses = []
        all_questions = []
        
        for message in user_messages:
            analysis = self.analyze_text(message)
            message_analyses.append(analysis)
            
            if analysis.get("has_questions", False):
                all_questions.extend(analysis.get("questions", []))
                
        if not all_questions:
            return {
                "has_questions": False,
                "message": "No se detectaron preguntas en la conversación.",
                "question_count": 0,
                "message_count": len(user_messages)
            }
            
        # Analizar todas las preguntas juntas
        question_analyses = []
        for question in all_questions:
            analysis = self.analyze_question(question)
            question_analyses.append(analysis)
            
        # Determinar intención predominante de la conversación
        intent_counts = {}
        for analysis in question_analyses:
            if analysis.get("is_question", False):
                intent = analysis.get("intent", {}).get("intent", "otro")
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
        predominant_intent = max(intent_counts.items(), key=lambda x: x[1]) if intent_counts else ("otro", 0)
        
        # Determinar complejidad predominante de la conversación
        complexity_counts = {}
        for analysis in question_analyses:
            if analysis.get("is_question", False):
                complexity = analysis.get("complexity", {}).get("complexity", "baja")
                complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
                
        predominant_complexity = max(complexity_counts.items(), key=lambda x: x[1]) if complexity_counts else ("baja", 0)
        
        # Calcular distribución de tipos de preguntas
        type_counts = {}
        for analysis in question_analyses:
            if analysis.get("is_question", False):
                question_type = analysis.get("predominant_type", {}).get("type", "otro")
                type_counts[question_type] = type_counts.get(question_type, 0) + 1
                
        return {
            "has_questions": True,
            "question_count": len(all_questions),
            "message_count": len(user_messages),
            "questions": all_questions,
            "analyses": question_analyses,
            "predominant_intent": predominant_intent[0],
            "predominant_complexity": predominant_complexity[0],
            "type_distribution": type_counts
        }
    
    def get_question_summary(self, text: str) -> Dict[str, Any]:
        """
        Genera un resumen conciso de las preguntas en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Resumen de preguntas
        """
        analysis = self.analyze_text(text)
        
        if not analysis.get("has_questions", False):
            return {
                "has_questions": False,
                "summary": "No se detectaron preguntas en el texto."
            }
            
        # Crear resumen
        question_count = analysis.get("question_count", 0)
        predominant_intent = analysis.get("predominant_intent", "otro")
        predominant_complexity = analysis.get("predominant_complexity", "baja")
        
        intent_display = {
            "información": "busca información factual o procedimientos",
            "comparación": "busca comparar opciones o alternativas",
            "validación": "busca verificar o aclarar información",
            "opinión": "busca opiniones o recomendaciones",
            "exploración": "explora escenarios hipotéticos",
            "otro": "tiene una intención no categorizada"
        }
        
        complexity_display = {
            "alta": "alta complejidad",
            "media": "complejidad media",
            "baja": "baja complejidad"
        }
        
        summary = f"Se detectaron {question_count} preguntas. "
        summary += f"Predominantemente {intent_display.get(predominant_intent, 'otro tipo')} "
        summary += f"con {complexity_display.get(predominant_complexity, 'complejidad no determinada')}."
        
        return {
            "has_questions": True,
            "question_count": question_count,
            "predominant_intent": predominant_intent,
            "predominant_complexity": predominant_complexity,
            "summary": summary
        }
