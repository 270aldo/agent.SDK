#!/bin/bash

# Script para ejecutar pruebas unitarias aisladas

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

echo -e "${BLUE}=== Ejecutando pruebas unitarias aisladas ===${NC}"

# Ejecutar pruebas unitarias de autenticación
echo -e "${YELLOW}Ejecutando pruebas unitarias de autenticación...${NC}"
python -m pytest tests/unit/auth/test_auth_utils_simple.py -v

# Ejecutar pruebas unitarias de middleware
echo -e "${YELLOW}Ejecutando pruebas unitarias de middleware...${NC}"
python -m pytest tests/unit/middleware/test_rate_limiter_simple.py -v

# Verificar si todas las pruebas pasaron
if [ $? -eq 0 ]; then
    echo -e "${GREEN}¡Todas las pruebas unitarias aisladas pasaron correctamente!${NC}"
    exit 0
else
    echo -e "${RED}Algunas pruebas unitarias aisladas fallaron. Revisa los errores.${NC}"
    exit 1
fi
