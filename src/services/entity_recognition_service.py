"""
Servicio para reconocimiento de entidades en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Set
import json

# Configurar logging
logger = logging.getLogger(__name__)

class EntityRecognitionService:
    """
    Servicio para reconocimiento de entidades en conversaciones.
    Identifica y extrae entidades como nombres, organizaciones, productos, etc.
    """
    
    # Patrones para reconocimiento de entidades
    ENTITY_PATTERNS = {
        'nombre_persona': [
            r'(?:me llamo|soy|nombre es|llámame) ([A-Z][a-záéíóúüñ]+(?: [A-Z][a-záéíóúüñ]+)?)',
            r'(?:el|la|mi|este) (?:señor|señora|sr\.|sra\.|dr\.|dra\.) ([A-Z][a-záéíóúüñ]+(?: [A-Z][a-záéíóúüñ]+)?)'
        ],
        'correo_electronico': [
            r'[\w\.-]+@[\w\.-]+\.\w+'
        ],
        'telefono': [
            r'(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}',
            r'(?:\+\d{1,3}[- ]?)?\d{10}',
            r'(?:\+\d{1,3}[- ]?)?\d{3}[- ]?\d{3}[- ]?\d{4}'
        ],
        'fecha': [
            r'\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}',
            r'\d{1,2} de (?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?: de \d{2,4})?'
        ],
        'hora': [
            r'\d{1,2}:\d{2}(?: ?(?:am|pm|AM|PM))?',
            r'\d{1,2} (?:en punto|y media|y cuarto|menos cuarto)'
        ],
        'dinero': [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})? (?:pesos|dólares|euros)'
        ],
        'porcentaje': [
            r'\d+(?:\.\d+)?%',
            r'\d+(?:\.\d+)? por ciento'
        ],
        'direccion': [
            r'(?:calle|avenida|av\.|blvd\.|boulevard|calzada) [A-Z][a-záéíóúüñ]+(?: [A-Z][a-záéíóúüñ]+)?(?: #?\d+)?(?:,? (?:colonia|col\.) [A-Z][a-záéíóúüñ]+(?: [A-Z][a-záéíóúüñ]+)?)?'
        ],
        'sitio_web': [
            r'https?://(?:www\.)?[\w\.-]+\.\w+(?:/[\w\.-]*)*',
            r'www\.[\w\.-]+\.\w+(?:/[\w\.-]*)*',
            r'[\w\.-]+\.\w{2,}(?:/[\w\.-]*)*'
        ],
        'producto': [
            r'(?:producto|servicio|plan|paquete) (?:[A-Z][a-záéíóúüñ]+|[A-Z]+)(?:[- ][A-Z][a-záéíóúüñ]+|\d+)?'
        ]
    }
    
    # Diccionarios de entidades conocidas
    KNOWN_ENTITIES = {
        'organizacion': [
            'Google', 'Microsoft', 'Apple', 'Amazon', 'Facebook', 'Twitter', 'LinkedIn',
            'Uber', 'Airbnb', 'Netflix', 'Spotify', 'Tesla', 'IBM', 'Intel', 'Samsung',
            'Huawei', 'Xiaomi', 'Oracle', 'SAP', 'Salesforce', 'Adobe', 'Cisco',
            'Telcel', 'Telmex', 'AT&T', 'Movistar', 'Claro', 'Izzi', 'Totalplay',
            'Megacable', 'CFE', 'Pemex', 'Banorte', 'BBVA', 'Santander', 'Banamex',
            'HSBC', 'Scotiabank', 'Inbursa', 'Bancomer', 'Citibanamex'
        ],
        'ubicacion': [
            'México', 'Ciudad de México', 'CDMX', 'Guadalajara', 'Monterrey', 'Puebla',
            'Querétaro', 'Cancún', 'Tijuana', 'Mérida', 'Veracruz', 'Acapulco',
            'Estado de México', 'Jalisco', 'Nuevo León', 'Baja California', 'Sonora',
            'Chihuahua', 'Yucatán', 'Quintana Roo', 'Guanajuato', 'San Luis Potosí'
        ],
        'producto_generico': [
            'teléfono', 'celular', 'smartphone', 'tablet', 'laptop', 'computadora',
            'televisión', 'TV', 'refrigerador', 'lavadora', 'microondas', 'horno',
            'internet', 'plan de datos', 'fibra óptica', 'banda ancha', 'wifi',
            'seguro', 'tarjeta de crédito', 'préstamo', 'hipoteca', 'inversión',
            'cuenta de ahorro', 'cuenta corriente', 'plan de pensiones'
        ]
    }
    
    def __init__(self):
        """Inicializar el servicio de reconocimiento de entidades."""
        logger.info("Servicio de reconocimiento de entidades inicializado")
        
        # Compilar patrones para mejor rendimiento
        self.compiled_patterns = {}
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            self.compiled_patterns[entity_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            
        # Crear conjunto de entidades conocidas para búsqueda eficiente
        self.known_entity_sets = {}
        for entity_type, entities in self.KNOWN_ENTITIES.items():
            self.known_entity_sets[entity_type] = set(entities)
            
        # Diccionario para almacenar entidades detectadas en la conversación
        self.conversation_entities = {}
    
    def extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extrae entidades de un texto utilizando patrones predefinidos.
        
        Args:
            text: Texto del que extraer entidades
            
        Returns:
            Dict: Diccionario con tipos de entidades y listas de entidades encontradas
        """
        entities = {}
        
        # Extraer entidades usando patrones regulares
        for entity_type, patterns in self.compiled_patterns.items():
            entities[entity_type] = []
            
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    if isinstance(matches[0], tuple):  # Si el patrón tiene grupos
                        for match in matches:
                            if match[0]:  # Usar el primer grupo capturado
                                entities[entity_type].append(match[0])
                    else:
                        entities[entity_type].extend(matches)
        
        # Eliminar duplicados
        for entity_type in entities:
            entities[entity_type] = list(set(entities[entity_type]))
            
        # Extraer entidades conocidas
        for entity_type, entity_set in self.known_entity_sets.items():
            if entity_type not in entities:
                entities[entity_type] = []
                
            for entity in entity_set:
                if re.search(r'\b' + re.escape(entity) + r'\b', text, re.IGNORECASE):
                    entities[entity_type].append(entity)
        
        # Filtrar listas vacías
        return {k: v for k, v in entities.items() if v}
    
    def update_conversation_entities(self, conversation_id: str, text: str, role: str = 'user'):
        """
        Actualiza las entidades detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            text: Texto del mensaje
            role: Rol del mensaje (user/assistant)
        """
        # Solo procesar mensajes del usuario
        if role != 'user':
            return
            
        # Inicializar si es la primera vez
        if conversation_id not in self.conversation_entities:
            self.conversation_entities[conversation_id] = {}
            
        # Extraer entidades
        new_entities = self.extract_entities_from_text(text)
        
        # Actualizar entidades de la conversación
        for entity_type, entities in new_entities.items():
            if entity_type not in self.conversation_entities[conversation_id]:
                self.conversation_entities[conversation_id][entity_type] = []
                
            # Añadir nuevas entidades sin duplicar
            current_entities = set(self.conversation_entities[conversation_id][entity_type])
            current_entities.update(entities)
            self.conversation_entities[conversation_id][entity_type] = list(current_entities)
    
    def get_conversation_entities(self, conversation_id: str) -> Dict[str, List[str]]:
        """
        Obtiene todas las entidades detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Diccionario con tipos de entidades y listas de entidades encontradas
        """
        return self.conversation_entities.get(conversation_id, {})
    
    def clear_conversation_entities(self, conversation_id: str):
        """
        Limpia las entidades almacenadas para una conversación.
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.conversation_entities:
            del self.conversation_entities[conversation_id]
    
    def get_entity_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Genera un resumen de las entidades más relevantes detectadas en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Resumen de entidades relevantes
        """
        entities = self.get_conversation_entities(conversation_id)
        
        if not entities:
            return {
                "has_entities": False,
                "summary": "No se han detectado entidades en esta conversación."
            }
            
        # Priorizar entidades importantes
        priority_entities = {
            "nombre_persona": "Nombre",
            "correo_electronico": "Correo electrónico",
            "telefono": "Teléfono",
            "organizacion": "Organización",
            "producto": "Producto",
            "ubicacion": "Ubicación"
        }
        
        summary = {}
        for entity_type, display_name in priority_entities.items():
            if entity_type in entities and entities[entity_type]:
                summary[display_name] = entities[entity_type]
                
        # Añadir otras entidades
        for entity_type, entity_list in entities.items():
            if entity_type not in priority_entities and entity_list:
                # Convertir snake_case a título
                display_name = " ".join(word.capitalize() for word in entity_type.split("_"))
                summary[display_name] = entity_list
                
        return {
            "has_entities": True,
            "summary": summary
        }
    
    def extract_entities_from_conversation(self, messages: List[Dict[str, str]], conversation_id: str = None) -> Dict[str, List[str]]:
        """
        Extrae entidades de una lista de mensajes de conversación.
        
        Args:
            messages: Lista de mensajes de la conversación
            conversation_id: ID opcional de la conversación para almacenar entidades
            
        Returns:
            Dict: Diccionario con tipos de entidades y listas de entidades encontradas
        """
        all_entities = {}
        
        # Procesar cada mensaje
        for message in messages:
            if message.get('role') == 'user':
                # Extraer entidades del mensaje
                entities = self.extract_entities_from_text(message.get('content', ''))
                
                # Actualizar entidades globales
                for entity_type, entity_list in entities.items():
                    if entity_type not in all_entities:
                        all_entities[entity_type] = []
                    all_entities[entity_type].extend(entity_list)
                
                # Actualizar entidades de la conversación si se proporciona ID
                if conversation_id:
                    self.update_conversation_entities(
                        conversation_id, 
                        message.get('content', ''),
                        message.get('role', 'user')
                    )
        
        # Eliminar duplicados
        for entity_type in all_entities:
            all_entities[entity_type] = list(set(all_entities[entity_type]))
            
        return all_entities
    
    def get_entity_context(self, entity: str, entity_type: str = None) -> Dict[str, Any]:
        """
        Obtiene información contextual sobre una entidad específica.
        
        Args:
            entity: Entidad a analizar
            entity_type: Tipo de entidad (opcional)
            
        Returns:
            Dict: Información contextual sobre la entidad
        """
        context = {
            "entity": entity,
            "type": entity_type if entity_type else "desconocido",
            "attributes": {}
        }
        
        # Analizar según el tipo de entidad
        if entity_type == "nombre_persona":
            parts = entity.split()
            if len(parts) > 1:
                context["attributes"]["primer_nombre"] = parts[0]
                context["attributes"]["apellido"] = parts[-1]
                
        elif entity_type == "correo_electronico":
            parts = entity.split("@")
            if len(parts) == 2:
                context["attributes"]["usuario"] = parts[0]
                context["attributes"]["dominio"] = parts[1]
                
        elif entity_type == "telefono":
            # Limpiar formato
            clean_number = re.sub(r'[^0-9]', '', entity)
            if len(clean_number) >= 10:
                context["attributes"]["numero_limpio"] = clean_number
                
        elif entity_type == "organizacion":
            # Verificar si es una organización conocida
            for known_type, entities in self.known_entity_sets.items():
                if known_type == "organizacion" and entity in entities:
                    context["attributes"]["conocida"] = True
                    break
            else:
                context["attributes"]["conocida"] = False
                
        return context
    
    def export_entities_to_json(self, conversation_id: str) -> str:
        """
        Exporta las entidades de una conversación a formato JSON.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            str: Representación JSON de las entidades
        """
        entities = self.get_conversation_entities(conversation_id)
        return json.dumps(entities, ensure_ascii=False, indent=2)
    
    def import_entities_from_json(self, conversation_id: str, json_data: str):
        """
        Importa entidades desde un formato JSON a una conversación.
        
        Args:
            conversation_id: ID de la conversación
            json_data: Datos JSON con entidades
        """
        try:
            entities = json.loads(json_data)
            self.conversation_entities[conversation_id] = entities
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON de entidades para conversación {conversation_id}")
            raise ValueError("Formato JSON inválido")
