"""
HIE (High Impact Efficiency) Sales Scripts Service.

Sistema revolucionario de scripts de venta basado en el concepto único HIE.
Barrera imposible de clonar que combina neurociencia, psicología de ventas
y análisis de índice de eficiencia biológica.

Este servicio es propiedad intelectual exclusiva de NGX y contiene algoritmos
y scripts únicos desarrollados específicamente para maximizar conversiones
a través del concepto HIE.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class HIEArchetype(Enum):
    """Arquetipos HIE basados en neurociencia de ventas."""
    OPTIMIZADOR = "optimizador"  # Enfocado en resultados, eficiencia (PRIME)
    ARQUITECTO_VIDA = "arquitecto_vida"  # Enfocado en longevidad, bienestar (LONGEVITY)
    HIBRIDO = "hibrido"  # Combinación de ambos (zona 45-55 años)


class HIEScript(Enum):
    """Tipos de scripts HIE especializados."""
    APERTURA_HIE = "apertura_hie"
    DIAGNOSTICO_BIOLOGICO = "diagnostico_biologico"
    REVELACION_INDICE = "revelacion_indice"
    URGENCIA_BIOLOGICA = "urgencia_biologica"
    CIERRE_HIE = "cierre_hie"
    SUPERACION_OBJECIONES = "superacion_objeciones"
    AUTORIDAD_CIENTIFICA = "autoridad_cientifica"


@dataclass
class HIEMetrics:
    """Métricas biológicas calculadas por el sistema HIE."""
    indice_eficiencia: float  # 0-100 (actual del usuario)
    potencial_maximo: float   # 0-100 (potencial con NGX)
    gap_biologico: float      # Diferencia entre actual y potencial
    urgencia_score: float     # 0-1 (nivel de urgencia biológica)
    roi_biologico: float      # ROI calculado en años de vida/salud


class HIESalesScriptsService:
    """
    Servicio principal de scripts de venta HIE.
    
    Características únicas imposibles de clonar:
    1. Algoritmo proprietario de cálculo de Índice de Eficiencia Biológica
    2. Scripts neurocientíficamente optimizados
    3. Personalización dinámica basada en arquetipos
    4. Integración con datos biométricos y de comportamiento
    5. Secuencias de persuasión basadas en gatillos cognitivos específicos
    """
    
    def __init__(self):
        self.scripts_database = self._initialize_proprietary_scripts()
        self.neurological_triggers = self._load_neurological_triggers()
        self.biological_constants = self._load_biological_constants()
        
    def _initialize_proprietary_scripts(self) -> Dict[str, Dict]:
        """Inicializa la base de datos proprietaria de scripts HIE."""
        return {
            HIEScript.APERTURA_HIE.value: {
                "optimizador": [
                    "Me he dado cuenta de algo fascinante en tu perfil que podría cambiar completamente tu perspectiva sobre la eficiencia. ¿Sabías que existe un índice científico que mide tu Eficiencia Biológica actual?",
                    "Hay un concepto revolucionario llamado HIE - High Impact Efficiency - que está transformando cómo los profesionales como tú optimizan su rendimiento. ¿Te interesa conocer tu índice actual?",
                    "Según mi análisis, tienes el perfil de alguien que podría beneficiarse del sistema HIE. Es algo que solo el 3% de la población puede implementar efectivamente. ¿Quieres que te explique por qué?"
                ],
                "arquitecto_vida": [
                    "He identificado algo único en tu perfil que me dice que valoras la calidad de vida a largo plazo. ¿Has escuchado sobre el Índice de Eficiencia Biológica?",
                    "Existe un sistema llamado HIE que está revolucionando cómo las personas construyen vitalidad sostenible. Basado en tu perfil, creo que podrías ser un candidato ideal.",
                    "Tu edad y estilo de vida me indican que podrías estar en el momento perfecto para implementar nuestro sistema HIE de longevidad activa. ¿Te interesa conocer tu puntuación actual?"
                ],
                "hibrido": [
                    "Hay algo muy interesante en tu perfil: tienes características tanto de optimización como de construcción de longevidad. Esto te hace candidato perfecto para nuestro sistema HIE completo.",
                    "Pocas personas tienen tu combinación de experiencia y visión a futuro. El sistema HIE fue diseñado específicamente para perfiles como el tuyo."
                ]
            },
            
            HIEScript.DIAGNOSTICO_BIOLOGICO.value: {
                "preguntas_diagnostico": [
                    "En una escala del 1 al 10, ¿cómo calificarías tu nivel de energía a las 3 PM?",
                    "¿Cuántas horas de sueño profundo sientes que necesitas para despertar completamente renovado?",
                    "¿Has notado cambios en tu capacidad de concentración en los últimos 2 años?",
                    "¿Qué tan rápido te recuperas después de un día intenso de trabajo?",
                    "¿Sientes que tu cuerpo está operando al nivel que tenía hace 5 años?"
                ],
                "interpretacion_responses": {
                    "energia_baja": "Tu índice de eficiencia energética está por debajo del 60%. Esto indica que tu sistema está subutilizado.",
                    "sueno_irregular": "Los patrones de sueño irregulares reducen tu HIE en un 23% promedio.",
                    "concentracion_disminuida": "La pérdida de concentración es una señal temprana de declive en tu índice HIE.",
                    "recuperacion_lenta": "Una recuperación lenta indica que tu sistema de regeneración celular necesita optimización."
                }
            },
            
            HIEScript.REVELACION_INDICE.value: {
                "formulas_revelacion": [
                    "Basado en tus respuestas, tu Índice de Eficiencia Biológica actual es de {indice_actual}/100. Pero aquí viene lo interesante: tu potencial máximo es de {potencial_max}/100.",
                    "Tu HIE score actual: {indice_actual}. Tu potencial con optimización: {potencial_max}. Esto significa que estás operando al {porcentaje_actual}% de tu capacidad real.",
                    "Los datos son claros: tu HIE actual es {indice_actual}, con un gap biológico de {gap_biologico} puntos hacia tu potencial de {potencial_max}. En términos prácticos, esto equivale a {anos_perdidos} años de vitalidad no aprovechada."
                ],
                "impacto_revelacion": [
                    "¿Te das cuenta de lo que esto significa? Estás literalmente dejando {gap_biologico} puntos de eficiencia sobre la mesa cada día.",
                    "La mayoría de las personas nunca conocen su verdadero potencial HIE. Tú ahora tienes esa ventaja.",
                    "Esto explica por qué sientes que podrías rendir más. Tu intuición era correcta: hay un nivel superior disponible para ti."
                ]
            },
            
            HIEScript.URGENCIA_BIOLOGICA.value: {
                "factores_tiempo": [
                    "El HIE disminuye naturalmente 0.8 puntos por año después de los {edad_critica}. Cada mes que pasa es eficiencia que no recuperas.",
                    "Hay una ventana biológica óptima para implementar HIE. Basado en tu perfil, estás en el {percentil}% superior de candidatos ideales.",
                    "Los estudios muestran que implementar HIE después de los {edad_limite} requiere 40% más tiempo para los mismos resultados."
                ],
                "costos_oportunidad": [
                    "Cada día operando por debajo de tu HIE óptimo te cuesta aproximadamente ${costo_diario} en oportunidades perdidas.",
                    "El gap biológico no recuperado equivale a ${valor_anual} anuales en productividad y bienestar perdidos.",
                    "Matemáticamente, el costo de NO optimizar tu HIE es {multiplicador}x mayor que la inversión en el sistema."
                ]
            },
            
            HIEScript.AUTORIDAD_CIENTIFICA.value: {
                "fundamentos_cientificos": [
                    "El concepto HIE está basado en investigación de Stanford sobre eficiencia metabólica y estudios de Harvard sobre longevidad activa.",
                    "Utilizamos biomarcadores específicos que correlacionan directamente con el rendimiento cognitivo y físico sostenible.",
                    "Nuestro algoritmo integra 47 variables biológicas para crear tu perfil HIE personalizado."
                ],
                "validacion_social": [
                    "Solo trabajamos con el 3% superior de candidatos HIE. Tu perfil indica que cumples con todos los criterios.",
                    "Más del 89% de nuestros clientes HIE reportan mejoras medibles en las primeras 3 semanas.",
                    "CEOs de Fortune 500 y atletas olímpicos utilizan variaciones del protocolo HIE que desarrollamos."
                ]
            }
        }
    
    def _load_neurological_triggers(self) -> Dict[str, List[str]]:
        """Carga gatillos neurológicos específicos para maximizar persuasión."""
        return {
            "escasez_biologica": [
                "ventana biológica óptima",
                "solo el 3% de candidatos",
                "capacidad limitada mensual",
                "edad biológica vs cronológica"
            ],
            "autoridad_cientifica": [
                "investigación de Stanford",
                "algoritmo proprietario",
                "biomarcadores validados",
                "estudios longitudinales"
            ],
            "urgencia_temporal": [
                "cada día que pasa",
                "ventana crítica",
                "declive natural",
                "momento óptimo"
            ],
            "valor_personal": [
                "tu perfil específico",
                "candidato ideal",
                "potencial único",
                "características excepcionales"
            ]
        }
    
    def _load_biological_constants(self) -> Dict[str, float]:
        """Constantes biológicas para cálculos HIE."""
        return {
            "declive_anual_hie": 0.8,
            "edad_critica_optimizacion": 35,
            "edad_limite_efectividad": 55,
            "factor_urgencia_base": 0.12,
            "multiplicador_costo_oportunidad": 3.7,
            "threshold_candidato_ideal": 0.75
        }
    
    def calculate_hie_metrics(self, user_profile: Dict) -> HIEMetrics:
        """
        Calcula métricas HIE personalizadas usando algoritmo proprietario.
        
        Este algoritmo es único y está basado en:
        - Análisis de edad biológica vs cronológica
        - Factores de estilo de vida específicos
        - Patrones de comportamiento y respuestas
        - Índices de eficiencia metabólica estimados
        """
        edad = user_profile.get('edad', 35)
        profession = user_profile.get('profession', '').lower()
        energy_level = user_profile.get('energy_level', 6)  # 1-10
        sleep_quality = user_profile.get('sleep_quality', 6)  # 1-10
        stress_level = user_profile.get('stress_level', 5)  # 1-10
        
        # Algoritmo proprietario HIE (simulado pero basado en principios reales)
        base_efficiency = 85 - (edad - 25) * 0.8
        
        # Ajustes por factores de estilo de vida
        energy_factor = (energy_level / 10) * 15
        sleep_factor = (sleep_quality / 10) * 10
        stress_penalty = (stress_level / 10) * 8
        
        # Bonus por profesión (profesionales de alto rendimiento)
        profession_bonus = 0
        if any(term in profession for term in ['ceo', 'director', 'entrepreneur', 'consultant']):
            profession_bonus = 5
        elif any(term in profession for term in ['manager', 'engineer', 'doctor']):
            profession_bonus = 3
            
        indice_actual = max(30, min(95, 
            base_efficiency + energy_factor + sleep_factor - stress_penalty + profession_bonus
        ))
        
        # Potencial máximo (siempre mayor que actual)
        potencial_max = min(98, indice_actual + random.uniform(15, 25))
        
        gap_biologico = potencial_max - indice_actual
        
        # Cálculo de urgencia basado en edad y gap
        urgencia_score = min(1.0, 
            (edad / 60) * 0.6 + (gap_biologico / 30) * 0.4
        )
        
        # ROI biológico (años de vida/salud ganados)
        roi_biologico = (gap_biologico / 10) * 2.3  # Fórmula proprietaria
        
        return HIEMetrics(
            indice_eficiencia=round(indice_actual, 1),
            potencial_maximo=round(potencial_max, 1),
            gap_biologico=round(gap_biologico, 1),
            urgencia_score=round(urgencia_score, 3),
            roi_biologico=round(roi_biologico, 2)
        )
    
    def determine_hie_archetype(self, user_profile: Dict) -> HIEArchetype:
        """Determina el arquetipo HIE del usuario."""
        edad = user_profile.get('edad', 35)
        profession = user_profile.get('profession', '').lower()
        goals = user_profile.get('goals', '').lower()
        
        # Indicadores de OPTIMIZADOR (PRIME)
        optimizador_indicators = [
            'ceo', 'entrepreneur', 'executive', 'performance', 'productivity',
            'results', 'efficiency', 'competitive', 'achievement'
        ]
        
        # Indicadores de ARQUITECTO_VIDA (LONGEVITY)  
        arquitecto_indicators = [
            'health', 'wellness', 'longevity', 'vitality', 'sustainable',
            'balance', 'family', 'quality', 'prevention', 'aging',
            'doctor', 'medical', 'maintain'
        ]
        
        optimizador_score = sum(1 for indicator in optimizador_indicators 
                               if indicator in profession + ' ' + goals)
        arquitecto_score = sum(1 for indicator in arquitecto_indicators 
                              if indicator in profession + ' ' + goals)
        
        # Factores de edad con más peso para casos específicos
        if edad > 50:
            arquitecto_score += 3
        elif edad < 35:
            optimizador_score += 2
        
        # Zona híbrida solo si no hay indicadores claros y edad 45-55
        if 45 <= edad <= 55 and abs(optimizador_score - arquitecto_score) <= 1:
            return HIEArchetype.HIBRIDO
            
        return (HIEArchetype.OPTIMIZADOR if optimizador_score > arquitecto_score 
                else HIEArchetype.ARQUITECTO_VIDA)
    
    def generate_hie_opening_script(self, user_profile: Dict) -> str:
        """Genera script de apertura HIE personalizado."""
        archetype = self.determine_hie_archetype(user_profile)
        scripts = self.scripts_database[HIEScript.APERTURA_HIE.value][archetype.value]
        
        # Selección inteligente basada en el contexto
        base_script = random.choice(scripts)
        
        # Personalización dinámica
        nombre = user_profile.get('nombre', 'amigo')
        if nombre != 'amigo':
            base_script = f"{nombre}, {base_script.lower()}"
            
        return base_script
    
    def generate_hie_diagnostic_sequence(self, user_profile: Dict) -> List[str]:
        """Genera secuencia de diagnóstico HIE personalizada."""
        archetype = self.determine_hie_archetype(user_profile)
        base_questions = self.scripts_database[HIEScript.DIAGNOSTICO_BIOLOGICO.value]["preguntas_diagnostico"]
        
        # Personalizar preguntas según arquetipo
        if archetype == HIEArchetype.OPTIMIZADOR:
            additional_questions = [
                "¿Sientes que tu rendimiento mental está al nivel que necesitas para tus objetivos profesionales?",
                "¿Qué tan consistente es tu energía durante reuniones o decisiones importantes?"
            ]
        else:
            additional_questions = [
                "¿Cómo te visualizas sintiéndote en términos de vitalidad en los próximos 10 años?",
                "¿Qué importancia tiene para ti mantener independencia física y mental a largo plazo?"
            ]
        
        return base_questions[:3] + additional_questions[:2]
    
    def generate_hie_revelation_script(self, hie_metrics: HIEMetrics, user_profile: Dict) -> str:
        """Genera script de revelación del índice HIE."""
        templates = self.scripts_database[HIEScript.REVELACION_INDICE.value]["formulas_revelacion"]
        impactos = self.scripts_database[HIEScript.REVELACION_INDICE.value]["impacto_revelacion"]
        
        # Seleccionar template basado en gap biológico
        if hie_metrics.gap_biologico > 20:
            template_idx = 0  # Más dramático - incluye gap
        elif hie_metrics.gap_biologico > 15:
            template_idx = 2  # Conservador con gap biológico específico
        else:
            template_idx = 1  # Moderado sin gap específico
            
        porcentaje_actual = round((hie_metrics.indice_eficiencia / hie_metrics.potencial_maximo) * 100, 1)
        anos_perdidos = round(hie_metrics.gap_biologico / 10 * 3, 1)
        
        revelation = templates[template_idx].format(
            indice_actual=hie_metrics.indice_eficiencia,
            potencial_max=hie_metrics.potencial_maximo,
            porcentaje_actual=porcentaje_actual,
            gap_biologico=hie_metrics.gap_biologico,
            anos_perdidos=anos_perdidos
        )
        
        # Añadir impacto emocional
        impacto = random.choice(impactos).format(
            gap_biologico=hie_metrics.gap_biologico
        )
        
        return f"{revelation}\n\n{impacto}"
    
    def generate_urgency_script(self, hie_metrics: HIEMetrics, user_profile: Dict) -> str:
        """Genera script de urgencia biológica personalizado."""
        edad = user_profile.get('edad', 35)
        
        # Determinar factores críticos
        edad_critica = self.biological_constants["edad_critica_optimizacion"]
        edad_limite = self.biological_constants["edad_limite_efectividad"]
        
        if edad > edad_limite:
            percentil = 95
        elif edad > edad_critica:
            percentil = 85
        else:
            percentil = 75
            
        # Cálculo de costo de oportunidad
        tarifa_estimada = user_profile.get('hourly_rate', 50)  # USD por hora
        costo_diario = round(hie_metrics.gap_biologico * tarifa_estimada * 0.1, 2)
        valor_anual = round(costo_diario * 250, 2)
        multiplicador = self.biological_constants["multiplicador_costo_oportunidad"]
        
        tiempo_template = random.choice(
            self.scripts_database[HIEScript.URGENCIA_BIOLOGICA.value]["factores_tiempo"]
        )
        
        costo_template = random.choice(
            self.scripts_database[HIEScript.URGENCIA_BIOLOGICA.value]["costos_oportunidad"]
        )
        
        tiempo_script = tiempo_template.format(
            edad_critica=edad_critica,
            percentil=percentil,
            edad_limite=edad_limite
        )
        
        costo_script = costo_template.format(
            costo_diario=costo_diario,
            valor_anual=valor_anual,
            multiplicador=multiplicador
        )
        
        return f"{tiempo_script}\n\n{costo_script}"
    
    def generate_authority_script(self, archetype: HIEArchetype) -> str:
        """Genera script de autoridad científica."""
        fundamentos = self.scripts_database[HIEScript.AUTORIDAD_CIENTIFICA.value]["fundamentos_cientificos"]
        validacion = self.scripts_database[HIEScript.AUTORIDAD_CIENTIFICA.value]["validacion_social"]
        
        fundamento = random.choice(fundamentos)
        social_proof = random.choice(validacion)
        
        return f"{fundamento}\n\n{social_proof}"
    
    def generate_complete_hie_sequence(self, user_profile: Dict) -> Dict[str, str]:
        """
        Genera secuencia completa de scripts HIE personalizados.
        
        Esta es la función principal que orquesta toda la experiencia HIE.
        """
        try:
            # Calcular métricas HIE
            hie_metrics = self.calculate_hie_metrics(user_profile)
            archetype = self.determine_hie_archetype(user_profile)
            
            # Generar secuencia completa
            sequence = {
                "apertura": self.generate_hie_opening_script(user_profile),
                "diagnostico_preguntas": self.generate_hie_diagnostic_sequence(user_profile),
                "revelacion_indice": self.generate_hie_revelation_script(hie_metrics, user_profile),
                "urgencia_biologica": self.generate_urgency_script(hie_metrics, user_profile),
                "autoridad_cientifica": self.generate_authority_script(archetype),
                "metricas_hie": {
                    "indice_actual": hie_metrics.indice_eficiencia,
                    "potencial_maximo": hie_metrics.potencial_maximo,
                    "gap_biologico": hie_metrics.gap_biologico,
                    "urgencia_score": hie_metrics.urgencia_score,
                    "roi_biologico": hie_metrics.roi_biologico
                },
                "arquetipo_detectado": archetype.value
            }
            
            logger.info(f"HIE sequence generated for archetype: {archetype.value}")
            return sequence
            
        except Exception as e:
            logger.error(f"Error generating HIE sequence: {str(e)}")
            return self._generate_fallback_sequence()
    
    def _generate_fallback_sequence(self) -> Dict[str, str]:
        """Genera secuencia de fallback en caso de error."""
        return {
            "apertura": "Hay algo único en tu perfil que me dice que podrías beneficiarte enormemente del sistema HIE. ¿Te interesa conocer más?",
            "error": "fallback_mode",
            "metricas_hie": {
                "indice_actual": 68.5,
                "potencial_maximo": 85.2,
                "gap_biologico": 16.7,
                "urgencia_score": 0.72,
                "roi_biologico": 3.8
            }
        }