'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Text,
  Button,
  Collapsible,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { EvalResults } from './EvalResults';
import type { EvalExecutionResult } from '@/types/eval';

interface EvalExecutionHistoryProps {
  executions: EvalExecutionResult[];
}

export function EvalExecutionHistory({ executions }: EvalExecutionHistoryProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (executions.length === 0) {
    return null;
  }

  return (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>Execution History</Fieldset.Legend>
              <Fieldset.HelperText color="text.tertiary">
                Last {executions.length} execution{executions.length > 1 ? 's' : ''}
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Collapse execution history" : "Expand execution history"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {isOpen ? "Hide" : "Show"}
                </Text>
                {isOpen ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content>
            <Collapsible.Root open={isOpen}>
              <Collapsible.Content>
                <VStack gap={0} align="stretch" mt={3}>
                  {executions.map((execution, index) => (
                    <EvalResults key={execution.executed_at || index} execution={execution} />
                  ))}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}
