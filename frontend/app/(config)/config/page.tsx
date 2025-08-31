"use client"

import { Box, Container, VStack } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import HostingStep from '../_components/HostingStep'
import AuthStep from '../_components/AuthStep'
import LLMStep from '../_components/LLMStep'
import AdminConfigStep from '../_components/AdminConfigStep'
import ReposConfigStep from '../_components/ReposConfigStep'
import { useConfigState } from '../_state/configState'
import { ConfigHeader } from '../_components/ConfigHeader'
import { postConfig } from '../_lib/postConfig'
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
  } = useConfigState();

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
        'You have been logged out. Please log in to access the configuration page.'
      )
      router.push('/')
    }
  }, [isAuthenticated, authLoading, hostingType, hostingTypeLoaded, router])

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await postConfig(configState.config);
    } finally {
      setIsSaving(false);
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

  // Show loading screen while initial data is being fetched
  if (configState.isLoading) {
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

  // Show unauthorized screen if there's an error (but not for individual hosting)
  if (configState.error && !shouldSkipAuth(hostingType)) {
    return (
      <UnauthorizedScreen />
    );
  }

  // Show loading screen while saving configurations
  if (configState.isSaving) {
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
        <ConfigHeader onSave={handleSave} isLoading={configState.isSaving} />
        <Container maxW="7xl" py={6}>
          <Box mb={6}>
            <HostingStep
              hostingType={configState.config.hostingType}
              setHostingType={(type) => updateConfigField("hostingType", type)}
              disabled={configState.isSaving}
            />
          </Box>
          {/* Conditional rendering based on hosting type */}
          {/* GitHub OAuth Configuration - hidden for individual and multi-tenant */}
          {configState.config.hostingType !== 'individual' && configState.config.hostingType !== 'multi-tenant' && (
            <Box mb={6}>
              <AuthStep
                hostingType={configState.config.hostingType}
                githubClientId={configState.config.githubClientId || ''}
                githubClientSecret={configState.config.githubClientSecret || ''}
                setGithubClientId={(id) => updateConfigField("githubClientId", id)}
                setGithubClientSecret={(secret) => updateConfigField("githubClientSecret", secret)}
                disabled={configState.isSaving}
              />
            </Box>
          )}
          
          {/* LLM Provider Configuration - hidden for multi-tenant */}
          {configState.config.hostingType !== 'multi-tenant' && (
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
              />
            </Box>
          )}
          
          {/* Repository Configuration - show for all hosting types */}
          <Box mb={6}>
            <ReposConfigStep
              hostingType={configState.config.hostingType}
              disabled={configState.isSaving}
            />
          </Box>
          
          {/* Admin Configuration - hidden for individual */}
          {configState.config.hostingType !== 'individual' && (
            <Box mb={6}>
              <AdminConfigStep
                adminEmails={configState.config.adminEmails || []}
                setAdminEmails={(emails) => updateConfigField("adminEmails", emails)}
                disabled={configState.isSaving}
              />
            </Box>
          )}
        </Container>
      </VStack>
    </Box>
  )
}