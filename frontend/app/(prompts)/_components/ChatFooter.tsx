'use client';

import { useState } from 'react';
import {
  VStack,
  Text,
  Box,
  Combobox,
  createListCollection,
  HStack,
  Button,
  Popover,
} from '@chakra-ui/react';
import { FaChevronDown, FaInfoCircle } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';
import { useToolsManagement } from '@/stores/chatStore/hooks';

export function ChatFooter() {
  const { availableTools, selectedTools, setSelectedTools } = useToolsManagement();
  const [toolSearchValue, setToolSearchValue] = useState('');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const linkColor = useColorModeValue('blue.500', 'blue.300');

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
      <Box mb={3}>
        <Text fontSize="xs" fontWeight="medium" mb={1} color={mutedTextColor}>
          Available Tools
        </Text>
        <Combobox.Root
          collection={toolsCollection}
          multiple
          value={selectedTools}
          onValueChange={(e) => setSelectedTools(e.value)}
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

      {/* Disclaimer Popover */}
      <HStack justify="flex-end">
        <Popover.Root>
          <Popover.Trigger asChild>
            <Button
              variant="plain"
              size="xs"
              color="fg.muted"
              fontSize="xs"
              px={2}
              py={1}
              height="auto"
              minHeight="auto"
            >
              <Text>Disclaimer!</Text>
            </Button>
          </Popover.Trigger>
          <Popover.Positioner>
            <Popover.Content maxWidth="400px">
              <Popover.Arrow>
                <Popover.ArrowTip />
              </Popover.Arrow>
              <Popover.Body>
                <VStack align="start" gap={3} fontSize="sm">
                  <Popover.Title fontWeight="medium" color={useColorModeValue('gray.800', 'gray.200')}>
                    Metrics Accuracy Disclaimer
                  </Popover.Title>
                  
                  <Text color={useColorModeValue('gray.700', 'gray.300')}>
                    The inference time, number of tokens, and cost displayed are realistic estimates but may not be entirely accurate:
                  </Text>
                  
                  <VStack align="start" gap={2} fontSize="sm">
                    <HStack align="start" gap={2}>
                      <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                      <Text color={useColorModeValue('gray.700', 'gray.300')}>
                        <Text as="span" fontWeight="medium">Cost:</Text> May be significantly lower if cache hits occur, as cached responses have reduced pricing
                      </Text>
                    </HStack>
                    <HStack align="start" gap={2}>
                      <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                      <Text color={useColorModeValue('gray.700', 'gray.300')}>
                        <Text as="span" fontWeight="medium">Inference time:</Text> Includes our processing time for API calls, not just model inference
                      </Text>
                    </HStack>
                    <HStack align="start" gap={2}>
                      <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                      <Text color={useColorModeValue('gray.700', 'gray.300')}>
                        <Text as="span" fontWeight="medium">Tokens:</Text> Calculated by word count when providers don&apos;t share exact tokenization data
                      </Text>
                    </HStack>
                  </VStack>
                  
                  <Text fontSize="xs" color={useColorModeValue('gray.600', 'gray.400')}>
                    These metrics provide useful estimates for understanding usage patterns and costs.
                  </Text>
                </VStack>
              </Popover.Body>
              <Popover.CloseTrigger />
            </Popover.Content>
          </Popover.Positioner>
        </Popover.Root>
      </HStack>
    </Box>
  );
}