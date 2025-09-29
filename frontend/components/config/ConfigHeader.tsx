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
      borderBottom="1px solid"
      borderColor="border.muted"
      py={2}
      position="sticky"
      top={0}
      zIndex={10}
      shadow="sm"
    >
      <Container maxW="7xl">
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold">
                Setup{' '} 
                <Text as="span" color="primary.500">
                  Registry
                </Text>
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