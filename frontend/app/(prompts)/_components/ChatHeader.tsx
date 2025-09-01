'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { LuRefreshCw } from 'react-icons/lu';
import { GiMagicLamp } from 'react-icons/gi'
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { Tool } from '../_types/ChatState';

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
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

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
        {/* Header with just description and reset button */}
        <HStack justify="space-between" align="center">
          <Text fontSize="xs" color={mutedTextColor}>
            Your playground to test prompts with AI agents
          </Text>
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

        {/* Tools Selection */}
        <Box>
          <Text fontSize="sm" fontWeight="medium" mb={2} color={mutedTextColor}>
            Available Tools
          </Text>
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
                <FaChevronDown size={12} />
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
    </Box>
  );
}