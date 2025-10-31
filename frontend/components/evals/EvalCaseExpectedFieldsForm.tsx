'use client';

import React, { useMemo } from 'react';
import { VStack, Box, Text, Field, Input, Textarea } from '@chakra-ui/react';
import { useMetricsStore } from '@/stores/metricsStore';
import type { MetricConfig, ExpectedEvaluationFieldsModel } from '@/types/eval';

interface EvalCaseExpectedFieldsFormProps {
  /** Metrics configured in the parent eval suite */
  suiteMetrics: MetricConfig[];
  /** Current expected fields values */
  expectedFields: ExpectedEvaluationFieldsModel;
  /** Callback when expected fields change */
  onExpectedFieldsChange: (fields: ExpectedEvaluationFieldsModel) => void;
}

/**
 * Form component for configuring expected evaluation fields for an eval case.
 * Dynamically generates forms based on metrics selected in the parent eval suite.
 */
export function EvalCaseExpectedFieldsForm({
  suiteMetrics,
  expectedFields,
  onExpectedFieldsChange,
}: EvalCaseExpectedFieldsFormProps) {
  const { getMetricMetadata, getRequiredExpectedFields } = useMetricsStore();

  // Collect all unique fields required by all metrics
  const allRequiredFields = useMemo(() => {
    const fieldsMap = new Map<string, {
      name: string;
      label: string;
      description?: string;
      type: string;
      required: boolean;
      usedByMetrics: string[];
    }>();

    suiteMetrics.forEach((metric) => {
      const metadata = getMetricMetadata(metric.type);
      const requiredFieldNames = getRequiredExpectedFields(metric.type);

      if (!metadata?.field_schema?.properties || requiredFieldNames.length === 0) return;

      const properties = metadata.field_schema.properties as Record<string, {
        type: string;
        description?: string;
      }>;

      requiredFieldNames.forEach((fieldName) => {
        const fieldDef = properties[fieldName];
        if (!fieldDef) return;

        const metricName = metric.type
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        if (fieldsMap.has(fieldName)) {
          // Field already exists, just add this metric to the list
          const existing = fieldsMap.get(fieldName)!;
          existing.usedByMetrics.push(metricName);
        } else {
          // New field
          fieldsMap.set(fieldName, {
            name: fieldName,
            label: fieldName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
            description: fieldDef.description,
            type: fieldDef.type,
            required: true,
            usedByMetrics: [metricName],
          });
        }
      });
    });

    return Array.from(fieldsMap.values());
  }, [suiteMetrics, getMetricMetadata, getRequiredExpectedFields]);

  const handleFieldChange = (fieldName: string, value: unknown) => {
    onExpectedFieldsChange({
      ...expectedFields,
      config: {
        ...expectedFields.config,
        [fieldName]: value,
      },
    });
  };

  if (allRequiredFields.length === 0) {
    return (
      <Box
        p={4}
        textAlign="center"
        border="1px dashed"
        borderColor="gray.300"
        borderRadius="md"
      >
        <Text fontSize="sm" color="gray.600">
          No metrics in this eval suite require expected fields.
        </Text>
        <Text fontSize="xs" color="gray.500" mt={2}>
          Deterministic metrics like exact match need expected values, while some LLM-based metrics may not.
        </Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={4}>
      {/* Header Section */}
      <Box>
        <Text fontSize="md" fontWeight="semibold" mb={1}>
          Expected Fields
        </Text>
        <Text fontSize="xs" color="gray.600">
          Configure the expected values required by your metrics. These values will be used to evaluate this specific eval case.
        </Text>
      </Box>

      {/* Render each unique field once */}
      {allRequiredFields.map((field) => {
        const currentValue = expectedFields.config?.[field.name] ?? '';
        const isLongText = field.type === 'string' && (
          field.name.toLowerCase().includes('output') ||
          field.name.toLowerCase().includes('text') ||
          field.description?.toLowerCase().includes('multiline')
        );

        return (
          <Field.Root key={field.name} required={field.required}>
            <Field.Label fontSize="xs" fontWeight="medium">
              {field.label}
              {field.required && <Field.RequiredIndicator />}
            </Field.Label>
            {isLongText ? (
              <Textarea
                value={String(currentValue)}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                rows={2}
                size="sm"
              />
            ) : (
              <Input
                value={String(currentValue)}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                placeholder={field.description || `Enter ${field.label.toLowerCase()}`}
                size="sm"
              />
            )}
            <Field.HelperText fontSize="xs">
              {field.description && (
                <Text as="span">
                  {field.description}
                  {" • "}
                </Text>
              )}
              <Text as="span" fontWeight="medium" color="gray.700">
                Used by: {field.usedByMetrics.join(', ')}
              </Text>
            </Field.HelperText>
          </Field.Root>
        );
      })}

    </VStack>
  );
}