import { useState, useEffect } from "react";
import type { SubmitEvent } from "react";
import {
  CloudSun,
  MessageSquarePlus,
  Send,
  User,
} from "lucide-react";

import { 
    askChat,
    getConversations,
    getConversation,
 } from "../services/api";
import type {
  ConversationSummary,
  Message,
} from "../types/api";

export function ChatPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    async function loadConversations() {
        setIsLoadingConversations(true);

        try {
            const data = await getConversations();
            setConversations(data);
        } catch (err) {
        console.error(
            "Failed to load conversations:",
            err,
        );
        } finally {
            setIsLoadingConversations(false);
        }
    }

    loadConversations();
    }, []);

  async function getCurrentLocation(): Promise<{
    latitude: number;
    longitude: number;
  } | null> {
    if (!navigator.geolocation) {
      return null;
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.warn(
            "Unable to get current location:",
            error.code,
            error.message,
          );

          resolve(null);
        },
        {
          enableHighAccuracy: false,
          timeout: 10000,
          maximumAge: 300000,
        },
      );
    });
  }

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    setError(null);
    setIsLoading(true);

    const temporaryUserMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      temporaryUserMessage,
    ]);

    setMessage("");

    try {
      const currentLocation =
        await getCurrentLocation();

      const response = await askChat({
        message: trimmedMessage,
        conversation_id: conversationId ?? undefined,
        latitude: currentLocation?.latitude,
        longitude: currentLocation?.longitude,
      });

      setConversationId(response.conversation_id);

      const updatedConversations = await getConversations();

    setConversations(updatedConversations);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        created_at: new Date().toISOString(),
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function startNewConversation() {
    setConversationId(null);
    setMessages([]);
    setMessage("");
    setError(null);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <CloudSun size={20} />
          </div>

          <div>
            <h1>Weather Advisor</h1>
            <span>Activity intelligence</span>
          </div>
        </div>

        <button
          className="new-chat-button"
          onClick={startNewConversation}
        >
          <MessageSquarePlus size={18} />
          <span>New conversation</span>
        </button>

        <div className="conversation-section">
          <p className="section-label">
            CONVERSATIONS
          </p>

          {isLoadingConversations ? (
            <div className="empty-conversations">
                <p>Loading conversations...</p>
            </div>
            ) : conversations.length === 0 ? (
            <div className="empty-conversations">
                <MessageSquarePlus size={20} />
                <p>
                Your conversations will appear here.
                </p>
            </div>
            ) : (
            <div className="conversation-list">
                {conversations.map((conversation) => (
                <button
                    key={conversation.id}
                    className={`conversation-item ${
                    conversation.id === conversationId
                        ? "active"
                        : ""
                    }`}
                    onClick={async () => {
                    try {
                        const data = await getConversation(
                        conversation.id,
                        );

                        setConversationId(data.id);
                        setMessages(data.messages);
                        setError(null);
                    } catch (err) {
                        setError(
                        err instanceof Error
                            ? err.message
                            : "Failed to load conversation.",
                        );
                    }
                    }}
                >
                    <MessageSquarePlus size={16} />

                    <span>
                        Conversation{" "}
                        {conversation.id.slice(0, 8)}`
                    </span>
                </button>
                ))}
            </div>
            )}
        </div>

        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Advisor online</span>
        </div>
      </aside>

      <section className="chat-area">
        <header className="chat-header">
          <div>
            <p className="eyebrow">
              ACTIVITY ADVISOR
            </p>

            <h2>
              {conversationId
                ? "Your activity plan"
                : "What are you planning?"}
            </h2>
          </div>

          <div className="header-status">
            <span className="status-dot" />
            {isLoading ? "Thinking..." : "Ready"}
          </div>
        </header>

        <div className="chat-content">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">
                <CloudSun size={30} />
              </div>

              <h3>
                Plan your activity with confidence.
              </h3>

              <p>
                Ask about an outdoor activity and I'll
                check the conditions and help you decide
                whether it's a good time to go.
              </p>

              <div className="suggestions">
                <button
                  onClick={() =>
                    setMessage(
                      "Can I go mountain biking tomorrow at 6 AM?",
                    )
                  }
                >
                  Mountain biking tomorrow
                </button>

                <button
                  onClick={() =>
                    setMessage(
                      "Is it a good time to go for a run?",
                    )
                  }
                >
                  Go for a run
                </button>

                <button
                  onClick={() =>
                    setMessage(
                      "Can I go hiking this weekend?",
                    )
                  }
                >
                  Hiking this weekend
                </button>
              </div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((item) => (
                <div
                  className={`message ${
                    item.role === "user"
                      ? "message-user"
                      : "message-assistant"
                  }`}
                  key={item.id}
                >
                  <div className="message-avatar">
                    {item.role === "user" ? (
                      <User size={16} />
                    ) : (
                      <CloudSun size={16} />
                    )}
                  </div>

                  <div className="message-body">
                    <span className="message-role">
                      {item.role === "user"
                        ? "You"
                        : "Weather Advisor"}
                    </span>

                    <div className="message-content">
                      {item.content}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message message-assistant">
                  <div className="message-avatar">
                    <CloudSun size={16} />
                  </div>

                  <div className="message-body">
                    <span className="message-role">
                      Weather Advisor
                    </span>

                    <div className="typing">
                      Checking conditions...
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="composer-wrapper">
          <form
            className="composer"
            onSubmit={handleSubmit}
          >
            <textarea
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              placeholder="Ask about an activity..."
              rows={1}
              disabled={isLoading}
            />

            <button
              type="submit"
              disabled={
                !message.trim() || isLoading
              }
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </form>

          <p className="composer-hint">
            Weather data is used to assess outdoor
            conditions.
          </p>
        </div>
      </section>
    </main>
  );
}