'use client';

import React from 'react';
import {
  Box,
  HStack,
  Text,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { CommitInfo } from '@/types/Prompt';

interface PromptTimelineProps {
  commits: (CommitInfo & { id?: string; isLatest?: boolean })[];
}

function TimelineNodeCompact({ commit, isLatest }: { commit: CommitInfo & { id?: string; isLatest?: boolean }; isLatest: boolean }) {
  const textColor = useColorModeValue('gray.700', 'gray.300');
  const metaColor = useColorModeValue('gray.500', 'gray.400');
  
  return (
    <Box position="relative" mb={8}>
      {/* Container with dot and content side by side */}
      <HStack gap={4} align="flex-start">
        {/* Dot Node */}
        <Box
          width={isLatest ? "15px" : "14px"}
          height={isLatest ? "15px" : "14px"}
          borderRadius="full"
          bg="bg.emphasized"
          border="2px solid"
          borderColor="bg.muted"
          animation={isLatest ? "pulse 1s infinite" : undefined}
          flexShrink={0}
          mt="2px"
          ml="-6px"
          mb={isLatest ? "95vh" : "12vh"}
        />
        
        {/* Commit Details - positioned to the right of dot */}
        {!isLatest && (
          <Box
            mt="-2px"
            minW={100}
          >
            {/* Commit Message */}
            <Text 
              fontFamily="mono"
              fontSize="xs"
              color="bg.emphasis"
              fontWeight="semibold"
            >
              {commit.commit_id.substring(0, 7)}
            </Text>
            <Text
              fontSize="xs"
              color={textColor}
            >
              {commit.message}
            </Text>

            {/* Time elapsed since commit */}
            <Text fontSize="xs" color={metaColor} mt={1}>
              {(() => {
                const now = new Date();
                const commitDate = new Date(commit.timestamp);
                const diffMs = now.getTime() - commitDate.getTime();
                const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                
                if (diffDays > 0) {
                  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
                } else if (diffHours > 0) {
                  return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
                } else if (diffMinutes > 0) {
                  return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
                } else {
                  return 'Just now';
                }
              })()}
            </Text>
          </Box>
        )}
      </HStack>
    </Box>
  );
}

export function PromptTimeline({ commits }: PromptTimelineProps) {
  const lineColor = useColorModeValue('gray.300', 'gray.600');

  return (
    <Box position="relative" height="120%" width="100%">
      {/* Continuous Timeline Line - extends full height */}
      <Box
        position="absolute"
        left="50%"
        top="12%"
        width="2px"
        height="85%"
        bg={lineColor}
        zIndex={1}
        transform="translateX(-50%)"
      >
        {/* Timeline Nodes - positioned to show below the basic information box */}
        <Box position="relative" mt="-15px">
          {commits.map((commit, index) => (
            <TimelineNodeCompact
              key={commit.id || commit.commit_id || index}
              commit={commit}
              isLatest={commit.isLatest || index === 0}
            />
          ))}
        </Box>
      </Box>
    </Box>
  );
}