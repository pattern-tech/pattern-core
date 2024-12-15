import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChatHistory } from "@/components/playground/chat-history";
import { ChatInput } from "@/components/playground/chat-input";
import { useChat } from "@/hooks/use-chat";
import { fetchClient } from "@/utils/fetchClient";
import { useParams } from "react-router-dom";
import sidebarClose from "@/assets/sidebarOpen.svg";
import sidebarOpen from "@/assets/sidebarClose.svg";
import addDoc from "@/assets/addDoc.svg";
import logoBlack from "@/assets/logoBlack.svg";

interface Conversation {
  id: string;
  name: string;
  project_id: string;
  deleted_at: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export function PlaygroundPage() {
  const { projectId } = useParams();
  const [selectedConversationId, setSelectedConversationId] = useState<string>("");
  const { messages, isLoading, sendMessage } = useChat(selectedConversationId);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    const getConversations = async () => {
      try {
        const response = await fetchClient(`/playground/conversation/${projectId}`);

        // Map the data to match the conversations structure
        const mappedConversations = response.data.map((conv: any) => ({
          id: conv.id,
          name: conv.name,
          project_id: conv.project_id,
          deleted_at: conv.deleted_at,
          user_id: conv.user_id,
          created_at: conv.created_at,
          updated_at: conv.updated_at,
        }));

        setConversations(mappedConversations);
      } catch (error) {
        console.error("Failed to fetch conversations:", error);
      }
    };

    getConversations();
  }, [projectId]);

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => !prev);
  };

  const handleConversationClick = (conversationId: string) => {
    setSelectedConversationId(conversationId);
  };

  const createConversation = async () => {
    try {
      const response = await fetchClient(`/playground/conversation`, {
        method: "POST",
        body: JSON.stringify({
          name: "New Conversation",
          project_id: projectId,
        }),
      });

      const newConversation = response.data;

      setConversations((prev) => [newConversation, ...prev]);
      setSelectedConversationId(newConversation.id);
    } catch (error) {
      console.error("Failed to create conversation:", error);
    }
  };

  return (
    <div className="flex">
      {/* Sidebar */}
      <div
        className={`${isSidebarCollapsed ? "w-16" : "w-64"
          } border-r border-gray-200 p-4 transition-all duration-300 ease-in-out`}
      >
        {/* Logo */}
        <div className="flex items-center justify-start mb-4">

          {!isSidebarCollapsed && (
            <img
              src={logoBlack}
              alt="Logo"
              className="h-8 w-auto"
            />
          )}

          <button
            onClick={toggleSidebar}
            className="p-2 rounded hover:bg-gray-100"
          >
            <img
              src={isSidebarCollapsed ? sidebarClose : sidebarOpen}
              alt={isSidebarCollapsed ? "Open Sidebar" : "Close Sidebar"}
              className="w-6 h-6"
            />
          </button>
        </div>

        <div className="flex items-center justify-start mb-4">

          {!isSidebarCollapsed && (
            <h2 className="text-lg font-semibold">Conversations</h2>
          )}

          <button
            onClick={createConversation}
            className="p-2 text-white rounded"
          >
            <img
              src={addDoc}
              alt="Add"
            />
          </button>
        </div>

        <ul className="space-y-2">
          {conversations.map((conv) => (
            <li
              key={conv.id}
              onClick={() => handleConversationClick(conv.id)}
              className={`cursor-pointer hover:bg-gray-100 p-2 rounded ${selectedConversationId === conv.id ? "bg-gray-200" : ""
                }`}
            >
              {isSidebarCollapsed ? conv.name[0] : conv.name}
            </li>
          ))}
        </ul>
      </div>

      {/* Main Chat Area */}
      <Card className="flex-1">
        <CardHeader>
          <CardTitle>AI Chat Playground</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ChatHistory messages={messages} />
          {selectedConversationId ? (
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
          ) : (
            <p className="text-gray-500 text-center">Please select a conversation to start chatting.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
