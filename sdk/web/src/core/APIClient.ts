import {
  APIResponse,
  ConversationStartResponse,
  MessageResponse,
  CustomerData,
  PlatformType
} from '../types';

export interface StartConversationRequest {
  customer_data?: CustomerData;
  program_type: string;
  platform: PlatformType;
}

export class APIClient {
  private baseURL: string;
  private apiKey?: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string, apiKey?: string) {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = apiKey;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };

    if (apiKey) {
      this.defaultHeaders['Authorization'] = `Bearer ${apiKey}`;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} ${errorText}`);
    }

    const data: APIResponse<T> = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Unknown API error');
    }

    return data.data as T;
  }

  async startConversation(
    request: StartConversationRequest
  ): Promise<ConversationStartResponse> {
    return this.request<ConversationStartResponse>('/conversations/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async sendMessage(
    conversationId: string,
    message: string
  ): Promise<MessageResponse> {
    return this.request<MessageResponse>(
      `/conversations/${conversationId}/message`,
      {
        method: 'POST',
        body: JSON.stringify({ message }),
      }
    );
  }

  async endConversation(conversationId: string): Promise<void> {
    return this.request<void>(`/conversations/${conversationId}/end`, {
      method: 'POST',
    });
  }

  async getConversation(conversationId: string): Promise<any> {
    return this.request<any>(`/conversations/${conversationId}`, {
      method: 'GET',
    });
  }

  async requestHumanTransfer(conversationId: string): Promise<void> {
    return this.request<void>(
      `/conversations/${conversationId}/transfer-human`,
      {
        method: 'POST',
      }
    );
  }

  async checkHealth(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health', {
      method: 'GET',
    });
  }
}