"""
Servicio para personalizar la comunicación según el perfil del usuario.
"""

import logging
from typing import Dict, Any, Optional, List

# Configurar logging
logger = logging.getLogger(__name__)

class PersonalizationService:
    """
    Servicio para personalizar la comunicación según el perfil del usuario.
    Ajusta el tono, estilo y contenido de los mensajes basado en las características del usuario.
    """
    
    # Perfiles de comunicación
    COMMUNICATION_PROFILES = {
        'formal': {
            'greeting': 'Estimado/a {name}, un placer saludarle.',
            'farewell': 'Ha sido un placer atenderle. Quedo a su disposición para cualquier consulta adicional.',
            'style': 'formal, respetuoso, profesional',
            'pronouns': 'usted',
            'vocabulary': 'técnico, preciso, elaborado'
        },
        'casual': {
            'greeting': 'Hola {name}, ¿cómo estás?',
            'farewell': '¡Gracias por tu tiempo! Estamos aquí para lo que necesites.',
            'style': 'cercano, amigable, conversacional',
            'pronouns': 'tú',
            'vocabulary': 'sencillo, directo, coloquial'
        },
        'enthusiastic': {
            'greeting': '¡Hola {name}! ¡Qué gusto saludarte!',
            'farewell': '¡Ha sido genial hablar contigo! ¡Estamos aquí para ayudarte en tu camino!',
            'style': 'energético, motivador, positivo',
            'pronouns': 'tú',
            'vocabulary': 'dinámico, inspirador, emotivo'
        },
        'technical': {
            'greeting': 'Hola {name}, bienvenido/a a nuestra plataforma.',
            'farewell': 'Gracias por tu interés. Si tienes más preguntas técnicas, no dudes en contactarnos.',
            'style': 'preciso, informativo, detallado',
            'pronouns': 'tú/usted',
            'vocabulary': 'técnico, específico, detallado'
        }
    }
    
    def __init__(self):
        """Inicializar el servicio de personalización."""
        logger.info("Servicio de personalización inicializado")
    
    def determine_communication_profile(self, user_data: Dict[str, Any]) -> str:
        """
        Determina el perfil de comunicación más adecuado para un usuario.
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            str: Perfil de comunicación recomendado
        """
        # Valores por defecto
        age = user_data.get('age', 35)
        occupation = user_data.get('occupation', '').lower()
        preferences = user_data.get('preferences', {})
        communication_style = preferences.get('communication_style', '')
        
        # Si el usuario ha especificado un estilo de comunicación, usarlo
        if communication_style and communication_style in self.COMMUNICATION_PROFILES:
            return communication_style
        
        # Determinar perfil basado en edad y ocupación
        if age >= 50:
            # Personas mayores suelen preferir comunicación más formal
            return 'formal'
        elif age <= 25:
            # Jóvenes suelen preferir comunicación más casual y entusiasta
            return 'enthusiastic'
        
        # Determinar por ocupación
        technical_occupations = ['ingeniero', 'programador', 'desarrollador', 'científico', 
                               'investigador', 'médico', 'técnico', 'analista']
        
        for tech_occ in technical_occupations:
            if tech_occ in occupation:
                return 'technical'
        
        # Por defecto, usar casual para la mayoría de los usuarios
        return 'casual'
    
    def personalize_message(self, message: str, user_data: Dict[str, Any], 
                          message_type: str = 'general') -> str:
        """
        Personaliza un mensaje según el perfil del usuario.
        
        Args:
            message: Mensaje original
            user_data: Datos del usuario
            message_type: Tipo de mensaje (greeting, farewell, general)
            
        Returns:
            str: Mensaje personalizado
        """
        # Determinar perfil de comunicación
        profile = self.determine_communication_profile(user_data)
        profile_data = self.COMMUNICATION_PROFILES.get(profile, self.COMMUNICATION_PROFILES['casual'])
        
        # Obtener nombre del usuario
        name = user_data.get('name', 'Cliente').split()[0]
        
        # Personalizar según tipo de mensaje
        if message_type == 'greeting':
            return profile_data['greeting'].format(name=name)
        elif message_type == 'farewell':
            return profile_data['farewell'].format(name=name)
        
        # Para mensajes generales, mantener el contenido pero ajustar el tono
        # según el perfil de comunicación
        personalized_message = message
        
        # Ajustar formalidad según el perfil
        if profile == 'formal':
            # Reemplazar expresiones informales por formales
            informal_to_formal = {
                'hola': 'Estimado/a',
                'qué tal': 'Cómo se encuentra',
                'gracias': 'Le agradezco',
                'por favor': 'Por favor,',
                'quieres': 'desea',
                'puedes': 'puede',
                'tu': 'su',
                'tus': 'sus'
            }
            
            for informal, formal in informal_to_formal.items():
                personalized_message = personalized_message.replace(informal, formal)
        
        return personalized_message
    
    def generate_personalized_greeting(self, user_data: Dict[str, Any]) -> str:
        """
        Genera un saludo personalizado según el perfil del usuario.
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            str: Saludo personalizado
        """
        # Determinar perfil de comunicación
        profile = self.determine_communication_profile(user_data)
        profile_data = self.COMMUNICATION_PROFILES.get(profile, self.COMMUNICATION_PROFILES['casual'])
        
        # Obtener nombre del usuario
        name = user_data.get('name', 'Cliente').split()[0]
        
        # Generar saludo personalizado
        greeting = profile_data['greeting'].format(name=name)
        
        # Añadir contexto según los datos del usuario
        if 'goals' in user_data and user_data['goals']:
            if profile == 'enthusiastic':
                greeting += f" ¡Estoy emocionado de ayudarte a alcanzar tus objetivos de {', '.join(user_data['goals'])}!"
            elif profile == 'formal':
                greeting += f" Me complace poder asistirle en sus objetivos relacionados con {', '.join(user_data['goals'])}."
            elif profile == 'technical':
                greeting += f" Estoy aquí para proporcionarte información detallada sobre cómo nuestro programa puede ayudarte con {', '.join(user_data['goals'])}."
            else:
                greeting += f" Estoy aquí para ayudarte con tus objetivos de {', '.join(user_data['goals'])}."
        
        return greeting
    
    def generate_personalized_farewell(self, user_data: Dict[str, Any], 
                                     conversation_context: Dict[str, Any] = None) -> str:
        """
        Genera una despedida personalizada según el perfil del usuario y el contexto de la conversación.
        
        Args:
            user_data: Datos del usuario
            conversation_context: Contexto de la conversación (opcional)
            
        Returns:
            str: Despedida personalizada
        """
        # Determinar perfil de comunicación
        profile = self.determine_communication_profile(user_data)
        profile_data = self.COMMUNICATION_PROFILES.get(profile, self.COMMUNICATION_PROFILES['casual'])
        
        # Obtener nombre del usuario
        name = user_data.get('name', 'Cliente').split()[0]
        
        # Generar despedida base
        farewell = profile_data['farewell'].format(name=name)
        
        # Personalizar según el contexto de la conversación
        if conversation_context:
            # Si hubo alta intención de compra
            if conversation_context.get('high_intent', False):
                if profile == 'enthusiastic':
                    farewell += f" ¡Estoy seguro de que tomarás una excelente decisión! ¡Hablamos pronto!"
                elif profile == 'formal':
                    farewell += f" Confío en que tomará la mejor decisión para sus necesidades. Estaré pendiente de su respuesta."
                elif profile == 'technical':
                    farewell += f" Te enviaré la información técnica detallada por correo para que puedas analizarla con calma."
                else:
                    farewell += f" Te enviaré más información por correo. ¡Hablamos pronto!"
            
            # Si hubo transferencia a humano
            elif conversation_context.get('transferred_to_human', False):
                if profile == 'enthusiastic':
                    farewell += f" ¡Nuestro equipo humano estará encantado de atenderte personalmente!"
                elif profile == 'formal':
                    farewell += f" Nuestro equipo de atención personalizada le atenderá con la mayor brevedad posible."
                else:
                    farewell += f" Un miembro de nuestro equipo te atenderá en breve."
        
        return farewell
    
    def adjust_message_complexity(self, message: str, user_data: Dict[str, Any]) -> str:
        """
        Ajusta la complejidad del mensaje según el perfil del usuario.
        
        Args:
            message: Mensaje original
            user_data: Datos del usuario
            
        Returns:
            str: Mensaje con complejidad ajustada
        """
        # Determinar nivel educativo o técnico del usuario
        education_level = user_data.get('education_level', 'medium')
        technical_knowledge = user_data.get('technical_knowledge', 'medium')
        
        # Ajustar complejidad
        if education_level == 'high' or technical_knowledge == 'high':
            # Mantener mensaje original para usuarios con alto nivel educativo o técnico
            return message
        elif education_level == 'low' or technical_knowledge == 'low':
            # Simplificar mensaje para usuarios con bajo nivel educativo o técnico
            # Acortar oraciones, usar vocabulario más simple
            simplified = message
            # Implementar lógica de simplificación aquí
            # Por ejemplo, dividir oraciones largas, reemplazar términos técnicos, etc.
            return simplified
        
        # Para nivel medio, mantener el mensaje original
        return message
