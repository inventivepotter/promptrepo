'use client';

import { useEffect } from 'react';
import { Box, VStack } from '@chakra-ui/react';
import { useConfigActions } from '@/stores/configStore';
import { useLoadingStore } from '@/stores/loadingStore';

interface ConfigSectionProps {
  children: React.ReactNode;
  autoLoad?: boolean;
  className?: string;
}

export const ConfigSection = ({
  children,
  autoLoad = true,
  className
}: ConfigSectionProps) => {
  const { getConfig, getHostingType, loadAvailableLLMProviders, loadAvailableRepos } = useConfigActions();
  const { showLoading, hideLoading } = useLoadingStore();

  // Initialize config data when component mounts
  useEffect(() => {
    if (autoLoad) {
      const initializeConfig = async () => {
        showLoading('Loading configuration...', 'Please wait while we load your settings');
        
        try {
          await Promise.all([
            getConfig(),
            getHostingType(),
            loadAvailableLLMProviders(),
            loadAvailableRepos(),
          ]);
        } catch (err) {
          console.error('Failed to initialize config:', err);
        } finally {
          hideLoading();
        }
      };

      initializeConfig();
    }
  }, [autoLoad, getConfig, getHostingType, loadAvailableLLMProviders, loadAvailableRepos, showLoading, hideLoading]);

  return (
    <Box className={className}>
      <VStack gap={4} align="stretch">
        {children}
      </VStack>
    </Box>
  );
};