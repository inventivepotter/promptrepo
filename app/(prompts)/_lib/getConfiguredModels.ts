import type { LLMProvider } from "@/types/LLMProvider";
import configuredModelProviders from './configuredModelProviders.json';

export const getModelOptions = () => {
  return getConfiguredProvidersNModels().flatMap(provider =>
    provider.models.map(model => ({
      value: provider.id + '/' + model.id,
      label: model.name + ` (${provider.name})`
    }))
  );
};

export const getConfiguredProvidersNModels = (): LLMProvider[] => {
  return configuredModelProviders.providers;
};
