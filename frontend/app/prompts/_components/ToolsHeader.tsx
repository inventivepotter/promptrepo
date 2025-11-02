import { HStack, Text, Badge } from '@chakra-ui/react';

interface ToolsHeaderProps {
  accentColor: string;
  mutedTextColor: string;
}

export function ToolsHeader({ accentColor, mutedTextColor }: ToolsHeaderProps) {
  return (
    <>
      <HStack justify="space-between" align="center" mb={1.5} minWidth={0}>
        <Text fontSize="xs" fontWeight="medium" color={accentColor} flexShrink={0}>
          Mock Tools
        </Text>
        <Badge colorPalette="gray" variant="subtle" size="xs" flexShrink={0}>
          Optional
        </Badge>
      </HStack>
      <Text fontSize="xs" color={mutedTextColor} mb={2} wordBreak="break-word">
        Simulated tools for testing — select to enable
      </Text>
    </>
  );
}