export interface LLMProvider {
  id: string;
  name: string;
  models: Array<{ id: string; name: string; }>;
}
