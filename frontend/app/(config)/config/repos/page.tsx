"use client"

import { Box, Container, VStack, Text } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ReposConfigStep from '../../_components/ReposConfigStep'
import { ConfigHeader } from '../../_components/ConfigHeader'
import { LoadingOverlay } from '@/components/LoadingOverlay'
import { UnauthorizedScreen } from '@/components/UnauthorizedScreen'
import { useAuth } from '@/app/(auth)/_components/AuthProvider'
import { infoNotification } from '@/lib/notifications'
import { getHostingType, shouldSkipAuth } from '@/utils/hostingType'

export default function ReposConfigPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const [hostingType, setHostingType] = useState<string>('')
  const [hostingTypeLoaded, setHostingTypeLoaded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
        'You are logged out. Please log in to access the repository configuration page.'
      )
      router.push('/')
    }
  }, [isAuthenticated, authLoading, hostingType, hostingTypeLoaded, router])

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // TODO: Implement repos configuration save logic
      console.log('Saving repos configuration...');
      // This will be implemented when we add state management for repos
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
          subtitle="Please wait while we initialize the repository configuration"
        />
      </Box>
    );
  }

  // Show loading screen while initial data is being fetched
  if (isLoading) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Loading Repository Configuration..."
          subtitle="Please wait while we load your repository settings"
        />
      </Box>
    );
  }

  // Show unauthorized screen if there's an error (but not for individual hosting)
  if (error && !shouldSkipAuth(hostingType)) {
    return (
      <UnauthorizedScreen />
    );
  }

  // Show loading screen while saving configurations
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
          title="Saving Repository Configuration..."
          subtitle="Please wait while we save your repository settings"
        />
      </Box>
    );
  }

  return (
    <Box width="100%">
      <VStack gap={8} align="stretch">
        <ConfigHeader
          onSave={handleSave}
          isLoading={isSaving}
          hostingType={hostingType}
        />
        <Container maxW="7xl" py={6}>
          {/* Repository Configuration */}
          <Box mb={6}>
            <ReposConfigStep
              hostingType={hostingType}
              disabled={isSaving}
            />
          </Box>
        </Container>
      </VStack>
    </Box>
  )
}