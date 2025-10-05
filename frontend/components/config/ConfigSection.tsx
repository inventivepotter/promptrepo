'use client';

import { useEffect } from 'react';
import { Box, VStack } from '@chakra-ui/react';
import { useConfigActions } from '@/stores/configStore';

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
  const { initializeConfig } = useConfigActions();

  // Initialize config data when component mounts
  useEffect(() => {
    if (autoLoad) {
      initializeConfig(true, true);
    }
  }, [autoLoad, initializeConfig]);

  return (
    <Box className={className}>
      <VStack gap={6} align="stretch">
        {children}
      </VStack>
    </Box>
  );
};