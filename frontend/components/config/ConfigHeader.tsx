'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Box,
  Container,
} from '@chakra-ui/react';

export function ConfigHeader() {

  return (
    <Box
      py={4}
      position="sticky"
      top={0}
      zIndex={10}
      bg="bg.subtle"
    >
      <Container maxW="7xl">
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <VStack align="start" gap={1}>
              <Text 
                color="fg.muted"
                fontSize="2xl"
                letterSpacing="tight"
                fontWeight="1000"
              >
                Configuration
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