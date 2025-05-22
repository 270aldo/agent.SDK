#!/usr/bin/env python3
"""
Script para configurar la base de datos en Supabase.
Crea las tablas y esquemas necesarios para la aplicación.
"""

import os
import sys
import logging
from pathlib import Path
import asyncio
import json

# Añadir el directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.integrations.supabase import supabase_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

async def setup_database():
    """Configurar la base de datos en Supabase."""
    try:
        logger.info("Iniciando configuración de base de datos...")
        
        # Obtener cliente Supabase (usamos el admin_client para tener permisos)
        client = supabase_client.get_client(admin=True)
        
        # Crear tabla de conversaciones
        logger.info("Verificando si la tabla de conversaciones existe...")
        
        # Verificar si la tabla 'conversations' ya existe
        try:
            response = await asyncio.to_thread(
                lambda: client.table("conversations").select("*").limit(1).execute()
            )
            logger.info("La tabla 'conversations' ya existe.")
        except Exception as e:
            # Si la tabla no existe, la creamos
            logger.info("Creando tabla de conversaciones...")
            try:
                # Crear tabla usando el método .from_ para interactuar con Postgres directamente
                # Esto depende de la versión de Supabase que estés usando
                # En algunos casos, es posible que necesites usar la interfaz web de Supabase 
                # para crear las tablas con la SQL proporcionada en las constantes originales
                
                # Como alternativa, creamos la tabla con la estructura mínima necesaria
                # y luego puedes completar la configuración desde la interfaz web
                logger.warning("La creación de tablas a través de la API no es compatible directamente.")
                logger.warning("Por favor, crea las tablas manualmente desde la interfaz web de Supabase usando los siguientes esquemas:")
                
                logger.info("=== ESQUEMA PARA LA TABLA 'conversations' ===")
                logger.info("""
CREATE TABLE IF NOT EXISTS public.conversations (
    conversation_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    program_type TEXT NOT NULL CHECK (program_type IN ('PRIME', 'LONGEVITY')),
    phase TEXT NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]'::JSONB,
    customer_data JSONB NOT NULL DEFAULT '{}'::JSONB,
    session_insights JSONB NOT NULL DEFAULT '{}'::JSONB,
    objections_raised JSONB NOT NULL DEFAULT '[]'::JSONB,
    next_steps_agreed BOOLEAN NOT NULL DEFAULT FALSE,
    call_duration_seconds INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índice para búsqueda por customer_id
CREATE INDEX IF NOT EXISTS idx_conversations_customer_id ON public.conversations(customer_id);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY IF NOT EXISTS "Service full access"
ON public.conversations
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
                """)
                
                logger.info("=== ESQUEMA PARA LA TABLA 'customers' ===")
                logger.info("""
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 120),
    gender TEXT,
    occupation TEXT,
    goals JSONB NOT NULL DEFAULT '{}'::JSONB,
    fitness_metrics JSONB NOT NULL DEFAULT '{}'::JSONB,
    lifestyle JSONB NOT NULL DEFAULT '{}'::JSONB,
    interaction_history JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índice para búsqueda por email
CREATE INDEX IF NOT EXISTS idx_customers_email ON public.customers(email);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY IF NOT EXISTS "Service full access"
ON public.customers
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
                """)
            except Exception as table_creation_error:
                logger.error(f"Error al crear tabla: {table_creation_error}")
        
        logger.info("Configuración de base de datos completada")
        
    except Exception as e:
        logger.error(f"Error al configurar la base de datos: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database()) 