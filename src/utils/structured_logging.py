"""
Módulo para configuración de registro estructurado.

Este módulo proporciona funciones para configurar el registro estructurado
en formato JSON, facilitando el análisis y monitoreo de logs.
"""

import logging
import json
import os
import sys
import time
import traceback
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional, List, Union

class JSONFormatter(logging.Formatter):
    """
    Formateador de logs en formato JSON para facilitar el análisis.
    """
    
    def __init__(self, include_stack_info: bool = False):
        """
        Inicializa el formateador JSON.
        
        Args:
            include_stack_info: Si se debe incluir información de la pila en los logs
        """
        super().__init__()
        self.include_stack_info = include_stack_info
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea el registro de log como JSON.
        
        Args:
            record: Registro de log a formatear
            
        Returns:
            str: Registro formateado como JSON
        """
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread
        }
        
        # Añadir información de excepción si está disponible
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self._format_traceback(record.exc_info[2]) if self.include_stack_info else None
            }
        
        # Añadir información adicional si está disponible
        if hasattr(record, "extra") and record.extra:
            log_data["extra"] = record.extra
        
        return json.dumps(log_data)
    
    def _format_traceback(self, tb) -> List[Dict[str, Any]]:
        """
        Formatea un traceback como una lista de diccionarios.
        
        Args:
            tb: Objeto traceback
            
        Returns:
            List[Dict[str, Any]]: Traceback formateado
        """
        frames = []
        while tb:
            frame = tb.tb_frame
            frames.append({
                "filename": frame.f_code.co_filename,
                "name": frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        return frames

class StructuredLogger:
    """
    Clase para gestionar el registro estructurado.
    """
    
    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        max_file_size_mb: int = 10,
        backup_count: int = 5,
        include_stack_info: bool = False
    ) -> None:
        """
        Configura el sistema de registro estructurado.
        
        Args:
            log_level: Nivel de registro (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Ruta al archivo de log (opcional)
            max_file_size_mb: Tamaño máximo del archivo de log en MB
            backup_count: Número de archivos de respaldo a mantener
            include_stack_info: Si se debe incluir información de la pila en los logs
        """
        # Convertir nivel de log a constante de logging
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configuración básica
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Limpiar handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Crear formateador JSON
        json_formatter = JSONFormatter(include_stack_info=include_stack_info)
        
        # Configurar handler de consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(json_formatter)
        root_logger.addHandler(console_handler)
        
        # Configurar handler de archivo si se proporciona ruta
        if log_file:
            # Asegurar que el directorio exista
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Configurar handler de archivo rotativo
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size_mb * 1024 * 1024,
                backupCount=backup_count
            )
            file_handler.setFormatter(json_formatter)
            root_logger.addHandler(file_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Obtiene un logger configurado con el nombre especificado.
        
        Args:
            name: Nombre del logger
            
        Returns:
            logging.Logger: Logger configurado
        """
        return logging.getLogger(name)

def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Union[bool, Exception]] = None
) -> None:
    """
    Registra un mensaje con contexto adicional.
    
    Args:
        logger: Logger a utilizar
        level: Nivel de log (debug, info, warning, error, critical)
        message: Mensaje a registrar
        extra: Información adicional para incluir en el log
        exc_info: Información de excepción a incluir
    """
    log_method = getattr(logger, level.lower())
    
    # Crear copia de extra para no modificar el original
    log_extra = {"extra": extra or {}}
    
    # Añadir timestamp
    log_extra["extra"]["timestamp_ms"] = int(time.time() * 1000)
    
    # Registrar con contexto
    log_method(message, extra=log_extra, exc_info=exc_info)
