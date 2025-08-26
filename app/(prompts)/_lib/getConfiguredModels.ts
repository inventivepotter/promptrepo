import type { Provider } from '../../(setup)/_components/LLMStep';

export const getModelOptions = () => {
  return getConfiguredProvidersNModels().flatMap(provider =>
    provider.models.map(model => ({
      value: provider.id + '/' + model.id,
      label: model.name + ` (${provider.name})`
    }))
  );
};

export const getConfiguredProvidersNModels = (): Provider[] => {
  return [
    {
      id: 'openai',
      name: 'OpenAI',
      models: [
        { id: 'gpt-4o', name: 'GPT-4o' },
        { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
      ]
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      models: [
        { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet' },
        { id: 'claude-3-haiku', name: 'Claude 3 Haiku' }
      ]
    },
    {
        id: 'google',
        name: 'Google',
        models: [
          { id: 'gemini-pro', name: 'Gemini Pro' },
          { id: 'gemini-pro-vision', name: 'Gemini Pro Vision' }
        ]
    }
  ];
};
