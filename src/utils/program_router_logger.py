"""
Configuración de logging específica para el sistema de routing de programas.
Proporciona logging estructurado para análisis y debugging del sistema de detección automática.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class ProgramRouterLogFormatter(logging.Formatter):
    """Formateador personalizado para logs del router de programas."""
    
    def format(self, record):
        # Crear timestamp ISO
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        # Extraer información estructurada del mensaje
        message = record.getMessage()
        
        # Formatear según el tipo de log
        if any(prefix in message for prefix in ["PROGRAM_DECISION:", "PROGRAM_SWITCH:", "FALLBACK_DECISION:"]):
            # Log estructurado para decisiones
            return f"[{timestamp}] {record.levelname} | {message}"
        else:
            # Log estándar
            return f"[{timestamp}] {record.levelname} | {record.name} | {message}"

def setup_program_router_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_structured_logs: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging para el router de programas.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Archivo de log opcional
        enable_structured_logs: Si habilitar logs estructurados
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("program_router")
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if enable_structured_logs:
        formatter = ProgramRouterLogFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)  # Archivo siempre con DEBUG
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_program_analytics(logger: logging.Logger, analytics: Dict[str, Any]):
    """
    Registra analytics del router de programas en formato estructurado.
    
    Args:
        logger: Logger configurado
        analytics: Datos de analytics del router
    """
    logger.info(
        f"ROUTER_ANALYTICS: total_decisions={analytics.get('total_decisions', 0)} | "
        f"prime_count={analytics.get('program_distribution', {}).get('PRIME', 0)} | "
        f"longevity_count={analytics.get('program_distribution', {}).get('LONGEVITY', 0)} | "
        f"hybrid_count={analytics.get('program_distribution', {}).get('HYBRID', 0)} | "
        f"avg_confidence={analytics.get('average_confidence', 0):.3f} | "
        f"high_confidence_rate={analytics.get('high_confidence_rate', 0):.3f}"
    )

def log_system_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    success: bool,
    details: Optional[Dict[str, Any]] = None
):
    """
    Registra métricas de performance del sistema.
    
    Args:
        logger: Logger configurado
        operation: Nombre de la operación
        duration_ms: Duración en milisegundos
        success: Si la operación fue exitosa
        details: Detalles adicionales
    """
    status = "SUCCESS" if success else "FAILED"
    details_str = ""
    
    if details:
        details_str = " | " + " | ".join([f"{k}={v}" for k, v in details.items()])
    
    logger.info(
        f"PERFORMANCE: operation={operation} | "
        f"duration_ms={duration_ms:.2f} | "
        f"status={status}{details_str}"
    )

class ProgramDecisionLogger:
    """Helper class para logging centralizado de decisiones de programa."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session_decisions = []
    
    def log_decision_start(self, customer_id: str, customer_data: Dict[str, Any]):
        """Registra el inicio de una decisión de programa."""
        self.logger.info(
            f"DECISION_START: customer_id={customer_id} | "
            f"age={customer_data.get('age', 'unknown')} | "
            f"interests_count={len(customer_data.get('interests', []))}"
        )
    
    def log_analysis_step(self, step: str, result: Dict[str, Any]):
        """Registra cada paso del análisis."""
        confidence = result.get('confidence', 0)
        reasoning = result.get('reasoning', '')
        
        self.logger.debug(
            f"ANALYSIS_STEP: step={step} | "
            f"confidence={confidence:.3f} | "
            f"reasoning={reasoning}"
        )
    
    def log_final_decision(self, decision, customer_data: Dict[str, Any]):
        """Registra la decisión final con contexto completo."""
        self.session_decisions.append({
            'customer_id': customer_data.get('id'),
            'program': decision.recommended_program,
            'confidence': decision.confidence_score,
            'timestamp': decision.timestamp.isoformat()
        })
        
        self.logger.info(
            f"DECISION_FINAL: program={decision.recommended_program} | "
            f"confidence={decision.confidence_score:.3f} | "
            f"customer_id={customer_data.get('id', 'unknown')} | "
            f"session_decisions_count={len(self.session_decisions)}"
        )
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de la sesión actual."""
        if not self.session_decisions:
            return {"total_decisions": 0}
        
        programs = [d['program'] for d in self.session_decisions]
        confidences = [d['confidence'] for d in self.session_decisions]
        
        return {
            "total_decisions": len(self.session_decisions),
            "programs": {
                "PRIME": programs.count("PRIME"),
                "LONGEVITY": programs.count("LONGEVITY"),
                "HYBRID": programs.count("HYBRID")
            },
            "average_confidence": sum(confidences) / len(confidences),
            "high_confidence_decisions": sum(1 for c in confidences if c >= 0.8)
        }

# Función de conveniencia para obtener logger configurado
def get_program_router_logger() -> logging.Logger:
    """Obtiene un logger configurado para el router de programas."""
    return setup_program_router_logging(
        log_level="INFO",
        log_file="logs/program_router.log",
        enable_structured_logs=True
    )