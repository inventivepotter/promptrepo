'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, Button, VStack, HStack, Input, Textarea, Field, Portal, Text, Card, Group } from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';
import { LuMessageSquare, LuMessagesSquare } from 'react-icons/lu';
import { TemplateVariableEditor } from './TemplateVariableEditor';
import { PromptSelector } from './PromptSelector';
import { EvalCaseExpectedFieldsForm } from './EvalCaseExpectedFieldsForm';
import { ConversationalTestEditor } from './ConversationalTestEditor';
import { useEvalStore } from '@/stores/evalStore';
import type { TestDefinition, MetricConfig, ExpectedTestFieldsModel, TestType, Turn, ConversationalTestConfig } from '@/types/eval';
import type { components } from '@/types/generated/api';
import { TemplateUtils } from '@/services/prompts';

type PromptMeta = components['schemas']['PromptMeta'];

interface TestEditorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  testItem: TestDefinition | null;
  onSave: (testItem: TestDefinition) => void;
  repoName: string;
  evalMetrics: MetricConfig[];
  isSaving?: boolean;
}

export function TestEditor({ open, onOpenChange, testItem, onSave, repoName, evalMetrics, isSaving = false }: TestEditorProps) {
  // Use store's editingTest instead of prop
  const editingTestFromStore = useEvalStore((state) => state.editingTest);
  const effectiveTestItem = editingTestFromStore || testItem;


  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [promptReference, setPromptReference] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [templateVariables, setTemplateVariables] = useState<Record<string, unknown>>({});
  const [expectedFields, setExpectedFields] = useState<ExpectedTestFieldsModel>({ config: {} });

  // Conversational test state
  const [testType, setTestType] = useState<TestType>('single_turn');
  const [turns, setTurns] = useState<Turn[]>([]);
  const [conversationalConfig, setConversationalConfig] = useState<ConversationalTestConfig>({});

  // Selected prompt's LLM config (for simulation)
  const [promptProvider, setPromptProvider] = useState<string>('');
  const [promptModel, setPromptModel] = useState<string>('');

  // Reset form when dialog opens or when effectiveTestItem changes
  useEffect(() => {
    if (open) {
      setName(effectiveTestItem?.name || '');
      setDescription(effectiveTestItem?.description || '');
      setPromptReference(effectiveTestItem?.prompt_reference || '');
      setUserMessage(effectiveTestItem?.user_message || '');
      setTemplateVariables(effectiveTestItem?.template_variables || {});
      setExpectedFields(effectiveTestItem?.test_fields || { config: {} });

      // Handle conversational test fields (from extended type)
      const extendedTest = effectiveTestItem as TestDefinition & {
        test_type?: TestType;
        turns?: Turn[];
        conversational_config?: ConversationalTestConfig;
      };
      setTestType(extendedTest?.test_type || 'single_turn');
      setTurns(extendedTest?.turns || []);
      setConversationalConfig(extendedTest?.conversational_config || {});
    }
  }, [open, effectiveTestItem]);

  const handleSave = () => {
    // Build the test definition with conversational fields
    const updatedTest = {
      name: name.trim(),
      description: description.trim() || null,
      prompt_reference: promptReference.trim(),
      user_message: testType === 'single_turn' ? (userMessage.trim() || null) : null,
      template_variables: templateVariables,
      test_fields: expectedFields,
      enabled: testItem?.enabled ?? true,
      // Conversational test fields
      test_type: testType,
      turns: testType === 'conversational' ? turns : undefined,
      conversational_config: testType === 'conversational' && Object.keys(conversationalConfig).length > 0
        ? conversationalConfig
        : undefined,
    } as TestDefinition;

    onSave(updatedTest);
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handlePromptSelection = (promptPath: string, promptMeta?: PromptMeta) => {
    setPromptReference(promptPath);

    // Capture the prompt's LLM configuration
    if (promptMeta?.prompt) {
      setPromptProvider(promptMeta.prompt.provider || '');
      setPromptModel(promptMeta.prompt.model || '');
    }

    if (promptMeta?.prompt?.prompt) {
      // Extract variables from prompt text using shared utility
      const variables = TemplateUtils.extractVariables(promptMeta.prompt.prompt);

      // Create template variables object with empty strings for new variables
      const newVariables: Record<string, unknown> = {};
      variables.forEach(varName => {
        // Keep existing value if it exists, otherwise set empty string
        newVariables[varName] = templateVariables[varName] ?? '';
      });

      setTemplateVariables(newVariables);
    }
  };

  return (
    <Dialog.Root open={open} onOpenChange={(e) => onOpenChange(e.open)} size="xl">
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxH="90vh" overflowY="auto">
            <Dialog.Header>
              <Dialog.Title>{effectiveTestItem ? 'Edit Test' : 'Create New Test'}</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                {/* Test Type Selector */}
                <Field.Root>
                  <Field.Label fontSize="xs" fontWeight="medium">Test Type</Field.Label>
                  <Group attached>
                    <Button
                      size="sm"
                      variant={testType === 'single_turn' ? 'solid' : 'outline'}
                      onClick={() => setTestType('single_turn')}
                      disabled={isSaving}
                    >
                      <LuMessageSquare size={14} />
                      Single Turn
                    </Button>
                    <Button
                      size="sm"
                      variant={testType === 'conversational' ? 'solid' : 'outline'}
                      onClick={() => setTestType('conversational')}
                      disabled={isSaving}
                    >
                      <LuMessagesSquare size={14} />
                      Conversational
                    </Button>
                  </Group>
                  <Field.HelperText fontSize="xs">
                    {testType === 'single_turn'
                      ? 'Test a single prompt/response pair'
                      : 'Test multi-turn conversations with your chatbot'}
                  </Field.HelperText>
                </Field.Root>

                {/* Name and Description - Prompt Reference */}
                <HStack align="start" gap={4}>
                  {/* Left Column: Name and Description (50%) */}
                  <VStack align="stretch" gap={4} width="50%">
                    <Field.Root required>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Test Name <Field.RequiredIndicator />
                      </Field.Label>
                      <Input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="test-answer-relevancy"
                        disabled={isSaving}
                        size="md"
                      />
                      <Field.HelperText fontSize="xs">Unique identifier for this test</Field.HelperText>
                    </Field.Root>

                    <Field.Root>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Description <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                      </Field.Label>
                      <Textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Describe what this test validates..."
                        rows={2}
                        resize="vertical"
                        disabled={isSaving}
                      />
                    </Field.Root>
                  </VStack>

                  {/* Right Column: Prompt Reference (50%) */}
                  <VStack align="stretch" gap={4} width="50%">
                    <Field.Root required>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Prompt Reference <Field.RequiredIndicator />
                      </Field.Label>
                      <PromptSelector
                        repoName={repoName}
                        value={promptReference}
                        onChange={handlePromptSelection}
                        disabled={isSaving}
                      />
                    </Field.Root>

                    {/* User Message - only for single turn */}
                    {testType === 'single_turn' && (
                      <Field.Root>
                        <Field.Label fontSize="xs" fontWeight="medium">
                          User Message <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                        </Field.Label>
                        <Textarea
                          value={userMessage}
                          onChange={(e) => setUserMessage(e.target.value)}
                          placeholder="What do you want to ask the prompt?"
                          rows={2}
                          resize="vertical"
                          disabled={isSaving}
                        />
                      </Field.Root>
                    )}
                  </VStack>
                </HStack>

                {/* Conversational Test Editor */}
                {testType === 'conversational' && (
                  <Card.Root>
                    <Card.Body>
                      <ConversationalTestEditor
                        turns={turns}
                        onTurnsChange={setTurns}
                        conversationalConfig={conversationalConfig}
                        onConfigChange={setConversationalConfig}
                        repoName={repoName}
                        promptReference={promptReference}
                        provider={promptProvider}
                        model={promptModel}
                        disabled={isSaving}
                      />
                    </Card.Body>
                  </Card.Root>
                )}

                {/* Template Variables */}
                <Field.Root>
                  <Field.Label fontSize="xs" fontWeight="medium">
                    Template Variables <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                  </Field.Label>
                  <TemplateVariableEditor
                    variables={templateVariables}
                    onChange={setTemplateVariables}
                  />
                </Field.Root>

                {/* Expected Evaluation Fields */}
                <EvalCaseExpectedFieldsForm
                  evalMetrics={evalMetrics}
                  expectedFields={expectedFields}
                  onExpectedFieldsChange={setExpectedFields}
                />
              </VStack>
            </Dialog.Body>
            <Dialog.Footer>
              <HStack gap={2}>
                <Dialog.ActionTrigger asChild>
                  <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                    Cancel
                  </Button>
                </Dialog.ActionTrigger>
                <Button
                  onClick={handleSave}
                  loading={isSaving}
                  disabled={
                    isSaving ||
                    !name.trim() ||
                    !promptReference.trim() ||
                    (testType === 'conversational' && turns.length === 0 && !conversationalConfig?.user_goal?.trim())
                  }
                >
                  {effectiveTestItem ? 'Save Changes' : 'Create Test'}
                </Button>
              </HStack>
            </Dialog.Footer>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" disabled={isSaving} />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
}