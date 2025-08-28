'use client';

import React from 'react';
import {
  Box,
  VStack,
  Spinner,
  Text,
} from '@chakra-ui/react';

interface LoadingOverlayProps {
  isVisible: boolean;
  title?: string;
  subtitle?: string;
}

export function LoadingOverlay({ 
  isVisible, 
  title = "Processing...", 
  subtitle = "Please wait while we process your request" 
}: LoadingOverlayProps) {
  if (!isVisible) return null;

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="rgba(0, 0, 0, 0.5)"
      zIndex={9999}
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Box
        bg="white"
        _dark={{ bg: "gray.800" }}
        p={8}
        borderRadius="lg"
        boxShadow="xl"
        textAlign="center"
        minW="300px"
      >
        <VStack gap={4}>
          <Spinner size="lg" color="blue.500" />
          <Text fontSize="lg" fontWeight="medium">
            {title}
          </Text>
          <Text fontSize="sm" opacity={0.7}>
            {subtitle}
          </Text>
        </VStack>
      </Box>
    </Box>
  );
}