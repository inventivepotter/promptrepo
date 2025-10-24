'use client';

import React, { useState } from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
  Combobox,
  createListCollection,
  Collapsible,
} from '@chakra-ui/react';
import { LuRefreshCw, LuBot, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Tool } from '../_types/ChatState';
import { ToolsHeader } from './ToolsHeader';

interface ChatHeaderProps {
  selectedTools: string[];
  availableTools: Tool[];
  onToolsChange: (tools: string[]) => void;
  onReset: () => void;
  isLoading?: boolean;
}

export function ChatHeader({
  selectedTools,
  availableTools,
  onToolsChange,
  onReset,
  isLoading = false
}: ChatHeaderProps) {
  const [toolSearchValue, setToolSearchValue] = React.useState('');
  const [showAgentSection, setShowAgentSection] = useState(true);
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const accentColor = useColorModeValue('gray.700', 'gray.300');

  // Filter tools based on search value
  const filteredTools = availableTools.filter(tool =>
    tool.name.toLowerCase().includes(toolSearchValue.toLowerCase()) ||
    tool.description.toLowerCase().includes(toolSearchValue.toLowerCase())
  );

  const toolsCollection = createListCollection({
    items: filteredTools.map(tool => ({
      value: tool.id,
      label: tool.name
    }))
  });

  return (
    <Box
      p={4}
      borderBottomWidth="1px"
    >
      <VStack gap={3} align="stretch">
        {/* Header with title and action buttons - Always visible */}
        <HStack justify="space-between" align="center">
          <HStack>
            <LuBot size={18} />
            <Text fontSize="lg" fontWeight="semibold">
              Agent
            </Text>
          </HStack>
          <HStack gap={2}>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setShowAgentSection(!showAgentSection)}
              aria-label={showAgentSection ? "Collapse agent section" : "Expand agent section"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {showAgentSection ? "Hide" : "Show"}
                </Text>
                {showAgentSection ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
            <Button
              size="sm"
              variant="ghost"
              colorPalette="red"
              onClick={onReset}
              disabled={isLoading}
              _hover={{ bg: 'red.50' }}
            >
              <HStack gap={2}>
                <LuRefreshCw size={14} />
                <Text>Reset</Text>
              </HStack>
            </Button>
          </HStack>
        </HStack>

        {/* Collapsible content - Only this part hides */}
        <Collapsible.Root open={showAgentSection}>
          <Collapsible.Content>
            <VStack gap={3} align="stretch">
              <Text fontSize="xs" color={mutedTextColor}>
                Your playground to test prompts with AI agents
              </Text>

              {/* Tools Selection */}
              <Box>
                <ToolsHeader accentColor={accentColor} mutedTextColor={mutedTextColor} />

                <Combobox.Root
            collection={toolsCollection}
            multiple
            value={selectedTools}
            onValueChange={(e) => onToolsChange(e.value)}
            inputValue={toolSearchValue}
            onInputValueChange={(e) => setToolSearchValue(e.inputValue)}
            openOnClick
            closeOnSelect={false}
          >
            <Combobox.Control position="relative">
              <Combobox.Input
                placeholder={selectedTools.length > 0 
                  ? `${selectedTools.length} tools selected` 
                  : "Select tools to enable"
                }
                paddingRight="2rem"
                fontSize="sm"
              />
              <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                <FaChevronDown size={10} />
              </Combobox.Trigger>
            </Combobox.Control>
            <Combobox.Positioner>
              <Combobox.Content>
                {filteredTools.length === 0 ? (
                  <Text p={3} fontSize="sm" color={mutedTextColor}>
                    No tools available
                  </Text>
                ) : (
                  filteredTools.map(tool => (
                    <Combobox.Item key={tool.id} item={tool.id}>
                      <VStack align="start" gap={1} py={1}>
                        <Combobox.ItemText fontSize="sm" fontWeight="medium">
                          {tool.name}
                        </Combobox.ItemText>
                        <Text fontSize="xs" color={mutedTextColor} lineClamp={2}>
                          {tool.description}
                        </Text>
                      </VStack>
                      <Combobox.ItemIndicator />
                    </Combobox.Item>
                  ))
                )}
              </Combobox.Content>
                </Combobox.Positioner>
                </Combobox.Root>
              </Box>
            </VStack>
          </Collapsible.Content>
        </Collapsible.Root>
      </VStack>
    </Box>
  );
}