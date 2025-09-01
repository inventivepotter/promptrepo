'use client';

import React from 'react';
import {
  VStack,
  Text,
  Box,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Tool } from '../_types/ChatState';

interface ChatFooterProps {
  selectedTools: string[];
  availableTools: Tool[];
  onToolsChange: (tools: string[]) => void;
}

export function ChatFooter({
  selectedTools,
  availableTools,
  onToolsChange
}: ChatFooterProps) {
  const [toolSearchValue, setToolSearchValue] = React.useState('');
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
      p={3}
      borderTopWidth="1px"
      borderColor="gray.200"
    >
      {/* Tools Selection */}
      <Box>
        <Text fontSize="xs" fontWeight="medium" mb={1} color={mutedTextColor}>
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
    </Box>
  );
}