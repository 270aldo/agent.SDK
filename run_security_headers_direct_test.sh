#!/bin/bash

# Colores para los mensajes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ejecutando prueba directa de encabezados de seguridad ===${NC}"

# Ejecutar la prueba específica de encabezados de seguridad
echo -e "${YELLOW}Ejecutando prueba directa del middleware de seguridad...${NC}"
python -m pytest tests/security/test_security_headers_direct.py -v

# Verificar si la prueba fue exitosa
if [ $? -eq 0 ]; then
    echo -e "${GREEN}La prueba de encabezados de seguridad fue exitosa.${NC}"
else
    echo -e "${RED}La prueba de encabezados de seguridad falló. Revisa los errores.${NC}"
fi
