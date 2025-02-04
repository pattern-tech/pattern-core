import { ScrollArea } from "@/components/ui/scroll-area";
import { Message } from "./message";
import type { Message as MessageType } from "./message";

interface ChatHistoryProps {
  messages: MessageType[];
}

export function ChatHistory({ messages }: ChatHistoryProps) {
  return (
    <ScrollArea className="h-[600px] pr-4">
      <div className="space-y-4">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  );
}