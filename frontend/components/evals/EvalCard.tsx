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
  IconButton,
} from '@chakra-ui/react';
import { FaCheckCircle, FaTimesCircle, FaClock, FaTrash } from 'react-icons/fa';
import type { EvalSummary } from '@/types/eval';

interface EvalCardProps {
  eval: EvalSummary;
  onView: (filePath: string) => void;
  onDelete?: (filePath: string) => void;
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

export function EvalCard({ eval: evalMeta, onView, onDelete }: EvalCardProps) {
  // Access the nested eval definition
  const evalDef = evalMeta.eval;
  
  const handleClick = () => {
    onView(evalMeta.file_path);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(evalMeta.file_path);
    }
  };

  // EvalMeta doesn't have execution info - just show pending status for now
  const getStatusColor = () => {
    return 'gray';
  };

  const getStatusIcon = () => {
    return FaClock;
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
          {/* Eval name and status */}
          <HStack justify="space-between" align="start">
            <VStack align="start" gap={1} flex={1}>
              <Text fontSize="lg" fontWeight="semibold" lineClamp={1}>
                {evalDef.name}
              </Text>
              {evalDef.description && (
                <Text fontSize="sm" color="fg.subtle" lineClamp={2}>
                  {evalDef.description}
                </Text>
              )}
            </VStack>
            <HStack gap={2}>
              <Icon
                as={getStatusIcon()}
                boxSize={5}
                color={`${getStatusColor()}.500`}
              />
              {onDelete && (
                <IconButton
                  aria-label="Delete eval"
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={handleDeleteClick}
                >
                  <FaTrash />
                </IconButton>
              )}
            </HStack>
          </HStack>

          {/* Test count and tags */}
          <HStack justify="space-between" align="center">
            <Badge colorScheme="blue" variant="subtle">
              {evalDef.tests?.length ?? 0} {(evalDef.tests?.length ?? 0) === 1 ? 'test' : 'tests'}
            </Badge>
            {(evalDef.tags?.length ?? 0) > 0 && (
              <HStack gap={1}>
                {evalDef.tags?.slice(0, 2).map((tag) => (
                  <Badge key={tag} variant="outline" size="sm">
                    {tag}
                  </Badge>
                ))}
                {(evalDef.tags?.length ?? 0) > 2 && (
                  <Badge variant="outline" size="sm">
                    +{(evalDef.tags?.length ?? 0) - 2}
                  </Badge>
                )}
              </HStack>
            )}
          </HStack>

          {/* Repository info */}
          <Box pt={2} borderTopWidth="1px" borderTopColor="bg.muted">
            <Text fontSize="xs" color="fg.subtle">
              {evalMeta.file_path}
            </Text>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}