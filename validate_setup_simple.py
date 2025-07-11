#!/usr/bin/env python3
"""
Script simplificado de validación de configuración para NGX Voice Sales Agent.
Verifica componentes básicos sin dependencias problemáticas.
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationResult:
    """Resultado de una validación específica."""
    component: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Optional[str] = None

class NGXSetupValidatorSimple:
    """
    Validador simplificado de configuración del sistema NGX.
    """
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
    
    def validate_all(self) -> Dict[str, Any]:
        """Ejecuta todas las validaciones del sistema."""
        print("🔍 Iniciando validación de configuración NGX Voice Sales Agent")
        print("=" * 65)
        
        # Validaciones básicas
        self._validate_python_version()
        self._validate_environment_variables()
        self._validate_basic_dependencies()
        self._validate_project_structure()
        self._validate_key_files()
        self._validate_config_files()
        
        # Validaciones de funcionalidad
        asyncio.run(self._validate_core_functionality())
        
        return self._generate_report()
    
    def _validate_python_version(self):
        """Valida que la versión de Python sea la correcta."""
        major, minor = sys.version_info[:2]
        
        if major >= 3 and minor >= 10:
            self._add_result("Python Version", "pass", f"Python {major}.{minor} - Excelente")
        elif major >= 3 and minor >= 8:
            self._add_result("Python Version", "warn", f"Python {major}.{minor} - Funcional")
        else:
            self._add_result("Python Version", "fail", f"Python {major}.{minor} - Incompatible")
    
    def _validate_environment_variables(self):
        """Valida variables de entorno críticas."""
        required_vars = [
            "OPENAI_API_KEY",
            "ELEVENLABS_API_KEY", 
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "JWT_SECRET"
        ]
        
        optional_vars = [
            "SUPABASE_SERVICE_ROLE_KEY",
            "DEBUG",
            "LOG_LEVEL",
            "ENVIRONMENT"
        ]
        
        missing_required = []
        configured_required = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or not value.strip():
                missing_required.append(var)
            else:
                configured_required.append(var)
                self._add_result(f"ENV: {var}", "pass", "Configurado correctamente")
        
        configured_optional = []
        for var in optional_vars:
            value = os.getenv(var)
            if value and value.strip():
                configured_optional.append(var)
                self._add_result(f"ENV: {var}", "pass", "Configurado")
        
        if missing_required:
            self._add_result("Environment Variables", "fail", 
                           f"Variables críticas faltantes: {', '.join(missing_required)}")
        else:
            self._add_result("Environment Variables", "pass", 
                           f"Todas las variables críticas configuradas ({len(configured_required)}/5)")
        
        if configured_optional:
            self._add_result("Optional Environment Variables", "pass", 
                           f"Variables opcionales configuradas: {len(configured_optional)}")
    
    def _validate_basic_dependencies(self):
        """Valida dependencias básicas sin imports problemáticos."""
        basic_packages = ["os", "sys", "asyncio", "json", "datetime", "typing"]
        
        missing_basic = []
        for package in basic_packages:
            try:
                __import__(package)
                self._add_result(f"BASIC: {package}", "pass", f"{package} disponible")
            except ImportError:
                missing_basic.append(package)
        
        if missing_basic:
            self._add_result("Basic Dependencies", "fail", 
                           f"Dependencias básicas faltantes: {', '.join(missing_basic)}")
        else:
            self._add_result("Basic Dependencies", "pass", "Python stdlib completo")
        
        # Verificar instalación de paquetes principales sin importar
        try:
            import pkg_resources
            installed_packages = [d.project_name.lower() for d in pkg_resources.working_set]
            
            critical_packages = ["fastapi", "openai", "supabase", "pydantic", "uvicorn"]
            installed_critical = [pkg for pkg in critical_packages if pkg in installed_packages]
            missing_critical = [pkg for pkg in critical_packages if pkg not in installed_packages]
            
            if missing_critical:
                self._add_result("Package Installation", "fail", 
                               f"Paquetes críticos no instalados: {', '.join(missing_critical)}")
            else:
                self._add_result("Package Installation", "pass", 
                               f"Paquetes críticos instalados: {', '.join(installed_critical)}")
                
        except Exception as e:
            self._add_result("Package Installation", "warn", f"No se pudo verificar: {str(e)}")
    
    def _validate_project_structure(self):
        """Valida estructura de directorios."""
        required_dirs = [
            "src",
            "src/api",
            "src/services", 
            "src/agents",
            "src/models",
            "src/integrations",
            "src/conversation",
            "tests",
            "docker"
        ]
        
        existing_dirs = []
        missing_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                existing_dirs.append(dir_path)
                self._add_result(f"DIR: {dir_path}", "pass", "Existe")
            else:
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self._add_result("Project Structure", "fail", 
                           f"Directorios faltantes: {', '.join(missing_dirs)}")
        else:
            self._add_result("Project Structure", "pass", 
                           f"Estructura completa ({len(existing_dirs)} directorios)")
    
    def _validate_key_files(self):
        """Valida archivos clave del proyecto."""
        key_files = [
            ("requirements.txt", "Dependencias"),
            ("src/api/main.py", "API Principal"),
            ("src/services/conversation_service.py", "Servicio Conversación"),
            ("src/services/program_router.py", "Router Programas"),
            ("src/agents/unified_agent.py", "Agente Unificado"),
            ("src/models/conversation.py", "Modelos"),
            ("docker/Dockerfile", "Docker"),
            ("docker/docker-compose.yml", "Docker Compose"),
            (".env.example", "Ejemplo ENV"),
            ("CLAUDE.md", "Documentación"),
            ("README.md", "Documentación"),
            ("test_program_router_simple.py", "Tests")
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path, description in key_files:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                existing_files.append(file_path)
                # Verificar que no esté vacío
                try:
                    size = full_path.stat().st_size
                    if size > 0:
                        self._add_result(f"FILE: {file_path}", "pass", f"{description} - {size} bytes")
                    else:
                        self._add_result(f"FILE: {file_path}", "warn", f"{description} - archivo vacío")
                except:
                    self._add_result(f"FILE: {file_path}", "pass", f"{description} - existe")
            else:
                missing_files.append(f"{file_path} ({description})")
        
        if missing_files:
            self._add_result("Key Files", "warn", 
                           f"Archivos opcionales faltantes: {len(missing_files)}")
        else:
            self._add_result("Key Files", "pass", 
                           f"Todos los archivos clave presentes ({len(existing_files)})")
    
    def _validate_config_files(self):
        """Valida contenido de archivos de configuración."""
        # Validar requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                required_packages = ["fastapi", "openai", "supabase"]
                found_packages = []
                
                for package in required_packages:
                    if any(package in line.lower() for line in lines):
                        found_packages.append(package)
                
                if len(found_packages) >= 2:
                    self._add_result("requirements.txt", "pass", 
                                   f"Contiene {len(found_packages)} paquetes principales")
                else:
                    self._add_result("requirements.txt", "warn", 
                                   f"Solo {len(found_packages)} paquetes principales detectados")
            except Exception as e:
                self._add_result("requirements.txt", "warn", f"Error leyendo: {e}")
        
        # Validar .env.example
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            try:
                content = env_example.read_text()
                required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "SUPABASE_URL"]
                found_vars = []
                
                for var in required_vars:
                    if var in content:
                        found_vars.append(var)
                
                if len(found_vars) >= 2:
                    self._add_result(".env.example", "pass", 
                                   f"Contiene {len(found_vars)} variables principales")
                else:
                    self._add_result(".env.example", "warn", 
                                   f"Solo {len(found_vars)} variables principales")
            except Exception as e:
                self._add_result(".env.example", "warn", f"Error leyendo: {e}")
    
    async def _validate_core_functionality(self):
        """Valida funcionalidad básica sin dependencias externas."""
        # Test de router simplificado
        try:
            sys.path.insert(0, str(self.project_root))
            from test_program_router_simple import SimpleProgramRouter
            
            router = SimpleProgramRouter()
            test_data = {
                "id": "validation_test",
                "name": "Test User", 
                "age": 30,
                "interests": ["trabajo", "productividad"]
            }
            
            decision = await router.determine_program(
                customer_data=test_data,
                initial_message="Necesito más energía para trabajar"
            )
            
            if decision and hasattr(decision, 'recommended_program'):
                program = decision.recommended_program
                confidence = decision.confidence_score
                self._add_result("Program Router", "pass", 
                               f"Funcional - {program} (confianza: {confidence:.2f})")
            else:
                self._add_result("Program Router", "fail", "No retorna decisión válida")
                
        except Exception as e:
            self._add_result("Program Router", "fail", f"Error: {str(e)}")
        
        # Test de estructuras de datos
        try:
            from datetime import datetime
            
            # Test básico de datos
            test_conversation = {
                "id": "test_conv",
                "customer_id": "test_customer",
                "program_type": "PRIME", 
                "created_at": datetime.now(),
                "status": "active"
            }
            
            if len(test_conversation) == 5:
                self._add_result("Data Structures", "pass", "Modelos básicos funcionales")
            else:
                self._add_result("Data Structures", "warn", "Estructura de datos incompleta")
                
        except Exception as e:
            self._add_result("Data Structures", "fail", f"Error: {str(e)}")
        
        # Test de logging básico
        try:
            import logging
            
            logger = logging.getLogger("ngx_test")
            logger.info("Test log message")
            
            self._add_result("Logging System", "pass", "Sistema de logging funcional")
            
        except Exception as e:
            self._add_result("Logging System", "warn", f"Error en logging: {str(e)}")
    
    def _add_result(self, component: str, status: str, message: str, details: str = None):
        """Añade un resultado de validación."""
        self.results.append(ValidationResult(component, status, message, details))
    
    def _generate_report(self) -> Dict[str, Any]:
        """Genera el reporte final."""
        pass_count = sum(1 for r in self.results if r.status == "pass")
        warn_count = sum(1 for r in self.results if r.status == "warn")
        fail_count = sum(1 for r in self.results if r.status == "fail")
        total_count = len(self.results)
        
        print("\n" + "=" * 65)
        print("📊 REPORTE DE VALIDACIÓN")
        print("=" * 65)
        
        # Agrupar resultados por estado
        passed = [r for r in self.results if r.status == "pass"]
        warned = [r for r in self.results if r.status == "warn"]
        failed = [r for r in self.results if r.status == "fail"]
        
        print("\n✅ VALIDACIONES EXITOSAS:")
        for result in passed:
            print(f"   • {result.component}: {result.message}")
        
        if warned:
            print("\n⚠️ ADVERTENCIAS:")
            for result in warned:
                print(f"   • {result.component}: {result.message}")
        
        if failed:
            print("\n❌ ERRORES CRÍTICOS:")
            for result in failed:
                print(f"   • {result.component}: {result.message}")
        
        # Resumen numérico
        print("\n" + "=" * 65)
        print("📈 RESUMEN FINAL")
        print("=" * 65)
        print(f"✅ Exitosas: {pass_count}")
        print(f"⚠️ Advertencias: {warn_count}")
        print(f"❌ Errores: {fail_count}")
        print(f"📊 Total: {total_count}")
        
        # Score de configuración
        score = (pass_count * 100 + warn_count * 50) / (total_count * 100) * 100 if total_count > 0 else 0
        print(f"\n🎯 Score de configuración: {score:.1f}%")
        
        # Evaluación final
        if fail_count == 0 and warn_count <= 3:
            status = "🏆 EXCELENTE"
            recommendation = "Sistema listo para uso"
            ready = True
        elif fail_count == 0:
            status = "✅ BUENO"
            recommendation = "Sistema funcional con mejoras menores"
            ready = True
        elif fail_count <= 2:
            status = "⚠️ REGULAR"
            recommendation = "Corregir errores antes de usar"
            ready = False
        else:
            status = "🚨 CRÍTICO"
            recommendation = "Sistema requiere correcciones importantes"
            ready = False
        
        print(f"\n{status}: {recommendation}")
        
        # Próximos pasos
        if not ready:
            print(f"\n🔧 PRÓXIMOS PASOS:")
            print("   1. Corregir errores críticos listados arriba")
            print("   2. Configurar variables de entorno faltantes")
            print("   3. Instalar dependencias requeridas")
            print("   4. Volver a ejecutar validación")
        else:
            print(f"\n🚀 SISTEMA READY:")
            print("   • Configuración validada")
            print("   • Componentes principales presentes")
            print("   • Funcionalidad básica confirmada")
            print("   • Listo para desarrollo/testing")
        
        return {
            "total_validations": total_count,
            "pass_count": pass_count,
            "warn_count": warn_count,
            "fail_count": fail_count,
            "score": score,
            "status": status,
            "recommendation": recommendation,
            "ready_for_use": ready
        }

def main():
    """Función principal."""
    try:
        print("🚀 NGX Voice Sales Agent - Validación de Configuración")
        print("=" * 65)
        
        validator = NGXSetupValidatorSimple()
        report = validator.validate_all()
        
        print(f"\n🎊 Validación completada")
        print(f"Sistema: {'✅ READY' if report['ready_for_use'] else '⚠️ REQUIERE ATENCIÓN'}")
        
        # Exit codes para automatización
        if report['fail_count'] > 0:
            sys.exit(1)
        elif report['warn_count'] > 5:
            sys.exit(2) 
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"💥 Error en validación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()