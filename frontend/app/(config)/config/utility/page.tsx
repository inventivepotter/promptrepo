"use client"

import { Box, Container, VStack, HStack, Text, Button } from '@chakra-ui/react'
import { useEffect } from 'react'
import AuthStep from '../../_components/GithubOAuthConfigTep'
import LLMStep from '../../_components/LLMConfigStep'
import { EnvVariablesDisplay } from '../../_components/EnvVariablesDisplay'
import { UtilityHeader } from '../../_components/UtilityHeader'
import { useUtilState } from '../../_state/utilState'

export default function UtilityPage() {
  const {
    utilState,
    updateField,
    addLLMConfig,
    removeLLMConfig,
    resetAll,
    loadProviders
  } = useUtilState()

  // Load providers on mount
  useEffect(() => {
    loadProviders()
  }, [loadProviders])

  const hasAnyConfig = Boolean((utilState.githubClientId && utilState.githubClientSecret) || utilState.llmConfigs.length > 0)

  return (
    <Box width="100%">
      {/* Header */}
      <UtilityHeader
        onReset={resetAll}
        hasConfig={hasAnyConfig}
      />
      
      <Container maxW="full" py={6}>

        {/* Split Layout: Configuration (50%) | Environment Variables (50%) */}
        <HStack gap={6} align="stretch" height="calc(100vh - 250px)">
          {/* Left Side - Configuration (50%) */}
          <Box flex="0 0 50%" overflowY="auto" pr={3}>
            <VStack gap={6} align="stretch">
              {/* GitHub OAuth Configuration */}
              <AuthStep
                hostingType="organization"
                githubClientId={utilState.githubClientId}
                githubClientSecret={utilState.githubClientSecret}
                setGithubClientId={(value) => updateField('githubClientId', value)}
                setGithubClientSecret={(value) => updateField('githubClientSecret', value)}
                disabled={false}
                showEnvNote={false}
              />
              
              {/* LLM Provider Configuration */}
              <LLMStep
                selectedProvider={utilState.selectedProvider}
                setSelectedProvider={(value) => updateField('selectedProvider', value)}
                selectedModel={utilState.selectedModel}
                setSelectedModel={(value) => updateField('selectedModel', value)}
                apiKey={utilState.apiKey}
                setApiKey={(value) => updateField('apiKey', value)}
                apiBaseUrl={utilState.apiBaseUrl}
                setApiBaseUrl={(value) => updateField('apiBaseUrl', value)}
                llmConfigs={utilState.llmConfigs}
                addLLMConfig={addLLMConfig}
                removeLLMConfig={removeLLMConfig}
                disabled={false}
                availableProviders={utilState.providers.available || []}
                isLoadingProviders={utilState.providers.isLoading}
                hostingType="individual"
              />
              
            </VStack>
          </Box>

          {/* Right Side - Environment Variables (50%) */}
          <Box flex="0 0 50%" pl={3} height="100%">
            {hasAnyConfig ? (
              <VStack gap={4} align="stretch" height="100%">
                <Box flex="1" overflowY="auto" minHeight="600px">
                  <EnvVariablesDisplay
                    hostingType="organization"
                    githubClientId={utilState.githubClientId}
                    githubClientSecret={utilState.githubClientSecret}
                    llmConfigs={utilState.llmConfigs}
                  />
                </Box>
              </VStack>
            ) : (
              <Box
                p={6}
                borderWidth="1px"
                borderRadius="md"
                borderColor="border.emphasized"
                bg="bg.subtle"
                height="600px"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <VStack gap={4} align="center">
                  <Text fontSize="lg" fontWeight="bold" color="muted.foreground">
                    Environment Variables
                  </Text>
                  <Text fontSize="sm" opacity={0.7} textAlign="center">
                    Configure GitHub OAuth or add LLM providers on the left to see generated environment variables here.
                  </Text>
                </VStack>
              </Box>
            )}
          </Box>
        </HStack>
      </Container>
    </Box>
  )
}