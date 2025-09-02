"use client"

import { Box, Container, VStack, Text, Link, HStack } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import NextLink from 'next/link'
import { LuExternalLink } from 'react-icons/lu'
import HostingStep from '../_components/HostingConfigStep'
import AuthStep from '../_components/GithubOAuthConfigTep'
import LLMStep from '../_components/LLMConfigStep'
import ReposConfigStep from '../_components/ReposConfigStep'
import { useConfigState } from '../_state/configState'
import { ConfigHeader } from '../_components/ConfigHeader'
import { postConfig } from '../_lib/postConfig'
import { postRepos } from '../_lib/postRepos'
import { LoadingOverlay } from '@/components/LoadingOverlay'
import { UnauthorizedScreen } from '@/components/UnauthorizedScreen'
import { useAuth } from '@/app/(auth)/_components/AuthProvider'
import { infoNotification } from '@/lib/notifications'
import { getHostingType, shouldSkipAuth } from '@/utils/hostingType'

export default function ConfigPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const [hostingType, setHostingType] = useState<string>('')
  const [hostingTypeLoaded, setHostingTypeLoaded] = useState(false)
  
  const {
    configState,
    setConfigState: updateConfigState,
    updateConfigField,
    updateCurrentStepField,
    addLLMConfig: addLLMConfigAction,
    removeLLMConfig: removeLLMConfigAction,
    setIsLoading,
    setIsSaving,
    updateConfiguredRepos,
  } = useConfigState();

  // For non-individual hosting, manage saving state locally
  const [localIsSaving, setLocalIsSaving] = useState(false);

  // Load hosting type on mount
  useEffect(() => {
    const loadHostingType = async () => {
      try {
        const type = await getHostingType();
        setHostingType(type);
      } catch (error) {
        console.warn('Failed to load hosting type:', error);
        setHostingType('individual');
      } finally {
        setHostingTypeLoaded(true);
      }
    };
    
    loadHostingType();
  }, []);

  // Handle authentication state changes
  useEffect(() => {
    // Skip if still loading auth state or hosting type
    if (authLoading || !hostingTypeLoaded) return;
    
    // Skip authentication checks for individual hosting
    if (shouldSkipAuth(hostingType)) return;
    
    // Redirect to home if not authenticated (only for non-individual hosting)
    if (!isAuthenticated) {
      infoNotification(
        'Logged Out',
        'You are logged out. Please log in to access the configuration page.'
      )
      router.push('/')
    }
  }, [isAuthenticated, authLoading, hostingType, hostingTypeLoaded, router])

  const handleSave = async () => {
    if (hostingType === 'individual') {
      setIsSaving(true);
      try {
        await postConfig(configState.config);
      } finally {
        setIsSaving(false);
      }
    } else {
      // For org/multi-tenant, save repositories using different endpoint
      setLocalIsSaving(true);
      try {
        await postRepos(configState.repos.configured);
      } finally {
        setLocalIsSaving(false);
      }
    }
  };

  // Show loading screen while authentication is being checked
  if (authLoading || !hostingTypeLoaded) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Loading..."
          subtitle="Please wait while we initialize the configuration"
        />
      </Box>
    );
  }

  // Show loading screen while initial data is being fetched (only for individual hosting)
  if (hostingType === 'individual' && configState.isLoading) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Loading Configuration..."
          subtitle="Please wait while we load your settings"
        />
      </Box>
    );
  }

  // Show unauthorized screen if there's an error (only for individual hosting)
  if (hostingType === 'individual' && configState.error && !shouldSkipAuth(hostingType)) {
    return (
      <UnauthorizedScreen />
    );
  }

  // Show loading screen while saving configurations
  const isSaving = hostingType === 'individual' ? configState.isSaving : localIsSaving;
  if (isSaving) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Saving Configuration..."
          subtitle="Please wait while we save your settings"
        />
      </Box>
    );
  }

  return (
    <Box width="100%">
      <VStack gap={8} align="stretch">
        <ConfigHeader
          onSave={handleSave}
          isLoading={hostingType === 'individual' ? configState.isSaving : localIsSaving}
          hostingType={hostingType === 'individual' ? configState.config.hostingType : hostingType}
        />
        <Container maxW="7xl" py={6}>
          {/* Conditional rendering based on hosting type */}
          {configState.config.hostingType === 'individual' ? (
            <>
              {/* Individual hosting: Show hosting step and all configuration sections */}
              <Box mb={6}>
                <HostingStep
                  hostingType={configState.config.hostingType}
                  setHostingType={(type) => updateConfigField("hostingType", type)}
                  disabled={configState.isSaving}
                />
              </Box>
              
              {/* GitHub OAuth Configuration */}
              <Box mb={6}>
                <AuthStep
                  hostingType={configState.config.hostingType}
                  githubClientId={configState.config.githubClientId || ''}
                  githubClientSecret={configState.config.githubClientSecret || ''}
                  setGithubClientId={(id) => updateConfigField("githubClientId", id)}
                  setGithubClientSecret={(secret) => updateConfigField("githubClientSecret", secret)}
                  disabled={configState.isSaving}
                  showEnvNote={true}
                />
              </Box>
              
              {/* LLM Provider Configuration */}
              <Box mb={6}>
                <LLMStep
                  selectedProvider={configState.currentStep.selectedProvider || ''}
                  setSelectedProvider={(provider: string) => updateCurrentStepField('selectedProvider', provider)}
                  selectedModel={configState.currentStep.selectedModel || ''}
                  setSelectedModel={(model: string) => updateCurrentStepField('selectedModel', model)}
                  apiKey={configState.currentStep.apiKey || ''}
                  setApiKey={(key: string) => updateCurrentStepField('apiKey', key)}
                  apiBaseUrl={configState.currentStep.apiBaseUrl || ''}
                  setApiBaseUrl={(url: string) => updateCurrentStepField('apiBaseUrl', url)}
                  llmConfigs={configState.config.llmConfigs || []}
                  addLLMConfig={addLLMConfigAction}
                  removeLLMConfig={removeLLMConfigAction}
                  disabled={configState.isSaving}
                  availableProviders={configState.providers.available || []}
                  isLoadingProviders={configState.providers.isLoading}
                  hostingType={configState.config.hostingType}
                />
              </Box>
              
              {/* Repository Configuration */}
              <Box mb={6}>
                <ReposConfigStep
                  hostingType={configState.config.hostingType}
                  disabled={configState.isSaving}
                  repos={configState.repos.available}
                  configuredRepos={configState.repos.configured}
                  isLoadingRepos={configState.repos.isLoading}
                  isLoadingConfiguredRepos={configState.repos.isLoading}
                  updateConfiguredRepos={updateConfiguredRepos}
                />
              </Box>
              
            </>
          ) : (
            <>
              {/* Non-individual hosting: Show only repository configuration */}
              <Box mb={6}>
                <ReposConfigStep
                  hostingType={hostingType}
                  disabled={localIsSaving}
                  repos={configState.repos.available}
                  configuredRepos={configState.repos.configured}
                  isLoadingRepos={configState.repos.isLoading}
                  isLoadingConfiguredRepos={configState.repos.isLoading}
                  updateConfiguredRepos={updateConfiguredRepos}
                />
              </Box>
            </>
          )}
          
          {/* Utility Config Link Note */}
          <Box
            mt={6}
            p={4}
            borderWidth="1px"
            borderRadius="md"
            borderColor="border.emphasized"
            bg="transparent"
          >
            <HStack gap={2} align="flex-start">
              <Text fontSize="sm" color="muted.foreground" opacity={0.7}>
                <strong>Note:</strong> Configurations must be set as ENV (if in k8s then as Kubernetes Secrets) at the time service start, this
              </Text>
              <Link
                as={NextLink}
                href="/config/utility"
                fontSize="sm"
                color="muted.foreground"
                opacity={0.8}
                _hover={{ opacity: 1, textDecoration: 'underline' }}
                display="flex"
                alignItems="center"
                gap={1}
                flexShrink={0}
              >
                <Text>utils page</Text>
                <LuExternalLink size={12} />
              </Link>
              <Text fontSize="sm" color="muted.foreground" opacity={0.7}>
                can help you come up with ENV.
              </Text>
            </HStack>
          </Box>
        </Container>
      </VStack>
    </Box>
  )
}