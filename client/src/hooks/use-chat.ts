import { useState, useEffect } from "react";
import type { Message } from "@/components/playground/message";
import { fetchClient } from "@/utils/fetchClient";
import { useParams } from "react-router-dom";

export function useChat(conversationId: string) {
  const { projectId } = useParams();

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load initial conversation history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const conversation = await getConversationHistory(conversationId);
        setMessages(conversation || []);
      } catch (error) {
        console.error("Error loading conversation history:", error);
      }
    };

    loadHistory();
  }, [conversationId]);

  const getConversationHistory = async (
    conversationId: string
  ): Promise<Message[]> => {
    try {
      const response = await fetchClient(
        `/playground/conversation/${projectId}/${conversationId}`
      );
      const { metadata } = response;

      // Extract and map the history to the Message format
      const history = metadata?.history || [];
      return history.map((item: { role: string; content: string }) => ({
        id: `${Date.now()}-${Math.random()}`,
        content: item.content,
        role: item.role,
        timestamp: new Date(),
      }));
    } catch (error) {
      console.error("Error fetching conversation history:", error);
      return [];
    }
  };

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: "human",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);
    try {
      const response = await fetchClient(`/playground/conversation/chat`, {
        method: "POST",
        body: JSON.stringify({
          conversation_id: conversationId,
          message: content,
          message_type: "text",
        }),
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data,
        role: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Something went wrong. Please try again later.",
        role: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    isLoading,
    sendMessage,
  };
}
