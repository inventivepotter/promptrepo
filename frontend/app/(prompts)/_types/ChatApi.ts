import type { OpenAIMessage } from './ChatState';

export interface ChatCompletionOptions {
  provider?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string[];
  stream?: boolean;
}

export interface ChatCompletionRequest {
  messages: OpenAIMessage[];
  provider: string;
  model: string;
  prompt_id?: string;
  stream?: boolean;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string[];
}

export interface ChatCompletionChoice {
  index: number;
  message: OpenAIMessage;
  finish_reason?: string;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatCompletionChoice[];
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  inference_time_ms?: number;
}

export interface ChatCompletionStreamChoice {
  index: number;
  delta: OpenAIMessage;
  finish_reason?: string;
}

export interface ChatCompletionStreamResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: ChatCompletionStreamChoice[];
}