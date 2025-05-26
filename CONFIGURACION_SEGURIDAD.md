# Configuración de Seguridad para la API

Este documento describe la configuración de seguridad necesaria para la API, incluyendo las variables de entorno requeridas y las mejores prácticas implementadas.

## Variables de Entorno

Las siguientes variables de entorno son necesarias para la configuración de seguridad de la API:

### Autenticación JWT

```
# Clave secreta para firmar los tokens JWT (debe ser una cadena segura y compleja)
JWT_SECRET=tu_clave_secreta_muy_segura

# Algoritmo de firma para JWT (recomendado: HS256)
JWT_ALGORITHM=HS256

# Tiempo de expiración del token de acceso en minutos
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tiempo de expiración del token de refresco en días
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Limitación de Tasa (Rate Limiting)

```
# Número máximo de solicitudes permitidas por minuto por usuario/IP
RATE_LIMIT_PER_MINUTE=60

# Número máximo de solicitudes permitidas por hora por usuario/IP
RATE_LIMIT_PER_HOUR=1000

# Lista de IPs separadas por comas que están exentas de la limitación de tasa
RATE_LIMIT_WHITELIST_IPS=127.0.0.1,192.168.1.1
```

### CORS (Cross-Origin Resource Sharing)

```
# Orígenes permitidos para CORS, separados por comas
# En producción, especificar dominios exactos en lugar de usar "*"
ALLOWED_ORIGINS=https://ejemplo.com,https://app.ejemplo.com
```

### Registro (Logging)

```
# Nivel de registro (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Ruta al archivo de registro
LOG_FILE=logs/api.log
```

### Entorno

```
# Entorno de ejecución (development, testing, production)
ENVIRONMENT=production
```

## Mejores Prácticas de Seguridad Implementadas

### 1. Autenticación y Autorización

- **JWT (JSON Web Tokens)**: Implementación segura para autenticación de usuarios.
- **Control de Acceso Basado en Roles**: Verificación de permisos para acceder a recursos específicos.
- **Tokens de Refresco**: Implementación de tokens de corta duración con capacidad de renovación.

### 2. Protección contra Ataques

- **Limitación de Tasa (Rate Limiting)**: Protección contra ataques de fuerza bruta y DoS.
- **Encabezados de Seguridad HTTP**: Protección contra ataques XSS, clickjacking y sniffing.
- **Validación Estricta de Entradas**: Uso de modelos Pydantic para validar todas las entradas.

### 3. Manejo Seguro de Errores

- **Mensajes de Error Sanitizados**: No se exponen detalles de implementación en errores.
- **Registro Estructurado**: Todos los errores se registran con contexto para análisis.
- **Respuestas de Error Consistentes**: Formato estandarizado para todas las respuestas de error.

### 4. Registro y Monitoreo

- **Registro Estructurado en JSON**: Facilita el análisis y monitoreo.
- **Seguimiento de Solicitudes**: Cada solicitud tiene un ID único para seguimiento.
- **Métricas de Rendimiento**: Se registran tiempos de respuesta para cada solicitud.

## Recomendaciones Adicionales

1. **Rotación Regular de Secretos**: Cambiar periódicamente las claves secretas de JWT.
2. **Monitoreo Activo**: Implementar alertas para patrones de tráfico sospechosos.
3. **Auditorías de Seguridad**: Realizar revisiones periódicas del código y configuración.
4. **Actualizaciones Regulares**: Mantener todas las dependencias actualizadas.
5. **Pruebas de Penetración**: Realizar pruebas de seguridad periódicas.

## Configuración de Permisos

Los siguientes permisos están definidos en el sistema:

- `read:models`: Permiso para leer información de modelos predictivos
- `write:models`: Permiso para modificar modelos predictivos
- `read:analytics`: Permiso para acceder a analíticas
- `write:objections`: Permiso para registrar objeciones
- `write:needs`: Permiso para registrar necesidades
- `write:conversions`: Permiso para registrar conversiones
- `write:training`: Permiso para programar entrenamientos de modelos
- `admin`: Permiso de administrador (incluye todos los permisos)

## Roles Predefinidos

- **usuario_basico**: `read:models`
- **analista**: `read:models`, `read:analytics`
- **entrenador**: `read:models`, `write:objections`, `write:needs`, `write:conversions`
- **administrador_modelos**: `read:models`, `write:models`, `read:analytics`, `write:training`
- **admin**: Todos los permisos
