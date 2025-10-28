'use client';

import React, { useMemo } from 'react';
import { VStack, Box, Field, Input, Textarea, Checkbox, NumberInput } from '@chakra-ui/react';
import { LuInfo } from 'react-icons/lu';
import { Tooltip } from '@/components/ui/tooltip';
import { useMetricsStore } from '@/stores/metricsStore';

interface MetricConfigurationFormProps {
  /** Metric type to configure */
  metricType: string;
  /** Current configuration values */
  config: Record<string, unknown>;
  /** Callback when configuration changes */
  onConfigChange: (config: Record<string, unknown>) => void;
}

/**
 * Dynamic form component for metric-specific configuration fields.
 * Generates form fields based on the metric's field schema from metadata.
 */
export function MetricConfigurationForm({ metricType, config, onConfigChange }: MetricConfigurationFormProps) {
  const getMetricMetadata = useMetricsStore((state) => state.getMetricMetadata);
  
  const metadata = useMemo(() => getMetricMetadata(metricType), [metricType, getMetricMetadata]);

  // Parse field schema
  const fields = useMemo(() => {
    if (!metadata?.field_schema?.properties) return [];
    
    const properties = metadata.field_schema.properties as Record<string, {
      type: string;
      description?: string;
      enum?: unknown[];
      items?: { type: string };
      minimum?: number;
      maximum?: number;
      default?: unknown;
    }>;
    
    const required = (metadata.field_schema.required as string[]) || [];
    
    return Object.entries(properties).map(([fieldName, fieldDef]) => ({
      name: fieldName,
      label: fieldName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
      type: fieldDef.type,
      description: fieldDef.description,
      required: required.includes(fieldName),
      enumValues: fieldDef.enum,
      itemType: fieldDef.items?.type,
      minimum: fieldDef.minimum,
      maximum: fieldDef.maximum,
      defaultValue: fieldDef.default,
    }));
  }, [metadata]);

  const handleFieldChange = (fieldName: string, value: unknown) => {
    onConfigChange({
      ...config,
      [fieldName]: value,
    });
  };

  const renderField = (field: {
    name: string;
    label: string;
    type: string;
    description?: string;
    required: boolean;
    enumValues?: unknown[];
    itemType?: string;
    minimum?: number;
    maximum?: number;
    defaultValue?: unknown;
  }) => {
    const currentValue = config[field.name] ?? field.defaultValue ?? '';

    switch (field.type) {
      case 'boolean':
        return (
          <Checkbox.Root
            key={field.name}
            checked={!!currentValue}
            onCheckedChange={(e) => handleFieldChange(field.name, !!e.checked)}
            size="sm"
          >
            <Checkbox.HiddenInput />
            <Checkbox.Control />
            <Checkbox.Label fontSize="sm">
              {field.label}
              {field.required && <Box as="span" color="red.500" ml={1}>*</Box>}
            </Checkbox.Label>
          </Checkbox.Root>
        );

      case 'number':
      case 'integer':
        return (
          <Field.Root key={field.name}>
            <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs" fontWeight="medium">
              {field.label}
              {field.required && <Box as="span" color="red.500">*</Box>}
              {field.description && (
                <Tooltip content={field.description}>
                  <Box cursor="help">
                    <LuInfo size={14} opacity={0.6} />
                  </Box>
                </Tooltip>
              )}
            </Field.Label>
            <NumberInput.Root
              value={String(currentValue)}
              onValueChange={(e) => handleFieldChange(field.name, Number(e.value))}
              min={field.minimum}
              max={field.maximum}
              size="sm"
            >
              <NumberInput.Input />
            </NumberInput.Root>
            {field.description && (
              <Field.HelperText fontSize="xs">{field.description}</Field.HelperText>
            )}
          </Field.Root>
        );

      case 'array':
        // For arrays, use a textarea with comma-separated values
        const arrayValue = Array.isArray(currentValue) ? currentValue.join(', ') : '';
        return (
          <Field.Root key={field.name}>
            <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs" fontWeight="medium">
              {field.label}
              {field.required && <Box as="span" color="red.500">*</Box>}
              {field.description && (
                <Tooltip content={field.description}>
                  <Box cursor="help">
                    <LuInfo size={14} opacity={0.6} />
                  </Box>
                </Tooltip>
              )}
            </Field.Label>
            <Textarea
              value={arrayValue}
              onChange={(e) => {
                const values = e.target.value.split(',').map(v => v.trim()).filter(Boolean);
                handleFieldChange(field.name, values);
              }}
              placeholder="Enter values separated by commas"
              size="sm"
              rows={3}
            />
            {field.description && (
              <Field.HelperText fontSize="xs">{field.description}</Field.HelperText>
            )}
          </Field.Root>
        );

      case 'string':
      default:
        // Check if multiline
        const isLongText = field.description?.toLowerCase().includes('multiline') || 
                           field.name.toLowerCase().includes('output') ||
                           field.name.toLowerCase().includes('text');
        
        return (
          <Field.Root key={field.name}>
            <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs" fontWeight="medium">
              {field.label}
              {field.required && <Box as="span" color="red.500">*</Box>}
              {field.description && (
                <Tooltip content={field.description}>
                  <Box cursor="help">
                    <LuInfo size={14} opacity={0.6} />
                  </Box>
                </Tooltip>
              )}
            </Field.Label>
            {isLongText ? (
              <Textarea
                value={String(currentValue)}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                size="sm"
                rows={4}
              />
            ) : (
              <Input
                value={String(currentValue)}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                size="sm"
              />
            )}
            {field.description && (
              <Field.HelperText fontSize="xs">{field.description}</Field.HelperText>
            )}
          </Field.Root>
        );
    }
  };

  if (!metadata) {
    return (
      <Box p={4} textAlign="center" color="gray.600" fontSize="sm">
        No configuration fields available for this metric
      </Box>
    );
  }

  if (fields.length === 0) {
    return (
      <Box p={4} textAlign="center" color="gray.600" fontSize="sm">
        This metric does not require additional configuration
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={4}>
      {fields.map(renderField)}
    </VStack>
  );
}