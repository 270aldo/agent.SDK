#!/bin/bash

# Script para ejecutar pruebas con pytest

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurar entorno de prueba
export ENVIRONMENT=testing
export JWT_SECRET=test_secret_key_for_testing_only
export JWT_ALGORITHM=HS256
export JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
export JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
export RATE_LIMIT_PER_MINUTE=60
export RATE_LIMIT_PER_HOUR=1000
export LOG_LEVEL=INFO

# Crear directorio para logs si no existe
mkdir -p logs

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== Script de Pruebas para API NGX ===${NC}"
    echo -e "Uso: $0 [opción]"
    echo -e "Opciones:"
    echo -e "  all        - Ejecutar todas las pruebas"
    echo -e "  unit       - Ejecutar solo pruebas unitarias"
    echo -e "  integration - Ejecutar solo pruebas de integración"
    echo -e "  security   - Ejecutar solo pruebas de seguridad"
    echo -e "  auth       - Ejecutar pruebas relacionadas con autenticación"
    echo -e "  coverage   - Ejecutar todas las pruebas con informe de cobertura"
    echo -e "  help       - Mostrar esta ayuda"
}

# Función para ejecutar pruebas con cobertura
run_with_coverage() {
    echo -e "${BLUE}=== Ejecutando pruebas con informe de cobertura ===${NC}"
    python -m pytest tests/ --cov=src --cov-report=term --cov-report=html:coverage_report
    echo -e "${GREEN}Informe de cobertura generado en 'coverage_report/index.html'${NC}"
}

# Procesar argumentos
case "$1" in
    "unit")
        echo -e "${BLUE}=== Ejecutando pruebas unitarias ===${NC}"
        python -m pytest tests/unit/ -v
        ;;
    "integration")
        echo -e "${BLUE}=== Ejecutando pruebas de integración ===${NC}"
        python -m pytest tests/integration/ -v
        ;;
    "security")
        echo -e "${BLUE}=== Ejecutando pruebas de seguridad ===${NC}"
        python -m pytest tests/security/ -v
        ;;
    "auth")
        echo -e "${BLUE}=== Ejecutando pruebas de autenticación ===${NC}"
        python -m pytest tests/unit/auth/ tests/integration/api/test_auth_router.py -v
        ;;
    "coverage")
        run_with_coverage
        ;;
    "help")
        show_help
        ;;
    *)
        echo -e "${BLUE}=== Ejecutando todas las pruebas ===${NC}"
        python -m pytest tests/ -v
        ;;
esac

# Verificar si las pruebas pasaron
if [ $? -eq 0 ]; then
    echo -e "${GREEN}¡Todas las pruebas pasaron correctamente!${NC}"
    exit 0
else
    echo -e "${RED}Algunas pruebas fallaron. Revisa los errores.${NC}"
    exit 1
fi
