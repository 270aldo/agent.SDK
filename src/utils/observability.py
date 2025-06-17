"""Configuración centralizada de observabilidad para la API NGX.

Inicializa trazas distribuidas y métricas usando OpenTelemetry. Exporta en formato
OTLP para ser consumido por Prometheus/Grafana u otros back-ends compatibles.
"""
import os
from typing import Optional
from fastapi import FastAPI

# Importar OpenTelemetry de forma segura
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    try:
        # Versión >=1.23.0
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    except ImportError:  # pragma: no cover
        # Compatibilidad con versiones <1.23
        from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
    except ImportError:
        HTTPXClientInstrumentor = None
        AsyncPGInstrumentor = None
        LoggingInstrumentor = None
    try:
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, OTLPMetricExporter
    except ImportError:
        MeterProvider = None
        PeriodicExportingMetricReader = None
        OTLPMetricExporter = None
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    # OpenTelemetry no disponible
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    metrics = None
import logging

logger = logging.getLogger(__name__)

_OTEL_ENDPOINT_ENV = "OTEL_EXPORTER_OTLP_ENDPOINT"
_DEFAULT_OTEL_ENDPOINT = "http://localhost:4317"


def _create_resource():
    if not OPENTELEMETRY_AVAILABLE:
        return None
    return Resource.create({
        "service.name": os.getenv("SERVICE_NAME", "ngx-sales-agent"),
        "service.version": os.getenv("SERVICE_VERSION", "0.1.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })


def init_observability(app: FastAPI, endpoint: Optional[str] = None) -> None:
    """Inicializa OpenTelemetry para la aplicación FastAPI.

    Args:
        app: instancia de FastAPI
        endpoint: URL del collector OTLP. Si no se especifica, se tomará de la
            variable de entorno `OTEL_EXPORTER_OTLP_ENDPOINT` o se usará el valor
            por defecto localhost.
    """
    if not OPENTELEMETRY_AVAILABLE:
        logger.warning("OpenTelemetry no disponible - observabilidad deshabilitada")
        return
        
    endpoint = endpoint or os.getenv(_OTEL_ENDPOINT_ENV, _DEFAULT_OTEL_ENDPOINT)

    # Traza
    tracer_provider = TracerProvider(resource=_create_resource())
    span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Métricas (solo si están disponibles)
    if PeriodicExportingMetricReader and OTLPMetricExporter:
        metric_reader = PeriodicExportingMetricReader(
            exporter=OTLPMetricExporter(endpoint=endpoint, insecure=True),
            export_interval_millis=int(os.getenv("OTEL_EXPORT_INTERVAL", "60000")),
        )
        meter_provider = MeterProvider(resource=_create_resource(), metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
    else:
        logger.warning("OpenTelemetry metrics not available - skipping metric configuration")

    # Instrumentaciones automáticas
    FastAPIInstrumentor.instrument_app(app)
    if HTTPXClientInstrumentor:
        HTTPXClientInstrumentor().instrument()
    if AsyncPGInstrumentor:
        AsyncPGInstrumentor().instrument()
    if LoggingInstrumentor:
        LoggingInstrumentor().instrument(set_logging_format=True)

    logger.info("OpenTelemetry inicializado para FastAPI", extra={"otel_endpoint": endpoint})
