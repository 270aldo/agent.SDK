#!/bin/bash

# Colores para los mensajes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ejecutando prueba específica de encabezados de seguridad ===${NC}"

# Ejecutar la prueba específica de encabezados de seguridad
echo -e "${YELLOW}Ejecutando prueba simplificada de encabezados de seguridad...${NC}"
python -m pytest tests/security/test_security_headers_only.py -v > pytest_security_headers.log

# Verificar si la prueba fue exitosa
if [ $? -eq 0 ]; then
    echo -e "${GREEN}La prueba de encabezados de seguridad fue exitosa.${NC}"
    cat pytest_security_headers.log
else
    echo -e "${RED}La prueba de encabezados de seguridad falló. Revisa los errores.${NC}"
    cat pytest_security_headers.log
fi
