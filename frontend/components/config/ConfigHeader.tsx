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
      bg="bg.subtle"
      borderBottom="1px solid"
      borderColor="border.muted"
      py={4}
      position="sticky"
      top={0}
      zIndex={10}
    >
      <Container maxW="7xl" mx="auto">
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Text
              color="fg.muted"
              fontSize="2xl"
              letterSpacing="tight"
              fontWeight="1000"
            >
              Configuration
            </Text>
            <Text fontSize="sm" color="text.secondary">
              Configure your application settings
            </Text>
          </VStack>
        </HStack>
      </Container>
    </Box>
  );
}