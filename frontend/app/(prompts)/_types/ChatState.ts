export interface BaseMessage {
  id: string;
  content: string;
  timestamp: Date;
}

export interface AIMessage extends BaseMessage {
  type: 'ai';
}

export interface SystemMessage extends BaseMessage {
  type: 'system';
}

export interface UserMessage extends BaseMessage {
  type: 'user';
}

export interface ToolMessage extends BaseMessage {
  type: 'tool';
  toolName: string;
  toolResult?: string | object;
}

export type ChatMessage = AIMessage | SystemMessage | UserMessage | ToolMessage;

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  selectedTools: string[];
  availableTools: string[];
}

export interface Tool {
  id: string;
  name: string;
  description: string;
}