# NGX Sales Agent - Memory Bank

Este documento sirve como banco de memoria para el proyecto NGX Sales Agent, proporcionando contexto sobre el estado actual, características implementadas y plan de mejora.

## Estado Actual del Proyecto

### Componentes Principales Implementados

#### 1. Servicios de Conversación y Análisis
- **ConversationService**: Servicio principal que integra todos los componentes y gestiona el flujo de conversación.
- **IntentAnalysisService**: Servicio básico para analizar la intención de compra.
- **EnhancedIntentAnalysisService**: Versión mejorada con análisis de sentimiento, personalización por industria y aprendizaje continuo.

#### 2. Servicios de Experiencia de Usuario
- **HumanTransferService**: Gestiona la transferencia de conversaciones a agentes humanos.
- **FollowUpService**: Maneja el seguimiento post-conversación con programación de emails y recordatorios.
- **PersonalizationService**: Personaliza la comunicación según el perfil del usuario.

#### 3. Servicios de Calificación
- **LeadQualificationService**: Califica leads según su potencial y gestiona sesiones de agentes de voz.

#### 4. Modelos de Datos
- **ConversationState**: Modelo principal para el estado de una conversación.
- **CustomerData**: Modelo para los datos del cliente.
- **Message**: Modelo para mensajes en la conversación.

#### 5. Integraciones
- **Supabase**: Almacenamiento de datos y persistencia.
- **ElevenLabs**: Síntesis de voz para respuestas de audio.
- **OpenAI**: Procesamiento de lenguaje natural mediante GPT-4.

### Tablas en Base de Datos

#### Tablas de Conversación
- **conversations**: Almacena el estado de las conversaciones.

#### Tablas de Calificación
- **lead_qualification_results**: Resultados de calificación de leads.
- **voice_agent_sessions**: Sesiones de agentes de voz.

#### Tablas de Transferencia a Humanos
- **human_transfer_requests**: Solicitudes de transferencia a agentes humanos.
- **human_agents**: Información sobre agentes humanos disponibles.

#### Tablas de Seguimiento
- **follow_up_requests**: Solicitudes de seguimiento programadas.
- **email_templates**: Plantillas para emails de seguimiento.

#### Tablas de Análisis de Intención
- **intent_models**: Modelos de intención por industria.
- **intent_analysis_results**: Resultados de análisis de intención por conversación.
- **intent_training_data**: Datos de entrenamiento para aprendizaje continuo.

## Características Implementadas

### 1. Análisis de Intención Mejorado
- **Análisis de Sentimiento**: Detecta el tono general del usuario más allá de palabras clave.
- **Personalización por Industria**: Adapta las palabras clave según el sector (salud, finanzas, tecnología, educación).
- **Aprendizaje Continuo**: Sistema que aprende de conversaciones pasadas para mejorar la detección.

### 2. Transferencia a Agentes Humanos
- **Detección de Solicitudes**: Identifica automáticamente cuando un usuario solicita hablar con una persona real.
- **Gestión de Transferencias**: Maneja el estado y asignación de las transferencias.
- **Mensajes de Transición**: Genera mensajes apropiados durante el proceso de transferencia.

### 3. Seguimiento Post-Conversación
- **Programación Automática**: Programa seguimientos basados en el resultado de la conversación.
- **Emails Personalizados**: Genera contenido personalizado según el tipo de seguimiento.
- **Gestión de Estados**: Maneja el ciclo de vida completo del seguimiento.

### 4. Personalización Dinámica
- **Perfiles de Comunicación**: Adapta el estilo de comunicación según el perfil del usuario.
- **Saludos y Despedidas**: Genera mensajes personalizados al inicio y fin de la conversación.
- **Ajuste de Complejidad**: Adapta la complejidad del mensaje según el nivel técnico del usuario.

## Plan de Mejora

### Fase 1: Estabilización y Pruebas (2-3 semanas)
- **Manejo de Errores Robusto**
  - Implementar sistema de reintentos para operaciones de base de datos
  - Crear caché local para funcionar offline temporalmente
  - Mejorar mensajes de error y logging

- **Pruebas Automatizadas**
  - Crear pruebas unitarias para cada servicio
  - Implementar pruebas de integración para flujos completos
  - Configurar CI/CD para ejecución automática

- **Optimización de Rendimiento**
  - Implementar caché para resultados frecuentes
  - Optimizar consultas a la base de datos
  - Utilizar procesamiento asíncrono para tareas pesadas

### Fase 2: Mejoras en NLP y Análisis (3-4 semanas)
- **Procesamiento de Lenguaje Natural Avanzado**
  - Integrar servicios como spaCy o Transformers
  - Implementar reconocimiento de entidades
  - Añadir análisis de dependencias sintácticas

- **Embeddings y Vectorización**
  - Implementar sistema de vectorización de texto
  - Utilizar embeddings para capturar mejor la intención
  - Crear búsqueda semántica para respuestas más precisas

- **Aprendizaje Continuo Mejorado**
  - Implementar algoritmos de aprendizaje más sofisticados
  - Crear sistema de feedback para mejorar el modelo
  - Desarrollar métricas de evaluación de calidad

### Fase 3: Personalización Avanzada (2-3 semanas)
- **Perfiles de Usuario Dinámicos**
  - Desarrollar sistema que aprenda de interacciones previas
  - Crear perfiles que evolucionen con el tiempo
  - Implementar clustering para identificar patrones efectivos

- **Ajustes de Voz Basados en Emociones**
  - Implementar ajustes dinámicos de tono, velocidad y emoción
  - Añadir detección de emociones en la voz del usuario
  - Mejorar transiciones en la conversación

- **Sistema de Recomendaciones**
  - Crear recomendaciones personalizadas de productos
  - Implementar sugerencias basadas en perfil y conversación
  - Desarrollar sistema de cross-selling y up-selling

### Fase 4: Capacidades Predictivas (3-4 semanas)
- **Modelos Predictivos**
  - Implementar predicción de objeciones
  - Crear anticipación de necesidades del usuario
  - Desarrollar predicción de probabilidad de conversión

- **Motor de Decisiones**
  - Crear sistema para optimizar flujo de conversación
  - Implementar árboles de decisión dinámicos
  - Desarrollar adaptación en tiempo real

- **Anticipación de Objeciones**
  - Crear biblioteca de respuestas a objeciones comunes
  - Implementar detección temprana de señales de objeción
  - Desarrollar estrategias proactivas de manejo de objeciones

## Notas Técnicas

### Integración con Supabase
- La conexión a Supabase está configurada y funcionando correctamente.
- Las tablas para todos los servicios han sido creadas.
- Se utiliza Row Level Security (RLS) para proteger los datos.

### Dependencias Principales
- **supabase-py**: Cliente de Python para Supabase
- **openai**: SDK de OpenAI para GPT-4
- **elevenlabs**: Cliente para la API de síntesis de voz
- **fastapi**: Framework para la API REST
- **pydantic**: Validación de datos y serialización

### Posibles Mejoras de Arquitectura
- Considerar la implementación de una arquitectura de microservicios para mayor escalabilidad.
- Evaluar la posibilidad de utilizar una cola de mensajes para procesar solicitudes asíncronas.
- Implementar un sistema de caché distribuido para mejorar el rendimiento.

## Historial de Cambios Importantes

### Mayo 2025
- Implementación del servicio mejorado de análisis de intención con análisis de sentimiento y aprendizaje continuo.
- Creación del servicio de transferencia a agentes humanos.
- Implementación del servicio de seguimiento post-conversación.
- Desarrollo del servicio de personalización dinámica.
- Creación de tablas en Supabase para todos los servicios.

## Contactos y Recursos

### Repositorio
- URL: [Repositorio GitHub](#)

### Documentación
- [API Docs](#)
- [Guía de Desarrollo](#)

### Servicios Externos
- Supabase: [Dashboard](#)
- OpenAI: [Dashboard](#)
- ElevenLabs: [Dashboard](#)
