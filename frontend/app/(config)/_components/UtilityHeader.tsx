'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
  Container,
} from '@chakra-ui/react';
import { LuRefreshCw, LuDownload } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';

interface UtilityHeaderProps {
  onReset: () => void;
  onExport?: () => void;
  hasConfig: boolean;
}

export function UtilityHeader({ onReset, onExport, hasConfig }: UtilityHeaderProps) {
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
      <Container maxW="100vw">
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold">
                Environment Variables Utility
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Configure your LLM provider and GitHub OAuth settings. Environment variables will automatically update as you make changes.
              </Text>
            </VStack>
          </HStack>
          {hasConfig && (
            <HStack gap={3}>
              {onExport && (
                <Button
                  variant="outline"
                  onClick={onExport}
                  size="sm"
                >
                  <HStack gap={2}>
                    <LuDownload size={16} />
                    <Text>Export .env</Text>
                  </HStack>
                </Button>
              )}
              <Button
                variant="outline"
                onClick={onReset}
                size="sm"
                colorScheme="red"
              >
                <HStack gap={2}>
                  <LuRefreshCw size={16} />
                  <Text>Reset All</Text>
                </HStack>
              </Button>
            </HStack>
          )}
        </HStack>
      </Container>
    </Box>
  );
}