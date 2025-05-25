# Documentación de API de Modelos Predictivos para NGX Sales Agent

## Introducción

Esta documentación describe la API de modelos predictivos implementada para el agente de ventas NGX. La API proporciona acceso a capacidades predictivas avanzadas que permiten anticipar objeciones, necesidades y probabilidad de conversión de los clientes, así como optimizar el flujo de conversación en tiempo real.

## Base URL

```
https://api.ngx-sales-agent.com/predictive
```

## Autenticación

Todas las llamadas a la API requieren autenticación mediante un token JWT en la cabecera de la solicitud:

```
Authorization: Bearer <token>
```

## Endpoints

### Predicción de Objeciones

#### Predecir Objeciones

```
POST /objections/predict
```

Predice posibles objeciones basadas en la conversación actual.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  }
}
```

**Respuesta:**

```json
{
  "objections": [
    {
      "type": "string",
      "confidence": 0.85,
      "suggested_responses": ["string"]
    }
  ],
  "confidence": 0.85,
  "signals": {
    "sentiment_negative": 0.7,
    "price_mentions": 0.8
  }
}
```

#### Registrar Objeción Real

```
POST /objections/record
```

Registra una objeción real para mejorar el modelo.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "objection_type": "string",
  "objection_text": "string"
}
```

**Respuesta:**

```json
{
  "id": "string",
  "status": "completed",
  "was_correct": true
}
```

#### Obtener Estadísticas de Objeciones

```
GET /objections/statistics?time_period=30
```

Obtiene estadísticas sobre objeciones detectadas.

**Parámetros de consulta:**
- `time_period`: Período de tiempo en días (opcional)

**Respuesta:**

```json
{
  "accuracy": {
    "accuracy": 0.82,
    "total_predictions": 150,
    "correct_predictions": 123,
    "confidence_avg": 0.78
  },
  "objection_distribution": {
    "price": 0.35,
    "value": 0.25,
    "need": 0.15,
    "authority": 0.10,
    "trust": 0.15
  },
  "total_objections": 150
}
```

### Predicción de Necesidades

#### Predecir Necesidades

```
POST /needs/predict
```

Predice las necesidades del cliente basándose en la conversación actual.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  }
}
```

**Respuesta:**

```json
{
  "needs": [
    {
      "category": "string",
      "confidence": 0.85,
      "suggested_actions": [
        {
          "type": "content | conversation | demo | contact",
          "action": "string",
          "priority": "high | medium | low"
        }
      ]
    }
  ],
  "confidence": 0.85,
  "features": {
    "explicit_requests": {
      "pricing": 0.9
    }
  }
}
```

#### Registrar Necesidad Real

```
POST /needs/record
```

Registra una necesidad real para mejorar el modelo.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "need_category": "string",
  "need_description": "string"
}
```

**Respuesta:**

```json
{
  "id": "string",
  "status": "completed",
  "was_correct": true
}
```

#### Obtener Estadísticas de Necesidades

```
GET /needs/statistics?time_period=30
```

Obtiene estadísticas sobre necesidades detectadas.

**Parámetros de consulta:**
- `time_period`: Período de tiempo en días (opcional)

**Respuesta:**

```json
{
  "accuracy": {
    "accuracy": 0.85,
    "total_predictions": 200,
    "correct_predictions": 170,
    "confidence_avg": 0.82
  },
  "needs_distribution": {
    "pricing": 0.30,
    "features": 0.25,
    "support": 0.15,
    "integration": 0.20,
    "training": 0.10
  },
  "total_needs": 200
}
```

### Predicción de Conversión

#### Predecir Conversión

```
POST /conversion/predict
```

Predice la probabilidad de conversión basada en la conversación actual.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"],
    "customer_since": "2023-01-15T00:00:00",
    "segment": "premium | standard | basic"
  }
}
```

**Respuesta:**

```json
{
  "probability": 0.75,
  "confidence": 0.80,
  "category": "high",
  "signals": {
    "buying_signals": 0.8,
    "engagement_level": 0.7,
    "positive_sentiment": 0.6
  },
  "recommendations": [
    {
      "type": "closing | customization | reassurance | relationship",
      "action": "string",
      "priority": "high | medium | low"
    }
  ]
}
```

#### Registrar Conversión Real

```
POST /conversion/record
```

Registra el resultado real de conversión para mejorar el modelo.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "did_convert": true,
  "conversion_details": {
    "value": 1000,
    "product": "string",
    "plan": "string"
  }
}
```

**Respuesta:**

```json
{
  "id": "string",
  "status": "completed",
  "was_correct": true
}
```

#### Obtener Estadísticas de Conversión

```
GET /conversion/statistics?time_period=30
```

Obtiene estadísticas sobre predicciones de conversión.

**Parámetros de consulta:**
- `time_period`: Período de tiempo en días (opcional)

**Respuesta:**

```json
{
  "accuracy": {
    "accuracy": 0.78,
    "total_predictions": 180,
    "correct_predictions": 140,
    "confidence_avg": 0.75
  },
  "conversion_rate": 0.32,
  "category_distribution": {
    "low": 0.25,
    "medium": 0.35,
    "high": 0.30,
    "very_high": 0.10
  },
  "total_predictions": 180
}
```

### Motor de Decisiones

#### Optimizar Flujo de Conversación

```
POST /decision/optimize
```

Optimiza el flujo de conversación basado en predicciones y objetivos.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  },
  "current_objectives": {
    "need_satisfaction": 0.35,
    "objection_handling": 0.25,
    "conversion_progress": 0.4
  }
}
```

**Respuesta:**

```json
{
  "next_actions": [
    {
      "id": "string",
      "type": "response | action | recommendation | exploration_action",
      "action_category": "objection_response | need_satisfaction | conversion_progression | exploration",
      "description": "string",
      "content": "string",
      "score": 0.85,
      "priority": "high | medium | low"
    }
  ],
  "decision_tree": {
    "id": "string",
    "type": "root",
    "description": "string",
    "children": [
      {
        "id": "string",
        "type": "objection_handling | need_satisfaction | conversion_progression | exploration",
        "description": "string",
        "confidence": 0.8,
        "score": 0.85,
        "children": []
      }
    ]
  },
  "objectives": {
    "need_satisfaction": 0.35,
    "objection_handling": 0.25,
    "conversion_progress": 0.4
  },
  "confidence": 0.82
}
```

#### Adaptar Estrategia en Tiempo Real

```
POST /decision/adapt
```

Adapta la estrategia de conversación en tiempo real basado en feedback y nuevos mensajes.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "current_strategy": {
    "next_actions": [],
    "decision_tree": {},
    "objectives": {},
    "confidence": 0.8
  },
  "feedback": {
    "success": false,
    "type": "objection_not_addressed | need_not_satisfied | conversion_stalled",
    "details": "string"
  },
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  }
}
```

**Respuesta:**

```json
{
  "next_actions": [],
  "decision_tree": {},
  "objectives": {},
  "confidence": 0.85,
  "adapted": true
}
```

#### Priorizar Objetivos

```
POST /decision/prioritize
```

Prioriza objetivos de conversación basado en el contexto actual.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  }
}
```

**Respuesta:**

```json
{
  "need_satisfaction": 0.40,
  "objection_handling": 0.35,
  "conversion_progress": 0.25
}
```

#### Evaluar Ruta de Conversación

```
POST /decision/evaluate
```

Evalúa la efectividad de una ruta de conversación específica.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "path_actions": [
    {
      "id": "string",
      "action_category": "objection_response | need_satisfaction | conversion_progression | exploration",
      "description": "string",
      "content": "string"
    }
  ],
  "customer_profile": {
    "industry": "string",
    "company_size": "string",
    "role": "string",
    "previous_purchases": ["string"]
  }
}
```

**Respuesta:**

```json
{
  "effectiveness": 0.78,
  "metrics": {
    "conversion_probability": 0.7,
    "objections_addressed": 0.8,
    "needs_satisfied": 0.85,
    "engagement_level": 0.75
  },
  "recommendations": [
    {
      "type": "objection_handling | need_satisfaction | engagement | conversion",
      "description": "string",
      "priority": "high | medium | low"
    }
  ]
}
```

#### Obtener Estadísticas de Decisiones

```
GET /decision/statistics?time_period=30
```

Obtiene estadísticas sobre decisiones tomadas por el motor.

**Parámetros de consulta:**
- `time_period`: Período de tiempo en días (opcional)

**Respuesta:**

```json
{
  "accuracy": {
    "accuracy": 0.80,
    "total_predictions": 250,
    "correct_predictions": 200,
    "confidence_avg": 0.78
  },
  "decision_types": {
    "decision": 150,
    "strategy_adaptation": 50,
    "objective_prioritization": 30,
    "path_evaluation": 20
  },
  "adaptation_rate": 0.25,
  "effectiveness": 0.82,
  "total_decisions": 250
}
```

### Gestión de Modelos Predictivos

#### Listar Modelos

```
GET /models?model_type=conversion
```

Lista todos los modelos predictivos registrados.

**Parámetros de consulta:**
- `model_type`: Tipo de modelo para filtrar (opcional)

**Respuesta:**

```json
[
  {
    "id": "string",
    "name": "objection_prediction_model",
    "type": "objection",
    "description": "string",
    "status": "active",
    "version": "1.0.0",
    "accuracy": 0.82,
    "training_samples": 1500,
    "created_at": "2023-01-15T00:00:00",
    "updated_at": "2023-05-20T00:00:00"
  }
]
```

#### Obtener Modelo

```
GET /models/{model_name}
```

Obtiene información de un modelo predictivo.

**Parámetros de ruta:**
- `model_name`: Nombre del modelo a obtener

**Respuesta:**

```json
{
  "id": "string",
  "name": "conversion_prediction_model",
  "type": "conversion",
  "parameters": "{}",
  "description": "string",
  "status": "active",
  "version": "1.0.0",
  "accuracy": 0.78,
  "training_samples": 1200,
  "created_at": "2023-01-15T00:00:00",
  "updated_at": "2023-05-20T00:00:00"
}
```

#### Actualizar Modelo

```
PUT /models/{model_name}
```

Actualiza un modelo predictivo existente.

**Parámetros de ruta:**
- `model_name`: Nombre del modelo a actualizar

**Parámetros de solicitud:**

```json
{
  "model_params": {
    "confidence_threshold": 0.7,
    "context_window": 15
  },
  "status": "active",
  "accuracy": 0.85
}
```

**Respuesta:**

```json
{
  "id": "string",
  "name": "needs_prediction_model",
  "type": "needs",
  "parameters": "{}",
  "description": "string",
  "status": "active",
  "version": "1.0.0",
  "accuracy": 0.85,
  "training_samples": 1800,
  "created_at": "2023-01-15T00:00:00",
  "updated_at": "2023-05-25T00:00:00"
}
```

## Integración con Puntos de Contacto

### Portal Web

Para integrar los modelos predictivos en el portal web, utiliza el siguiente flujo:

1. Al iniciar una conversación, crea un nuevo `conversation_id`
2. Después de cada mensaje del usuario, envía la conversación completa a `/predictive/decision/optimize`
3. Utiliza las acciones recomendadas para guiar la respuesta del agente
4. Si el usuario muestra señales de objeción, utiliza `/predictive/objections/predict` para obtener respuestas específicas
5. Registra los resultados reales con los endpoints `/record` correspondientes

### Aplicación Móvil

La integración con la aplicación móvil sigue un patrón similar al portal web, con algunas consideraciones adicionales:

1. Implementa un sistema de caché para reducir la latencia en conexiones móviles
2. Utiliza notificaciones push basadas en predicciones de `/predictive/conversion/predict`
3. Adapta la interfaz según las necesidades detectadas con `/predictive/needs/predict`

### Centro de Llamadas

Para el centro de llamadas, implementa un panel de asistencia que:

1. Muestra predicciones de objeciones en tiempo real
2. Sugiere respuestas basadas en `/predictive/decision/optimize`
3. Proporciona indicadores visuales de sentimiento y probabilidad de conversión
4. Permite a los representantes registrar resultados reales para mejorar los modelos

### Kioscos en Tienda

Para kioscos en tienda, implementa una versión simplificada que:

1. Utiliza `/predictive/needs/predict` para anticipar necesidades basadas en interacciones cortas
2. Implementa flujos optimizados basados en `/predictive/decision/optimize`
3. Integra con inventario local para recomendaciones inmediatas

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Solicitud incorrecta. Verifica los parámetros. |
| 401 | No autorizado. Verifica tu token de autenticación. |
| 404 | Recurso no encontrado. |
| 500 | Error interno del servidor. |

## Límites de Tasa

- 100 solicitudes por minuto por API key
- 5,000 solicitudes por día por API key

## Soporte

Para soporte técnico, contacta a api-support@ngx-sales-agent.com o abre un ticket en el portal de desarrolladores.
