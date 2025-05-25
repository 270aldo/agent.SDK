"""
Servicio para extracción mejorada de palabras clave en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Set
import json
from collections import Counter
import string

# Configurar logging
logger = logging.getLogger(__name__)

class KeywordExtractionService:
    """
    Servicio para extracción mejorada de palabras clave en conversaciones.
    Identifica términos relevantes, frases importantes y conceptos clave.
    """
    
    # Palabras vacías (stopwords) en español
    STOPWORDS = {
        'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra',
        'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e', 'el', 'ella',
        'ellas', 'ellos', 'en', 'entre', 'era', 'erais', 'eran', 'eras', 'eres', 'es',
        'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estaba', 'estabais', 'estaban',
        'estabas', 'estad', 'estada', 'estadas', 'estado', 'estados', 'estamos', 'estando',
        'estar', 'estaremos', 'estará', 'estarán', 'estarás', 'estaré', 'estaréis',
        'estaría', 'estaríais', 'estaríamos', 'estarían', 'estarías', 'estas', 'este',
        'estemos', 'esto', 'estos', 'estoy', 'estuve', 'estuviera', 'estuvierais',
        'estuvieran', 'estuvieras', 'estuvieron', 'estuviese', 'estuvieseis', 'estuviesen',
        'estuvieses', 'estuvimos', 'estuviste', 'estuvisteis', 'estuviéramos',
        'estuviésemos', 'estuvo', 'fue', 'fuera', 'fuerais', 'fueran', 'fueras', 'fueron',
        'fuese', 'fueseis', 'fuesen', 'fueses', 'fui', 'fuimos', 'fuiste', 'fuisteis',
        'fuéramos', 'fuésemos', 'ha', 'habida', 'habidas', 'habido', 'habidos', 'habiendo',
        'habremos', 'habrá', 'habrán', 'habrás', 'habré', 'habréis', 'habría', 'habríais',
        'habríamos', 'habrían', 'habrías', 'habéis', 'había', 'habíais', 'habíamos',
        'habían', 'habías', 'han', 'has', 'hasta', 'hay', 'haya', 'hayamos', 'hayan',
        'hayas', 'hayáis', 'he', 'hemos', 'hube', 'hubiera', 'hubierais', 'hubieran',
        'hubieras', 'hubieron', 'hubiese', 'hubieseis', 'hubiesen', 'hubieses', 'hubimos',
        'hubiste', 'hubisteis', 'hubiéramos', 'hubiésemos', 'hubo', 'la', 'las', 'le',
        'les', 'lo', 'los', 'me', 'mi', 'mis', 'mucho', 'muchos', 'muy', 'más', 'mí',
        'mía', 'mías', 'mío', 'míos', 'nada', 'ni', 'no', 'nos', 'nosotras', 'nosotros',
        'nuestra', 'nuestras', 'nuestro', 'nuestros', 'o', 'os', 'otra', 'otras', 'otro',
        'otros', 'para', 'pero', 'poco', 'por', 'porque', 'que', 'quien', 'quienes', 'qué',
        'se', 'sea', 'seamos', 'sean', 'seas', 'seremos', 'será', 'serán', 'serás', 'seré',
        'seréis', 'sería', 'seríais', 'seríamos', 'serían', 'serías', 'seáis', 'si', 'sido',
        'siendo', 'sin', 'sobre', 'sois', 'somos', 'son', 'soy', 'su', 'sus', 'suya',
        'suyas', 'suyo', 'suyos', 'sí', 'también', 'tanto', 'te', 'tendremos', 'tendrá',
        'tendrán', 'tendrás', 'tendré', 'tendréis', 'tendría', 'tendríais', 'tendríamos',
        'tendrían', 'tendrías', 'tened', 'tenemos', 'tenga', 'tengamos', 'tengan', 'tengas',
        'tengo', 'tengáis', 'tenida', 'tenidas', 'tenido', 'tenidos', 'teniendo', 'tenéis',
        'tenía', 'teníais', 'teníamos', 'tenían', 'tenías', 'ti', 'tiene', 'tienen',
        'tienes', 'todo', 'todos', 'tu', 'tus', 'tuve', 'tuviera', 'tuvierais', 'tuvieran',
        'tuvieras', 'tuvieron', 'tuviese', 'tuvieseis', 'tuviesen', 'tuvieses', 'tuvimos',
        'tuviste', 'tuvisteis', 'tuviéramos', 'tuviésemos', 'tuvo', 'tuya', 'tuyas', 'tuyo',
        'tuyos', 'tú', 'un', 'una', 'uno', 'unos', 'vosotras', 'vosotros', 'vuestra',
        'vuestras', 'vuestro', 'vuestros', 'y', 'ya', 'yo', 'él', 'éramos'
    }
    
    # Categorías de palabras clave para clasificación
    KEYWORD_CATEGORIES = {
        'producto': [
            'producto', 'servicio', 'artículo', 'dispositivo', 'equipo', 'herramienta',
            'aplicación', 'app', 'software', 'hardware', 'sistema', 'plataforma', 'solución',
            'modelo', 'versión', 'plan', 'paquete', 'suscripción', 'membresía'
        ],
        'característica': [
            'característica', 'función', 'funcionalidad', 'capacidad', 'opción', 'propiedad',
            'atributo', 'aspecto', 'cualidad', 'especificación', 'detalle', 'prestación',
            'beneficio', 'ventaja', 'mejora', 'innovación', 'tecnología', 'rendimiento'
        ],
        'precio': [
            'precio', 'costo', 'valor', 'tarifa', 'cuota', 'tasa', 'importe', 'monto',
            'pago', 'cobro', 'factura', 'facturación', 'descuento', 'oferta', 'promoción',
            'rebaja', 'ahorro', 'económico', 'barato', 'caro', 'costoso', 'asequible'
        ],
        'calidad': [
            'calidad', 'rendimiento', 'desempeño', 'eficiencia', 'eficacia', 'efectividad',
            'fiabilidad', 'confiabilidad', 'durabilidad', 'resistencia', 'robustez',
            'solidez', 'estabilidad', 'precisión', 'exactitud', 'consistencia'
        ],
        'problema': [
            'problema', 'error', 'fallo', 'defecto', 'bug', 'inconveniente', 'dificultad',
            'obstáculo', 'barrera', 'limitación', 'restricción', 'complicación', 'molestia',
            'inconformidad', 'insatisfacción', 'queja', 'reclamo', 'incidencia'
        ],
        'soporte': [
            'soporte', 'ayuda', 'asistencia', 'apoyo', 'servicio', 'atención', 'contacto',
            'consulta', 'asesoría', 'orientación', 'guía', 'instrucción', 'tutorial',
            'manual', 'documentación', 'capacitación', 'entrenamiento', 'formación'
        ],
        'tiempo': [
            'tiempo', 'plazo', 'periodo', 'duración', 'fecha', 'momento', 'instante',
            'hora', 'día', 'semana', 'mes', 'año', 'trimestre', 'semestre', 'anual',
            'mensual', 'semanal', 'diario', 'horario', 'calendario', 'cronograma'
        ],
        'ubicación': [
            'ubicación', 'lugar', 'sitio', 'localización', 'posición', 'dirección',
            'domicilio', 'residencia', 'sede', 'sucursal', 'tienda', 'oficina', 'local',
            'establecimiento', 'instalación', 'región', 'zona', 'área', 'sector', 'país'
        ]
    }
    
    def __init__(self):
        """Inicializar el servicio de extracción de palabras clave."""
        logger.info("Servicio de extracción de palabras clave inicializado")
        
        # Crear conjunto de stopwords para búsqueda eficiente
        self.stopwords_set = self.STOPWORDS
        
        # Crear conjuntos de categorías para clasificación
        self.category_word_sets = {}
        for category, words in self.KEYWORD_CATEGORIES.items():
            self.category_word_sets[category] = set(words)
            
        # Historial de palabras clave para análisis contextual
        self.conversation_keywords = {}
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesa el texto para extracción de palabras clave.
        
        Args:
            text: Texto a preprocesar
            
        Returns:
            str: Texto preprocesado
        """
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar signos de puntuación
        translator = str.maketrans('', '', string.punctuation + '¿¡')
        text = text.translate(translator)
        
        # Eliminar números
        text = re.sub(r'\d+', '', text)
        
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
        """
        Extrae palabras clave individuales de un texto.
        
        Args:
            text: Texto del que extraer palabras clave
            min_length: Longitud mínima de las palabras clave
            max_keywords: Número máximo de palabras clave a devolver
            
        Returns:
            List[str]: Lista de palabras clave
        """
        # Preprocesar texto
        processed_text = self.preprocess_text(text)
        
        # Dividir en palabras
        words = processed_text.split()
        
        # Filtrar stopwords y palabras cortas
        filtered_words = [
            word for word in words
            if word not in self.stopwords_set and len(word) >= min_length
        ]
        
        # Contar frecuencia de palabras
        word_counts = Counter(filtered_words)
        
        # Obtener las palabras más frecuentes
        keywords = [word for word, count in word_counts.most_common(max_keywords)]
        
        return keywords
    
    def extract_ngrams(self, text: str, n: int = 2, min_freq: int = 2, max_ngrams: int = 10) -> List[str]:
        """
        Extrae n-gramas (frases de n palabras) de un texto.
        
        Args:
            text: Texto del que extraer n-gramas
            n: Número de palabras en cada n-grama
            min_freq: Frecuencia mínima para considerar un n-grama
            max_ngrams: Número máximo de n-gramas a devolver
            
        Returns:
            List[str]: Lista de n-gramas
        """
        # Preprocesar texto
        processed_text = self.preprocess_text(text)
        
        # Dividir en palabras
        words = processed_text.split()
        
        # Generar n-gramas
        ngrams = []
        for i in range(len(words) - n + 1):
            # Verificar que ninguna palabra del n-grama sea una stopword
            if not any(words[i+j] in self.stopwords_set for j in range(n)):
                ngram = ' '.join(words[i:i+n])
                ngrams.append(ngram)
        
        # Contar frecuencia de n-gramas
        ngram_counts = Counter(ngrams)
        
        # Filtrar por frecuencia mínima
        filtered_ngrams = [
            ngram for ngram, count in ngram_counts.items()
            if count >= min_freq
        ]
        
        # Obtener los n-gramas más frecuentes
        top_ngrams = filtered_ngrams[:max_ngrams]
        
        return top_ngrams
    
    def classify_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Clasifica palabras clave en categorías predefinidas.
        
        Args:
            keywords: Lista de palabras clave a clasificar
            
        Returns:
            Dict: Diccionario con categorías y sus palabras clave
        """
        classified = {}
        
        for category, word_set in self.category_word_sets.items():
            classified[category] = []
            
            for keyword in keywords:
                # Verificar si la palabra clave está en la categoría
                if keyword in word_set:
                    classified[category].append(keyword)
                    continue
                    
                # Verificar si la palabra clave contiene alguna palabra de la categoría
                for category_word in word_set:
                    if category_word in keyword:
                        classified[category].append(keyword)
                        break
        
        # Eliminar categorías vacías
        classified = {k: v for k, v in classified.items() if v}
        
        return classified
    
    def extract_keywords_with_scores(self, text: str, min_length: int = 3, max_keywords: int = 20) -> Dict[str, float]:
        """
        Extrae palabras clave con sus puntuaciones de relevancia.
        
        Args:
            text: Texto del que extraer palabras clave
            min_length: Longitud mínima de las palabras clave
            max_keywords: Número máximo de palabras clave a devolver
            
        Returns:
            Dict: Diccionario con palabras clave y sus puntuaciones (0-1)
        """
        # Preprocesar texto
        processed_text = self.preprocess_text(text)
        
        # Dividir en palabras
        words = processed_text.split()
        
        # Filtrar stopwords y palabras cortas
        filtered_words = [
            word for word in words
            if word not in self.stopwords_set and len(word) >= min_length
        ]
        
        # Contar frecuencia de palabras
        word_counts = Counter(filtered_words)
        
        # Calcular puntuaciones
        total_words = len(filtered_words)
        keyword_scores = {}
        
        if total_words > 0:
            # Obtener la frecuencia máxima para normalizar
            max_freq = word_counts.most_common(1)[0][1] if word_counts else 1
            
            # Calcular puntuación normalizada (0-1)
            for word, count in word_counts.most_common(max_keywords):
                score = count / max_freq
                keyword_scores[word] = score
        
        return keyword_scores
    
    def update_conversation_keywords(self, conversation_id: str, text: str, role: str = 'user'):
        """
        Actualiza las palabras clave detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            text: Texto del mensaje
            role: Rol del mensaje (user/assistant)
        """
        # Solo procesar mensajes del usuario
        if role != 'user':
            return
            
        # Inicializar si es la primera vez
        if conversation_id not in self.conversation_keywords:
            self.conversation_keywords[conversation_id] = {
                "keywords": {},
                "ngrams": [],
                "categories": {}
            }
            
        # Extraer palabras clave con puntuaciones
        keywords = self.extract_keywords_with_scores(text)
        
        # Extraer n-gramas
        ngrams = self.extract_ngrams(text)
        
        # Clasificar palabras clave
        categories = self.classify_keywords(list(keywords.keys()))
        
        # Actualizar palabras clave de la conversación
        for keyword, score in keywords.items():
            if keyword in self.conversation_keywords[conversation_id]["keywords"]:
                # Actualizar puntuación (promedio ponderado)
                current_score = self.conversation_keywords[conversation_id]["keywords"][keyword]
                self.conversation_keywords[conversation_id]["keywords"][keyword] = (current_score + score) / 2
            else:
                # Añadir nueva palabra clave
                self.conversation_keywords[conversation_id]["keywords"][keyword] = score
        
        # Actualizar n-gramas
        self.conversation_keywords[conversation_id]["ngrams"].extend(ngrams)
        
        # Actualizar categorías
        for category, words in categories.items():
            if category in self.conversation_keywords[conversation_id]["categories"]:
                # Añadir nuevas palabras a la categoría
                self.conversation_keywords[conversation_id]["categories"][category].extend(words)
                # Eliminar duplicados
                self.conversation_keywords[conversation_id]["categories"][category] = list(set(self.conversation_keywords[conversation_id]["categories"][category]))
            else:
                # Añadir nueva categoría
                self.conversation_keywords[conversation_id]["categories"][category] = words
    
    def get_conversation_keywords(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene todas las palabras clave detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Diccionario con palabras clave, n-gramas y categorías
        """
        return self.conversation_keywords.get(conversation_id, {
            "keywords": {},
            "ngrams": [],
            "categories": {}
        })
    
    def clear_conversation_keywords(self, conversation_id: str):
        """
        Limpia las palabras clave almacenadas para una conversación.
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.conversation_keywords:
            del self.conversation_keywords[conversation_id]
    
    def get_top_keywords(self, conversation_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Obtiene las palabras clave más relevantes de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            limit: Número máximo de palabras clave a devolver
            
        Returns:
            List: Lista de tuplas (palabra_clave, puntuación)
        """
        keywords = self.get_conversation_keywords(conversation_id).get("keywords", {})
        
        # Ordenar por puntuación
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:limit]
    
    def get_top_ngrams(self, conversation_id: str, limit: int = 5) -> List[str]:
        """
        Obtiene los n-gramas más frecuentes de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            limit: Número máximo de n-gramas a devolver
            
        Returns:
            List: Lista de n-gramas
        """
        ngrams = self.get_conversation_keywords(conversation_id).get("ngrams", [])
        
        # Contar frecuencia
        ngram_counts = Counter(ngrams)
        
        # Obtener los más frecuentes
        top_ngrams = [ngram for ngram, _ in ngram_counts.most_common(limit)]
        
        return top_ngrams
    
    def get_dominant_categories(self, conversation_id: str) -> Dict[str, int]:
        """
        Obtiene las categorías dominantes en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Diccionario con categorías y su conteo de palabras clave
        """
        categories = self.get_conversation_keywords(conversation_id).get("categories", {})
        
        # Contar palabras en cada categoría
        category_counts = {category: len(words) for category, words in categories.items()}
        
        return category_counts
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de palabras clave en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Resultados del análisis
        """
        # Extraer palabras clave con puntuaciones
        keywords = self.extract_keywords_with_scores(text)
        
        # Extraer n-gramas
        ngrams = self.extract_ngrams(text)
        
        # Clasificar palabras clave
        categories = self.classify_keywords(list(keywords.keys()))
        
        # Determinar categorías dominantes
        category_counts = {category: len(words) for category, words in categories.items()}
        dominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        
        return {
            "keywords": keywords,
            "ngrams": ngrams,
            "categories": categories,
            "dominant_category": dominant_category
        }
    
    def analyze_conversation(self, messages: List[Dict[str, str]], conversation_id: str = None) -> Dict[str, Any]:
        """
        Analiza palabras clave en una conversación completa.
        
        Args:
            messages: Lista de mensajes de la conversación
            conversation_id: ID opcional de la conversación para almacenar palabras clave
            
        Returns:
            Dict: Análisis de palabras clave en la conversación
        """
        # Extraer solo mensajes del usuario
        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                "has_keywords": False,
                "message": "No hay mensajes de usuario en la conversación."
            }
            
        # Concatenar todos los mensajes
        all_text = " ".join(user_messages)
        
        # Analizar cada mensaje individual
        message_analyses = []
        for i, message in enumerate(user_messages):
            # Actualizar historial de palabras clave si se proporciona ID
            if conversation_id:
                self.update_conversation_keywords(
                    conversation_id, 
                    message,
                    'user'
                )
                
            # Analizar mensaje
            analysis = self.analyze_text(message)
            message_analyses.append(analysis)
        
        # Analizar texto completo
        full_analysis = self.analyze_text(all_text)
        
        # Obtener palabras clave de la conversación si se proporciona ID
        conversation_keywords = None
        if conversation_id:
            conversation_keywords = self.get_conversation_keywords(conversation_id)
            
        return {
            "has_keywords": bool(full_analysis["keywords"]),
            "message_count": len(user_messages),
            "full_analysis": full_analysis,
            "message_analyses": message_analyses,
            "conversation_keywords": conversation_keywords
        }
    
    def get_keyword_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Genera un resumen conciso de las palabras clave detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Resumen de palabras clave
        """
        # Obtener palabras clave de la conversación
        conversation_data = self.get_conversation_keywords(conversation_id)
        
        if not conversation_data.get("keywords"):
            return {
                "has_keywords": False,
                "summary": "No se han detectado palabras clave relevantes en esta conversación."
            }
            
        # Obtener top keywords
        top_keywords = self.get_top_keywords(conversation_id, 5)
        
        # Obtener top n-gramas
        top_ngrams = self.get_top_ngrams(conversation_id, 3)
        
        # Obtener categorías dominantes
        category_counts = self.get_dominant_categories(conversation_id)
        dominant_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:2]
        
        # Crear resumen
        keyword_text = ", ".join([keyword for keyword, _ in top_keywords])
        ngram_text = ", ".join(top_ngrams) if top_ngrams else "ninguno"
        category_text = ", ".join([category for category, _ in dominant_categories]) if dominant_categories else "ninguna"
        
        summary = f"Palabras clave principales: {keyword_text}. "
        summary += f"Frases relevantes: {ngram_text}. "
        summary += f"Categorías dominantes: {category_text}."
        
        return {
            "has_keywords": True,
            "top_keywords": top_keywords,
            "top_ngrams": top_ngrams,
            "dominant_categories": dominant_categories,
            "summary": summary
        }
