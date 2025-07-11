"""
NGX Consultant Knowledge Base - Base de conocimiento conversacional.

Esta base de conocimiento contiene toda la información que el consultor NGX necesita:
- Dominio completo de programas NGX (PRIME/LONGEVITY)
- Fitness básico para conectar con clientes
- HIE como diferenciador único
- Casos de éxito y testimoniales relevantes
- Manejo conversacional de objeciones

ENFOQUE: CONSULTOR EXPERTO, NO VENDEDOR AGRESIVO.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class NGXProgram:
    """Información completa de un programa NGX."""
    name: str
    target_age: str
    target_audience: str
    primary_benefits: List[str]
    unique_features: List[str]
    pricing_tiers: Dict[str, int]
    ideal_candidates: List[str]
    success_metrics: List[str]


@dataclass
class HIECapability:
    """Capacidad específica del Hybrid Intelligence Engine."""
    agent_name: str
    specialization: str
    unique_value: str
    client_benefit: str
    competitive_advantage: str


@dataclass
class SuccessStory:
    """Historia de éxito para social proof."""
    client_profile: str
    initial_challenge: str
    ngx_solution: str
    results_achieved: str
    timeframe: str
    key_quote: str


class NGXConsultantKnowledge:
    """
    Base de conocimiento completa para el consultor NGX.
    
    Contiene todo lo necesario para ser un consultor experto:
    - Información completa de productos NGX
    - Conocimiento de fitness básico
    - HIE como diferenciador único
    - Casos de éxito y social proof
    """
    
    def __init__(self):
        self.ngx_programs = self._initialize_ngx_programs()
        self.hie_capabilities = self._initialize_hie_capabilities()
        self.success_stories = self._initialize_success_stories()
        self.fitness_basics = self._initialize_fitness_knowledge()
        self.objection_responses = self._initialize_consultive_objection_responses()
        self.competitive_advantages = self._initialize_competitive_advantages()
    
    def _initialize_ngx_programs(self) -> Dict[str, NGXProgram]:
        """Inicializa información completa de programas NGX."""
        return {
            "PRIME": NGXProgram(
                name="NGX PRIME",
                target_age="25-50 años",
                target_audience="Profesionales y ejecutivos orientados al rendimiento",
                primary_benefits=[
                    "Optimización cognitiva para máximo rendimiento",
                    "Protocolos de alta eficiencia para ejecutivos",
                    "Integración perfecta con rutinas de alto impacto",
                    "Incremento de productividad del 25% comprobado",
                    "3 horas extra productivas diarias",
                    "Reducción del 40% en tiempo de decisión"
                ],
                unique_features=[
                    "Algoritmo de optimización ejecutiva",
                    "Análisis predictivo de rendimiento",
                    "Coaching híbrido 24/7 con HIE",
                    "Protocolos de energía y focus",
                    "Optimización circadiana para ejecutivos"
                ],
                pricing_tiers={
                    "Essential": 79,
                    "Pro": 149,
                    "Elite": 199,
                    "PRIME Premium": 3997
                },
                ideal_candidates=[
                    "Ejecutivos con horarios demandantes",
                    "Emprendedores que buscan optimización",
                    "Profesionales con metas de alto rendimiento",
                    "Líderes que necesitan energía sostenida",
                    "Personas con lifestyle de alta presión"
                ],
                success_metrics=[
                    "25% incremento en productividad mensual",
                    "3 horas adicionales de energía productiva",
                    "40% reducción en tiempo de decisión",
                    "Mejora del 60% en calidad de sueño",
                    "35% reducción en niveles de estrés"
                ]
            ),
            
            "LONGEVITY": NGXProgram(
                name="NGX LONGEVITY",
                target_age="45+ años",
                target_audience="Adultos enfocados en envejecimiento saludable y prevención",
                primary_benefits=[
                    "Protocolos de longevidad basados en ciencia",
                    "Prevención predictiva de declive cognitivo",
                    "Optimización de healthspan y lifespan",
                    "+10 años de vitalidad proyectada",
                    "Reducción del 60% en riesgo de enfermedades",
                    "Mejora del 80% en marcadores de longevidad"
                ],
                unique_features=[
                    "Algoritmo de envejecimiento predictivo",
                    "Protocolos de medicina preventiva",
                    "Coaching de longevidad personalizado",
                    "Análisis de biomarcadores de edad",
                    "Optimización hormonal natural"
                ],
                pricing_tiers={
                    "Essential": 79,
                    "Pro": 149,
                    "Elite": 199,
                    "LONGEVITY Premium": 3997
                },
                ideal_candidates=[
                    "Adultos 45+ preocupados por el envejecimiento",
                    "Personas con historial familiar de enfermedades",
                    "Individuos enfocados en prevención",
                    "Profesionales de la salud conscientes",
                    "Personas que buscan vitalidad a largo plazo"
                ],
                success_metrics=[
                    "10 años adicionales de vitalidad proyectada",
                    "60% reducción en riesgo de enfermedades",
                    "80% mejora en marcadores de longevidad",
                    "50% mejora en energía diaria",
                    "70% mejora en calidad de vida general"
                ]
            )
        }
    
    def _initialize_hie_capabilities(self) -> List[HIECapability]:
        """Inicializa las 11 capacidades del Hybrid Intelligence Engine."""
        return [
            HIECapability(
                agent_name="Metabolic Optimizer",
                specialization="Optimización metabólica personalizada",
                unique_value="Análisis en tiempo real de marcadores metabólicos",
                client_benefit="Energía sostenida y composición corporal óptima",
                competitive_advantage="Imposible de replicar - algoritmo propietario"
            ),
            HIECapability(
                agent_name="Circadian Coordinator",
                specialization="Optimización de ritmos circadianos",
                unique_value="Sincronización perfecta de ciclos naturales",
                client_benefit="Sueño profundo y energía natural durante el día",
                competitive_advantage="18 meses adelante de cualquier competidor"
            ),
            HIECapability(
                agent_name="Cognitive Enhancer",
                specialization="Mejora del rendimiento cognitivo",
                unique_value="Protocolos nootrópicos naturales personalizados",
                client_benefit="Focus, memoria y claridad mental superiores",
                competitive_advantage="Combinación única de ciencia y tecnología"
            ),
            HIECapability(
                agent_name="Stress Manager",
                specialization="Manejo inteligente del estrés",
                unique_value="Adaptógenos personalizados según perfil de estrés",
                client_benefit="Resiliencia al estrés y recuperación acelerada",
                competitive_advantage="Algoritmo de detección de patrones único"
            ),
            HIECapability(
                agent_name="Recovery Specialist",
                specialization="Optimización de recuperación",
                unique_value="Protocolos de recovery basados en biomarcadores",
                client_benefit="Recuperación más rápida y rendimiento sostenido",
                competitive_advantage="Integración con wearables en tiempo real"
            ),
            HIECapability(
                agent_name="Longevity Predictor",
                specialization="Análisis predictivo de longevidad",
                unique_value="Predicción de riesgos de salud futuros",
                client_benefit="Prevención proactiva y envejecimiento saludable",
                competitive_advantage="Tecnología exclusiva de medicina predictiva"
            ),
            HIECapability(
                agent_name="Nutrition Strategist",
                specialization="Estrategias nutricionales personalizadas",
                unique_value="Análisis de comidas con foto + recomendaciones",
                client_benefit="Nutrición optimizada sin complejidad",
                competitive_advantage="IA visual única en el mercado"
            ),
            HIECapability(
                agent_name="Hormone Balancer",
                specialization="Equilibrio hormonal natural",
                unique_value="Optimización hormonal sin medicamentos",
                client_benefit="Energía, libido y bienestar hormonal óptimos",
                competitive_advantage="Protocolos naturales científicamente validados"
            ),
            HIECapability(
                agent_name="Exercise Optimizer",
                specialization="Optimización de protocolos de ejercicio",
                unique_value="Entrenamientos personalizados según objetivos",
                client_benefit="Máximos resultados con mínimo tiempo invertido",
                competitive_advantage="Adaptación en tiempo real según progreso"
            ),
            HIECapability(
                agent_name="Supplement Selector",
                specialization="Selección inteligente de suplementos",
                unique_value="Recomendaciones basadas en análisis individual",
                client_benefit="Solo los suplementos que realmente necesitas",
                competitive_advantage="Evita suplementación innecesaria"
            ),
            HIECapability(
                agent_name="Progress Tracker",
                specialization="Seguimiento inteligente de progreso",
                unique_value="Analytics predictivos de resultados",
                client_benefit="Saber exactamente qué está funcionando",
                competitive_advantage="Predicción de resultados con 85% precisión"
            )
        ]
    
    def _initialize_success_stories(self) -> List[SuccessStory]:
        """Inicializa historias de éxito para social proof."""
        return [
            # PRIME Success Stories
            SuccessStory(
                client_profile="CEO de fintech, 38 años",
                initial_challenge="Fatiga extrema, decisiones lentas, 60 horas de trabajo semanales",
                ngx_solution="NGX PRIME Elite con focus en optimización cognitiva",
                results_achieved="40% más productividad, 3 horas extra energía, decisiones 50% más rápidas",
                timeframe="6 semanas",
                key_quote="NGX transformó mi capacidad de liderazgo. Tengo la energía de mis 20s con la experiencia de mis 30s."
            ),
            SuccessStory(
                client_profile="Directora de marketing, 34 años",
                initial_challenge="Estrés constante, insomnio, dificultad para concentrarse",
                ngx_solution="NGX PRIME Pro con protocolos de manejo de estrés",
                results_achieved="Sueño profundo restaurado, 60% reducción en estrés, focus laser",
                timeframe="4 semanas",
                key_quote="Por primera vez en años duermo 8 horas seguidas y despierto con energía real."
            ),
            SuccessStory(
                client_profile="Emprendedor, 29 años",
                initial_challenge="Burnout, múltiples proyectos, energía inconsistente",
                ngx_solution="NGX PRIME Essential con optimización circadiana",
                results_achieved="Energía sostenida todo el día, duplicó productividad efectiva",
                timeframe="3 semanas",
                key_quote="NGX me dio la energía y claridad para escalar mi startup sin sacrificar mi salud."
            ),
            
            # LONGEVITY Success Stories
            SuccessStory(
                client_profile="Médico, 58 años",
                initial_challenge="Preocupación por declive cognitivo, fatiga, marcadores de salud",
                ngx_solution="NGX LONGEVITY Premium con análisis genético",
                results_achieved="Todos los marcadores mejorados, energía de hace 10 años",
                timeframe="8 semanas",
                key_quote="Como médico soy escéptico, pero NGX superó mis expectativas científicas más exigentes."
            ),
            SuccessStory(
                client_profile="Profesora universitaria, 52 años",
                initial_challenge="Menopausia, cambios hormonales, pérdida de vitalidad",
                ngx_solution="NGX LONGEVITY Elite con equilibrio hormonal natural",
                results_achieved="Síntomas de menopausia minimizados, vitalidad restaurada",
                timeframe="6 semanas",
                key_quote="Siento que tengo control sobre mi cuerpo otra vez. La menopausia ya no me define."
            ),
            SuccessStory(
                client_profile="Ingeniero jubilado, 65 años", 
                initial_challenge="Preocupación por independencia futura, declive físico",
                ngx_solution="NGX LONGEVITY Pro con protocolos preventivos",
                results_achieved="Fuerza y movilidad mejoradas, confianza en el futuro",
                timeframe="12 semanas",
                key_quote="NGX me dio la tranquilidad de saber que puedo envejecer con dignidad e independencia."
            )
        ]
    
    def _initialize_fitness_knowledge(self) -> Dict[str, str]:
        """Inicializa conocimiento básico de fitness para conectar con clientes."""
        return {
            "energy_systems": (
                "El cuerpo tiene 3 sistemas energéticos principales: fosfocreatina (explosivo), "
                "glucólisis (intenso), y oxidativo (sostenido). NGX optimiza los tres según "
                "tus necesidades específicas."
            ),
            "metabolism_basics": (
                "Tu metabolismo no es fijo - puede optimizarse. NGX analiza tu perfil metabólico "
                "único y crea protocolos personalizados para acelerar la quema de grasa y "
                "mejorar la energía."
            ),
            "recovery_importance": (
                "La recuperación es donde ocurre el progreso real. Sin recuperación óptima, "
                "estás entrenando en vano. NGX optimiza tu recovery para maximizar resultados "
                "con menos tiempo de entrenamiento."
            ),
            "hormonal_optimization": (
                "Las hormonas controlan todo: energía, composición corporal, estado de ánimo. "
                "NGX utiliza métodos naturales para optimizar tu perfil hormonal sin medicamentos."
            ),
            "circadian_health": (
                "Tu reloj biológico afecta todo: sueño, energía, digestión, hormonas. "
                "NGX sincroniza tus ritmos circadianos para optimizar cada aspecto de tu bienestar."
            ),
            "stress_physiology": (
                "El estrés crónico es el asesino silencioso del rendimiento y la salud. "
                "NGX identifica tus patrones de estrés únicos y crea protocolos adaptativos "
                "para manejarlos efectivamente."
            ),
            "longevity_science": (
                "La ciencia de la longevidad ha avanzado dramáticamente. Ahora sabemos que "
                "el envejecimiento es modificable. NGX aplica los últimos descubrimientos "
                "en protocolos prácticos y personalizados."
            )
        }
    
    def _initialize_consultive_objection_responses(self) -> Dict[str, Dict]:
        """Inicializa respuestas consultivas (no agresivas) a objeciones."""
        return {
            "price_concern": {
                "approach": "Entender la preocupación real, ofrecer alternativas",
                "responses": [
                    "Entiendo completamente tu preocupación sobre el precio. Mi trabajo es "
                    "encontrar la solución que funcione para tu situación específica. "
                    "¿Qué rango de inversión sería cómodo para ti?",
                    
                    "El precio es una consideración importante. NGX tiene diferentes niveles "
                    "precisamente para adaptarse a diferentes situaciones. Empezar con "
                    "Essential te da acceso al HIE core, y siempre puedes ajustar después.",
                    
                    "Permíteme preguntarte esto: ¿cuánto inviertes actualmente en tu salud "
                    "y bienestar? A menudo NGX reemplaza varios otros gastos, haciendo que "
                    "el costo neto sea mucho menor."
                ],
                "tier_adjustments": {
                    "Elite → Pro": "Pro mantiene las funciones core del HIE a mejor precio",
                    "Pro → Essential": "Essential te da acceso completo al HIE core",
                    "Premium → Elite": "Elite incluye la mayoría de beneficios premium"
                }
            },
            
            "time_concern": {
                "approach": "Mostrar cómo NGX ahorra tiempo, no lo consume",
                "responses": [
                    "Entiendo la preocupación sobre el tiempo - es precisamente por eso que "
                    "NGX existe. El sistema está diseñado para personas ocupadas como tú. "
                    "¿Cuánto tiempo tienes realísticamente por día?",
                    
                    "La mayoría de mis clientes ejecutivos me dicen que NGX les da MÁS tiempo, "
                    "no menos. Al optimizar tu energía y focus, recuperas horas de productividad "
                    "que compensan cualquier tiempo invertido.",
                    
                    "NGX se integra en tu rutina existente - no requiere tiempo adicional. "
                    "Es optimización, no adición."
                ]
            },
            
            "skepticism": {
                "approach": "Validar escepticismo, ofrecer evidencia, garantías",
                "responses": [
                    "Tu escepticismo es completamente válido - hay mucho ruido en la industria "
                    "del wellness. NGX es diferente porque es medible. ¿Qué tipo de evidencia "
                    "te haría sentir más cómodo?",
                    
                    "Aprecio que seas escéptico - significa que tomas decisiones informadas. "
                    "Por eso NGX tiene garantía de resultados. Si no ves mejoras medibles "
                    "en 30 días, reembolso completo.",
                    
                    "Como profesional en tu campo, valoras la evidencia. NGX está respaldado "
                    "por estudios y datos reales de clientes. ¿Te gustaría ver algunos casos "
                    "específicos de tu industria?"
                ]
            },
            
            "need_to_think": {
                "approach": "Respetar el proceso, ofrecer información adicional",
                "responses": [
                    "Por supuesto, es una decisión importante y merece consideración. "
                    "¿Hay alguna información específica que te ayudaría en tu análisis?",
                    
                    "Entiendo completamente - es inteligente tomarse tiempo para decisiones "
                    "importantes. ¿Qué preguntas o preocupaciones puedo aclarar mientras lo piensas?",
                    
                    "Tomar tiempo para decidir muestra que valoras hacer la elección correcta. "
                    "¿Te gustaría que programemos una llamada de seguimiento para cuando "
                    "hayas tenido tiempo de procesarlo?"
                ]
            }
        }
    
    def _initialize_competitive_advantages(self) -> Dict[str, str]:
        """Inicializa ventajas competitivas únicas de NGX."""
        return {
            "hie_uniqueness": (
                "El Hybrid Intelligence Engine es literalmente imposible de clonar. "
                "Hemos invertido 3 años y millones en desarrollar esta tecnología. "
                "Ningún competidor tiene algo remotamente parecido."
            ),
            "personalization_depth": (
                "Otros programas ofrecen 'personalización' básica. NGX analiza más de "
                "200 puntos de datos para crear un protocolo único para ti. La diferencia "
                "es como un traje a medida vs uno de rack."
            ),
            "scientific_backing": (
                "NGX no se basa en tendencias - se basa en ciencia peer-reviewed. "
                "Cada protocolo está respaldado por estudios, no por marketing. "
                "Es medicina de precisión aplicada al wellness."
            ),
            "technology_advantage": (
                "Tenemos 18 meses de ventaja tecnológica sobre cualquier competidor. "
                "Mientras otros están empezando a pensar en IA para wellness, "
                "nosotros ya tenemos la segunda generación funcionando."
            ),
            "results_guarantee": (
                "Ofrecemos garantía de resultados porque sabemos que funciona. "
                "La mayoría de competidores no pueden ofrecer esto porque "
                "no tienen la precisión ni la efectividad de NGX."
            ),
            "integration_simplicity": (
                "NGX se integra perfectamente en tu vida existente. No requiere "
                "cambios drásticos o tiempo adicional. Es optimización inteligente, "
                "no disrupción de lifestyle."
            )
        }
    
    # ===== MÉTODOS PARA ACCESO A CONOCIMIENTO =====
    
    def get_program_info(self, program_name: str) -> Optional[NGXProgram]:
        """Obtiene información completa de un programa NGX."""
        return self.ngx_programs.get(program_name.upper())
    
    def get_hie_capabilities(self) -> List[HIECapability]:
        """Obtiene todas las capacidades del HIE."""
        return self.hie_capabilities
    
    def get_relevant_success_story(self, client_profile: str, program: str) -> Optional[SuccessStory]:
        """Obtiene historia de éxito relevante para el cliente."""
        for story in self.success_stories:
            if program.upper() in story.ngx_solution and \
               any(keyword in story.client_profile.lower() 
                   for keyword in client_profile.lower().split()):
                return story
        
        # Fallback: return first story for the program
        for story in self.success_stories:
            if program.upper() in story.ngx_solution:
                return story
        
        return None
    
    def get_fitness_explanation(self, topic: str) -> str:
        """Obtiene explicación básica de fitness para conectar con cliente."""
        return self.fitness_basics.get(topic, 
            "NGX utiliza ciencia avanzada para optimizar tu bienestar de manera personalizada.")
    
    def get_consultive_objection_response(self, objection_type: str) -> Dict:
        """Obtiene respuesta consultiva para tipo de objeción."""
        return self.objection_responses.get(objection_type, {
            "approach": "Escuchar y entender la preocupación",
            "responses": ["Entiendo tu preocupación. ¿Puedes contarme más sobre qué te preocupa específicamente?"]
        })
    
    def get_competitive_advantage(self, aspect: str) -> str:
        """Obtiene explicación de ventaja competitiva específica."""
        return self.competitive_advantages.get(aspect,
            "NGX ofrece tecnología única que no encontrarás en ningún otro lugar.")
    
    def get_tier_explanation(self, program: str, tier: str) -> str:
        """Obtiene explicación consultiva de un tier específico."""
        program_info = self.get_program_info(program)
        if not program_info:
            return f"{tier} incluye acceso completo al Hybrid Intelligence Engine."
        
        price = program_info.pricing_tiers.get(tier, 0)
        
        if tier == "Essential":
            return (
                f"{program} Essential (${price}/mes) te da acceso completo al HIE core - "
                f"los 11 agentes especializados trabajando para optimizar tu bienestar. "
                f"Es una excelente forma de comenzar y experimentar los beneficios."
            )
        elif tier == "Pro":
            return (
                f"{program} Pro (${price}/mes) incluye todo Essential plus análisis de "
                f"comidas con foto, reportes semanales detallados, e integración con wearables. "
                f"Es el sweet spot para la mayoría de clientes."
            )
        elif tier == "Elite":
            return (
                f"{program} Elite (${price}/mes) añade voz natural con los agentes, "
                f"análisis en tiempo real por HRV, y soporte prioritario. Para quienes "
                f"quieren la experiencia premium completa."
            )
        else:  # Premium
            return (
                f"{program} Premium (${price}/mes) incluye coaching personal híbrido, "
                f"análisis genético, y sesiones 1:1 con especialistas. Es transformación "
                f"completa con acompañamiento premium."
            )
    
    def explain_hie_in_context(self, client_needs: List[str]) -> str:
        """Explica HIE en contexto de las necesidades específicas del cliente."""
        relevant_agents = []
        
        need_to_agent = {
            "energy": "Metabolic Optimizer y Circadian Coordinator",
            "stress": "Stress Manager y Recovery Specialist", 
            "focus": "Cognitive Enhancer",
            "sleep": "Circadian Coordinator",
            "fitness": "Exercise Optimizer y Recovery Specialist",
            "nutrition": "Nutrition Strategist",
            "aging": "Longevity Predictor y Hormone Balancer"
        }
        
        for need in client_needs:
            if need in need_to_agent:
                relevant_agents.append(need_to_agent[need])
        
        if relevant_agents:
            agents_text = ", ".join(set(relevant_agents))
            return (
                f"Para tus necesidades específicas, el HIE utilizaría principalmente "
                f"{agents_text}. Estos agentes especializados analizan tu situación "
                f"única y crean protocolos personalizados que ningún programa genérico "
                f"puede ofrecer."
            )
        else:
            return (
                "El Hybrid Intelligence Engine con sus 11 agentes especializados "
                "analiza tu perfil completo y crea un protocolo único para ti. "
                "Es como tener un equipo de especialistas trabajando 24/7 "
                "exclusivamente para tu optimización."
            )