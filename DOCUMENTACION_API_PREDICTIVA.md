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

## Formatos de Respuesta

Todas las respuestas de la API siguen el siguiente formato:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

En caso de error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error"
  }
}
```

## Endpoints

### Predicción de Objeciones

#### POST /objections/predict

Predice posibles objeciones que un cliente podría presentar durante una conversación de ventas.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "probability": 0.75,
    "objections": [
      {
        "type": "price",
        "description": "El cliente considera que el precio es demasiado alto",
        "confidence": 0.85,
        "suggested_responses": [
          "Enfatizar el valor a largo plazo",
          "Ofrecer opciones de financiamiento"
        ]
      },
      {
        "type": "features",
        "description": "El cliente no ve suficientes funcionalidades",
        "confidence": 0.65,
        "suggested_responses": [
          "Destacar características exclusivas",
          "Ofrecer demostración detallada"
        ]
      }
    ],
    "timestamp": "2025-05-25T20:10:30Z"
  },
  "error": null
}
```

### Predicción de Necesidades

#### POST /needs/predict

Identifica y predice las necesidades del cliente basado en la conversación actual y su perfil.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "needs": [
      {
        "category": "efficiency",
        "description": "El cliente busca mejorar la eficiencia de sus procesos",
        "priority": "high",
        "confidence": 0.92,
        "satisfaction_level": 0.3,
        "suggested_solutions": [
          "Presentar módulo de automatización",
          "Compartir casos de éxito similares"
        ]
      },
      {
        "category": "cost_reduction",
        "description": "El cliente necesita reducir costos operativos",
        "priority": "medium",
        "confidence": 0.78,
        "satisfaction_level": 0.5,
        "suggested_solutions": [
          "Destacar ROI a corto plazo",
          "Ofrecer plan escalonado de implementación"
        ]
      }
    ],
    "timestamp": "2025-05-25T20:11:15Z"
  },
  "error": null
}
```

### Predicción de Conversión

#### POST /conversion/predict

Predice la probabilidad de conversión del cliente y proporciona recomendaciones para aumentarla.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  },
  "product_id": "string"
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "probability": 0.68,
    "conversion_stage": "consideration",
    "estimated_time_to_conversion": "3 days",
    "key_factors": [
      {
        "factor": "product_fit",
        "impact": 0.7,
        "description": "El producto se ajusta bien a las necesidades expresadas"
      },
      {
        "factor": "price_sensitivity",
        "impact": -0.3,
        "description": "El cliente muestra sensibilidad al precio"
      }
    ],
    "recommendations": [
      {
        "action": "Ofrecer prueba gratuita",
        "expected_impact": 0.15,
        "priority": "high"
      },
      {
        "action": "Compartir testimonios de clientes similares",
        "expected_impact": 0.1,
        "priority": "medium"
      }
    ],
    "timestamp": "2025-05-25T20:12:00Z"
  },
  "error": null
}
```

### Motor de Decisiones

#### POST /decision-engine/optimize

Optimiza el flujo de conversación basado en predicciones y objetivos para maximizar la probabilidad de conversión.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  },
  "current_objectives": {
    "conversion": 0.5,
    "satisfaction": 0.3,
    "efficiency": 0.2
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "conversation_stage": "middle",
    "next_actions": [
      {
        "type": "address_objection",
        "id": "price_objection",
        "description": "Abordar objeción de precio destacando valor a largo plazo",
        "confidence": 0.85,
        "priority": "high"
      },
      {
        "type": "present_feature",
        "id": "automation_feature",
        "description": "Presentar características de automatización",
        "confidence": 0.75,
        "priority": "medium"
      }
    ],
    "decision_tree": { ... },
    "timestamp": "2025-05-25T20:13:30Z"
  },
  "error": null
}
```

#### POST /decision-engine/adapt

Adapta la estrategia de conversación en tiempo real basado en feedback del usuario.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "feedback": {
    "type": "satisfaction | objection | interest",
    "value": 0.4,
    "details": {
      "objection_type": "price",
      "category": "product_features"
    }
  },
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  },
  "current_objectives": {
    "conversion": 0.5,
    "satisfaction": 0.3,
    "efficiency": 0.2
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "adjusted_objectives": {
      "conversion": 0.4,
      "satisfaction": 0.5,
      "efficiency": 0.1
    },
    "next_actions": [
      {
        "type": "address_objection",
        "id": "price_objection",
        "description": "Abordar objeción de precio destacando valor a largo plazo",
        "confidence": 0.85,
        "priority": "high"
      },
      {
        "type": "present_feature",
        "id": "automation_feature",
        "description": "Presentar características de automatización",
        "confidence": 0.75,
        "priority": "medium"
      }
    ],
    "timestamp": "2025-05-25T20:14:15Z"
  },
  "error": null
}
```

#### POST /decision-engine/evaluate-path

Evalúa la efectividad de una ruta de conversación específica.

**Parámetros de solicitud:**

```json
{
  "conversation_id": "string",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "timestamp": "ISO-8601 string"
    }
  ],
  "path_actions": [
    {
      "type": "address_objection",
      "id": "price_objection",
      "timestamp": "ISO-8601 string"
    },
    {
      "type": "present_feature",
      "id": "automation_feature",
      "timestamp": "ISO-8601 string"
    }
  ],
  "customer_profile": {
    "id": "string",
    "demographics": { ... },
    "purchase_history": [ ... ],
    "preferences": { ... }
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "prediction_id": "string",
    "effectiveness": 0.72,
    "metrics": {
      "objection_reduction": 0.8,
      "needs_satisfaction": 0.65,
      "conversion_progress": 0.7,
      "action_alignment": 0.75
    },
    "recommendations": [
      {
        "type": "need_satisfaction",
        "description": "Satisfacer necesidad: El cliente busca más información sobre integraciones",
        "priority": "high"
      },
      {
        "type": "conversion_progression",
        "description": "Ofrecer una demostración personalizada",
        "priority": "medium"
      }
    ],
    "timestamp": "2025-05-25T20:15:00Z"
  },
  "error": null
}
```

### Estadísticas y Análisis

#### GET /analytics/objections

Obtiene estadísticas sobre predicciones de objeciones.

**Parámetros de consulta:**

- `time_period` (opcional): Período de tiempo en días (por defecto: 30)
- `customer_segment` (opcional): Segmento de clientes para filtrar

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "accuracy": {
      "accuracy": 0.82,
      "precision": 0.85,
      "recall": 0.78,
      "f1_score": 0.81
    },
    "most_common_objections": [
      {
        "type": "price",
        "count": 156,
        "percentage": 42
      },
      {
        "type": "features",
        "count": 89,
        "percentage": 24
      }
    ],
    "time_series": [
      {
        "date": "2025-05-01",
        "objection_count": 12,
        "accuracy": 0.8
      },
      {
        "date": "2025-05-02",
        "objection_count": 15,
        "accuracy": 0.83
      }
    ],
    "total_predictions": 371
  },
  "error": null
}
```

#### GET /analytics/needs

Obtiene estadísticas sobre predicciones de necesidades.

**Parámetros de consulta:**

- `time_period` (opcional): Período de tiempo en días (por defecto: 30)
- `customer_segment` (opcional): Segmento de clientes para filtrar

**Respuesta exitosa:**

Similar a `/analytics/objections` pero con datos específicos de necesidades.

#### GET /analytics/conversion

Obtiene estadísticas sobre predicciones de conversión.

**Parámetros de consulta:**

- `time_period` (opcional): Período de tiempo en días (por defecto: 30)
- `customer_segment` (opcional): Segmento de clientes para filtrar
- `product_id` (opcional): ID del producto para filtrar

**Respuesta exitosa:**

Similar a los endpoints anteriores pero con datos específicos de conversión.

#### GET /analytics/decision-engine

Obtiene estadísticas sobre el motor de decisiones.

**Parámetros de consulta:**

- `time_period` (opcional): Período de tiempo en días (por defecto: 30)

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "accuracy": {
      "accuracy": 0.85,
      "total_predictions": 523
    },
    "decision_types": {
      "address_objection": 187,
      "present_feature": 156,
      "offer_discount": 92,
      "provide_case_study": 88
    },
    "adaptation_rate": 0.32,
    "effectiveness": 0.76,
    "total_decisions": 523
  },
  "error": null
}
```

## Códigos de Error

| Código | Descripción |
|---------|-------------|
| `INVALID_REQUEST` | La solicitud contiene datos inválidos o falta información requerida |
| `UNAUTHORIZED` | No autorizado para acceder a este recurso |
| `RESOURCE_NOT_FOUND` | El recurso solicitado no existe |
| `MODEL_ERROR` | Error en el modelo predictivo |
| `RATE_LIMIT_EXCEEDED` | Se ha excedido el límite de solicitudes |
| `INTERNAL_SERVER_ERROR` | Error interno del servidor |

### Entrenamiento Automático de Modelos

#### POST /training/schedule

Programa el entrenamiento de un modelo predictivo.

**Parámetros de solicitud:**

```json
{
  "model_name": "string",
  "force_training": false,
  "training_config": {
    "param_exploration_rate": 0.2,
    "param_adaptation_threshold": 0.3
  }
}
```

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "success": true,
    "training_id": "training-decision_engine_model-20250525201530",
    "message": "Entrenamiento programado para el modelo 'decision_engine_model'",
    "estimated_completion": "2025-05-25T21:00:00Z"
  },
  "error": null
}
```

#### GET /training/status/{training_id}

Obtiene el estado actual de un entrenamiento.

**Parámetros de ruta:**

- `training_id`: ID del entrenamiento

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "success": true,
    "training_id": "training-decision_engine_model-20250525201530",
    "model_name": "decision_engine_model",
    "status": "in_progress",
    "start_time": "2025-05-25T20:15:30Z",
    "progress": 0.5,
    "metrics": null
  },
  "error": null
}
```

#### GET /training/list

Lista los entrenamientos de modelos con filtros opcionales.

**Parámetros de consulta:**

- `model_name` (opcional): Filtrar por nombre de modelo
- `status` (opcional): Filtrar por estado (scheduled, in_progress, completed, failed)
- `limit` (opcional): Número máximo de registros a devolver (por defecto: 10)

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "success": true,
    "trainings": [
      {
        "id": "training-decision_engine_model-20250525201530",
        "model_name": "decision_engine_model",
        "status": "completed",
        "start_time": "2025-05-25T20:15:30Z",
        "end_time": "2025-05-25T20:45:30Z",
        "metrics": {
          "accuracy": 0.85,
          "precision": 0.82,
          "recall": 0.87,
          "f1_score": 0.84
        }
      },
      {
        "id": "training-objection_prediction_model-20250525195530",
        "model_name": "objection_prediction_model",
        "status": "completed",
        "start_time": "2025-05-25T19:55:30Z",
        "end_time": "2025-05-25T20:25:30Z",
        "metrics": {
          "accuracy": 0.78,
          "precision": 0.75,
          "recall": 0.82,
          "f1_score": 0.78
        }
      }
    ],
    "count": 2
  },
  "error": null
}
```

#### GET /training/criteria/{model_name}

Verifica si un modelo cumple con los criterios para ser reentrenado.

**Parámetros de ruta:**

- `model_name`: Nombre del modelo a verificar

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "model_name": "decision_engine_model",
    "should_train": true,
    "reason": "Han pasado 10 días desde el último entrenamiento"
  },
  "error": null
}
```

#### POST /training/auto-schedule

Programa automáticamente el entrenamiento de todos los modelos que cumplan con los criterios.

**Respuesta exitosa:**

```json
{
  "success": true,
  "data": {
    "scheduled_trainings": [
      {
        "model_name": "decision_engine_model",
        "training_id": "training-decision_engine_model-20250525201530",
        "reason": "Han pasado 10 días desde el último entrenamiento"
      },
      {
        "model_name": "objection_prediction_model",
        "training_id": "training-objection_prediction_model-20250525201531",
        "reason": "Hay 65 registros de retroalimentación nuevos"
      }
    ],
    "skipped_models": [
      {
        "model_name": "needs_prediction_model",
        "reason": "No se cumplen los criterios para reentrenamiento"
      }
    ],
    "total_scheduled": 2,
    "total_skipped": 1
  },
  "error": null
}
```

## Limitaciones

- Máximo 10 solicitudes por segundo por cliente
- Máximo 100,000 solicitudes por día por cliente
- Tamaño máximo de solicitud: 1MB
- Máximo 50 mensajes por conversación en una solicitud
- Los entrenamientos de modelos pueden tardar hasta 30 minutos en completarse

## Ejemplos de Uso

### Ejemplo: Predecir objeciones

```python
import requests
import json

url = "https://api.ngx-sales-agent.com/predictive/objections/predict"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

data = {
    "conversation_id": "conv-12345",
    "messages": [
        {
            "role": "assistant",
            "content": "¿Qué características son más importantes para usted en un CRM?",
            "timestamp": "2025-05-25T19:55:00Z"
        },
        {
            "role": "user",
            "content": "Necesito algo fácil de usar y que se integre con nuestras herramientas actuales. ¿Cuánto cuesta la implementación?",
            "timestamp": "2025-05-25T19:56:30Z"
        }
    ],
    "customer_profile": {
        "id": "cust-6789",
        "demographics": {
            "industry": "retail",
            "company_size": "medium"
        }
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()

print(json.dumps(result, indent=2))
```
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
