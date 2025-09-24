'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
  Container,
  Spinner,
} from '@chakra-ui/react';
import { LuSave } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';

interface ConfigHeaderProps {
  onSave: () => void;
  isLoading?: boolean;
}

export function ConfigHeader({ onSave, isLoading = false }: ConfigHeaderProps) {
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
          <Button
            variant="solid"
            onClick={onSave}
            size="sm"
            disabled={isLoading}
            loading={isLoading}
          >
            <HStack gap={2}>
              {isLoading ? (
                <Spinner size="sm" />
              ) : (
                <LuSave size={16} />
              )}
              <Text>
                {isLoading ? 'Saving...' : 'Save Configuration'}
              </Text>
            </HStack>
          </Button>
        </HStack>
      </Container>
    </Box>
  );
}