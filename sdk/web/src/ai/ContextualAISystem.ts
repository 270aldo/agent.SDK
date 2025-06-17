/**
 * Contextual AI System for NGX Voice Agent
 * Personalizes conversation flow and messaging based on touchpoint and user behavior
 */

export interface UserContext {
  // Basic demographics
  age?: number;
  gender?: 'male' | 'female' | 'other';
  location?: {
    country?: string;
    city?: string;
    timezone?: string;
  };
  
  // Behavioral data
  touchpoint: string;
  userIntent: 'cold' | 'warm' | 'hot';
  engagementLevel: 'low' | 'medium' | 'high';
  conversationStage: 'discovery' | 'interest' | 'consideration' | 'decision' | 'retention';
  
  // Session data
  timeOnPage: number;
  scrollDepth: number;
  previousInteractions: number;
  referralSource?: string;
  campaignData?: {
    id?: string;
    source?: string;
    medium?: string;
    content?: string;
  };
  
  // Fitness/health specific (for NGX)
  fitnessProfile?: {
    experience: 'beginner' | 'intermediate' | 'advanced';
    goals: string[];
    challenges: string[];
    currentProgram?: string;
    budget?: 'low' | 'medium' | 'high';
  };
  
  // Previous context if returning user
  previousConversations?: {
    count: number;
    lastTopic?: string;
    lastOutcome?: 'qualified' | 'unqualified' | 'follow-up' | 'closed';
    lastDate?: Date;
  };
}

export interface ConversationPersonality {
  tone: 'friendly' | 'professional' | 'energetic' | 'empathetic' | 'confident' | 'casual';
  approach: 'educational' | 'consultative' | 'sales-focused' | 'supportive' | 'solution-oriented';
  energy: 'calm' | 'moderate' | 'high';
  formality: 'casual' | 'semi-formal' | 'formal';
  pace: 'slow' | 'moderate' | 'fast';
}

export interface ConversationFlow {
  welcomeMessage: string;
  discoveryQuestions: string[];
  objectionHandling: Record<string, string>;
  callToAction: string;
  followUpStrategy: string;
  maxDuration: number; // in seconds
  keyTopics: string[];
  transitionTriggers: string[];
}

export interface AIResponse {
  message: string;
  personality: ConversationPersonality;
  suggestedQuestions: string[];
  nextStage: string;
  confidence: number;
  shouldEscalate?: boolean;
  customData?: Record<string, any>;
}

class ContextualAISystem {
  private context: UserContext;
  private conversationHistory: string[] = [];
  private currentStage: string = 'discovery';
  private detectedIntents: string[] = [];
  
  constructor(context: UserContext) {
    this.context = context;
  }

  /**
   * Generate contextual welcome message based on touchpoint and user data
   */
  public generateWelcomeMessage(): string {
    const { touchpoint, userIntent, previousConversations } = this.context;
    
    // Returning user
    if (previousConversations && previousConversations.count > 0) {
      return this.generateReturningUserWelcome();
    }
    
    // First-time user based on touchpoint
    switch (touchpoint) {
      case 'landing-page':
        return this.generateLandingPageWelcome();
      case 'lead-magnet':
        return this.generateLeadMagnetWelcome();
      case 'webinar-end':
        return this.generateWebinarWelcome();
      case 'exit-intent':
        return this.generateExitIntentWelcome();
      case 'email-campaign':
        return this.generateEmailCampaignWelcome();
      case 'blog':
        return this.generateBlogWelcome();
      default:
        return this.generateGenericWelcome();
    }
  }

  /**
   * Determine conversation personality based on context
   */
  public getConversationPersonality(): ConversationPersonality {
    const { touchpoint, userIntent, engagementLevel, fitnessProfile } = this.context;
    
    // Base personality
    let personality: ConversationPersonality = {
      tone: 'friendly',
      approach: 'consultative',
      energy: 'moderate',
      formality: 'semi-formal',
      pace: 'moderate'
    };
    
    // Adjust based on touchpoint
    switch (touchpoint) {
      case 'landing-page':
        personality.approach = userIntent === 'hot' ? 'sales-focused' : 'consultative';
        personality.energy = 'high';
        break;
      case 'lead-magnet':
        personality.approach = 'educational';
        personality.tone = 'empathetic';
        break;
      case 'webinar-end':
        personality.approach = 'solution-oriented';
        personality.energy = 'high';
        personality.tone = 'confident';
        break;
      case 'exit-intent':
        personality.approach = 'supportive';
        personality.tone = 'empathetic';
        personality.pace = 'slow';
        break;
      case 'blog':
        personality.approach = 'educational';
        personality.tone = 'friendly';
        personality.formality = 'casual';
        break;
    }
    
    // Adjust based on fitness experience
    if (fitnessProfile?.experience === 'beginner') {
      personality.tone = 'empathetic';
      personality.pace = 'slow';
      personality.approach = 'educational';
    } else if (fitnessProfile?.experience === 'advanced') {
      personality.tone = 'confident';
      personality.formality = 'professional';
      personality.approach = 'solution-oriented';
    }
    
    // Adjust based on engagement level
    if (engagementLevel === 'high') {
      personality.energy = 'high';
      personality.pace = 'fast';
    } else if (engagementLevel === 'low') {
      personality.tone = 'empathetic';
      personality.pace = 'slow';
    }
    
    return personality;
  }

  /**
   * Generate AI response based on user input and context
   */
  public async generateResponse(userInput: string): Promise<AIResponse> {
    // Analyze user intent
    const detectedIntent = this.analyzeUserIntent(userInput);
    this.detectedIntents.push(detectedIntent);
    
    // Update conversation stage
    this.updateConversationStage(userInput, detectedIntent);
    
    // Generate contextual response
    const message = await this.generateContextualMessage(userInput, detectedIntent);
    
    // Get personality
    const personality = this.getConversationPersonality();
    
    // Generate follow-up questions
    const suggestedQuestions = this.generateFollowUpQuestions(detectedIntent);
    
    // Determine confidence and escalation
    const confidence = this.calculateResponseConfidence(userInput, detectedIntent);
    const shouldEscalate = this.shouldEscalateToHuman(detectedIntent, confidence);
    
    // Store in conversation history
    this.conversationHistory.push(`User: ${userInput}`);
    this.conversationHistory.push(`AI: ${message}`);
    
    return {
      message,
      personality,
      suggestedQuestions,
      nextStage: this.currentStage,
      confidence,
      shouldEscalate,
      customData: {
        detectedIntent,
        touchpoint: this.context.touchpoint,
        stage: this.currentStage
      }
    };
  }

  /**
   * Get conversation flow configuration for current context
   */
  public getConversationFlow(): ConversationFlow {
    const { touchpoint, userIntent } = this.context;
    
    const baseFlow: ConversationFlow = {
      welcomeMessage: this.generateWelcomeMessage(),
      discoveryQuestions: this.getDiscoveryQuestions(),
      objectionHandling: this.getObjectionHandling(),
      callToAction: this.getCallToAction(),
      followUpStrategy: this.getFollowUpStrategy(),
      maxDuration: 420, // 7 minutes
      keyTopics: this.getKeyTopics(),
      transitionTriggers: this.getTransitionTriggers()
    };
    
    // Customize based on touchpoint
    switch (touchpoint) {
      case 'landing-page':
        baseFlow.maxDuration = userIntent === 'hot' ? 300 : 420; // 5-7 minutes
        baseFlow.keyTopics = ['program_overview', 'results', 'pricing', 'next_steps'];
        break;
      case 'lead-magnet':
        baseFlow.maxDuration = 480; // 8 minutes for education
        baseFlow.keyTopics = ['resource_application', 'challenges', 'personalization', 'next_level'];
        break;
      case 'webinar-end':
        baseFlow.maxDuration = 360; // 6 minutes, they're already educated
        baseFlow.keyTopics = ['implementation', 'support', 'results', 'enrollment'];
        break;
      case 'exit-intent':
        baseFlow.maxDuration = 180; // 3 minutes, quick recovery
        baseFlow.keyTopics = ['quick_value', 'objection_resolution', 'alternative_offer'];
        break;
    }
    
    return baseFlow;
  }

  /**
   * Analyze user intent from input
   */
  private analyzeUserIntent(input: string): string {
    const inputLower = input.toLowerCase();
    
    // Define intent patterns
    const intentPatterns = {
      price_inquiry: ['price', 'cost', 'expensive', 'cheap', 'money', 'budget', 'afford'],
      program_interest: ['program', 'course', 'training', 'workout', 'plan', 'system'],
      results_question: ['results', 'work', 'effective', 'success', 'guarantee', 'proof'],
      time_concern: ['time', 'busy', 'schedule', 'quick', 'fast', 'long'],
      skepticism: ['skeptical', 'doubt', 'scam', 'fake', 'real', 'legit', 'trust'],
      personal_situation: ['me', 'my', 'personal', 'situation', 'case', 'specific'],
      comparison: ['compare', 'versus', 'vs', 'different', 'alternative', 'other'],
      ready_to_buy: ['buy', 'purchase', 'enroll', 'sign up', 'start', 'ready', 'yes'],
      more_info: ['more', 'details', 'information', 'explain', 'tell me', 'learn'],
      objection: ['but', 'however', 'problem', 'issue', 'concern', 'worry']
    };
    
    // Check for patterns
    for (const [intent, patterns] of Object.entries(intentPatterns)) {
      if (patterns.some(pattern => inputLower.includes(pattern))) {
        return intent;
      }
    }
    
    // Default to discovery if no specific intent detected
    return 'discovery';
  }

  /**
   * Update conversation stage based on user interaction
   */
  private updateConversationStage(input: string, intent: string): void {
    const progressionMap = {
      discovery: ['interest', 'consideration'],
      interest: ['consideration', 'decision'],
      consideration: ['decision', 'retention'],
      decision: ['retention'],
      retention: ['retention']
    };
    
    // Intent-based progression
    const advancingIntents = ['program_interest', 'ready_to_buy', 'more_info'];
    const stallIntents = ['skepticism', 'price_inquiry', 'objection'];
    
    if (advancingIntents.includes(intent) && progressionMap[this.currentStage]) {
      const nextStages = progressionMap[this.currentStage];
      this.currentStage = nextStages[0];
    } else if (stallIntents.includes(intent)) {
      // Stay in current stage or regress if needed
      if (this.currentStage === 'decision') {
        this.currentStage = 'consideration';
      }
    }
  }

  /**
   * Generate contextual message based on input and intent
   */
  private async generateContextualMessage(input: string, intent: string): Promise<string> {
    const personality = this.getConversationPersonality();
    const { touchpoint, fitnessProfile } = this.context;
    
    // Base responses by intent
    const responseTemplates = {
      price_inquiry: this.generatePriceResponse(),
      program_interest: this.generateProgramResponse(),
      results_question: this.generateResultsResponse(),
      time_concern: this.generateTimeResponse(),
      skepticism: this.generateTrustResponse(),
      personal_situation: this.generatePersonalResponse(),
      comparison: this.generateComparisonResponse(),
      ready_to_buy: this.generateReadyToBuyResponse(),
      more_info: this.generateMoreInfoResponse(),
      objection: this.generateObjectionResponse(input),
      discovery: this.generateDiscoveryResponse()
    };
    
    let baseResponse = responseTemplates[intent] || responseTemplates.discovery;
    
    // Personalize based on personality
    baseResponse = this.personalizeMessage(baseResponse, personality);
    
    // Add context-specific details
    baseResponse = this.addContextualDetails(baseResponse, touchpoint, fitnessProfile);
    
    return baseResponse;
  }

  // Response generators for different intents
  private generatePriceResponse(): string {
    return "Entiendo que el presupuesto es importante. Nuestros programas están diseñados para ofrecer un valor excepcional. ¿Qué te parece si primero determinamos cuál sería el programa perfecto para ti, y luego vemos las opciones de inversión disponibles?";
  }

  private generateProgramResponse(): string {
    return "¡Excelente! Nuestros programas están personalizados según tus objetivos específicos. Para recomendarte el mejor enfoque, cuéntame: ¿cuál es tu principal objetivo de fitness ahora mismo?";
  }

  private generateResultsResponse(): string {
    return "¡Me encanta que preguntes sobre resultados! Tenemos casos de éxito increíbles. La clave está en la personalización - cada persona es diferente. ¿Te gustaría que te cuente sobre resultados específicos para alguien con un perfil similar al tuyo?";
  }

  private generateTimeResponse(): string {
    return "Totalmente comprensible, todos tenemos agendas ocupadas. Nuestros programas están diseñados específicamente para personas con poco tiempo. ¿Cuánto tiempo realísticamente podrías dedicar por semana?";
  }

  private generateTrustResponse(): string {
    return "Aprecio tu honestidad, es natural tener dudas. He visto muchas promesas exageradas en esta industria. Por eso nos enfocamos en resultados reales y sostenibles. ¿Qué experiencias pasadas te han hecho ser cauteloso?";
  }

  private generatePersonalResponse(): string {
    return "Absolutamente, cada situación es única. Eso es exactamente por lo que personalizo cada recomendación. Cuéntame más sobre tu situación específica - ¿qué desafíos particulares estás enfrentando?";
  }

  private generateComparisonResponse(): string {
    return "Excelente pregunta. La diferencia principal está en la personalización y el seguimiento continuo. ¿Has probado otros programas antes? Me ayudaría saber qué funcionó y qué no para ti.";
  }

  private generateReadyToBuyResponse(): string {
    return "¡Increíble! Me emociona tu determinación. Para asegurarme de que elijas el programa perfecto, déjame hacerte un par de preguntas rápidas para personalizar tu experiencia desde el día uno.";
  }

  private generateMoreInfoResponse(): string {
    return "Por supuesto, me encanta explicar los detalles. ¿Hay algún aspecto específico que te interese más? ¿Los métodos de entrenamiento, la nutrición, el seguimiento, o algo más específico?";
  }

  private generateObjectionResponse(input: string): string {
    return "Entiendo tu preocupación. Muchas personas han tenido esa misma duda inicialmente. ¿Qué específicamente te preocupa más para que podamos abordarlo directamente?";
  }

  private generateDiscoveryResponse(): string {
    return "Gracias por compartir eso conmigo. Para poder ayudarte mejor, cuéntame: ¿cuál dirías que es tu mayor desafío en este momento relacionado con tus objetivos de salud y fitness?";
  }

  // Helper methods for personalization and context
  private personalizeMessage(message: string, personality: ConversationPersonality): string {
    // Adjust tone based on personality
    if (personality.tone === 'energetic') {
      message = message.replace(/\./g, '!').replace(/,/g, ',');
    } else if (personality.tone === 'empathetic') {
      message = 'Entiendo perfectamente. ' + message;
    }
    
    return message;
  }

  private addContextualDetails(message: string, touchpoint: string, fitnessProfile?: any): string {
    // Add touchpoint-specific context
    if (touchpoint === 'lead-magnet' && message.includes('programa')) {
      message += ' Basándome en el recurso que descargaste, veo que ya tienes interés en mejorar tu situación.';
    }
    
    return message;
  }

  // Additional helper methods
  private getDiscoveryQuestions(): string[] {
    return [
      "¿Cuál es tu principal objetivo de fitness actualmente?",
      "¿Qué te ha impedido alcanzar tus objetivos hasta ahora?",
      "¿Cuánto tiempo podrías dedicar por semana?",
      "¿Has intentado otros programas antes? ¿Qué pasó?"
    ];
  }

  private getObjectionHandling(): Record<string, string> {
    return {
      price: "Entiendo la preocupación sobre el precio. Veamos el valor que obtienes...",
      time: "El tiempo es valioso. Por eso diseñamos programas eficientes...",
      skepticism: "Es natural tener dudas. Dejame mostrarte evidencia real...",
      "not_ready": "No hay problema, el timing es importante. ¿Qué necesitarías para estar listo?"
    };
  }

  private getCallToAction(): string {
    switch (this.context.touchpoint) {
      case 'landing-page':
        return "¿Te gustaría que agendemos una llamada personalizada para diseñar tu plan específico?";
      case 'lead-magnet':
        return "¿Qué tal si conversamos sobre cómo implementar esto en tu rutina específica?";
      default:
        return "¿Te interesaría conocer más detalles sobre cómo podemos ayudarte específicamente?";
    }
  }

  private getFollowUpStrategy(): string {
    return "Seguimiento personalizado basado en intereses y objeciones identificadas";
  }

  private getKeyTopics(): string[] {
    return ['goals', 'challenges', 'timeline', 'support', 'results'];
  }

  private getTransitionTriggers(): string[] {
    return ['program_interest', 'ready_to_buy', 'more_info'];
  }

  private generateFollowUpQuestions(intent: string): string[] {
    const questionMap = {
      price_inquiry: [
        "¿Qué presupuesto habías considerado?",
        "¿Prefieres opciones de pago flexibles?"
      ],
      program_interest: [
        "¿Qué tipo de ejercicio disfrutas más?",
        "¿Prefieres entrenar en casa o en gimnasio?"
      ],
      ready_to_buy: [
        "¿Cuándo te gustaría empezar?",
        "¿Tienes alguna pregunta específica antes de comenzar?"
      ]
    };
    
    return questionMap[intent] || [
      "¿Qué más te gustaría saber?",
      "¿Hay algo específico que te preocupe?"
    ];
  }

  private calculateResponseConfidence(input: string, intent: string): number {
    // Base confidence on intent clarity and conversation context
    let confidence = 0.7;
    
    // Higher confidence for clear intents
    const highConfidenceIntents = ['ready_to_buy', 'more_info', 'program_interest'];
    if (highConfidenceIntents.includes(intent)) {
      confidence += 0.2;
    }
    
    // Lower confidence for objections or skepticism
    const lowConfidenceIntents = ['skepticism', 'objection'];
    if (lowConfidenceIntents.includes(intent)) {
      confidence -= 0.3;
    }
    
    return Math.min(Math.max(confidence, 0.1), 1.0);
  }

  private shouldEscalateToHuman(intent: string, confidence: number): boolean {
    // Escalate for complex objections or low confidence
    const escalationIntents = ['skepticism', 'comparison', 'objection'];
    return escalationIntents.includes(intent) && confidence < 0.5;
  }

  // Welcome message generators by touchpoint
  private generateLandingPageWelcome(): string {
    const energy = this.context.engagementLevel === 'high' ? '¡Increíble!' : 'Hola';
    return `${energy} Veo que estás explorando nuestros programas de transformación. Soy tu consultor experto de NGX. ¿Tienes 7 minutos para conversar sobre cómo podemos ayudarte a alcanzar tus objetivos específicos?`;
  }

  private generateLeadMagnetWelcome(): string {
    return "¡Excelente! Veo que descargaste nuestro recurso. Soy tu consultor personal de NGX. El contenido que acabas de obtener es solo el comienzo. ¿Conversamos 7 minutos sobre cómo aplicar esto específicamente a tu situación?";
  }

  private generateWebinarWelcome(): string {
    return "¡Qué increíble sesión acabamos de tener! Soy tu consultor de seguimiento de NGX. Ahora que tienes toda esa información valiosa, tengo 7 minutos para ayudarte con preguntas específicas sobre tu transformación. ¿Empezamos?";
  }

  private generateExitIntentWelcome(): string {
    return "¡Espera un momento! Antes de irte, soy tu consultor experto de NGX. ¿Puedo hacerte 2 preguntas rápidas para enviarte algo realmente personalizado que podría cambiar tu perspectiva?";
  }

  private generateEmailCampaignWelcome(): string {
    const campaign = this.context.campaignData;
    return `¡Hola! Veo que interactuaste con nuestro contenido sobre ${campaign?.content || 'transformación'}. Soy tu consultor personal de NGX. ¿Conversamos 7 minutos sobre tu situación específica?`;
  }

  private generateBlogWelcome(): string {
    return "¡Hola! Veo que estás leyendo sobre fitness y bienestar. Soy tu consultor experto de NGX. ¿Te gustaría conversar 7 minutos sobre cómo aplicar estos conceptos a tu situación personal?";
  }

  private generateReturningUserWelcome(): string {
    const lastOutcome = this.context.previousConversations?.lastOutcome;
    const count = this.context.previousConversations?.count || 0;
    
    if (lastOutcome === 'follow-up') {
      return `¡Hola de nuevo! Soy tu consultor de NGX. Prometí hacer seguimiento sobre ${this.context.previousConversations?.lastTopic}. ¿Cómo te fue con lo que conversamos?`;
    }
    
    return `¡Qué gusto verte de nuevo! Esta es nuestra ${count + 1}ª conversación. ¿Hay algo específico en lo que pueda ayudarte hoy?`;
  }

  private generateGenericWelcome(): string {
    return "¡Hola! Soy tu consultor experto de NGX. Veo que estás interesado en transformar tu vida. ¿Tienes 7 minutos para una conversación personalizada que podría cambiar tu perspectiva completamente?";
  }

  // Public getters for external access
  public getCurrentStage(): string {
    return this.currentStage;
  }

  public getDetectedIntents(): string[] {
    return this.detectedIntents;
  }

  public getConversationHistory(): string[] {
    return this.conversationHistory;
  }

  public updateContext(newContext: Partial<UserContext>): void {
    this.context = { ...this.context, ...newContext };
  }
}

export default ContextualAISystem;