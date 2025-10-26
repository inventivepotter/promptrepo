'use client';

import { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Textarea,
  Button,
  IconButton,
  Badge,
  Card,
} from '@chakra-ui/react';
import { HiTrash, HiPlus } from 'react-icons/hi';
import { useColorModeValue } from '@/components/ui/color-mode';
import type { ParameterSchema, ToolParameterType } from '@/types/tools';

interface ParameterEditorProps {
  parameters: Record<string, ParameterSchema>;
  required: string[];
  onParametersChange: (parameters: Record<string, ParameterSchema>) => void;
  onRequiredChange: (required: string[]) => void;
}

export function ParameterEditor({
  parameters,
  required,
  onParametersChange,
  onRequiredChange,
}: ParameterEditorProps) {
  const [newParamName, setNewParamName] = useState('');
  const borderColor = "bg.muted";
  const bgColor = useColorModeValue('white', 'gray.800');

  const handleAddParameter = () => {
    if (!newParamName.trim()) return;
    if (parameters[newParamName]) {
      alert('Parameter with this name already exists');
      return;
    }

    const newParam: ParameterSchema = {
      type: 'string',
      description: '',
    };

    onParametersChange({
      ...parameters,
      [newParamName]: newParam,
    });
    setNewParamName('');
  };

  const handleDeleteParameter = (name: string) => {
    const newParams = { ...parameters };
    delete newParams[name];
    onParametersChange(newParams);

    // Remove from required if present
    if (required.includes(name)) {
      onRequiredChange(required.filter(r => r !== name));
    }
  };

  const handleParameterChange = (name: string, updates: Partial<ParameterSchema>) => {
    onParametersChange({
      ...parameters,
      [name]: {
        ...parameters[name],
        ...updates,
      },
    });
  };

  const handleRequiredChange = (name: string, isRequired: boolean) => {
    if (isRequired) {
      if (!required.includes(name)) {
        onRequiredChange([...required, name]);
      }
    } else {
      onRequiredChange(required.filter(r => r !== name));
    }
  };

  const parameterNames = Object.keys(parameters);

  return (
    <VStack gap={4} align="stretch">
      {/* Add new parameter */}
      <HStack>
        <Input
          placeholder="New parameter name"
          value={newParamName}
          onChange={(e) => setNewParamName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleAddParameter();
            }
          }}
        />
        <Button onClick={handleAddParameter} colorPalette="blue">
          <HiPlus /> Add
        </Button>
      </HStack>

      {/* Parameters list */}
      {parameterNames.length === 0 ? (
        <Box p={4} textAlign="center" color="gray.500">
          No parameters yet. Add one above.
        </Box>
      ) : (
        <VStack gap={4} align="stretch">
          {parameterNames.map(name => (
            <Card.Root key={name} borderWidth="1px" borderColor={borderColor}>
              <Card.Body>
                <VStack gap={3} align="stretch">
                  <HStack justify="space-between">
                    <HStack gap={2}>
                      <Text fontWeight="bold">{name}</Text>
                      {required.includes(name) && (
                        <Badge colorPalette="orange">Required</Badge>
                      )}
                    </HStack>
                    <IconButton
                      aria-label="Delete parameter"
                      size="sm"
                      variant="ghost"
                      colorPalette="red"
                      onClick={() => handleDeleteParameter(name)}
                    >
                      <HiTrash />
                    </IconButton>
                  </HStack>

                  <Box>
                    <Text fontSize="xs" fontWeight="medium" mb={1}>
                      Type
                    </Text>
                    <select
                      value={parameters[name].type}
                      onChange={(e) =>
                        handleParameterChange(name, { type: e.target.value as ToolParameterType })
                      }
                      style={{
                        width: '100%',
                        padding: '0.5rem 0.75rem',
                        borderRadius: '0.375rem',
                        borderWidth: '1px',
                        borderColor: borderColor,
                        backgroundColor: bgColor,
                        fontSize: '0.875rem',
                      }}
                    >
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                      <option value="array">Array</option>
                      <option value="object">Object</option>
                    </select>
                  </Box>

                  <Box>
                    <Text fontSize="xs" fontWeight="medium" mb={1}>
                      Description
                    </Text>
                    <Textarea
                      value={parameters[name].description}
                      onChange={(e) =>
                        handleParameterChange(name, { description: e.target.value })
                      }
                      placeholder="Describe this parameter"
                      rows={2}
                      size="sm"
                    />
                  </Box>

                  <HStack gap={2}>
                    <input
                      type="checkbox"
                      id={`required-${name}`}
                      checked={required.includes(name)}
                      onChange={(e) => handleRequiredChange(name, e.target.checked)}
                      style={{ cursor: 'pointer' }}
                    />
                    <label
                      htmlFor={`required-${name}`}
                      style={{ fontSize: '0.875rem', cursor: 'pointer' }}
                    >
                      Required parameter
                    </label>
                  </HStack>

                  {parameters[name].type === 'string' && (
                    <Box>
                      <Text fontSize="xs" fontWeight="medium" mb={1}>
                        Enum Values (optional, one per line)
                      </Text>
                      <Textarea
                        value={parameters[name].enum?.join('\n') || ''}
                        onChange={(e) => {
                          const values = e.target.value.split('\n').filter(v => v.trim());
                          handleParameterChange(name, {
                            enum: values.length > 0 ? values : undefined,
                          });
                        }}
                        placeholder="value1&#10;value2&#10;value3"
                        rows={3}
                        size="sm"
                      />
                    </Box>
                  )}

                  <Box>
                    <Text fontSize="xs" fontWeight="medium" mb={1}>
                      Default Value (optional)
                    </Text>
                    <Input
                      value={parameters[name].default as string || ''}
                      onChange={(e) =>
                        handleParameterChange(name, { default: e.target.value || undefined })
                      }
                      placeholder="Default value"
                      size="sm"
                    />
                  </Box>
                </VStack>
              </Card.Body>
            </Card.Root>
          ))}
        </VStack>
      )}
    </VStack>
  );
}