export interface LLMProviderModel {
  id: string;
  name: string;
}

export interface LLMProvider {
  id: string;
  name: string;
  custom_api_base: boolean;
}
