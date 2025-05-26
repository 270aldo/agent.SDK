#!/bin/bash

# Colores para los mensajes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Configurando entorno virtual para pruebas de seguridad ===${NC}"

# Crear entorno virtual para pruebas
echo -e "${YELLOW}Creando entorno virtual para pruebas...${NC}"
python -m venv test_venv

# Activar entorno virtual
echo -e "${YELLOW}Activando entorno virtual...${NC}"
source test_venv/bin/activate

# Instalar dependencias específicas para pruebas
echo -e "${YELLOW}Instalando dependencias compatibles para pruebas...${NC}"
pip install fastapi==0.95.1 starlette==0.26.1 httpx==0.23.3 pytest pytest-asyncio pytest-cov python-dotenv pyjwt uuid

# Crear script para ejecutar pruebas en el entorno virtual
echo -e "${YELLOW}Creando script para ejecutar pruebas en el entorno virtual...${NC}"
cat > run_security_tests_in_venv.sh << 'EOF'
#!/bin/bash

# Colores para los mensajes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ejecutando pruebas de seguridad en entorno virtual ===${NC}"

# Activar entorno virtual
source test_venv/bin/activate

# Ejecutar prueba directa de encabezados de seguridad
echo -e "${YELLOW}Ejecutando prueba directa de encabezados de seguridad...${NC}"
python -m pytest tests/security/test_security_headers_direct.py -v

# Verificar si la prueba fue exitosa
if [ $? -eq 0 ]; then
    echo -e "${GREEN}La prueba de encabezados de seguridad fue exitosa.${NC}"
else
    echo -e "${RED}La prueba de encabezados de seguridad falló. Revisa los errores.${NC}"
fi

# Desactivar entorno virtual
deactivate
EOF

# Hacer ejecutable el script
chmod +x run_security_tests_in_venv.sh

echo -e "${GREEN}Entorno virtual para pruebas configurado correctamente.${NC}"
echo -e "${GREEN}Para ejecutar las pruebas, usa: ./run_security_tests_in_venv.sh${NC}"

# Desactivar entorno virtual
deactivate
