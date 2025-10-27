'use client';

import { useState } from 'react';
import {
  VStack,
  HStack,
  Textarea,
  Field,
  Button,
  Card,
  Text,
  RadioGroup,
  IconButton,
  Input,
} from '@chakra-ui/react';
import { LuTrash2, LuPlus } from 'react-icons/lu';
import type { MockConfig, ParameterSchema } from '@/types/tools';

interface MockDataEditorProps {
  mockConfig: MockConfig;
  parameters: Record<string, ParameterSchema>;
  onChange: (mockConfig: MockConfig) => void;
}

interface ConditionalRule {
  conditions: Record<string, string | number | boolean>;
  output: string;
}

export function MockDataEditor({ mockConfig, parameters, onChange }: MockDataEditorProps) {
  const mockType = mockConfig.mock_type || 'static';
  const [conditionalRules, setConditionalRules] = useState<ConditionalRule[]>(
    (mockConfig.conditional_rules as ConditionalRule[]) || []
  );

  const handleMockTypeChange = (value: string) => {
    onChange({
      ...mockConfig,
      mock_type: value as 'static' | 'conditional' | 'python',
    });
  };

  const handleStaticResponseChange = (value: string) => {
    onChange({
      ...mockConfig,
      static_response: value,
    });
  };

  const handlePythonCodeChange = (value: string) => {
    onChange({
      ...mockConfig,
      python_code: value,
    });
  };

  const handleAddConditionalRule = () => {
    const newRule: ConditionalRule = {
      conditions: {},
      output: '',
    };
    const updatedRules = [...conditionalRules, newRule];
    setConditionalRules(updatedRules);
    onChange({
      ...mockConfig,
      conditional_rules: updatedRules,
    });
  };

  const handleRemoveConditionalRule = (index: number) => {
    const updatedRules = conditionalRules.filter((_, i) => i !== index);
    setConditionalRules(updatedRules);
    onChange({
      ...mockConfig,
      conditional_rules: updatedRules,
    });
  };

  const handleConditionChange = (ruleIndex: number, paramName: string, value: string | number | boolean) => {
    const updatedRules = conditionalRules.map((rule, i) => {
      if (i === ruleIndex) {
        return {
          ...rule,
          conditions: {
            ...rule.conditions,
            [paramName]: value,
          },
        };
      }
      return rule;
    });
    setConditionalRules(updatedRules);
    onChange({
      ...mockConfig,
      conditional_rules: updatedRules,
    });
  };

  const handleOutputChange = (ruleIndex: number, output: string) => {
    const updatedRules = conditionalRules.map((rule, i) => {
      if (i === ruleIndex) {
        return {
          ...rule,
          output,
        };
      }
      return rule;
    });
    setConditionalRules(updatedRules);
    onChange({
      ...mockConfig,
      conditional_rules: updatedRules,
    });
  };

  const parameterNames = Object.keys(parameters);

  return (
    <VStack gap={4} align="stretch">
      {/* Mock Type Selector */}
      <Field.Root>
        <Field.Label fontSize="xs" fontWeight="medium">Mock Type</Field.Label>
        <RadioGroup.Root
          value={mockType}
          onValueChange={(details) => {
            if (details.value) {
              handleMockTypeChange(details.value);
            }
          }}
        >
          <HStack gap={4}>
            <RadioGroup.Item value="static">
              <RadioGroup.ItemHiddenInput />
              <RadioGroup.ItemControl />
              <RadioGroup.ItemText fontSize="sm">Static</RadioGroup.ItemText>
            </RadioGroup.Item>
            <RadioGroup.Item value="conditional">
              <RadioGroup.ItemHiddenInput />
              <RadioGroup.ItemControl />
              <RadioGroup.ItemText fontSize="sm">Conditional</RadioGroup.ItemText>
            </RadioGroup.Item>
            <RadioGroup.Item value="python">
              <RadioGroup.ItemHiddenInput />
              <RadioGroup.ItemControl />
              <RadioGroup.ItemText fontSize="sm">Python Code</RadioGroup.ItemText>
            </RadioGroup.Item>
          </HStack>
        </RadioGroup.Root>
      </Field.Root>

      {/* Static Mock UI */}
      {mockType === 'static' && (
        <Field.Root>
          <Field.Label fontSize="xs" fontWeight="medium">Static Response</Field.Label>
          <Textarea
            value={mockConfig.static_response || ''}
            onChange={(e) => handleStaticResponseChange(e.target.value)}
            placeholder="Enter static mock response..."
            rows={8}
            resize="vertical"
            fontFamily="mono"
            fontSize="sm"
          />
        </Field.Root>
      )}

      {/* Conditional Mock UI */}
      {mockType === 'conditional' && (
        <VStack gap={3} align="stretch">
          <HStack justify="space-between" align="center">
            <Text fontSize="xs" fontWeight="medium" color="fg.muted">
              Conditional Rules
            </Text>
            <Button
              size="sm"
              variant="outline"
              onClick={handleAddConditionalRule}
            >
              <LuPlus size={14} />
              <Text fontSize="xs" ml={1}>Add Rule</Text>
            </Button>
          </HStack>

          {conditionalRules.length === 0 && (
            <Card.Root bg="bg.subtle" borderStyle="dashed">
              <Card.Body p={4}>
                <Text fontSize="sm" color="fg.muted" textAlign="center">
                  No conditional rules defined. Click &ldquo;Add Rule&rdquo; to create one.
                </Text>
              </Card.Body>
            </Card.Root>
          )}

          {conditionalRules.map((rule, ruleIndex) => (
            <Card.Root key={ruleIndex} borderColor="border.emphasized">
              <Card.Body p={4}>
                <VStack gap={3} align="stretch">
                  <HStack justify="space-between" align="center">
                    <Text fontSize="xs" fontWeight="semibold" color="fg">
                      Rule {ruleIndex + 1}
                    </Text>
                    <IconButton
                      size="xs"
                      variant="ghost"
                      colorPalette="red"
                      onClick={() => handleRemoveConditionalRule(ruleIndex)}
                      aria-label="Remove rule"
                    >
                      <LuTrash2 />
                    </IconButton>
                  </HStack>

                  {/* Conditions */}
                  <VStack gap={2} align="stretch">
                    <Text fontSize="xs" fontWeight="medium" color="fg.muted">
                      Conditions
                    </Text>
                    {parameterNames.length === 0 ? (
                      <Text fontSize="xs" color="fg.muted">
                        No parameters defined. Add parameters first.
                      </Text>
                    ) : (
                      parameterNames.map((paramName) => (
                        <HStack key={paramName} gap={2}>
                          <Text fontSize="xs" color="fg.muted" minW="100px">
                            {paramName}:
                          </Text>
                          <Input
                            size="sm"
                            value={String(rule.conditions[paramName] ?? '')}
                            onChange={(e) =>
                              handleConditionChange(ruleIndex, paramName, e.target.value)
                            }
                            placeholder={`Value for ${paramName}`}
                            flex={1}
                            fontSize="sm"
                          />
                        </HStack>
                      ))
                    )}
                  </VStack>

                  {/* Output */}
                  <Field.Root>
                    <Field.Label fontSize="xs" fontWeight="medium">Output</Field.Label>
                    <Textarea
                      value={rule.output}
                      onChange={(e) => handleOutputChange(ruleIndex, e.target.value)}
                      placeholder="Enter output for this condition..."
                      rows={4}
                      resize="vertical"
                      fontFamily="mono"
                      fontSize="sm"
                    />
                  </Field.Root>
                </VStack>
              </Card.Body>
            </Card.Root>
          ))}
        </VStack>
      )}

      {/* Python Code Mock UI */}
      {mockType === 'python' && (
        <Field.Root>
          <Field.Label fontSize="xs" fontWeight="medium">Python Code</Field.Label>
          <Field.HelperText fontSize="xs" color="fg.muted" mb={2}>
            Python code that returns the mock response. Parameters available as variables.
          </Field.HelperText>
          <Textarea
            value={mockConfig.python_code || ''}
            onChange={(e) => handlePythonCodeChange(e.target.value)}
            placeholder={`# Example:\nresult = f"Hello {name}"\nreturn result`}
            rows={12}
            resize="vertical"
            fontFamily="mono"
            fontSize="sm"
          />
        </Field.Root>
      )}
    </VStack>
  );
}