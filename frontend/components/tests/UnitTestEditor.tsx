'use client';

import React, { useState } from 'react';
import { Dialog, Button, VStack, HStack, Input, Textarea, Field, Portal } from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';
import { TemplateVariableEditor } from './TemplateVariableEditor';
import { PromptSelector } from './PromptSelector';
import { TestCaseExpectedFieldsForm } from './TestCaseExpectedFieldsForm';
import type { UnitTestDefinition, MetricConfig, ExpectedEvaluationFieldsModel } from '@/types/test';
import type { components } from '@/types/generated/api';
import { TemplateUtils } from '@/services/prompts';

type PromptMeta = components['schemas']['PromptMeta'];

interface UnitTestEditorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  test: UnitTestDefinition | null;
  onSave: (test: UnitTestDefinition) => void;
  repoName: string;
  suiteMetrics: MetricConfig[];
  isSaving?: boolean;
}

export function UnitTestEditor({ open, onOpenChange, test, onSave, repoName, suiteMetrics, isSaving = false }: UnitTestEditorProps) {
  const [name, setName] = useState(test?.name || '');
  const [description, setDescription] = useState(test?.description || '');
  const [promptReference, setPromptReference] = useState(test?.prompt_reference || '');
  const [userMessage, setUserMessage] = useState(
    (test?.template_variables?.user_message as string) || ''
  );
  const [templateVariables, setTemplateVariables] = useState<Record<string, unknown>>(
    test?.template_variables || {}
  );
  const [expectedFields, setExpectedFields] = useState<ExpectedEvaluationFieldsModel>(
    test?.evaluation_fields || { config: {} }
  );

  const handleSave = () => {
    // Merge user_message into template variables
    const allVariables = {
      ...templateVariables,
      ...(userMessage.trim() ? { user_message: userMessage.trim() } : {})
    };

    const updatedTest: UnitTestDefinition = {
      name: name.trim(),
      description: description.trim() || null,
      prompt_reference: promptReference.trim(),
      template_variables: allVariables,
      evaluation_fields: expectedFields,
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
                {/* Name and Description - Prompt Reference and User Message */}
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

                  {/* Right Column: Prompt Reference and User Message (50%) */}
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
                  </VStack>
                </HStack>

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
                <TestCaseExpectedFieldsForm
                  suiteMetrics={suiteMetrics}
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
                  disabled={isSaving || !name.trim() || !promptReference.trim()}
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