'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
} from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';

interface PromptCommit {
  id: string;
  message: string;
  author: string;
  timestamp: string;
  changes: {
    added: number;
    deleted: number;
  };
  hash: string;
  isLatest?: boolean;
}

interface PromptTimelineProps {
  commits: PromptCommit[];
}

function TimelineNodeCompact({ commit, isLatest }: { commit: PromptCommit; isLatest: boolean }) {

  return (
    <Box position="relative" mb={8} display="flex" flexDirection="column" alignItems="center">
      {/* Dot Node - centered */}
      <Box position="relative" zIndex={2}>
        {isLatest ? (
          <Box
            width="15px"
            height="15px"
            marginBottom="90vh"
            borderRadius="full"
            bg="blue.500"
            border="2px solid"
            borderColor="gray.200"
            animation="pulse 1s infinite"
          />
        ) : (
          <Box
            width="14px"
            height="14px"
            borderRadius="full"
            bg="blue.500"
            border="2px solid"
            borderColor="gray.200"
          />
        )}
      </Box>

      {/* Commit Details - positioned below the dot (no text labels) */}
    </Box>
  );
}

export function PromptTimeline({ commits }: PromptTimelineProps) {
  const lineColor = useColorModeValue('gray.300', 'gray.600');

  return (
    <Box position="relative" height="100%" width="100%">
      {/* Continuous Timeline Line - extends full height */}
      <Box
        position="absolute"
        left="50%"
        top="12%"
        width="2px"
        height="100%"
        bg={lineColor}
        zIndex={1}
        transform="translateX(-50%)"
      >
        {/* Timeline Nodes - positioned to show below the basic information box */}
        <Box position="relative" mt="-15px">
          {commits.map((commit, index) => (
            <TimelineNodeCompact
              key={commit.id}
              commit={commit}
              isLatest={commit.isLatest || index === 0}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
}