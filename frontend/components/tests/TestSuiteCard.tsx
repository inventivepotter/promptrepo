'use client';

import React from 'react';
import {
  Card,
  HStack,
  VStack,
  Text,
  Badge,
  Box,
  Icon,
} from '@chakra-ui/react';
import { FaCheckCircle, FaTimesCircle, FaClock } from 'react-icons/fa';
import type { TestSuiteSummary } from '@/types/test';

interface TestSuiteCardProps {
  suite: TestSuiteSummary;
  onView: (suiteName: string) => void;
}

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} month${months > 1 ? 's' : ''} ago`;
  const years = Math.floor(months / 12);
  return `${years} year${years > 1 ? 's' : ''} ago`;
};

export function TestSuiteCard({ suite, onView }: TestSuiteCardProps) {
  const handleClick = () => {
    onView(suite.name);
  };

  const getStatusColor = () => {
    if (suite.last_execution_passed === null) return 'gray';
    return suite.last_execution_passed ? 'green' : 'red';
  };

  const getStatusIcon = () => {
    if (suite.last_execution_passed === null) return FaClock;
    return suite.last_execution_passed ? FaCheckCircle : FaTimesCircle;
  };

  return (
    <Card.Root
      onClick={handleClick}
      cursor="pointer"
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-2px)',
        shadow: 'md',
        borderColor: 'primary.500',
      }}
      borderWidth="1px"
      borderColor="transparent"
    >
      <Card.Body>
        <VStack align="stretch" gap={4}>
          {/* Suite name and status */}
          <HStack justify="space-between" align="start">
            <VStack align="start" gap={1} flex={1}>
              <Text fontSize="lg" fontWeight="semibold" lineClamp={1}>
                {suite.name}
              </Text>
              {suite.description && (
                <Text fontSize="sm" color="fg.subtle" lineClamp={2}>
                  {suite.description}
                </Text>
              )}
            </VStack>
            <Icon
              as={getStatusIcon()}
              boxSize={5}
              color={`${getStatusColor()}.500`}
            />
          </HStack>

          {/* Test count and tags */}
          <HStack justify="space-between" align="center">
            <Badge colorScheme="blue" variant="subtle">
              {suite.test_count} {suite.test_count === 1 ? 'test' : 'tests'}
            </Badge>
            {suite.tags.length > 0 && (
              <HStack gap={1}>
                {suite.tags.slice(0, 2).map((tag) => (
                  <Badge key={tag} variant="outline" size="sm">
                    {tag}
                  </Badge>
                ))}
                {suite.tags.length > 2 && (
                  <Badge variant="outline" size="sm">
                    +{suite.tags.length - 2}
                  </Badge>
                )}
              </HStack>
            )}
          </HStack>

          {/* Last execution info */}
          {suite.last_execution && (
            <Box pt={2} borderTopWidth="1px" borderTopColor="bg.muted">
              <Text fontSize="xs" color="fg.subtle">
                Last run: {formatTimeAgo(suite.last_execution)}
              </Text>
            </Box>
          )}

          {!suite.last_execution && (
            <Box pt={2} borderTopWidth="1px" borderTopColor="bg.muted">
              <Text fontSize="xs" color="fg.subtle">
                Never executed
              </Text>
            </Box>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}