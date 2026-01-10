'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  VStack,
  Text,
  Box,
  HStack,
  Button,
  Input,
  Textarea,
  Field,
  Card,
  Fieldset,
  Stack,
  Collapsible,
  ScrollArea,
} from '@chakra-ui/react';
import { HiCheck } from 'react-icons/hi';
import { LuArrowLeft, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import type { ToolDefinition, ParameterSchema, MockConfig, ReturnsSchema } from '@/types/tools';
import { ToolsService } from '@/services/tools';
import { errorNotification } from '@/lib/notifications';
import { ParameterEditor } from '../../_components/ParameterEditor';
import { MockDataEditor } from '../../_components/MockDataEditor';
import { toaster } from '@/components/ui/toaster';
import { decodeBase64Url, buildToolEditorUrl } from '@/lib/urlEncoder';

export default function ToolEditorPage() {
  const router = useRouter();
  const pathname = usePathname();
  
  // Parse path: /tools/editor/{base64_repo}/{base64_tool_name}
  const pathParts = pathname.split('/').filter(Boolean);
  // pathParts = ['tools', 'editor', '{base64_repo}', '{base64_tool_name}']
  const repoName = pathParts.length >= 3 ? decodeBase64Url(pathParts[2]) : '';
  // Check if it's 'new' BEFORE decoding to avoid decoding the literal string 'new'
  const isNewTool = pathParts[3] === 'new';
  const toolName = isNewTool ? 'new' : (pathParts.length >= 4 ? decodeBase64Url(pathParts[3]) : '');

  const [isLoading, setIsLoading] = useState(!isNewTool);
  const [isSaving, setIsSaving] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [parameters, setParameters] = useState<Record<string, ParameterSchema>>({});
  const [required, setRequired] = useState<string[]>([]);
  const [returns, setReturns] = useState<ReturnsSchema | undefined | null>(undefined);
  const [mockConfig, setMockConfig] = useState<MockConfig>({
    enabled: true,
    mock_type: 'static',
    content_type: 'string',
    static_response: '',
  });
  // Collapsible section state
  const [showBasicInfo, setShowBasicInfo] = useState(true);
  const [showParameters, setShowParameters] = useState(true);
  const [showReturns, setShowReturns] = useState(false);

  // Load existing tool if editing
  useEffect(() => {
    if (!repoName) {
      errorNotification('No Repository', 'Please select a repository from the tools page');
      router.push('/tools');
      return;
    }
    
    if (!isNewTool && repoName) {
      loadTool();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname, isNewTool, repoName]);

  const loadTool = async () => {
    if (!repoName) return;
    
    try {
      setIsLoading(true);
      const tool = await ToolsService.getTool(decodeURIComponent(toolName), repoName);
      setName(tool.name);
      setDescription(tool.description);
      setParameters(tool.parameters?.properties || {});
      setRequired(tool.parameters?.required || []);
      setReturns(tool.returns);
      setMockConfig({
        enabled: tool.mock?.enabled ?? true,
        mock_type: tool.mock?.mock_type || 'static',
        content_type: tool.mock?.content_type || 'string',
        static_response: tool.mock?.static_response,
        conditional_rules: tool.mock?.conditional_rules,
        python_code: tool.mock?.python_code,
      });
    } catch (error) {
      console.error('Failed to load tool:', error);
      errorNotification('Load Failed', 'Failed to load tool');
      router.push('/tools');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!repoName) {
      errorNotification('No Repository', 'Repository is required');
      return;
    }

    // Validation
    if (!name.trim()) {
      errorNotification('Validation Error', 'Tool name is required');
      return;
    }
    // Validate tool name format (must be valid function name)
    if (!/^[a-z][a-z0-9_]*$/.test(name.trim())) {
      errorNotification(
        'Validation Error',
        'Tool name must be in function-name format (lowercase, start with letter, contain only letters, numbers, and underscores)'
      );
      return;
    }
    if (!description.trim()) {
      errorNotification('Validation Error', 'Tool description is required');
      return;
    }

    const tool: ToolDefinition = {
      name: name.trim(),
      description: description.trim(),
      parameters: {
        type: 'object',
        properties: parameters,
        required: required,
      },
      returns: returns,
      mock: mockConfig,
    };

    setIsSaving(true);
    
    try {
      const savePromise = ToolsService.saveTool(tool, repoName, isNewTool ? 'new' : toolName);

      toaster.promise(savePromise, {
        loading: {
          title: 'Saving...',
          description: 'Creating a PR for your changes.',
        },
        success: (data) => {
          const prInfo = data?.pr_info as { pr_url?: string; pr_number?: number } | null | undefined;
          const prUrl = prInfo?.pr_url;
          const prNumber = prInfo?.pr_number;

          if (prUrl) {
            return {
              title: 'Successfully saved!',
              description: `Pull Request #${prNumber} created`,
              duration: 30000,
              closable: true,
              action: {
                label: 'View PR',
                onClick: () => {
                  window.open(prUrl, '_blank', 'noopener,noreferrer');
                },
              },
            };
          }

          return {
            title: 'Successfully saved!',
            description: `Tool "${tool.name}" ${isNewTool ? 'created' : 'updated'} successfully`,
            duration: 5000,
            closable: true,
          };
        },
        error: {
          title: 'Save failed',
          description: 'Something went wrong while saving',
        },
      });

      const result = await savePromise;
      
      // Redirect after successful save for new tools
      if (isNewTool && result?.file_path) {
        setTimeout(() => {
          router.push(buildToolEditorUrl(repoName, result.file_path));
        }, 1000);
      }
    } catch (error) {
      console.error('Failed to save tool:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    router.push('/tools');
  };

  if (isLoading) {
    return (
      <Box height="100vh" width="100%" display="flex" alignItems="center" justifyContent="center">
        <Text>Loading...</Text>
      </Box>
    );
  }

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Sticky Header */}
      <Box
        py={4}
        px={6}
        position="sticky"
        top={0}
        zIndex={10}
        bg="bg.subtle"
      >
        <HStack justify="space-between" align="center" maxW="1400px" mx="auto">
          <HStack gap={4}>
            <Button
              variant="outline"
              onClick={handleCancel}
              size="sm"
            >
              <HStack gap={2}>
                <LuArrowLeft size={16} />
                <Text>Back</Text>
              </HStack>
            </Button>
            <VStack align="start" gap={1}>
              <Text
                color="fg.muted"
                fontSize="2xl"
                letterSpacing="tight"
                fontWeight="1000"
              >
                {isNewTool ? 'Create New Tool' : name || 'New Tool'}
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                {isNewTool ? 'Configure tool settings and mock responses.' : 'Edit tool configuration.'} Click Save to push changes and create a PR.
              </Text>
            </VStack>
          </HStack>
          <HStack gap={3}>
            <Button
              colorScheme="blue"
              onClick={handleSave}
              loading={isSaving}
              disabled={isSaving}
            >
              <HiCheck /> {isSaving ? 'Saving...' : 'Save Tool'}
            </Button>
          </HStack>
        </HStack>
      </Box>

      <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "5rem",
            maskImage:
              "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-top]": {
              maskImage:
                "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-bottom]": {
              maskImage:
                "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
          }}
        >
          <ScrollArea.Content>
            <Box position="relative">
              {/* Two-column layout */}
              <Box p={6}>
                <HStack gap={6} align="start" maxW="1400px" mx="auto">
                  {/* Left Column - Tool Settings (55%) */}
                  <Box width="55%">
                    <VStack gap={6} align="stretch">
                      {/* Basic Information Section */}
                      <Card.Root position="relative">
                        <Card.Body pt={6}>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Basic Information</Fieldset.Legend>
                                <Fieldset.HelperText color="fg.muted">
                                  Configure the tool name and description
                                </Fieldset.HelperText>
                              </Stack>
                              <Button
                                variant="ghost"
                                _hover={{ bg: "bg.subtle" }}
                                size="sm"
                                onClick={() => setShowBasicInfo(!showBasicInfo)}
                                aria-label={showBasicInfo ? "Collapse basic info" : "Expand basic info"}
                              >
                                <HStack gap={1}>
                                  <Text fontSize="xs" fontWeight="medium">
                                    {showBasicInfo ? "Hide" : "Show"}
                                  </Text>
                                  {showBasicInfo ? <LuChevronUp /> : <LuChevronDown />}
                                </HStack>
                              </Button>
                            </HStack>

                            <Fieldset.Content>
                              <Collapsible.Root open={showBasicInfo}>
                                <Collapsible.Content>
                                  <VStack gap={4} align="stretch" mt={3}>
                                    <Field.Root required>
                                      <Field.Label fontSize="xs" fontWeight="medium">
                                        Tool Name <Field.RequiredIndicator />
                                      </Field.Label>
                                      <Input
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="my_tool"
                                        disabled={!isNewTool}
                                        size="md"
                                      />
                                      <Field.HelperText fontSize="xs" color="fg.muted">
                                        Unique identifier in function-name format (lowercase, underscores)
                                      </Field.HelperText>
                                    </Field.Root>

                                    <Field.Root required>
                                      <Field.Label fontSize="xs" fontWeight="medium">
                                        Description <Field.RequiredIndicator />
                                      </Field.Label>
                                      <Textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Describe what this tool does..."
                                        rows={4}
                                        resize="vertical"
                                      />
                                    </Field.Root>
                                  </VStack>
                                </Collapsible.Content>
                              </Collapsible.Root>
                            </Fieldset.Content>
                          </Fieldset.Root>
                        </Card.Body>
                      </Card.Root>

                      {/* Parameters Section */}
                      <Card.Root>
                        <Card.Body>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Parameters</Fieldset.Legend>
                                <Fieldset.HelperText color="fg.muted">
                                  Define the input parameters for this tool
                                </Fieldset.HelperText>
                              </Stack>
                              <Button
                                variant="ghost"
                                _hover={{ bg: "bg.subtle" }}
                                size="sm"
                                onClick={() => setShowParameters(!showParameters)}
                                aria-label={showParameters ? "Collapse parameters" : "Expand parameters"}
                              >
                                <HStack gap={1}>
                                  <Text fontSize="xs" fontWeight="medium">
                                    {showParameters ? "Hide" : "Show"}
                                  </Text>
                                  {showParameters ? <LuChevronUp /> : <LuChevronDown />}
                                </HStack>
                              </Button>
                            </HStack>

                            <Fieldset.Content>
                              <Collapsible.Root open={showParameters}>
                                <Collapsible.Content>
                                  <Box mt={3}>
                                    <ParameterEditor
                                      parameters={parameters}
                                      required={required}
                                      onParametersChange={setParameters}
                                      onRequiredChange={setRequired}
                                    />
                                  </Box>
                                </Collapsible.Content>
                              </Collapsible.Root>
                            </Fieldset.Content>
                          </Fieldset.Root>
                        </Card.Body>
                      </Card.Root>

                      {/* Returns Section */}
                      <Card.Root>
                        <Card.Body>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Return Type (Optional)</Fieldset.Legend>
                                <Fieldset.HelperText color="fg.muted">
                                  Define the structure of the return value
                                </Fieldset.HelperText>
                              </Stack>
                              <Button
                                variant="ghost"
                                _hover={{ bg: "bg.subtle" }}
                                size="sm"
                                onClick={() => setShowReturns(!showReturns)}
                                aria-label={showReturns ? "Collapse returns" : "Expand returns"}
                              >
                                <HStack gap={1}>
                                  <Text fontSize="xs" fontWeight="medium">
                                    {showReturns ? "Hide" : "Show"}
                                  </Text>
                                  {showReturns ? <LuChevronUp /> : <LuChevronDown />}
                                </HStack>
                              </Button>
                            </HStack>

                            <Fieldset.Content>
                              <Collapsible.Root open={showReturns}>
                                <Collapsible.Content>
                                  <Box mt={3}>
                                    <VStack gap={3} align="stretch">
                                      <Text fontSize="xs" color="fg.muted">
                                        {returns ? 'Return type is configured' : 'No return type configured'}
                                      </Text>
                                      <Text fontSize="xs" color="fg.muted">
                                        Note: Return type configuration UI will be added in a future update.
                                      </Text>
                                    </VStack>
                                  </Box>
                                </Collapsible.Content>
                              </Collapsible.Root>
                            </Fieldset.Content>
                          </Fieldset.Root>
                        </Card.Body>
                      </Card.Root>

                    </VStack>
                  </Box>

                  {/* Right Column - Mock Data (45%) */}
                  <Box width="45%">
                    <Card.Root>
                      <Card.Body>
                        <Fieldset.Root>
                          <Stack>
                            <Fieldset.Legend>Mock Data Configuration</Fieldset.Legend>
                            <Fieldset.HelperText color="fg.muted">
                              Configure mock responses for testing this tool
                            </Fieldset.HelperText>
                          </Stack>

                          <Fieldset.Content>
                            <Box mt={4}>
                              <MockDataEditor
                                mockConfig={mockConfig}
                                parameters={parameters}
                                onChange={setMockConfig}
                              />
                            </Box>
                          </Fieldset.Content>
                        </Fieldset.Root>
                      </Card.Body>
                    </Card.Root>
                  </Box>
                </HStack>
              </Box>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>
    </Box>
  );
}