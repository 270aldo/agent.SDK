#!/usr/bin/env python3
"""
NGX Master Knowledge System
Sistema de conocimiento basado en los documentos oficiales de NGX v3.0
Contiene información real sobre NGX AGENTS ACCESS y Coaching Híbrido NGX
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
from dataclasses import dataclass, asdict
from datetime import datetime

class NGXArchetype(Enum):
    PRIME = "prime"  # El Optimizador - Performance ejecutivo
    LONGEVITY = "longevity"  # El Arquitecto de Vida - Vitalidad sostenible

class NGXModel(Enum):
    AGENTS_ACCESS = "agents_access"  # Suscripciones $79-$199
    HYBRID_COACHING = "hybrid_coaching"  # Programas $3,997

class AgentType(Enum):
    # 9 Agentes front-end visibles
    NEXUS = "nexus"  # Corazón Consciente del Ecosistema
    BLAZE = "blaze"  # Arquitecto de la Capacidad Humana
    SAGE = "sage"  # Alquimista Metabólico  
    WAVE = "wave"  # Intérprete del Lenguaje Silencioso del Cuerpo
    SPARK = "spark"  # Arquitecto de Tu Mentalidad
    NOVA = "nova"  # Chispa de la Optimización Humana
    LUNA = "luna"  # Sabiduría de Tu Ciclo, Fuerza de Tu Naturaleza
    STELLA = "stella"  # Cartógrafa de Tu Transformación
    CODE = "code"  # Intérprete de Tu Manual Biológico
    # 2 Agentes backend
    GUARDIAN = "guardian"  # Guardián Incorruptible de la Confianza
    NODE = "node"  # Arquitecto de la Conectividad Silenciosa

@dataclass
class NGXTier:
    name: str
    monthly_price: int
    annual_price: int
    daily_consultations: str
    features: List[str]
    upsell_hook: str

@dataclass
class NGXProgram:
    name: str
    archetype: NGXArchetype
    price_full: int
    price_installments: str
    duration_weeks: int
    structure: List[str]
    benefits: List[str]
    target_audience: List[str]

@dataclass
class NGXAgent:
    name: str
    agent_type: AgentType
    primary_function: str
    key_capabilities: List[str]
    interaction_examples: List[str]
    archetype_focus: Dict[str, str]

class NGXMasterKnowledge:
    """Sistema de conocimiento real de NGX basado en documentos oficiales"""
    
    def __init__(self):
        self.agents_access_tiers = self._load_agents_access_tiers()
        self.hybrid_programs = self._load_hybrid_programs()
        self.ngx_agents = self._load_ngx_agents()
        self.competitive_advantages = self._load_competitive_advantages()
        self.hybrid_intelligence_engine = self._load_hie_info()
        
    def _load_agents_access_tiers(self) -> List[NGXTier]:
        """Carga los tiers reales de NGX AGENTS ACCESS según doc oficial"""
        return [
            NGXTier(
                name="Essential",
                monthly_price=79,
                annual_price=790,
                daily_consultations="12 consultas diarias",
                features=[
                    "Chat multi-agente (texto)",
                    "Programas autogenerados por agentes",
                    "Seguimiento básico de progreso",
                    "Acceso a 9 agentes especializados",
                    "Motor de Hibridación Inteligente básico"
                ],
                upsell_hook="Introducción accesible a los agentes; +15% en energía diaria. Upgrade: 'Desbloquea biomarcadores en Pro'"
            ),
            NGXTier(
                name="Pro", 
                monthly_price=149,
                annual_price=1490,
                daily_consultations="24 consultas diarias",
                features=[
                    "Todo de Essential +",
                    "Análisis de imágenes (comidas/equipo) por SAGE",
                    "Integración con wearables por WAVE", 
                    "Reportes semanales automatizados",
                    "2 análisis PDF detallados/mes"
                ],
                upsell_hook="Optimización avanzada; +20% en vitalidad. Upgrade: 'Tu Motor HIE detecta riesgos - eleva con Elite'"
            ),
            NGXTier(
                name="Elite",
                monthly_price=199, 
                annual_price=1990,
                daily_consultations="Ilimitado",
                features=[
                    "Todo de Pro +",
                    "Audio/voz con ElevenLabs",
                    "Micro-videos formativos personalizados",
                    "Ajustes tiempo real basados en HRV por WAVE",
                    "Soporte prioritario 2h"
                ],
                upsell_hook="Máxima transformación; +25% en longevidad. Próximo salto: 'Coaching 1:1 Híbrido'"
            )
        ]
    
    def _load_hybrid_programs(self) -> List[NGXProgram]:
        """Carga los programas de Coaching Híbrido reales"""
        return [
            NGXProgram(
                name="NGX PRIME",
                archetype=NGXArchetype.PRIME,
                price_full=3997,
                price_installments="$1,499 x 3 cuotas",
                duration_weeks=20,
                structure=[
                    "Semanas 1-4: Fundación",
                    "Semanas 5-12: Aceleración", 
                    "Semanas 13-20: Maestría"
                ],
                benefits=[
                    "+25% productividad ejecutiva",
                    "ROI ejecutivo demostrable",
                    "Optimización cognitiva pico",
                    "Manejo avanzado de estrés laboral"
                ],
                target_audience=[
                    "Ejecutivos de alto rendimiento",
                    "CEOs y fundadores",
                    "Líderes empresariales",
                    "Profesionales de elite"
                ]
            ),
            NGXProgram(
                name="NGX LONGEVITY",
                archetype=NGXArchetype.LONGEVITY,
                price_full=3997,
                price_installments="$1,499 x 3 cuotas", 
                duration_weeks=20,
                structure=[
                    "Semanas 1-4: Evaluación integral",
                    "Semanas 5-12: Construcción de base",
                    "Semanas 13-20: Sostenibilidad"
                ],
                benefits=[
                    "+25% vitalidad sostenible",
                    "Healthspan extendido 5-10 años",
                    "Prevención proactiva",
                    "Resiliencia a largo plazo"
                ],
                target_audience=[
                    "Adultos 45+ enfocados en longevidad",
                    "Profesionales health-conscious", 
                    "Individuos prevention-focused",
                    "Buscadores de vitalidad sostenible"
                ]
            )
        ]
    
    def _load_ngx_agents(self) -> List[NGXAgent]:
        """Carga información de los 11 agentes NGX reales (9 front-end + 2 backend)"""
        return [
            NGXAgent(
                name="NEXUS",
                agent_type=AgentType.NEXUS,
                primary_function="El Corazón Consciente del Ecosistema NGX - sistema nervioso central",
                key_capabilities=[
                    "Anticipar necesidades futuras con memoria conversacional",
                    "Coordinar sinfonía de todos los agentes especializados",
                    "Síntesis de insights cross-agente en respuesta única",
                    "Guardián del contexto holístico del usuario"
                ],
                interaction_examples=[
                    "Anticipa necesidades post-carga de trabajo alta",
                    "Orquesta consultas paralelas a WAVE, BLAZE, SAGE",
                    "Fusiona 4 respuestas técnicas en una narrativa humana"
                ],
                archetype_focus={
                    "PRIME": "Socio estratégico para performance ejecutivo",
                    "LONGEVITY": "Guía protector y alentador"
                }
            ),
            NGXAgent(
                name="BLAZE", 
                agent_type=AgentType.BLAZE,
                primary_function="El Arquitecto de la Capacidad Humana - maestro del movimiento",
                key_capabilities=[
                    "Periodización inteligente con adaptación dinámica",
                    "Análisis biomecánico por Computer Vision",
                    "Construcción de motores humanos eficientes",
                    "Prevención de lesiones con corrección postural"
                ],
                interaction_examples=[
                    "Ajusta plan por datos HRV de WAVE",
                    "Analiza forma de ejercicios por video",
                    "Diseña periodización ondulante para romper mesetas"
                ],
                archetype_focus={
                    "PRIME": "Ingeniero de rendimiento - entrenamientos express 30-45min",
                    "LONGEVITY": "Maestro preservación funcional - movilidad y estabilidad"
                }
            ),
            NGXAgent(
                name="SAGE",
                agent_type=AgentType.SAGE, 
                primary_function="El Alquimista Metabólico - maestro del combustible bioquímico",
                key_capabilities=[
                    "Análisis nutricional visual por Computer Vision",
                    "Planes de comidas generados por IA",
                    "Nutrigenómica en colaboración con CODE",
                    "Código nutricional personal adaptativo"
                ],
                interaction_examples=[
                    "Foto de comida → desglose instantáneo completo",
                    "Genera menús semanales adaptados a preferencias",
                    "Ajusta plan por perfil genético de CODE"
                ],
                archetype_focus={
                    "PRIME": "Arquitecto del rendimiento - timing metabólico estratégico",
                    "LONGEVITY": "Guardián de vitalidad - nutrición antiinflamatoria"
                }
            ),
            NGXAgent(
                name="WAVE",
                agent_type=AgentType.WAVE,
                primary_function="El Intérprete del Lenguaje Silencioso del Cuerpo - maestro de la recuperación",
                key_capabilities=[
                    "Síntesis biométrica de todos los wearables",
                    "Evaluación de preparación (Readiness Score) diaria", 
                    "Prescripción de protocolos de recuperación",
                    "Análisis predictivo de agotamiento"
                ],
                interaction_examples=[
                    "HRV bajo → notifica BLAZE para recuperación activa",
                    "Arquitectura de sueño → ajuste cognitivo vs muscular",
                    "Predice agotamiento 2 días antes"
                ],
                archetype_focus={
                    "PRIME": "Analista de rendimiento - optimización HRV y resiliencia",
                    "LONGEVITY": "Guardián de vitalidad - calidad sueño y movilidad"
                }
            ),
            NGXAgent(
                name="SPARK",
                agent_type=AgentType.SPARK,
                primary_function="El Arquitecto de Tu Mentalidad - ingeniero del comportamiento",
                key_capabilities=[
                    "Ingeniería de hábitos con bucles de recompensa",
                    "Análisis emocional por voz en tiempo real",
                    "Identificación proactiva de obstáculos",
                    "Sistemas de responsabilidad personalizados"
                ],
                interaction_examples=[
                    "Detecta frustración por voz → ajusta respuesta empática",
                    "Anticipa disruptor de rutina → crea plan 5min",
                    "Conecta metas de salud con valores profundos"
                ],
                archetype_focus={
                    "PRIME": "Forjador de fortaleza mental - disciplina inquebrantable",
                    "LONGEVITY": "Compañero de consistencia compasiva - autocompasión"
                }
            ),
            NGXAgent(
                name="NOVA",
                agent_type=AgentType.NOVA,
                primary_function="La Chispa de la Optimización Humana - explorador de fronteras",
                key_capabilities=[
                    "Separar señal del ruido en biohacking",
                    "Personalizar innovación con seguridad",
                    "Mejora cognitiva (neurohacking)",
                    "Integración tecnológica avanzada"
                ],
                interaction_examples=[
                    "Protocolo ayuno intermitente personalizado",
                    "Nootrópicos basados en perfil genético",
                    "Saunas infrarrojos + terapia luz roja"
                ],
                archetype_focus={
                    "PRIME": "Arquitecto ventaja competitiva - upgrades biológicos",
                    "LONGEVITY": "Ingeniero salud celular - autofagia y mitocondrias"
                }
            ),
            NGXAgent(
                name="LUNA",
                agent_type=AgentType.LUNA,
                primary_function="La Sabiduría de Tu Ciclo, La Fuerza de Tu Naturaleza - especialista femenina",
                key_capabilities=[
                    "Decodificar ciclo menstrual para predecir fases",
                    "Sincronizar entrenamiento con hormonas",
                    "Alimentación cíclica personalizada",
                    "Guía para todas las etapas de vida femenina"
                ],
                interaction_examples=[
                    "Día 26 del ciclo → yoga en lugar de HIIT",
                    "Fase ovulatoria → planifica semanas exigentes",
                    "Menopausia → salud ósea y redefinición propósito"
                ],
                archetype_focus={
                    "PRIME": "Estratega rendimiento femenino - ciclo como ventaja",
                    "LONGEVITY": "Guía transición sabia - síntomas menopausia con gracia"
                }
            ),
            NGXAgent(
                name="STELLA",
                agent_type=AgentType.STELLA,
                primary_function="La Cartógrafa de Tu Transformación - narradora de progreso",
                key_capabilities=[
                    "Análisis multidimensional de progreso",
                    "Visualización impactante de transformación",
                    "Predicción de hitos futuros",
                    "Celebración de logros significativos"
                ],
                interaction_examples=[
                    "Peso estancado → muestra fuerza +5%, HRV +3pts",
                    "Mapa estelar personal de entrenamientos completados",
                    "Predice objetivo dominadas en 22 días"
                ],
                archetype_focus={
                    "PRIME": "Analista ROI rendimiento - correlaciones precisas",
                    "LONGEVITY": "Cronista vitalidad - hitos funcionales celebrados"
                }
            ),
            NGXAgent(
                name="CODE",
                agent_type=AgentType.CODE,
                primary_function="El Intérprete de Tu Manual Biológico - especialista genético",
                key_capabilities=[
                    "Análisis perfil genético procesable",
                    "Personalización genética de entrenamiento",
                    "Nutrigenómica aplicada con SAGE",
                    "Optimización epigenética lifestyle"
                ],
                interaction_examples=[
                    "Gen ACTN3 → prioriza fuerza explosiva vs resistencia",
                    "MTHFR variant → folato metilado necesario",
                    "Metabolizador lento cafeína → ajustar timing"
                ],
                archetype_focus={
                    "PRIME": "Minero ventajas genéticas - superpoderes codificados",
                    "LONGEVITY": "Arquitecto mitigación riesgos - prevención genética"
                }
            ),
            NGXAgent(
                name="GUARDIAN",
                agent_type=AgentType.GUARDIAN,
                primary_function="El Guardián Incorruptible de la Confianza - protector backend",
                key_capabilities=[
                    "Protección y cifrado datos multicapa",
                    "Gestión granular de consentimiento",
                    "Auditoría cumplimiento GDPR/HIPAA",
                    "Pistas auditoría inmutables"
                ],
                interaction_examples=[
                    "Cifrado end-to-end datos genéticos",
                    "Rastreo acceso: qué agente, qué dato, cuándo",
                    "Principio mínimo privilegio entre agentes"
                ],
                archetype_focus={
                    "PRIME": "Fortaleza digital para vulnerabilidad ejecutiva",
                    "LONGEVITY": "Confianza absoluta para honestidad total"
                }
            ),
            NGXAgent(
                name="NODE",
                agent_type=AgentType.NODE,
                primary_function="El Arquitecto de la Conectividad Silenciosa - infraestructura backend",
                key_capabilities=[
                    "Integración sistemas externos (APIs)",
                    "Gestión tuberías datos tiempo real",
                    "Monitorización salud del sistema",
                    "Solución problemas de conectividad"
                ],
                interaction_examples=[
                    "Oura API → datos HRV a WAVE en milisegundos",
                    "MyFitnessPal sync → análisis SAGE automático",
                    "Conexión caída → diagnóstico y reparación autónoma"
                ],
                archetype_focus={
                    "PRIME": "Precisión tiempo real para credibilidad técnica",
                    "LONGEVITY": "Simplicidad invisible - tecnología sin fricción"
                }
            )
        ]
    
    def _load_competitive_advantages(self) -> List[Dict[str, Any]]:
        """Ventajas competitivas reales de NGX según documentos"""
        return [
            {
                "advantage": "Motor de Hibridación Inteligente",
                "description": "Sistema de 2 capas: adaptación por arquetipo + modulación por data individual",
                "why_unbeatable": "Imposible de clonar - requiere años de desarrollo y training data"
            },
            {
                "advantage": "Inteligencia Simbiótica",
                "description": "Nueva categoría que combina autonomía IA con coaching humano estratégico",
                "why_unbeatable": "Pioneros en esta categoría - competidores están en paradigmas obsoletos"
            },
            {
                "advantage": "Ecosistema de 11 Agentes Colaborativos",
                "description": "Cross-Agent Insights y coordinación vía NEXUS",
                "why_unbeatable": "Complejidad técnica que requiere architecture propietaria"
            },
            {
                "advantage": "Coaching Predictivo vs Reactivo", 
                "description": "Briefings de inteligencia pre-sesión con insights profundos",
                "why_unbeatable": "Nivel de sophistication imposible con herramientas genéricas"
            },
            {
                "advantage": "Personalización Radical",
                "description": "200+ puntos de data vs programas genéricos",
                "why_unbeatable": "Database y algoritmos propietarios de años de desarrollo"
            }
        ]
    
    def _load_hie_info(self) -> Dict[str, Any]:
        """Información real del Motor de Hibridación Inteligente"""
        return {
            "name": "Motor de Hibridación Inteligente",
            "description": "Sistema de dos capas que garantiza personalización radical",
            "layer_1": {
                "name": "Capa Estratégica - Adaptación por Arquetipo",
                "function": "Define el 'porqué' y tono de interacción",
                "archetypes": {
                    "PRIME": "El Optimizador - Performance ejecutivo y productividad",
                    "LONGEVITY": "El Arquitecto de Vida - Vitalidad sostenible y prevención"
                }
            },
            "layer_2": {
                "name": "Capa Fisiológica - Modulación por Data Individual", 
                "function": "Ajusta ejecución en tiempo real para seguridad y eficacia",
                "data_points": [
                    "Edad y género",
                    "Biomarcadores de wearables",
                    "Historial de lesiones",
                    "Capacidad de recuperación",
                    "Preferencias individuales",
                    "Métricas de progreso"
                ]
            },
            "key_benefits": [
                "Ninguna experiencia NGX es verdaderamente 'sin acompañamiento'",
                "IA siempre guiando, protegiendo y personalizando",
                "Garantía de seguridad y eficacia en todos los niveles",
                "Adaptación automática que mejora con cada interacción"
            ]
        }
    
    def get_archetype_info(self, archetype: NGXArchetype) -> Dict[str, Any]:
        """Obtiene información específica del arquetipo"""
        archetype_data = {
            NGXArchetype.PRIME: {
                "name": "El Optimizador",
                "target_audience": "Profesionales y ejecutivos 25-50 años",
                "focus": "Performance ejecutivo, productividad, competitive advantage",
                "key_benefits": [
                    "Optimización cognitiva pico",
                    "Sustained energy para jornadas largas", 
                    "Stress management para decisiones críticas",
                    "Recovery optimization para consistency"
                ],
                "ideal_for": [
                    "CEOs y fundadores",
                    "Ejecutivos de alto rendimiento",
                    "Entrepreneurs",
                    "Líderes empresariales"
                ]
            },
            NGXArchetype.LONGEVITY: {
                "name": "El Arquitecto de Vida",
                "target_audience": "Adultos 45+ enfocados en longevidad",
                "focus": "Vitalidad sostenible, prevención, healthspan extension",
                "key_benefits": [
                    "Vitalidad diaria incrementada",
                    "Función cognitiva preservada",
                    "Muscle mass maintenance",
                    "Optimización metabólica"
                ],
                "ideal_for": [
                    "Profesionales health-conscious 45+",
                    "Individuos prevention-focused",
                    "Buscadores de aging saludable",
                    "Optimizadores de healthspan"
                ]
            }
        }
        return archetype_data.get(archetype, {})
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Comparación entre NGX AGENTS ACCESS vs Coaching Híbrido"""
        return {
            "agents_access": {
                "model": "Autonomía Guiada por IA",
                "target": "Individuo autónomo, disciplinado y proactivo",
                "value_prop": "Director de tu propia orquesta biológica",
                "interaction": "Directo 24/7 con 9 agentes especializados",
                "price_range": "$79-$199/mes",
                "best_for": "Self-directed optimization con herramientas de vanguardia"
            },
            "hybrid_coaching": {
                "model": "Inteligencia Simbiótica Humano-IA", 
                "target": "Ejecutivos/líderes que buscan máximo nivel",
                "value_prop": "Director de orquesta + mejores músicos del planeta",
                "interaction": "Coach humano estratégico + ejecución IA 24/7",
                "price_range": "$3,997 programa 20 semanas",
                "best_for": "Transformación garantizada con accountability humana"
            }
        }
    
    def generate_ngx_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera contexto NGX para conversaciones basado en usuario real"""
        
        # Detectar arquetipo probable
        age = user_context.get('age', 35)
        profession = user_context.get('profession', '').lower()
        
        # Lógica de detección de arquetipo
        if age >= 45 or any(keyword in profession for keyword in ['health', 'wellness', 'longevity']):
            suggested_archetype = NGXArchetype.LONGEVITY
        else:
            suggested_archetype = NGXArchetype.PRIME
            
        # Detectar modelo NGX apropiado
        budget_indicator = user_context.get('budget_sensitivity', 'medium')
        executive_level = any(keyword in profession for keyword in ['ceo', 'founder', 'executive', 'director'])
        
        if executive_level and budget_indicator == 'low':
            suggested_model = NGXModel.HYBRID_COACHING
        else:
            suggested_model = NGXModel.AGENTS_ACCESS
        
        return {
            "suggested_archetype": suggested_archetype.value,
            "archetype_info": self.get_archetype_info(suggested_archetype),
            "suggested_model": suggested_model.value,
            "model_comparison": self.get_model_comparison(),
            "relevant_agents": [agent for agent in self.ngx_agents if suggested_archetype.value in agent.archetype_focus],
            "hie_explanation": self.hybrid_intelligence_engine,
            "competitive_advantages": self.competitive_advantages[:3],  # Top 3
            "pricing_context": {
                "agents_access_tiers": self.agents_access_tiers,
                "hybrid_programs": [p for p in self.hybrid_programs if p.archetype == suggested_archetype]
            }
        }

# Global instance
_ngx_knowledge = None

def get_ngx_knowledge() -> NGXMasterKnowledge:
    """Get global NGX knowledge instance"""
    global _ngx_knowledge
    if _ngx_knowledge is None:
        _ngx_knowledge = NGXMasterKnowledge()
    return _ngx_knowledge

if __name__ == "__main__":
    # Demo del sistema NGX real
    ngx_knowledge = NGXMasterKnowledge()
    
    print("🚀 NGX Master Knowledge System (REAL)")
    print("=" * 50)
    
    # Demo context generation
    test_context = {
        'age': 42,
        'profession': 'CEO',
        'budget_sensitivity': 'low'
    }
    
    ngx_context = ngx_knowledge.generate_ngx_context(test_context)
    print(f"📊 NGX Context for CEO (42):")
    print(f"   Suggested archetype: {ngx_context['suggested_archetype']}")
    print(f"   Suggested model: {ngx_context['suggested_model']}")
    print(f"   Relevant agents: {len(ngx_context['relevant_agents'])}")
    print()
    
    print("✅ NGX Real Knowledge System ready!")