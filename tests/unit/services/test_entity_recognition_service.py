"""
Pruebas unitarias para el servicio de reconocimiento de entidades.
"""

import pytest
import json
from src.services.entity_recognition_service import EntityRecognitionService

class TestEntityRecognitionService:
    """Pruebas para el servicio de reconocimiento de entidades."""
    
    @pytest.fixture
    def entity_service(self):
        """Fixture para crear una instancia del servicio de reconocimiento de entidades."""
        return EntityRecognitionService()
    
    def test_extract_entities_from_text_nombre(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente nombres de personas."""
        text = "Hola, me llamo Juan Pérez y soy cliente desde hace 2 años."
        result = entity_service.extract_entities_from_text(text)
        
        assert "nombre_persona" in result
        assert "Juan Pérez" in result["nombre_persona"]
    
    def test_extract_entities_from_text_correo(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente correos electrónicos."""
        text = "Mi correo es usuario@ejemplo.com, pueden contactarme ahí."
        result = entity_service.extract_entities_from_text(text)
        
        assert "correo_electronico" in result
        assert "usuario@ejemplo.com" in result["correo_electronico"]
    
    def test_extract_entities_from_text_telefono(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente números de teléfono."""
        text = "Mi número de teléfono es 555-123-4567 o también pueden llamar al (555) 987-6543."
        result = entity_service.extract_entities_from_text(text)
        
        assert "telefono" in result
        assert len(result["telefono"]) == 2
        assert "555-123-4567" in result["telefono"] or "(555) 987-6543" in result["telefono"]
    
    def test_extract_entities_from_text_fecha(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente fechas."""
        text = "La reunión está programada para el 15/06/2023 o el 20 de julio de 2023."
        result = entity_service.extract_entities_from_text(text)
        
        assert "fecha" in result
        assert len(result["fecha"]) == 2
        assert "15/06/2023" in result["fecha"] or "20 de julio de 2023" in result["fecha"]
    
    def test_extract_entities_from_text_organizacion(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente organizaciones conocidas."""
        text = "Trabajo en Microsoft y antes estuve en Google."
        result = entity_service.extract_entities_from_text(text)
        
        assert "organizacion" in result
        assert "Microsoft" in result["organizacion"]
        assert "Google" in result["organizacion"]
    
    def test_extract_entities_from_text_ubicacion(self, entity_service):
        """Prueba que extract_entities_from_text detecte correctamente ubicaciones conocidas."""
        text = "Vivo en Ciudad de México pero viajo mucho a Monterrey."
        result = entity_service.extract_entities_from_text(text)
        
        assert "ubicacion" in result
        assert "Ciudad de México" in result["ubicacion"] or "CDMX" in result["ubicacion"]
        assert "Monterrey" in result["ubicacion"]
    
    def test_extract_entities_from_text_multiple(self, entity_service):
        """Prueba que extract_entities_from_text detecte múltiples tipos de entidades en un texto."""
        text = """
        Hola, soy María López y trabajo en Telcel.
        Mi correo es maria.lopez@ejemplo.com y mi teléfono es 555-123-4567.
        Vivo en Guadalajara y estoy interesada en un plan de datos.
        """
        result = entity_service.extract_entities_from_text(text)
        
        assert "nombre_persona" in result
        assert "correo_electronico" in result
        assert "telefono" in result
        assert "organizacion" in result
        assert "ubicacion" in result
        assert "producto_generico" in result
    
    def test_update_conversation_entities(self, entity_service):
        """Prueba que update_conversation_entities actualice correctamente las entidades de una conversación."""
        conversation_id = "conv123"
        text1 = "Hola, soy Juan Pérez."
        text2 = "Mi correo es juan.perez@ejemplo.com."
        
        # Actualizar con primer mensaje
        entity_service.update_conversation_entities(conversation_id, text1, 'user')
        result1 = entity_service.get_conversation_entities(conversation_id)
        
        assert "nombre_persona" in result1
        assert "Juan Pérez" in result1["nombre_persona"]
        
        # Actualizar con segundo mensaje
        entity_service.update_conversation_entities(conversation_id, text2, 'user')
        result2 = entity_service.get_conversation_entities(conversation_id)
        
        assert "nombre_persona" in result2
        assert "correo_electronico" in result2
        assert "Juan Pérez" in result2["nombre_persona"]
        assert "juan.perez@ejemplo.com" in result2["correo_electronico"]
    
    def test_ignore_assistant_messages(self, entity_service):
        """Prueba que update_conversation_entities ignore los mensajes del asistente."""
        conversation_id = "conv123"
        text = "Mi nombre es Juan Pérez y mi correo es juan.perez@ejemplo.com."
        
        # Actualizar con mensaje del asistente
        entity_service.update_conversation_entities(conversation_id, text, 'assistant')
        result = entity_service.get_conversation_entities(conversation_id)
        
        # No debería haber entidades
        assert result == {}
    
    def test_clear_conversation_entities(self, entity_service):
        """Prueba que clear_conversation_entities elimine correctamente las entidades de una conversación."""
        conversation_id = "conv123"
        text = "Hola, soy Juan Pérez."
        
        # Actualizar entidades
        entity_service.update_conversation_entities(conversation_id, text, 'user')
        assert entity_service.get_conversation_entities(conversation_id) != {}
        
        # Limpiar entidades
        entity_service.clear_conversation_entities(conversation_id)
        assert entity_service.get_conversation_entities(conversation_id) == {}
    
    def test_get_entity_summary_with_entities(self, entity_service):
        """Prueba que get_entity_summary genere un resumen correcto cuando hay entidades."""
        conversation_id = "conv123"
        text = """
        Hola, soy María López y trabajo en Telcel.
        Mi correo es maria.lopez@ejemplo.com y mi teléfono es 555-123-4567.
        Vivo en Guadalajara y estoy interesada en un plan de datos.
        """
        
        entity_service.update_conversation_entities(conversation_id, text, 'user')
        result = entity_service.get_entity_summary(conversation_id)
        
        assert result["has_entities"] == True
        assert "summary" in result
        assert "Nombre" in result["summary"]
        assert "Correo electrónico" in result["summary"]
        assert "Teléfono" in result["summary"]
        assert "Organización" in result["summary"]
        assert "Ubicación" in result["summary"]
    
    def test_get_entity_summary_without_entities(self, entity_service):
        """Prueba que get_entity_summary genere un resumen correcto cuando no hay entidades."""
        conversation_id = "conv_empty"
        result = entity_service.get_entity_summary(conversation_id)
        
        assert result["has_entities"] == False
        assert "summary" in result
        assert result["summary"] == "No se han detectado entidades en esta conversación."
    
    def test_extract_entities_from_conversation(self, entity_service):
        """Prueba que extract_entities_from_conversation extraiga entidades de una lista de mensajes."""
        messages = [
            {"role": "user", "content": "Hola, soy Juan Pérez."},
            {"role": "assistant", "content": "Hola Juan, ¿en qué puedo ayudarte?"},
            {"role": "user", "content": "Mi correo es juan.perez@ejemplo.com y vivo en Monterrey."}
        ]
        
        result = entity_service.extract_entities_from_conversation(messages)
        
        assert "nombre_persona" in result
        assert "correo_electronico" in result
        assert "ubicacion" in result
        assert "Juan Pérez" in result["nombre_persona"]
        assert "juan.perez@ejemplo.com" in result["correo_electronico"]
        assert "Monterrey" in result["ubicacion"]
    
    def test_get_entity_context_nombre(self, entity_service):
        """Prueba que get_entity_context genere contexto correcto para nombres."""
        entity = "Juan Pérez"
        entity_type = "nombre_persona"
        
        result = entity_service.get_entity_context(entity, entity_type)
        
        assert result["entity"] == "Juan Pérez"
        assert result["type"] == "nombre_persona"
        assert "attributes" in result
        assert "primer_nombre" in result["attributes"]
        assert "apellido" in result["attributes"]
        assert result["attributes"]["primer_nombre"] == "Juan"
        assert result["attributes"]["apellido"] == "Pérez"
    
    def test_get_entity_context_correo(self, entity_service):
        """Prueba que get_entity_context genere contexto correcto para correos."""
        entity = "usuario@ejemplo.com"
        entity_type = "correo_electronico"
        
        result = entity_service.get_entity_context(entity, entity_type)
        
        assert result["entity"] == "usuario@ejemplo.com"
        assert result["type"] == "correo_electronico"
        assert "attributes" in result
        assert "usuario" in result["attributes"]
        assert "dominio" in result["attributes"]
        assert result["attributes"]["usuario"] == "usuario"
        assert result["attributes"]["dominio"] == "ejemplo.com"
    
    def test_export_import_entities_json(self, entity_service):
        """Prueba que export_entities_to_json e import_entities_from_json funcionen correctamente."""
        conversation_id = "conv123"
        text = "Hola, soy Juan Pérez y mi correo es juan.perez@ejemplo.com."
        
        # Actualizar entidades
        entity_service.update_conversation_entities(conversation_id, text, 'user')
        
        # Exportar a JSON
        json_data = entity_service.export_entities_to_json(conversation_id)
        
        # Limpiar entidades
        entity_service.clear_conversation_entities(conversation_id)
        assert entity_service.get_conversation_entities(conversation_id) == {}
        
        # Importar desde JSON
        entity_service.import_entities_from_json(conversation_id, json_data)
        result = entity_service.get_conversation_entities(conversation_id)
        
        assert "nombre_persona" in result
        assert "correo_electronico" in result
        assert "Juan Pérez" in result["nombre_persona"]
        assert "juan.perez@ejemplo.com" in result["correo_electronico"]
