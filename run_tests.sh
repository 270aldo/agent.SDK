#!/bin/bash

# Script para ejecutar pruebas con pytest

# Configurar entorno de prueba
export ENVIRONMENT=testing
export JWT_SECRET=test_secret_key_for_testing_only
export JWT_ALGORITHM=HS256
export JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
export JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Crear directorio para logs si no existe
mkdir -p logs

# Ejecutar todas las pruebas
echo "Ejecutando todas las pruebas..."
python -m pytest tests/ -v

# Ejecutar pruebas por categoría
if [ "$1" = "unit" ]; then
    echo "Ejecutando pruebas unitarias..."
    python -m pytest tests/unit/ -v
elif [ "$1" = "integration" ]; then
    echo "Ejecutando pruebas de integración..."
    python -m pytest tests/integration/ -v
elif [ "$1" = "security" ]; then
    echo "Ejecutando pruebas de seguridad..."
    python -m pytest tests/security/ -v
fi

# Mostrar resumen
echo "Pruebas completadas."
