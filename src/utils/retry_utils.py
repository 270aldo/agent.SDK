"""
Utilidades para implementar operaciones con reintentos automáticos.
Proporciona funciones para manejar errores transitorios en operaciones de base de datos
y otras operaciones que pueden fallar temporalmente.
"""

import logging
import asyncio
import random
from typing import Callable, TypeVar, Any, Optional, Dict, List, Union
from functools import wraps

# Configurar logging
logger = logging.getLogger(__name__)

# Definir tipo genérico para la función de reintento
T = TypeVar('T')

async def retry_async_operation(
    operation_func: Callable[..., Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    jitter: bool = True,
    exceptions_to_retry: tuple = (Exception,),
    retry_condition: Optional[Callable[[Exception], bool]] = None,
    *args,
    **kwargs
) -> Any:
    """
    Ejecuta una operación asíncrona con reintentos automáticos en caso de error.
    
    Args:
        operation_func: Función asíncrona a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Tiempo base de espera entre reintentos (en segundos)
        jitter: Si se debe añadir variación aleatoria al tiempo de espera
        exceptions_to_retry: Tupla de excepciones que deberían provocar un reintento
        retry_condition: Función opcional que evalúa si se debe reintentar basado en la excepción
        *args, **kwargs: Argumentos para pasar a la función
        
    Returns:
        El resultado de la operación
        
    Raises:
        La última excepción capturada si se agotan los reintentos
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 para incluir el intento inicial
        try:
            return await operation_func(*args, **kwargs)
        except exceptions_to_retry as e:
            last_exception = e
            
            # Verificar si debemos reintentar basado en la condición personalizada
            if retry_condition and not retry_condition(e):
                logger.warning(f"No se reintentará debido a la condición de reintento: {e}")
                raise
                
            # Si es el último intento, no reintentar
            if attempt == max_retries:
                logger.error(f"Se agotaron los reintentos ({max_retries}). Último error: {e}")
                raise
                
            # Calcular tiempo de espera con backoff exponencial
            delay = base_delay * (2 ** attempt)
            
            # Añadir jitter (variación aleatoria) si está habilitado
            if jitter:
                delay = delay * (0.5 + random.random())
                
            logger.warning(
                f"Intento {attempt + 1}/{max_retries + 1} falló con error: {e}. "
                f"Reintentando en {delay:.2f} segundos..."
            )
            
            # Esperar antes del siguiente intento
            await asyncio.sleep(delay)
    
    # Este punto nunca debería alcanzarse, pero por si acaso
    if last_exception:
        raise last_exception
    raise RuntimeError("Error inesperado en retry_async_operation")

def retry_async(
    max_retries: int = 3,
    base_delay: float = 1.0,
    jitter: bool = True,
    exceptions_to_retry: tuple = (Exception,),
    retry_condition: Optional[Callable[[Exception], bool]] = None
) -> Callable:
    """
    Decorador para funciones asíncronas que implementa reintentos automáticos.
    
    Args:
        max_retries: Número máximo de reintentos
        base_delay: Tiempo base de espera entre reintentos (en segundos)
        jitter: Si se debe añadir variación aleatoria al tiempo de espera
        exceptions_to_retry: Tupla de excepciones que deberían provocar un reintento
        retry_condition: Función opcional que evalúa si se debe reintentar basado en la excepción
        
    Returns:
        Decorador para aplicar a funciones asíncronas
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_async_operation(
                func,
                max_retries=max_retries,
                base_delay=base_delay,
                jitter=jitter,
                exceptions_to_retry=exceptions_to_retry,
                retry_condition=retry_condition,
                *args,
                **kwargs
            )
        return wrapper
    return decorator

# Función sincrónica para operaciones no asíncronas
def retry_operation(
    operation_func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    jitter: bool = True,
    exceptions_to_retry: tuple = (Exception,),
    retry_condition: Optional[Callable[[Exception], bool]] = None,
    *args,
    **kwargs
) -> T:
    """
    Ejecuta una operación sincrónica con reintentos automáticos en caso de error.
    
    Args:
        operation_func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Tiempo base de espera entre reintentos (en segundos)
        jitter: Si se debe añadir variación aleatoria al tiempo de espera
        exceptions_to_retry: Tupla de excepciones que deberían provocar un reintento
        retry_condition: Función opcional que evalúa si se debe reintentar basado en la excepción
        *args, **kwargs: Argumentos para pasar a la función
        
    Returns:
        El resultado de la operación
        
    Raises:
        La última excepción capturada si se agotan los reintentos
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 para incluir el intento inicial
        try:
            return operation_func(*args, **kwargs)
        except exceptions_to_retry as e:
            last_exception = e
            
            # Verificar si debemos reintentar basado en la condición personalizada
            if retry_condition and not retry_condition(e):
                logger.warning(f"No se reintentará debido a la condición de reintento: {e}")
                raise
                
            # Si es el último intento, no reintentar
            if attempt == max_retries:
                logger.error(f"Se agotaron los reintentos ({max_retries}). Último error: {e}")
                raise
                
            # Calcular tiempo de espera con backoff exponencial
            delay = base_delay * (2 ** attempt)
            
            # Añadir jitter (variación aleatoria) si está habilitado
            if jitter:
                delay = delay * (0.5 + random.random())
                
            logger.warning(
                f"Intento {attempt + 1}/{max_retries + 1} falló con error: {e}. "
                f"Reintentando en {delay:.2f} segundos..."
            )
            
            # Esperar antes del siguiente intento
            import time
            time.sleep(delay)
    
    # Este punto nunca debería alcanzarse, pero por si acaso
    if last_exception:
        raise last_exception
    raise RuntimeError("Error inesperado en retry_operation")

def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    jitter: bool = True,
    exceptions_to_retry: tuple = (Exception,),
    retry_condition: Optional[Callable[[Exception], bool]] = None
) -> Callable:
    """
    Decorador para funciones sincrónicas que implementa reintentos automáticos.
    
    Args:
        max_retries: Número máximo de reintentos
        base_delay: Tiempo base de espera entre reintentos (en segundos)
        jitter: Si se debe añadir variación aleatoria al tiempo de espera
        exceptions_to_retry: Tupla de excepciones que deberían provocar un reintento
        retry_condition: Función opcional que evalúa si se debe reintentar basado en la excepción
        
    Returns:
        Decorador para aplicar a funciones sincrónicas
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return retry_operation(
                func,
                max_retries=max_retries,
                base_delay=base_delay,
                jitter=jitter,
                exceptions_to_retry=exceptions_to_retry,
                retry_condition=retry_condition,
                *args,
                **kwargs
            )
        return wrapper
    return decorator

# Funciones específicas para operaciones de base de datos
async def retry_db_operation(
    operation_func: Callable[..., Any],
    max_retries: int = 3,
    *args,
    **kwargs
) -> Any:
    """
    Ejecuta una operación de base de datos con reintentos específicos para errores de DB.
    
    Args:
        operation_func: Función asíncrona a ejecutar
        max_retries: Número máximo de reintentos
        *args, **kwargs: Argumentos para pasar a la función
        
    Returns:
        El resultado de la operación
    """
    # Excepciones específicas de base de datos que deberían provocar reintentos
    db_exceptions = (
        # Añadir aquí excepciones específicas de la base de datos
        # Por ejemplo, para PostgreSQL: psycopg2.OperationalError, psycopg2.InterfaceError
        # Para Supabase, podríamos tener que capturar excepciones HTTP como:
        TimeoutError,
        ConnectionError,
        asyncio.TimeoutError
    )
    
    # Condición para reintentar solo ciertos tipos de errores de DB
    def should_retry_db_error(exception: Exception) -> bool:
        # Ejemplo: reintentar en caso de timeout o conexión perdida
        error_msg = str(exception).lower()
        return any(keyword in error_msg for keyword in [
            'timeout', 'connection', 'network', 'temporarily unavailable',
            'too many connections', 'server is busy'
        ])
    
    return await retry_async_operation(
        operation_func,
        max_retries=max_retries,
        base_delay=0.5,  # Tiempo base más corto para operaciones de DB
        jitter=True,
        exceptions_to_retry=db_exceptions,
        retry_condition=should_retry_db_error,
        *args,
        **kwargs
    )

# Decorador específico para operaciones de base de datos
def retry_db(max_retries: int = 3) -> Callable:
    """
    Decorador específico para operaciones de base de datos.
    
    Args:
        max_retries: Número máximo de reintentos
        
    Returns:
        Decorador para aplicar a funciones de base de datos
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_db_operation(
                func,
                max_retries=max_retries,
                *args,
                **kwargs
            )
        return wrapper
    return decorator
