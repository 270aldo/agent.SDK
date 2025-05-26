"""
Utilidades para implementar caché local para operaciones de base de datos.
Permite funcionar temporalmente sin conexión y mejorar el rendimiento.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading

# Configurar logging
logger = logging.getLogger(__name__)

class LocalCache:
    """
    Implementa una caché local para operaciones de base de datos.
    Permite almacenar y recuperar datos cuando no hay conexión a la base de datos.
    """
    
    def __init__(self, cache_dir: str = ".cache", max_age_seconds: int = 3600):
        """
        Inicializar la caché local.
        
        Args:
            cache_dir: Directorio para almacenar los archivos de caché
            max_age_seconds: Tiempo máximo en segundos que un elemento puede permanecer en caché
        """
        self.cache_dir = cache_dir
        self.max_age_seconds = max_age_seconds
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.pending_operations: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        
        # Crear directorio de caché si no existe
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # Cargar caché desde disco
        self._load_cache_from_disk()
        
        logger.info(f"Caché local inicializada en {cache_dir}")
    
    def _get_cache_file_path(self, table: str) -> str:
        """
        Obtener la ruta del archivo de caché para una tabla.
        
        Args:
            table: Nombre de la tabla
            
        Returns:
            str: Ruta del archivo de caché
        """
        return os.path.join(self.cache_dir, f"{table}.json")
    
    def _get_pending_operations_file_path(self) -> str:
        """
        Obtener la ruta del archivo de operaciones pendientes.
        
        Returns:
            str: Ruta del archivo de operaciones pendientes
        """
        return os.path.join(self.cache_dir, "pending_operations.json")
    
    def _load_cache_from_disk(self) -> None:
        """Cargar la caché desde los archivos en disco."""
        try:
            # Buscar todos los archivos de caché
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json") and filename != "pending_operations.json":
                    table = filename[:-5]  # Quitar extensión .json
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            table_data = json.load(f)
                            self.memory_cache[table] = table_data
                            logger.debug(f"Caché cargada para tabla {table}: {len(table_data)} registros")
                    except Exception as e:
                        logger.warning(f"Error al cargar caché para tabla {table}: {e}")
            
            # Cargar operaciones pendientes
            pending_file = self._get_pending_operations_file_path()
            if os.path.exists(pending_file):
                try:
                    with open(pending_file, 'r') as f:
                        self.pending_operations = json.load(f)
                        logger.info(f"Operaciones pendientes cargadas: {len(self.pending_operations)}")
                except Exception as e:
                    logger.warning(f"Error al cargar operaciones pendientes: {e}")
        except Exception as e:
            logger.error(f"Error al cargar caché desde disco: {e}")
    
    def _save_cache_to_disk(self, table: str) -> None:
        """
        Guardar la caché de una tabla en disco.
        
        Args:
            table: Nombre de la tabla a guardar
        """
        try:
            if table in self.memory_cache:
                file_path = self._get_cache_file_path(table)
                with open(file_path, 'w') as f:
                    json.dump(self.memory_cache[table], f)
                logger.debug(f"Caché guardada para tabla {table}")
        except Exception as e:
            logger.error(f"Error al guardar caché para tabla {table}: {e}")
    
    def _save_pending_operations(self) -> None:
        """Guardar las operaciones pendientes en disco."""
        try:
            file_path = self._get_pending_operations_file_path()
            with open(file_path, 'w') as f:
                json.dump(self.pending_operations, f)
            logger.debug(f"Operaciones pendientes guardadas: {len(self.pending_operations)}")
        except Exception as e:
            logger.error(f"Error al guardar operaciones pendientes: {e}")
    
    def get(self, table: str, id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtener datos de la caché.
        
        Args:
            table: Nombre de la tabla
            id: ID del registro a obtener (opcional)
            filters: Filtros para aplicar (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de registros que coinciden con los criterios
        """
        with self.lock:
            if table not in self.memory_cache:
                return []
            
            table_data = self.memory_cache[table]
            
            # Si se especifica un ID, buscar por ID
            if id:
                for record in table_data:
                    if record.get('id') == id:
                        return [record]
                return []
            
            # Si se especifican filtros, aplicarlos
            if filters:
                result = []
                for record in table_data:
                    match = True
                    for key, value in filters.items():
                        if key not in record or record[key] != value:
                            match = False
                            break
                    if match:
                        result.append(record)
                return result
            
            # Si no se especifica ID ni filtros, devolver todos los registros
            return list(table_data)
    
    def set(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], operation: str = "upsert") -> Dict[str, Any]:
        """
        Almacenar datos en la caché y registrar la operación pendiente.
        
        Args:
            table: Nombre de la tabla
            data: Datos a almacenar (un registro o lista de registros)
            operation: Tipo de operación (insert, update, upsert, delete)
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        with self.lock:
            # Asegurarse de que la tabla existe en la caché
            if table not in self.memory_cache:
                self.memory_cache[table] = []
            
            # Convertir datos a lista si es un solo registro
            records = data if isinstance(data, list) else [data]
            
            # Procesar cada registro según la operación
            if operation in ["insert", "upsert"]:
                for record in records:
                    # Verificar si el registro tiene ID
                    if "id" not in record:
                        logger.warning(f"Registro sin ID no puede ser almacenado en caché: {record}")
                        continue
                    
                    # Para upsert, verificar si el registro ya existe
                    if operation == "upsert":
                        existing_index = None
                        for i, existing in enumerate(self.memory_cache[table]):
                            if existing.get("id") == record["id"]:
                                existing_index = i
                                break
                        
                        if existing_index is not None:
                            # Actualizar registro existente
                            self.memory_cache[table][existing_index] = record
                        else:
                            # Insertar nuevo registro
                            self.memory_cache[table].append(record)
                    else:
                        # Para insert, simplemente añadir el registro
                        self.memory_cache[table].append(record)
            
            elif operation == "update":
                for record in records:
                    # Verificar si el registro tiene ID
                    if "id" not in record:
                        logger.warning(f"Registro sin ID no puede ser actualizado en caché: {record}")
                        continue
                    
                    # Buscar y actualizar el registro existente
                    for i, existing in enumerate(self.memory_cache[table]):
                        if existing.get("id") == record["id"]:
                            self.memory_cache[table][i].update(record)
                            break
            
            elif operation == "delete":
                # Para delete, eliminar los registros que coincidan con los criterios
                if isinstance(data, dict) and "id" in data:
                    # Eliminar por ID
                    self.memory_cache[table] = [r for r in self.memory_cache[table] if r.get("id") != data["id"]]
                elif isinstance(data, dict):
                    # Eliminar por filtros
                    self.memory_cache[table] = [
                        r for r in self.memory_cache[table] 
                        if not all(r.get(k) == v for k, v in data.items())
                    ]
            
            # Registrar operación pendiente
            self.pending_operations.append({
                "table": table,
                "operation": operation,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Guardar en disco
            self._save_cache_to_disk(table)
            self._save_pending_operations()
            
            return {"success": True, "data": records}
    
    def clear_expired(self) -> int:
        """
        Eliminar elementos expirados de la caché.
        
        Returns:
            int: Número de elementos eliminados
        """
        with self.lock:
            count = 0
            now = datetime.now()
            
            for table in list(self.memory_cache.keys()):
                original_count = len(self.memory_cache[table])
                
                # Filtrar registros no expirados
                self.memory_cache[table] = [
                    record for record in self.memory_cache[table]
                    if "cached_at" not in record or 
                    datetime.fromisoformat(record["cached_at"]) > now - timedelta(seconds=self.max_age_seconds)
                ]
                
                removed = original_count - len(self.memory_cache[table])
                if removed > 0:
                    count += removed
                    logger.info(f"Eliminados {removed} registros expirados de la tabla {table}")
                    self._save_cache_to_disk(table)
            
            return count
    
    def get_pending_operations(self) -> List[Dict[str, Any]]:
        """
        Obtener la lista de operaciones pendientes.
        
        Returns:
            List[Dict[str, Any]]: Lista de operaciones pendientes
        """
        with self.lock:
            return self.pending_operations.copy()
    
    def mark_operation_completed(self, index: int) -> bool:
        """
        Marcar una operación pendiente como completada.
        
        Args:
            index: Índice de la operación en la lista de operaciones pendientes
            
        Returns:
            bool: True si se marcó correctamente, False en caso contrario
        """
        with self.lock:
            if 0 <= index < len(self.pending_operations):
                del self.pending_operations[index]
                self._save_pending_operations()
                return True
            return False
    
    def clear_all(self) -> None:
        """Eliminar toda la caché."""
        with self.lock:
            self.memory_cache.clear()
            self.pending_operations.clear()
            
            # Eliminar archivos de caché
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                    except Exception as e:
                        logger.error(f"Error al eliminar archivo de caché {filename}: {e}")
            
            logger.info("Caché completamente eliminada")

# Instancia global de la caché
local_cache = LocalCache()
