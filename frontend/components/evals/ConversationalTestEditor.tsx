'use client';

import React, { useState } from 'react';
import {
  VStack,
  HStack,
  Box,
  Text,
  Button,
  Textarea,
  Input,
  Field,
  IconButton,
  Tabs,
  Card,
  Badge,
  Spinner,
  NumberInput,
} from '@chakra-ui/react';
import { LuTrash2, LuUser, LuBot, LuPlay, LuArrowUp, LuArrowDown } from 'react-icons/lu';
import type { Turn, TurnRole, ConversationalTestConfig } from '@/types/eval';
import { ConversationalService } from '@/services/conversational';

interface ConversationalTestEditorProps {
  /** Current conversation turns */
  turns: Turn[];
  /** Callback when turns change */
  onTurnsChange: (turns: Turn[]) => void;
  /** Conversational config for goal-based simulation */
  conversationalConfig?: ConversationalTestConfig;
  /** Callback when config changes */
  onConfigChange: (config: ConversationalTestConfig) => void;
  /** Repository name */
  repoName: string;
  /** Prompt reference for the chatbot being tested */
  promptReference: string;
  /** LLM provider for AI features */
  provider: string;
  /** LLM model for AI features */
  model: string;
  /** Whether the component is disabled */
  disabled?: boolean;
}

/**
 * Editor for conversational tests with manual turn editing and goal-based simulation.
 *
 * Features:
 * 1. Manual Turns: User can manually define conversation turns
 * 2. Goal-Based Simulation: Define user goal and let AI simulate the conversation
 */
export function ConversationalTestEditor({
  turns,
  onTurnsChange,
  conversationalConfig,
  onConfigChange,
  repoName,
  promptReference,
  provider,
  model,
  disabled = false,
}: ConversationalTestEditorProps) {
  const [activeTab, setActiveTab] = useState<'manual' | 'simulation'>('manual');
  const [isSimulating, setIsSimulating] = useState(false);

  // Manual turns mode handlers
  const handleAddTurn = (role: TurnRole) => {
    const newTurn: Turn = { role, content: '' };
    onTurnsChange([...turns, newTurn]);
  };

  const handleRemoveTurn = (index: number) => {
    const newTurns = turns.filter((_, i) => i !== index);
    onTurnsChange(newTurns);
  };

  const handleUpdateTurnContent = (index: number, content: string) => {
    const newTurns = [...turns];
    newTurns[index] = { ...newTurns[index], content };
    onTurnsChange(newTurns);
  };

  const handleMoveTurn = (index: number, direction: 'up' | 'down') => {
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= turns.length) return;

    const newTurns = [...turns];
    [newTurns[index], newTurns[newIndex]] = [newTurns[newIndex], newTurns[index]];
    onTurnsChange(newTurns);
  };

  // Goal-based simulation
  const handleSimulateConversation = async () => {
    if (!conversationalConfig?.user_goal?.trim() || !promptReference) return;

    setIsSimulating(true);
    try {
      const response = await ConversationalService.simulateConversation({
        repo_name: repoName,
        prompt_reference: promptReference,
        user_goal: conversationalConfig.user_goal,
        user_persona: conversationalConfig.user_persona,
        min_turns: conversationalConfig.min_turns || 3,
        max_turns: conversationalConfig.max_turns || 6,
        stopping_criteria: conversationalConfig.stopping_criteria,
        // Only pass provider/model if explicitly set, otherwise let backend use prompt's config
        ...(provider && { provider }),
        ...(model && { model }),
      });

      onTurnsChange(response.turns);
    } catch {
      // Error is handled by the service with notification
    } finally {
      setIsSimulating(false);
    }
  };

  // Config handlers
  const updateConfig = (updates: Partial<ConversationalTestConfig>) => {
    onConfigChange({ ...conversationalConfig, ...updates });
  };

  return (
    <VStack align="stretch" gap={4}>
      <Tabs.Root
        value={activeTab}
        onValueChange={(e) => setActiveTab(e.value as 'manual' | 'simulation')}
      >
        <Tabs.List>
          <Tabs.Trigger value="manual">Manual Turns</Tabs.Trigger>
          <Tabs.Trigger value="simulation">Goal-Based Simulation</Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="manual">
          <VStack align="stretch" gap={4} mt={4}>
            {/* Turn List */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="medium" fontSize="sm">Conversation Turns</Text>
                <HStack gap={1}>
                  <Button
                    size="xs"
                    variant="outline"
                    onClick={() => handleAddTurn('user')}
                    disabled={disabled}
                  >
                    <LuUser />
                    Add User
                  </Button>
                  <Button
                    size="xs"
                    variant="outline"
                    onClick={() => handleAddTurn('assistant')}
                    disabled={disabled}
                  >
                    <LuBot />
                    Add Assistant
                  </Button>
                </HStack>
              </HStack>

              {turns.length === 0 ? (
                <Box p={4} borderWidth="1px" borderStyle="dashed" borderRadius="md" textAlign="center">
                  <Text color="fg.muted" fontSize="sm">
                    No turns yet. Click &quot;Add User&quot; or &quot;Add Assistant&quot; to add conversation turns.
                  </Text>
                </Box>
              ) : (
                <VStack align="stretch" gap={2}>
                  {turns.map((turn, index) => (
                    <Card.Root
                      key={index}
                      size="sm"
                      borderLeftWidth="3px"
                      borderLeftColor={turn.role === 'user' ? 'blue.500' : 'green.500'}
                    >
                      <Card.Body py={2}>
                        <VStack align="stretch" gap={2}>
                          <HStack justify="space-between">
                            <HStack>
                              {turn.role === 'user' ? <LuUser size={14} /> : <LuBot size={14} />}
                              <Badge
                                colorPalette={turn.role === 'user' ? 'blue' : 'green'}
                                size="sm"
                              >
                                {turn.role === 'user' ? 'User' : 'Assistant'}
                              </Badge>
                              <Text fontSize="xs" color="fg.muted">Turn {index + 1}</Text>
                            </HStack>
                            <HStack gap={0}>
                              <IconButton
                                aria-label="Move up"
                                size="2xs"
                                variant="ghost"
                                onClick={() => handleMoveTurn(index, 'up')}
                                disabled={disabled || index === 0}
                              >
                                <LuArrowUp size={12} />
                              </IconButton>
                              <IconButton
                                aria-label="Move down"
                                size="2xs"
                                variant="ghost"
                                onClick={() => handleMoveTurn(index, 'down')}
                                disabled={disabled || index === turns.length - 1}
                              >
                                <LuArrowDown size={12} />
                              </IconButton>
                              <IconButton
                                aria-label="Remove turn"
                                size="2xs"
                                variant="ghost"
                                colorPalette="red"
                                onClick={() => handleRemoveTurn(index)}
                                disabled={disabled}
                              >
                                <LuTrash2 size={12} />
                              </IconButton>
                            </HStack>
                          </HStack>
                          <Textarea
                            value={turn.content}
                            onChange={(e) => handleUpdateTurnContent(index, e.target.value)}
                            placeholder={`Enter ${turn.role} message...`}
                            rows={2}
                            resize="vertical"
                            disabled={disabled}
                            fontSize="sm"
                          />
                        </VStack>
                      </Card.Body>
                    </Card.Root>
                  ))}
                </VStack>
              )}
            </Box>
          </VStack>
        </Tabs.Content>

        <Tabs.Content value="simulation">
          <VStack align="stretch" gap={4} mt={4}>
            <Card.Root>
              <Card.Body>
                <VStack align="stretch" gap={4}>
                  <Text fontWeight="medium" fontSize="sm">
                    Configure the simulated user persona and goal. The system will simulate a conversation
                    by having an AI play the user role while your chatbot responds.
                  </Text>

                  <Field.Root required>
                    <Field.Label fontSize="xs" fontWeight="medium">
                      User Goal <Field.RequiredIndicator />
                    </Field.Label>
                    <Textarea
                      value={conversationalConfig?.user_goal || ''}
                      onChange={(e) => updateConfig({ user_goal: e.target.value })}
                      placeholder="e.g., 'Get help with a refund for order #12345'"
                      rows={2}
                      disabled={disabled}
                    />
                    <Field.HelperText fontSize="xs">
                      What the simulated user is trying to accomplish
                    </Field.HelperText>
                  </Field.Root>

                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="medium">User Persona</Field.Label>
                    <Textarea
                      value={conversationalConfig?.user_persona || ''}
                      onChange={(e) => updateConfig({ user_persona: e.target.value })}
                      placeholder="e.g., 'A frustrated customer who has been waiting 2 weeks for their refund'"
                      rows={2}
                      disabled={disabled}
                    />
                    <Field.HelperText fontSize="xs">
                      How the simulated user should behave
                    </Field.HelperText>
                  </Field.Root>

                  <HStack gap={4}>
                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs" fontWeight="medium">Min Turns</Field.Label>
                      <NumberInput.Root
                        value={String(conversationalConfig?.min_turns || 3)}
                        onValueChange={(e) => updateConfig({ min_turns: parseInt(e.value) || 3 })}
                        min={1}
                        max={20}
                        disabled={disabled}
                      >
                        <NumberInput.Control>
                          <NumberInput.IncrementTrigger />
                          <NumberInput.DecrementTrigger />
                        </NumberInput.Control>
                        <NumberInput.Input />
                      </NumberInput.Root>
                    </Field.Root>
                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs" fontWeight="medium">Max Turns</Field.Label>
                      <NumberInput.Root
                        value={String(conversationalConfig?.max_turns || 6)}
                        onValueChange={(e) => updateConfig({ max_turns: parseInt(e.value) || 6 })}
                        min={1}
                        max={20}
                        disabled={disabled}
                      >
                        <NumberInput.Control>
                          <NumberInput.IncrementTrigger />
                          <NumberInput.DecrementTrigger />
                        </NumberInput.Control>
                        <NumberInput.Input />
                      </NumberInput.Root>
                    </Field.Root>
                  </HStack>

                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="medium">Stopping Criteria</Field.Label>
                    <Input
                      value={conversationalConfig?.stopping_criteria || ''}
                      onChange={(e) => updateConfig({ stopping_criteria: e.target.value })}
                      placeholder="e.g., 'When the user's refund request is resolved'"
                      disabled={disabled}
                    />
                    <Field.HelperText fontSize="xs">
                      When should the simulation stop
                    </Field.HelperText>
                  </Field.Root>

                  <Button
                    onClick={handleSimulateConversation}
                    disabled={disabled || isSimulating || !conversationalConfig?.user_goal?.trim() || !promptReference}
                    colorPalette="green"
                    size="md"
                  >
                    {isSimulating ? <Spinner size="sm" /> : <LuPlay />}
                    {isSimulating ? 'Simulating...' : 'Run Simulation'}
                  </Button>
                </VStack>
              </Card.Body>
            </Card.Root>

            {/* Preview of simulated turns */}
            {turns.length > 0 && (
              <Box>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                  Simulated Conversation Preview
                </Text>
                <VStack align="stretch" gap={2}>
                  {turns.map((turn, index) => (
                    <Card.Root
                      key={index}
                      size="sm"
                      borderLeftWidth="3px"
                      borderLeftColor={turn.role === 'user' ? 'blue.500' : 'green.500'}
                    >
                      <Card.Body py={2}>
                        <HStack align="start" gap={2}>
                          <Badge
                            colorPalette={turn.role === 'user' ? 'blue' : 'green'}
                            size="sm"
                          >
                            {turn.role === 'user' ? 'User' : 'Assistant'}
                          </Badge>
                          <Text fontSize="sm" flex={1}>{turn.content}</Text>
                        </HStack>
                      </Card.Body>
                    </Card.Root>
                  ))}
                </VStack>
              </Box>
            )}
          </VStack>
        </Tabs.Content>
      </Tabs.Root>
    </VStack>
  );
}
