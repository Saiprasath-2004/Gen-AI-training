export interface ChatRequest {
    message: string;
    conversation_id?: string | null;
    latitude?: number | null;
    longitude?: number | null;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
}