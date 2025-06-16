#!/bin/bash
# Script para ejecutar pruebas de servicios predictivos

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

echo -e "${BLUE}=== Ejecutando pruebas de servicios predictivos ===${NC}"

# Instalar pytest-asyncio si no está instalado
pip install pytest-asyncio > /dev/null 2>&1

# Ejecutar pruebas del servicio de predicción de objeciones
echo -e "${YELLOW}Ejecutando pruebas del servicio de predicción de objeciones...${NC}"
python -m pytest tests/unit/services/predictive/test_objection_prediction_service.py -v

# Ejecutar pruebas del servicio de predicción de necesidades
echo -e "${YELLOW}Ejecutando pruebas del servicio de predicción de necesidades...${NC}"
python -m pytest tests/unit/services/predictive/test_needs_prediction_service.py -v

# Verificar si todas las pruebas pasaron
if [ $? -eq 0 ]; then
    echo -e "${GREEN}¡Todas las pruebas de servicios predictivos pasaron correctamente!${NC}"
    exit 0
else
    echo -e "${RED}Algunas pruebas de servicios predictivos fallaron. Revisa los errores.${NC}"
    exit 1
fi
