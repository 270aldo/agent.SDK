# Guía de Implementación: Agente Unificado NGX v2.0

## Resumen de Mejoras Implementadas

### 1. **Nuevas Herramientas Adaptativas**

Se han agregado 4 herramientas nuevas al agente:

#### `analyze_customer_profile`
- **Uso**: Después de 30-60 segundos de conversación
- **Función**: Analiza las señales del cliente para determinar el programa ideal
- **Retorna**: Programa recomendado, confianza, señales detectadas

#### `switch_program_focus`
- **Uso**: Cuando se detecta que el programa inicial no es el correcto
- **Función**: Proporciona scripts de transición natural entre programas
- **Retorna**: Script de transición y nuevas directrices de conversación

#### `get_adaptive_responses`
- **Uso**: Para obtener respuestas apropiadas según el modo actual
- **Función**: Proporciona preguntas, frases y vocabulario contextual
- **Retorna**: Respuestas adaptadas a la etapa y modo de conversación

#### `track_conversation_metrics`
- **Uso**: Para registrar métricas importantes de la conversación
- **Función**: Guarda datos para optimización continua
- **Retorna**: Confirmación y recomendaciones

### 2. **Sistema de Detección Mejorado**

El agente ahora incluye:

- **Detección en 3 fases**:
  1. DISCOVERY (0-60s): Preguntas neutrales
  2. ANALYSIS (30-90s): Análisis de señales
  3. FOCUSED (60s+): Enfoque específico en programa detectado

- **Zona Híbrida (45-55 años)**:
  - Evaluación basada en estilo de vida, no solo edad
  - Capacidad de presentar ambos programas
  - Transiciones suaves según señales

- **Métricas de Calidad**:
  - Velocidad de detección
  - Estabilidad (menos cambios = mejor)
  - Confianza en la recomendación

### 3. **Vocabulario y Tono Adaptativo**

El agente ajusta automáticamente:

- **Para PRIME**: Lenguaje ejecutivo, ritmo dinámico
- **Para LONGEVITY**: Lenguaje empático, ritmo pausado
- **Para HYBRID**: Balance entre ambos enfoques

## Mejores Prácticas de Implementación

### 1. **Configuración Inicial**

```python
# Contexto inicial completo
initial_context = {
    "age": 45,  # Si está disponible del test
    "score": 82,  # Score del lead magnet
    "interests": ["energía", "productividad"],  # Del test
    "lead_source": "lead magnet ejecutivo",
    "test_results_summary": "Necesita mejorar energía y manejo del estrés"
}

agent = NGXUnifiedAgent(initial_context=initial_context)
```

### 2. **Flujo de Conversación Óptimo**

#### Minuto 0-1: Apertura y Discovery
```
Cliente: "Hola, acabo de ver mis resultados del test"
Agente: "Hola [nombre], soy Carlos de NGX. ¿Qué fue lo que más te llamó la atención de tus resultados?"
```

#### Minuto 1-2: Análisis y Detección
- El agente debe usar `analyze_customer_profile` internamente
- Hacer 2-3 preguntas clave de discovery
- Identificar señales principales

#### Minuto 2-4: Presentación Adaptada
- Cambiar a modo FOCUSED cuando confianza > 70%
- Usar vocabulario específico del programa
- Mencionar beneficios relevantes

#### Minuto 4-6: Manejo de Objeciones
- Usar `handle_price_objection` si es necesario
- Mantener el tono adaptado al programa

#### Minuto 6-7: Cierre
- Crear urgencia sin presionar
- Ofrecer opciones de pago
- Si no hay decisión, agendar seguimiento

### 3. **Casos Especiales**

#### Ejecutivo Senior (50+ con perfil PRIME)
```python
# El agente detectará señales ejecutivas a pesar de la edad
# Ejemplo: CEO de 52 años
# Resultado esperado: PRIME con transición suave
```

#### Jubilado Joven (48 años con perfil LONGEVITY)
```python
# El agente detectará señales de longevidad a pesar de la edad
# Ejemplo: Jubilado anticipado enfocado en prevención
# Resultado esperado: LONGEVITY con explicación
```

#### Zona Híbrida Genuina
```python
# Para clientes 45-55 con señales mixtas
# El agente presentará ambas opciones
# Dejará que el cliente elija según sus prioridades
```

### 4. **Monitoreo y Optimización**

El agente genera métricas automáticamente:

```python
# Obtener contexto adaptativo actual
context = agent.get_adaptive_context()
print(f"Modo: {context['current_mode']}")
print(f"Programa: {context['detected_program']}")
print(f"Confianza: {context['confidence_score']}")

# Obtener insights de detección
insights = agent.get_detection_insights()
print(f"Calidad: {insights['recommendation_quality']}")
print(f"Estabilidad: {insights['detection_stability']}")
```

## Scripts de Transición Ejemplos

### De PRIME a LONGEVITY
```
"Sabes qué, escuchándote hablar sobre tu preocupación por [prevención/familia/salud a largo plazo], 
creo que tengo algo incluso mejor que PRIME para ti. NGX LONGEVITY está diseñado específicamente 
para personas como tú que buscan [objetivo detectado]..."
```

### De LONGEVITY a PRIME
```
"Me impresiona tu energía y ambición. Aunque inicialmente pensé en LONGEVITY por tu edad, 
tu estilo de vida activo y enfoque en [productividad/rendimiento] me dice que NGX PRIME 
sería perfecto para ti..."
```

### Presentación Híbrida
```
"Estás en ese punto perfecto donde podrías beneficiarte de cualquiera de nuestros dos programas. 
PRIME se enfoca en optimización inmediata de rendimiento, mientras que LONGEVITY se centra en 
vitalidad a largo plazo. Basándome en lo que me cuentas sobre [objetivos], ¿cuál resuena más contigo?"
```

## Configuración de Producción

### Variables de Entorno Recomendadas
```bash
# Configuración del agente
AGENT_DETECTION_THRESHOLD=0.7
AGENT_DETECTION_TIMEOUT=90
AGENT_HYBRID_AGE_MIN=45
AGENT_HYBRID_AGE_MAX=55

# Tracking
ENABLE_CONVERSATION_TRACKING=true
TRACK_DETECTION_METRICS=true
```

### Integración con API

```python
# En el endpoint de conversación
@app.post("/conversations/{conversation_id}/message")
async def process_message(conversation_id: str, message: MessageInput):
    # Obtener o crear agente
    agent = get_or_create_agent(conversation_id)
    
    # Procesar mensaje
    response = await agent.process(message.content)
    
    # Guardar métricas si la detección se completó
    if agent.detection_completed:
        await save_detection_metrics(
            conversation_id,
            agent.get_detection_insights()
        )
    
    return response
```

## Métricas de Éxito

### KPIs Principales
1. **Precisión de Detección**: Meta 85%+
2. **Tiempo de Detección**: Meta <60 segundos
3. **Estabilidad**: Meta >80% (pocos cambios)
4. **Satisfacción**: NPS >70

### Reportes Sugeridos
- Distribución de programas detectados
- Tiempo promedio de detección por segmento
- Tasa de cambios de programa
- Conversión por modo de detección

## Troubleshooting

### Problema: Detección muy lenta
**Solución**: Revisar las preguntas iniciales, deben ser más directas

### Problema: Muchos cambios de programa
**Solución**: Aumentar el umbral de confianza a 0.75

### Problema: No detecta zona híbrida
**Solución**: Verificar que la edad esté en rango 45-55 Y haya señales mixtas

## Conclusión

El agente unificado NGX v2.0 ofrece una experiencia de ventas más natural y efectiva mediante:
- Detección inteligente del programa ideal
- Adaptación dinámica del tono y vocabulario  
- Transiciones suaves cuando es necesario
- Métricas para optimización continua

La clave del éxito es confiar en el sistema de detección y permitir que el agente se adapte naturalmente a cada cliente.
