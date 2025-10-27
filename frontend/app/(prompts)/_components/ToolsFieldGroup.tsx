'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  VStack,
  HStack,
  Card,
  Text,
  Fieldset,
  Stack,
  Button,
  Collapsible,
  IconButton,
  Select,
  Portal,
  createListCollection,
} from '@chakra-ui/react';
import { LuChevronDown, LuChevronUp, LuPlus, LuX } from 'react-icons/lu';
import { useCurrentPrompt, useUpdateCurrentPromptField } from '@/stores/promptStore/hooks';
import httpClient from '@/lib/httpClient';
import type { components } from '@/types/generated/api';
import { ResponseStatus, isStandardResponse } from '@/types/OpenApiResponse';

type ToolSummary = components['schemas']['ToolSummary'];

export function ToolsFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const updateField = useUpdateCurrentPromptField();
  const [showTools, setShowTools] = useState(true);
  const [availableTools, setAvailableTools] = useState<ToolSummary[]>([]);
  const [isLoadingTools, setIsLoadingTools] = useState(false);

  // Load available tools when component mounts or repo changes
  useEffect(() => {
    const loadTools = async () => {
      if (!currentPrompt?.repo_name) return;
      
      setIsLoadingTools(true);
      try {
        const searchParams = new URLSearchParams();
        searchParams.append('repo_name', currentPrompt.repo_name);
        
        const response = await httpClient.get<ToolSummary[]>(
          `/api/v0/tools/?${searchParams.toString()}`
        );
        
        if (response.status === ResponseStatus.SUCCESS && isStandardResponse(response) && response.data) {
          // response.data is ToolSummary[] when using StandardResponse[List[ToolSummary]]
          const tools = Array.isArray(response.data) ? response.data : [];
          setAvailableTools(tools);
        }
      } catch (error) {
        console.error('Failed to load tools:', error);
      } finally {
        setIsLoadingTools(false);
      }
    };

    loadTools();
  }, [currentPrompt?.repo_name]);

  const tools = Array.isArray(currentPrompt?.prompt?.tools) ? currentPrompt.prompt.tools : [];

  const handleAddTool = (toolPath: string) => {
    if (!tools.includes(toolPath)) {
      updateField('tools', [...tools, toolPath]);
    }
  };

  const handleRemoveTool = (toolPath: string) => {
    updateField('tools', tools.filter((t) => t !== toolPath));
  };

  const getToolNameFromPath = (toolPath: string) => {
    // Extract tool name from path like "file:///.promptrepo/mock_tools/temp_tool.tool.yaml"
    const parts = toolPath.split('/');
    const fileName = parts[parts.length - 1];
    return fileName.replace('.tool.yaml', '').replace('.tool.yml', '');
  };

  // Create collection for tool selection - only show tools not already selected
  const toolCollection = useMemo(() => {
    const unselectedTools = availableTools.filter(
      tool => !tools.includes(tool.file_path)
    );
    
    return createListCollection({
      items: unselectedTools.map(tool => ({
        label: tool.name,
        value: tool.file_path,
      })),
    });
  }, [availableTools, tools]);

  if (!currentPrompt) {
    return null;
  }

  return (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>Tools</Fieldset.Legend>
              <Fieldset.HelperText color="text.tertiary">
                Select mock tools to use with this prompt
              </Fieldset.HelperText>
            </Stack>
            <HStack gap={2}>
              <Button
                variant="ghost"
                _hover={{ bg: "bg.subtle" }}
                size="sm"
                onClick={() => window.open('/tools?mode=new', '_self')}
                aria-label="Create new tool"
              >
                <HStack gap={1}>
                  <LuPlus size="xs" />
                  <Text fontSize="xs" fontWeight="medium">
                    Add Mock Tool
                  </Text>
                </HStack>
              </Button>
              <Button
                variant="ghost"
                _hover={{ bg: "bg.subtle" }}
                size="sm"
                onClick={() => setShowTools(!showTools)}
                aria-label={showTools ? "Collapse tools" : "Expand tools"}
              >
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="medium">
                    {showTools ? "Hide" : "Show"}
                  </Text>
                  {showTools ? <LuChevronUp /> : <LuChevronDown />}
                </HStack>
              </Button>
            </HStack>
          </HStack>

          <Fieldset.Content>
            <Collapsible.Root open={showTools}>
              <Collapsible.Content>
                <VStack gap={4} mt={3} align="stretch">
                  {/* Tool Selection */}
                  <VStack gap={2} align="stretch">

                    <Select.Root
                      collection={toolCollection}
                      size="sm"
                      value={[]}
                      onValueChange={(e: { value: string[] }) => {
                        if (e.value[0]) {
                          handleAddTool(e.value[0]);
                        }
                      }}
                      disabled={isLoadingTools || toolCollection.items.length === 0}
                    >
                      <Select.HiddenSelect />
                      <Select.Control>
                        <Select.Trigger>
                          <Select.ValueText 
                            placeholder={
                              isLoadingTools 
                                ? "Loading tools..." 
                                : toolCollection.items.length === 0 
                                  ? "No tools available" 
                                  : "Select a tool"
                            } 
                          />
                        </Select.Trigger>
                        <Select.IndicatorGroup>
                          <Select.Indicator />
                        </Select.IndicatorGroup>
                      </Select.Control>
                      <Portal>
                        <Select.Positioner>
                          <Select.Content>
                            {toolCollection.items.map((tool) => {
                              const toolInfo = availableTools.find(t => t.file_path === tool.value);
                              return (
                                <Select.Item key={tool.value} item={tool}>
                                  <VStack align="start" gap={0}>
                                    <Text fontSize="sm" fontWeight="medium">{tool.label}</Text>
                                    {toolInfo && (
                                      <Text fontSize="xs" color="fg.muted">{toolInfo.description}</Text>
                                    )}
                                  </VStack>
                                  <Select.ItemIndicator />
                                </Select.Item>
                              );
                            })}
                          </Select.Content>
                        </Select.Positioner>
                      </Portal>
                    </Select.Root>
                  </VStack>

                  {/* Selected Tools List */}
                  {tools.length > 0 && (
                    <VStack gap={2} align="stretch">
                      <Text fontSize="xs" fontWeight="medium">Selected Tools ({tools.length})</Text>
                      {tools.map((toolPath, index) => {
                        const toolName = getToolNameFromPath(toolPath);
                        const toolInfo = availableTools.find(t => t.file_path === toolPath);
                        
                        return (
                          <Card.Root key={index} size="sm" variant="outline">
                            <Card.Body>
                              <HStack justify="space-between">
                                <VStack align="start" gap={0} flex={1}>
                                  <Text fontSize="xs" fontWeight="medium">{toolName}</Text>
                                  {toolInfo && (
                                    <Text fontSize="xs" color="fg.muted" lineClamp={1}>
                                      {toolInfo.description}
                                    </Text>
                                  )}
                                  <Text fontSize="xs" color="fg.muted" opacity={0.6} fontFamily="mono">
                                    {toolPath}
                                  </Text>
                                </VStack>
                                <IconButton
                                  aria-label={`Remove ${toolName}`}
                                  size="xs"
                                  variant="ghost"
                                  colorPalette="red"
                                  onClick={() => handleRemoveTool(toolPath)}
                                >
                                  <LuX />
                                </IconButton>
                              </HStack>
                            </Card.Body>
                          </Card.Root>
                        );
                      })}
                    </VStack>
                  )}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}