'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, Button, VStack, HStack, Input, Textarea, Field, Portal } from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';
import { TemplateVariableEditor } from './TemplateVariableEditor';
import { PromptSelector } from './PromptSelector';
import { EvalCaseExpectedFieldsForm } from './EvalCaseExpectedFieldsForm';
import { useEvalStore } from '@/stores/evalStore';
import type { EvalDefinition, MetricConfig, ExpectedEvaluationFieldsModel } from '@/types/eval';
import type { components } from '@/types/generated/api';
import { TemplateUtils } from '@/services/prompts';

type PromptMeta = components['schemas']['PromptMeta'];

interface EvalEditorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evalItem: EvalDefinition | null;
  onSave: (evalItem: EvalDefinition) => void;
  repoName: string;
  suiteMetrics: MetricConfig[];
  isSaving?: boolean;
}

export function EvalEditor({ open, onOpenChange, evalItem, onSave, repoName, suiteMetrics, isSaving = false }: EvalEditorProps) {
  // Use store's editingEval instead of prop
  const editingEvalFromStore = useEvalStore((state) => state.editingEval);
  const effectiveEvalItem = editingEvalFromStore || evalItem;
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [promptReference, setPromptReference] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [templateVariables, setTemplateVariables] = useState<Record<string, unknown>>({});
  const [expectedFields, setExpectedFields] = useState<ExpectedEvaluationFieldsModel>({ config: {} });
  
  // Reset form when dialog opens or when effectiveEvalItem changes
  useEffect(() => {
    if (open) {
      setName(effectiveEvalItem?.name || '');
      setDescription(effectiveEvalItem?.description || '');
      setPromptReference(effectiveEvalItem?.prompt_reference || '');
      setUserMessage(effectiveEvalItem?.user_message || '');
      setTemplateVariables(effectiveEvalItem?.template_variables || {});
      setExpectedFields(effectiveEvalItem?.evaluation_fields || { config: {} });
    }
  }, [open, effectiveEvalItem]);

  const handleSave = () => {
    const updatedEval: EvalDefinition = {
      name: name.trim(),
      description: description.trim() || null,
      prompt_reference: promptReference.trim(),
      user_message: userMessage.trim() || null,
      template_variables: templateVariables,
      evaluation_fields: expectedFields,
      enabled: evalItem?.enabled ?? true,
    };

    onSave(updatedEval);
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handlePromptSelection = (promptPath: string, promptMeta?: PromptMeta) => {
    setPromptReference(promptPath);
    
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
              <Dialog.Title>{effectiveEvalItem ? 'Edit Eval' : 'Create New Eval'}</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                {/* Name and Description - Prompt Reference and User Message */}
                <HStack align="start" gap={4}>
                  {/* Left Column: Name and Description (50%) */}
                  <VStack align="stretch" gap={4} width="50%">
                    <Field.Root required>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Eval Name <Field.RequiredIndicator />
                      </Field.Label>
                      <Input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="eval-answer-relevancy"
                        disabled={isSaving}
                        size="md"
                      />
                      <Field.HelperText fontSize="xs">Unique identifier for this eval</Field.HelperText>
                    </Field.Root>

                    <Field.Root>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Description <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                      </Field.Label>
                      <Textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Describe what this eval validates..."
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
                <EvalCaseExpectedFieldsForm
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
                  {effectiveEvalItem ? 'Save Changes' : 'Create Eval'}
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