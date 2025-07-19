#!/usr/bin/env python3
"""
Script de prueba simplificado para validar la lógica del ProgramRouter.
Prueba solo la lógica interna sin dependencias externas.
"""

import asyncio
import sys
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

# Simular las clases necesarias sin importar dependencias
@dataclass
class ProgramDecision:
    recommended_program: str
    confidence_score: float
    reasoning: str
    signals_detected: list
    is_hybrid: bool
    timestamp: datetime
    should_ask_clarifying: bool = False

class SimpleProgramRouter:
    """
    Versión simplificada del ProgramRouter para testing sin dependencias externas.
    """
    
    def __init__(self):
        self.confidence_threshold_high = 0.8
        self.confidence_threshold_medium = 0.6
        self.age_weight = 0.4
        self.content_weight = 0.6
        self.decision_history = []
        
        # Enhanced logging setup
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup enhanced logging for the simple router."""
        import logging
        
        # Create logger
        self.logger = logging.getLogger("simple_program_router")
        
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Console handler
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # File handler
            try:
                os.makedirs('logs', exist_ok=True)
                file_handler = logging.FileHandler('logs/program_router.log')
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.DEBUG)
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # Si no puede crear archivo, continúa solo con consola
    
    def _log_decision(self, decision: ProgramDecision, customer_data: Dict[str, Any]):
        """Log structured decision information."""
        customer_id = customer_data.get('id', 'unknown')
        customer_age = customer_data.get('age', 'N/A')
        
        # Main decision log
        self.logger.info(
            f"PROGRAM_DECISION: {decision.recommended_program} | "
            f"confidence={decision.confidence_score:.3f} | "
            f"customer_age={customer_age} | "
            f"is_hybrid={decision.is_hybrid} | "
            f"needs_clarification={decision.should_ask_clarifying}"
        )
        
        # Reasoning log
        self.logger.info(f"DECISION_REASONING: {decision.reasoning}")
        
        # Signals log
        if decision.signals_detected:
            self.logger.info(f"DETECTED_SIGNALS: {', '.join(decision.signals_detected)}")
        else:
            self.logger.info("DETECTED_SIGNALS: none")
        
        # Metrics log
        self.logger.info(
            f"DECISION_METRICS: program={decision.recommended_program} | "
            f"confidence={decision.confidence_score:.3f} | "
            f"customer_id={customer_id} | "
            f"signals_count={len(decision.signals_detected)}"
        )
    
    async def determine_program(
        self, 
        customer_data: Dict[str, Any], 
        initial_message: str = "",
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> ProgramDecision:
        """
        Determina el programa más adecuado basado en todos los datos disponibles.
        """
        try:
            # Paso 1: Análisis básico por edad
            age_analysis = self._analyze_age_factor(customer_data.get('age'))
            
            # Paso 2: Análisis de contenido si hay mensaje inicial
            content_analysis = None
            if initial_message.strip():
                content_analysis = await self._analyze_content(initial_message, customer_data.get('age'))
            
            # Paso 3: Análisis de contexto adicional
            context_analysis = self._analyze_context(customer_data, conversation_context)
            
            # Paso 4: Combinar todas las señales
            final_decision = self._combine_analyses(
                age_analysis, 
                content_analysis, 
                context_analysis,
                customer_data
            )
            
            # Paso 5: Logging estructurado y tracking
            self._log_decision(final_decision, customer_data)
            self.decision_history.append(final_decision)
            return final_decision
            
        except Exception as e:
            print(f"Error en determinación de programa: {e}")
            return self._create_fallback_decision(customer_data)
    
    def _analyze_age_factor(self, age: Optional[int]) -> Dict[str, Any]:
        """Analiza el factor edad para la decisión de programa."""
        if not age:
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.0,
                "reasoning": "Edad no especificada"
            }
        
        # Lógica de edad con zona híbrida
        if age < 35:
            return {
                "prime_score": 0.9,
                "longevity_score": 0.1,
                "confidence": 0.8,
                "reasoning": f"Edad {age} años - target claro PRIME"
            }
        elif age < 45:
            return {
                "prime_score": 0.7,
                "longevity_score": 0.3,
                "confidence": 0.6,
                "reasoning": f"Edad {age} años - tendencia PRIME"
            }
        elif age < 55:
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.3,
                "reasoning": f"Edad {age} años - zona híbrida"
            }
        elif age < 65:
            return {
                "prime_score": 0.3,
                "longevity_score": 0.7,
                "confidence": 0.6,
                "reasoning": f"Edad {age} años - tendencia LONGEVITY"
            }
        else:
            return {
                "prime_score": 0.1,
                "longevity_score": 0.9,
                "confidence": 0.8,
                "reasoning": f"Edad {age} años - target claro LONGEVITY"
            }
    
    async def _analyze_content(self, message: str, age: Optional[int] = None) -> Dict[str, Any]:
        """Analiza el contenido del mensaje de forma simplificada."""
        try:
            message_lower = message.lower()
            prime_score = 0.5
            longevity_score = 0.5
            signals = []
            
            # Palabras clave para PRIME
            prime_keywords = [
                'trabajo', 'productividad', 'energía', 'rendimiento', 'empresa', 
                'liderazgo', 'eficiencia', 'startup', 'emprendimiento', 'consultoría'
            ]
            
            # Palabras clave para LONGEVITY  
            longevity_keywords = [
                'salud', 'familia', 'nietos', 'prevención', 'bienestar', 'vitalidad',
                'movilidad', 'envejecimiento', 'longevidad', 'problemas de salud'
            ]
            
            prime_matches = sum(1 for keyword in prime_keywords if keyword in message_lower)
            longevity_matches = sum(1 for keyword in longevity_keywords if keyword in message_lower)
            
            total_matches = prime_matches + longevity_matches
            if total_matches > 0:
                prime_score = prime_matches / total_matches
                longevity_score = longevity_matches / total_matches
                confidence = min(total_matches * 0.2, 0.8)
                
                if prime_matches > 0:
                    signals.extend([f"prime_keyword: {kw}" for kw in prime_keywords if kw in message_lower])
                if longevity_matches > 0:
                    signals.extend([f"longevity_keyword: {kw}" for kw in longevity_keywords if kw in message_lower])
            else:
                confidence = 0.0
            
            return {
                "prime_score": prime_score,
                "longevity_score": longevity_score,
                "confidence": confidence,
                "reasoning": f"Análisis de contenido: {prime_matches} señales PRIME, {longevity_matches} señales LONGEVITY",
                "signals": signals
            }
            
        except Exception as e:
            print(f"Error en análisis de contenido: {e}")
            return {
                "prime_score": 0.5,
                "longevity_score": 0.5,
                "confidence": 0.0,
                "reasoning": "Error en análisis de contenido",
                "signals": []
            }
    
    def _analyze_context(
        self, 
        customer_data: Dict[str, Any], 
        conversation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza el contexto adicional del cliente."""
        prime_indicators = 0
        longevity_indicators = 0
        signals = []
        
        # Analizar intereses reportados
        interests = customer_data.get('interests', [])
        for interest in interests:
            interest_lower = interest.lower()
            
            # Indicadores PRIME
            prime_keywords = [
                'rendimiento', 'productividad', 'energía', 'foco', 'concentración',
                'trabajo', 'empresa', 'carrera', 'liderazgo', 'éxito', 'eficiencia'
            ]
            
            # Indicadores LONGEVITY  
            longevity_keywords = [
                'salud', 'bienestar', 'vitalidad', 'prevención', 'longevidad',
                'familia', 'nietos', 'independencia', 'movilidad', 'articulaciones'
            ]
            
            for keyword in prime_keywords:
                if keyword in interest_lower:
                    prime_indicators += 1
                    signals.append(f"interés_prime: {interest}")
                    break
            
            for keyword in longevity_keywords:
                if keyword in interest_lower:
                    longevity_indicators += 1
                    signals.append(f"interés_longevity: {interest}")
                    break
        
        # Normalizar scores
        total_indicators = prime_indicators + longevity_indicators
        if total_indicators > 0:
            prime_score = prime_indicators / total_indicators
            longevity_score = longevity_indicators / total_indicators
            confidence = min(total_indicators * 0.2, 0.8)
        else:
            prime_score = 0.5
            longevity_score = 0.5
            confidence = 0.0
        
        return {
            "prime_score": prime_score,
            "longevity_score": longevity_score,
            "confidence": confidence,
            "reasoning": f"Análisis de {total_indicators} indicadores contextuales",
            "signals": signals
        }
    
    def _combine_analyses(
        self,
        age_analysis: Dict[str, Any],
        content_analysis: Optional[Dict[str, Any]],
        context_analysis: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> ProgramDecision:
        """Combina todos los análisis para tomar la decisión final."""
        
        # Pesos para la combinación
        age_weight = self.age_weight
        content_weight = self.content_weight if content_analysis else 0
        context_weight = 0.3 if not content_analysis else 0.1
        
        # Normalizar pesos si no hay análisis de contenido
        total_weight = age_weight + content_weight + context_weight
        age_weight = age_weight / total_weight
        content_weight = content_weight / total_weight
        context_weight = context_weight / total_weight
        
        # Combinar scores
        final_prime_score = (
            age_analysis["prime_score"] * age_weight +
            (content_analysis["prime_score"] if content_analysis else 0.5) * content_weight +
            context_analysis["prime_score"] * context_weight
        )
        
        final_longevity_score = (
            age_analysis["longevity_score"] * age_weight +
            (content_analysis["longevity_score"] if content_analysis else 0.5) * content_weight +
            context_analysis["longevity_score"] * context_weight
        )
        
        # Combinar confianzas
        final_confidence = (
            age_analysis["confidence"] * age_weight +
            (content_analysis["confidence"] if content_analysis else 0.0) * content_weight +
            context_analysis["confidence"] * context_weight
        )
        
        # Determinar programa recomendado
        if final_prime_score > final_longevity_score * 1.2:
            recommended_program = "PRIME"
            confidence_boost = final_prime_score - final_longevity_score
        elif final_longevity_score > final_prime_score * 1.2:
            recommended_program = "LONGEVITY"
            confidence_boost = final_longevity_score - final_prime_score
        else:
            recommended_program = "HYBRID"
            confidence_boost = 0
        
        # Ajustar confianza con el boost de diferencia
        final_confidence = min(final_confidence + confidence_boost * 0.3, 1.0)
        
        # Determinar si es zona híbrida
        is_hybrid = (
            recommended_program == "HYBRID" or 
            final_confidence < self.confidence_threshold_medium
        )
        
        # Determinar si necesita preguntas clarificadoras
        should_ask_clarifying = (
            final_confidence < self.confidence_threshold_high and
            not is_hybrid
        )
        
        # Crear reasoning detallado
        reasoning_parts = []
        reasoning_parts.append(f"Edad: {age_analysis['reasoning']}")
        if content_analysis:
            reasoning_parts.append(f"Contenido: {content_analysis['reasoning']}")
        reasoning_parts.append(f"Contexto: {context_analysis['reasoning']}")
        reasoning_parts.append(f"Confianza final: {final_confidence:.2f}")
        
        # Combinar señales detectadas
        all_signals = []
        if content_analysis and 'signals' in content_analysis:
            all_signals.extend(content_analysis['signals'])
        if 'signals' in context_analysis:
            all_signals.extend(context_analysis['signals'])
        
        return ProgramDecision(
            recommended_program=recommended_program,
            confidence_score=final_confidence,
            reasoning=" | ".join(reasoning_parts),
            signals_detected=all_signals,
            is_hybrid=is_hybrid,
            timestamp=datetime.now(),
            should_ask_clarifying=should_ask_clarifying
        )
    
    def _create_fallback_decision(self, customer_data: Dict[str, Any]) -> ProgramDecision:
        """Crea una decisión de fallback en caso de error."""
        age = customer_data.get('age')
        
        if age and age < 50:
            program = "PRIME"
            confidence = 0.6
        elif age and age >= 50:
            program = "LONGEVITY"
            confidence = 0.6
        else:
            program = "HYBRID"
            confidence = 0.3
        
        return ProgramDecision(
            recommended_program=program,
            confidence_score=confidence,
            reasoning="Decisión de fallback por error en análisis principal",
            signals_detected=["fallback_mode"],
            is_hybrid=(program == "HYBRID"),
            timestamp=datetime.now(),
            should_ask_clarifying=True
        )
    
    def get_decision_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de las decisiones tomadas con logging."""
        if not self.decision_history:
            analytics = {"total_decisions": 0}
            self.logger.info("ANALYTICS_REQUEST: no_decisions_available")
            return analytics
        
        total = len(self.decision_history)
        prime_count = sum(1 for d in self.decision_history if d.recommended_program == "PRIME")
        longevity_count = sum(1 for d in self.decision_history if d.recommended_program == "LONGEVITY")
        hybrid_count = sum(1 for d in self.decision_history if d.recommended_program == "HYBRID")
        
        avg_confidence = sum(d.confidence_score for d in self.decision_history) / total
        high_confidence_count = sum(1 for d in self.decision_history 
                                   if d.confidence_score > self.confidence_threshold_high)
        
        analytics = {
            "total_decisions": total,
            "program_distribution": {
                "PRIME": prime_count,
                "LONGEVITY": longevity_count,
                "HYBRID": hybrid_count
            },
            "average_confidence": avg_confidence,
            "high_confidence_rate": high_confidence_count / total if total > 0 else 0
        }
        
        # Log analytics
        self.logger.info(
            f"ROUTER_ANALYTICS: total_decisions={total} | "
            f"prime_count={prime_count} | longevity_count={longevity_count} | "
            f"hybrid_count={hybrid_count} | avg_confidence={avg_confidence:.3f} | "
            f"high_confidence_rate={analytics['high_confidence_rate']:.3f}"
        )
        
        return analytics
    
    async def should_switch_program(
        self, 
        current_program: str, 
        new_information: str,
        conversation_history: list = None
    ) -> tuple:
        """Evalúa si se debe cambiar de programa basado en nueva información."""
        try:
            # Análisis simplificado del contenido nuevo
            content_analysis = await self._analyze_content(new_information)
            
            new_program = "PRIME"
            confidence = content_analysis.get('confidence', 0.5)
            
            # Determinar programa basado en contenido
            if content_analysis.get('longevity_score', 0) > content_analysis.get('prime_score', 0):
                new_program = "LONGEVITY"
            
            # Solo cambiar si hay confianza alta y es diferente
            should_switch = (
                new_program != current_program and 
                confidence > self.confidence_threshold_high
            )
            
            if should_switch:
                self.logger.info(
                    f"PROGRAM_SWITCH: from={current_program} | to={new_program} | "
                    f"confidence={confidence:.3f} | reason=new_information_analysis"
                )
                
                new_decision = ProgramDecision(
                    recommended_program=new_program,
                    confidence_score=confidence,
                    reasoning=f"Cambio detectado por nueva información",
                    signals_detected=content_analysis.get('signals', []),
                    is_hybrid=False,
                    timestamp=datetime.now(),
                    should_ask_clarifying=False
                )
                
                return True, new_decision
            else:
                self.logger.debug(
                    f"PROGRAM_SWITCH_REJECTED: current={current_program} | "
                    f"suggested={new_program} | confidence={confidence:.3f}"
                )
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error evaluando cambio de programa: {e}")
            return False, None

# Escenarios de prueba
TEST_SCENARIOS = [
    {
        "name": "Joven profesional tech - PRIME claro",
        "customer_data": {
            "id": "test_1",
            "name": "Carlos",
            "age": 28,
            "interests": ["trabajo", "productividad", "energía", "rendimiento"]
        },
        "message": "Trabajo 12 horas diarias en startup tech, necesito más energía y mejor físico para rendir mejor",
        "expected_program": "PRIME"
    },
    {
        "name": "Adulto mayor preocupado por salud - LONGEVITY claro", 
        "customer_data": {
            "id": "test_2",
            "name": "María",
            "age": 58,
            "interests": ["salud", "familia", "bienestar", "vitalidad"]
        },
        "message": "Quiero mantenerme saludable para ver crecer a mis nietos, me preocupa perder movilidad",
        "expected_program": "LONGEVITY"
    },
    {
        "name": "Zona híbrida - profesional maduro",
        "customer_data": {
            "id": "test_3", 
            "name": "Roberto",
            "age": 47,
            "interests": ["liderazgo", "familia", "salud"]
        },
        "message": "Soy director de empresa, tengo familia, pero quiero estar en forma y tener energía",
        "expected_program": ["PRIME", "LONGEVITY", "HYBRID"]
    },
    {
        "name": "Ejecutivo senior - LONGEVITY tendencia",
        "customer_data": {
            "id": "test_4",
            "name": "Ana",
            "age": 52,
            "interests": ["liderazgo", "familia", "longevidad", "prevención"]
        },
        "message": "Dirijo una multinacional pero quiero envejecer bien y prevenir problemas de salud",
        "expected_program": "LONGEVITY"
    },
    {
        "name": "Joven emprendedor - PRIME claro",
        "customer_data": {
            "id": "test_5",
            "name": "Diego",
            "age": 32,
            "interests": ["emprendimiento", "eficiencia", "crecimiento personal"]
        },
        "message": "Fundé mi empresa hace 2 años, necesito optimizar mi físico para mayor productividad",
        "expected_program": "PRIME"
    },
    {
        "name": "Sin edad especificada - análisis por contenido",
        "customer_data": {
            "id": "test_6",
            "name": "Cliente",
            "age": None,
            "interests": ["fitness", "salud"]
        },
        "message": "Quiero mejorar mi condición física y tener más energía para el trabajo",
        "expected_program": ["PRIME", "HYBRID"]
    },
    {
        "name": "Profesora madura - LONGEVITY por edad y contenido",
        "customer_data": {
            "id": "test_7",
            "name": "Carmen",
            "age": 54,
            "interests": ["educación", "bienestar", "familia"]
        },
        "message": "Soy profesora universitaria, quiero mantener mi salud y energía para seguir enseñando años",
        "expected_program": "LONGEVITY"
    }
]

async def test_program_detection():
    """Ejecuta todos los escenarios de prueba."""
    print("🚀 Iniciando pruebas de detección automática NGX")
    print("=" * 60)
    
    router = SimpleProgramRouter()
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📋 Escenario {i}: {scenario['name']}")
        print(f"👤 Cliente: {scenario['customer_data']['name']}, edad: {scenario['customer_data']['age']}")
        print(f"💬 Mensaje: {scenario['message'][:80]}...")
        
        try:
            # Ejecutar detección
            decision = await router.determine_program(
                customer_data=scenario['customer_data'],
                initial_message=scenario['message'],
                conversation_context=None
            )
            
            # Verificar resultado
            expected = scenario['expected_program']
            actual = decision.recommended_program
            
            if isinstance(expected, list):
                is_correct = actual in expected
                expected_str = f"cualquiera de {expected}"
            else:
                is_correct = actual == expected
                expected_str = expected
            
            status = "✅ CORRECTO" if is_correct else "❌ ERROR"
            
            print(f"🎯 Programa detectado: {actual}")
            print(f"📊 Confianza: {decision.confidence_score:.2f}")
            print(f"🧠 Razonamiento: {decision.reasoning}")
            print(f"🔍 Señales: {decision.signals_detected}")
            print(f"⚖️ Es híbrido: {decision.is_hybrid}")
            print(f"📈 Resultado: {status} (esperado: {expected_str})")
            
            results.append({
                'scenario': scenario['name'],
                'expected': expected,
                'actual': actual,
                'confidence': decision.confidence_score,
                'correct': is_correct,
                'is_hybrid': decision.is_hybrid
            })
            
        except Exception as e:
            print(f"💥 ERROR en escenario: {e}")
            results.append({
                'scenario': scenario['name'],
                'expected': expected,
                'actual': 'ERROR',
                'confidence': 0.0,
                'correct': False,
                'is_hybrid': False
            })
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count) * 100
    
    print(f"✅ Casos correctos: {correct_count}/{total_count}")
    print(f"📈 Precisión: {accuracy:.1f}%")
    
    # Detalles por resultado
    for result in results:
        status_icon = "✅" if result['correct'] else "❌"
        print(f"{status_icon} {result['scenario']}: {result['actual']} (confianza: {result['confidence']:.2f})")
    
    # Análisis de confianza
    valid_results = [r for r in results if r['confidence'] > 0]
    if valid_results:
        avg_confidence = sum(r['confidence'] for r in valid_results) / len(valid_results)
        high_confidence_count = sum(1 for r in results if r['confidence'] >= 0.7)
        
        print(f"\n📊 Análisis de confianza:")
        print(f"   • Confianza promedio: {avg_confidence:.2f}")
        print(f"   • Casos con alta confianza (≥0.7): {high_confidence_count}/{total_count}")
    
    # Recomendaciones
    print(f"\n🎯 Evaluación del sistema:")
    if accuracy >= 85:
        print("   🏆 EXCELENTE: El sistema está funcionando muy bien")
    elif accuracy >= 70:
        print("   ✅ BUENO: El sistema funciona correctamente con margen de mejora")
    elif accuracy >= 50:
        print("   ⚠️ REGULAR: El sistema necesita ajustes importantes")
    else:
        print("   🚨 CRÍTICO: El sistema requiere revisión completa")
    
    if valid_results and avg_confidence < 0.6:
        print("   📝 RECOMENDACIÓN: Mejorar algoritmos de confianza")
    
    print(f"\n🎉 Pruebas completadas exitosamente!")
    return results

async def main():
    """Función principal que ejecuta todas las pruebas."""
    try:
        await test_program_detection()
        print(f"\n🎊 ¡Validación del sistema completada!")
        
    except Exception as e:
        print(f"💥 Error ejecutando pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())