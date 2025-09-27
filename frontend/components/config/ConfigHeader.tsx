'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Box,
  Container,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';

export function ConfigHeader() {
  const headerBg = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box
      bg={headerBg}
      borderBottom="1px solid"
      borderColor="border.muted"
      py={4}
      position="sticky"
      top={0}
      zIndex={10}
    >
      <Container maxW="7xl">
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold">
                Setup Configuration
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Configure your application settings
              </Text>
            </VStack>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
}