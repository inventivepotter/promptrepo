// OpenAI standard message format
export interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_call_id?: string;
  tool_calls?: Array<{
    id: string;
    type: 'function';
    function: {
      name: string;
      arguments: string;
    };
  }>;
}

// Internal chat message format (extends OpenAI with UI-specific fields)
export interface ChatMessage extends OpenAIMessage {
  id: string;
  timestamp: Date;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  inferenceTimeMs?: number; // Time taken for inference in milliseconds
}


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