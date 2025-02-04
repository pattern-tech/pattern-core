import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import ReactMarkdown from 'react-markdown';

export interface Message {
  id: string;
  content: string;
  role: 'human' | 'ai';
  timestamp: Date;
}

interface MessageProps {
  message: Message;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'human';

  return (
    <div className={cn("flex gap-3 mb-4", isUser && "flex-row-reverse")}>
      <Avatar className="h-8 w-8">
        {isUser ? (
          <>
            <AvatarImage src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80" />
            <AvatarFallback>U</AvatarFallback>
          </>
        ) : (
          <>
            <AvatarImage src="/bot-avatar.png" />
            <AvatarFallback>AI</AvatarFallback>
          </>
        )}
      </Avatar>
      <Card className={cn(
        "px-4 py-3 max-w-[80%]",
        isUser ? "bg-primary text-primary-foreground" : "bg-muted"
      )}>
        <ReactMarkdown>{message.content}</ReactMarkdown>
        <time className="text-xs opacity-70 mt-1 block">
          {new Date(message.timestamp).toLocaleTimeString()}
        </time>
      </Card>
    </div>
  );
}