import type {
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationSummary
} from "../types/api";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function askChat(
  request: ChatRequest,
): Promise<ChatResponse> {
  const response = await fetch(
    `${API_BASE_URL}/chat/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error("Failed to get advisor response.");
  }

  return response.json();
}

export async function getConversation(
  conversationId: string,
): Promise<Conversation> {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations/${conversationId}`,
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Conversation not found.");
    }

    throw new Error("Failed to load conversation.");
  }

  return response.json();
}

export async function getConversations(): Promise<
  ConversationSummary[]
> {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations`,
  );

  if (!response.ok) {
    throw new Error("Failed to load conversations.");
  }

  return response.json();
}