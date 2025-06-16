#!/bin/bash
# Script para ejecutar pruebas específicas de seguridad

# Establecer variables de entorno para pruebas
export ENVIRONMENT="testing"
export JWT_SECRET="test_secret_key_for_testing_only"
export JWT_ALGORITHM="HS256"
export JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30"
export JWT_REFRESH_TOKEN_EXPIRE_DAYS="7"
export RATE_LIMIT_PER_MINUTE="60"
export RATE_LIMIT_PER_HOUR="1000"
export LOG_LEVEL="INFO"

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ejecutando pruebas específicas de seguridad ===${NC}"

# Ejecutar todas las pruebas de seguridad en test_security_measures.py
echo -e "${YELLOW}Ejecutando pruebas de seguridad de test_security_measures.py y generando reporte de cobertura...${NC}"
python -m pytest -vv tests/security/test_security_measures.py --cov=src --cov-report=term-missing > pytest_output.log 2>&1
PYTEST_EXIT_CODE=$?

cp pytest_output.log pytest_results_visible.txt
rm pytest_output.log

# Verificar si todas las pruebas pasaron
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}¡Todas las pruebas de seguridad de test_security_measures.py pasaron correctamente!${NC}"
    exit 0
else
    echo -e "${RED}Algunas pruebas de seguridad de test_security_measures.py fallaron. Revisa los errores.${NC}"
    exit 1
fi
