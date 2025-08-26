"use client"

import { Container, VStack, Box } from '@chakra-ui/react'
import HostingStep from '../_components/HostingStep'
import AuthStep from '../_components/AuthStep'
import LLMStep from '../_components/LLMStep'
import Configurations from '../_components/Configurations'
import { useConfigState } from '../_state/configState'


export default function SetupPage() {
  const {
    configState,
    updateHostingType,
    updateGithubClientId,
    updateGithubClientSecret,
    updateCurrentStepField,
    addLLMConfig: addLLMConfigAction,
    removeLLMConfig: removeLLMConfigAction,
  } = useConfigState();

  return (
    <Container width="100%" marginLeft={0} py={8}>
      <VStack gap={8} align="stretch">
        <HostingStep
          hostingType={configState.hostingType}
          setHostingType={updateHostingType}
        />
        <AuthStep
          hostingType={configState.hostingType}
          githubClientId={configState.githubClientId}
          githubClientSecret={configState.githubClientSecret}
          setGithubClientId={updateGithubClientId}
          setGithubClientSecret={updateGithubClientSecret}
        />
        <LLMStep
          selectedProvider={configState.currentStep.selectedProvider}
          setSelectedProvider={(provider: string) => updateCurrentStepField('selectedProvider', provider)}
          selectedModel={configState.currentStep.selectedModel}
          setSelectedModel={(model: string) => updateCurrentStepField('selectedModel', model)}
          apiKey={configState.currentStep.apiKey}
          setApiKey={(key: string) => updateCurrentStepField('apiKey', key)}
          llmConfigs={configState.llmConfigs}
          addLLMConfig={addLLMConfigAction}
          removeLLMConfig={removeLLMConfigAction}
          downloadEnvFile={() => {
            let envContent = '# Generated Environment Configuration\n\n'
            envContent += `HOSTING_TYPE=${configState.hostingType}\n\n`
            if (configState.hostingType === 'multi-user') {
              envContent += '# GitHub OAuth Configuration\n'
              envContent += `GITHUB_CLIENT_ID=${configState.githubClientId}\n`
              envContent += `GITHUB_CLIENT_SECRET=${configState.githubClientSecret}\n\n`
            }
            envContent += '# LLM Provider Configurations\n'
            configState.llmConfigs.forEach((config) => {
              const providerKey = config.provider.toUpperCase()
              envContent += `${providerKey}_API_KEY=${config.apiKey}\n`
              envContent += `${providerKey}_MODEL=${config.model}\n`
            })
            const blob = new Blob([envContent], { type: 'text/plain' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = '.env'
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
          }}
        />
        <Configurations downloadEnvFile={() => {}} />
      </VStack>
    </Container>
  )
}