'use client';

import React, { useState } from 'react';
import { Dialog, Button, VStack, HStack, Input, Textarea, Field, Portal, Tabs } from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';
import { TemplateVariableEditor } from './TemplateVariableEditor';
import { MetricSelector } from './MetricSelector';
import { PromptSelector } from './PromptSelector';
import type { UnitTestDefinition } from '@/types/test';
import type { components } from '@/types/generated/api';
import { TemplateUtils } from '@/services/prompts';

type PromptMeta = components['schemas']['PromptMeta'];

interface UnitTestEditorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  test: UnitTestDefinition | null;
  onSave: (test: UnitTestDefinition) => void;
  repoName: string;
  isSaving?: boolean;
}

export function UnitTestEditor({ open, onOpenChange, test, onSave, repoName, isSaving = false }: UnitTestEditorProps) {
  const [name, setName] = useState(test?.name || '');
  const [description, setDescription] = useState(test?.description || '');
  const [promptReference, setPromptReference] = useState(test?.prompt_reference || '');
  const [userMessage, setUserMessage] = useState(
    (test?.template_variables?.user_message as string) || ''
  );
  const [templateVariables, setTemplateVariables] = useState<Record<string, unknown>>(
    test?.template_variables || {}
  );
  const [expectedOutput, setExpectedOutput] = useState(test?.expected_output || '');
  const [retrievalContext, setRetrievalContext] = useState<string>(
    test?.retrieval_context?.join('\n') || ''
  );
  const [metrics, setMetrics] = useState(test?.metrics || []);

  const handleSave = () => {
    const retrievalContextArray = retrievalContext
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    // Merge user_message into template variables
    const allVariables = {
      ...templateVariables,
      ...(userMessage.trim() ? { user_message: userMessage.trim() } : {})
    };

    const updatedTest: UnitTestDefinition = {
      name: name.trim(),
      description: description.trim() || undefined,
      prompt_reference: promptReference.trim(),
      template_variables: allVariables,
      expected_output: expectedOutput.trim() || null,
      retrieval_context: retrievalContextArray.length > 0 ? retrievalContextArray : null,
      metrics,
      enabled: test?.enabled ?? true,
    };

    onSave(updatedTest);
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handlePromptSelection = (promptPath: string, promptMeta?: PromptMeta) => {
    setPromptReference(promptPath);
    
    if (promptMeta?.prompt?.prompt) {
      // Extract variables from prompt text using shared utility
      const variables = TemplateUtils.extractVariables(promptMeta.prompt.prompt)
        .filter(v => v !== 'user_message'); // Exclude user_message as it has dedicated field
      
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
              <Dialog.Title>{test ? 'Edit Test' : 'Create New Test'}</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                <Field.Root required>
                  <Field.Label>Test Name</Field.Label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="test-answer-relevancy"
                    disabled={isSaving}
                  />
                  <Field.HelperText>Unique identifier for this test</Field.HelperText>
                </Field.Root>

                <Field.Root>
                  <Field.Label>Description</Field.Label>
                  <Textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe what this test validates..."
                    rows={2}
                    disabled={isSaving}
                  />
                </Field.Root>

                <Field.Root required>
                  <Field.Label>Prompt Reference</Field.Label>
                  <PromptSelector
                    repoName={repoName}
                    value={promptReference}
                    onChange={handlePromptSelection}
                    disabled={isSaving}
                  />
                </Field.Root>

                <Field.Root required>
                  <Field.Label>User Message</Field.Label>
                  <Textarea
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    placeholder="What do you want to ask the prompt?"
                    rows={3}
                    disabled={isSaving}
                  />
                  <Field.HelperText>The message/input to send to the prompt for evaluation</Field.HelperText>
                </Field.Root>

                <Tabs.Root defaultValue="variables">
                  <Tabs.List>
                    <Tabs.Trigger value="variables">Template Variables</Tabs.Trigger>
                    <Tabs.Trigger value="metrics">Metrics</Tabs.Trigger>
                    <Tabs.Trigger value="expected">Expected Output & Context</Tabs.Trigger>
                  </Tabs.List>

                  <Tabs.Content value="variables" pt={4}>
                    <TemplateVariableEditor
                      variables={templateVariables}
                      onChange={setTemplateVariables}
                    />
                  </Tabs.Content>

                  <Tabs.Content value="metrics" pt={4}>
                    <MetricSelector metrics={metrics} onChange={setMetrics} />
                  </Tabs.Content>

                  <Tabs.Content value="expected" pt={4}>
                    <VStack align="stretch" gap={4}>
                      <Field.Root>
                        <Field.Label>Expected Output (Optional)</Field.Label>
                        <Textarea
                          value={expectedOutput}
                          onChange={(e) => setExpectedOutput(e.target.value)}
                          placeholder="The expected response from the prompt..."
                          rows={4}
                          disabled={isSaving}
                        />
                        <Field.HelperText>
                          Used for comparison metrics like faithfulness
                        </Field.HelperText>
                      </Field.Root>

                      <Field.Root>
                        <Field.Label>Retrieval Context (Optional)</Field.Label>
                        <Textarea
                          value={retrievalContext}
                          onChange={(e) => setRetrievalContext(e.target.value)}
                          placeholder="Context item 1&#10;Context item 2&#10;Context item 3"
                          rows={4}
                          disabled={isSaving}
                        />
                        <Field.HelperText>
                          One context item per line. Required for RAG evaluation metrics.
                        </Field.HelperText>
                      </Field.Root>
                    </VStack>
                  </Tabs.Content>
                </Tabs.Root>
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
                  disabled={isSaving || !name.trim() || !promptReference.trim() || !userMessage.trim()}
                >
                  {test ? 'Save Changes' : 'Create Test'}
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