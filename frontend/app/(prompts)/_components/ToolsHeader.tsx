import { HStack, Text, Badge } from '@chakra-ui/react';

interface ToolsHeaderProps {
  accentColor: string;
  mutedTextColor: string;
}

export function ToolsHeader({ accentColor, mutedTextColor }: ToolsHeaderProps) {
  return (
    <>
      <HStack justify="space-between" align="center" mb={1.5}>
        <Text fontSize="xs" fontWeight="medium" color={accentColor}>
          Mock Tools
        </Text>
        <Badge colorPalette="gray" variant="subtle" size="xs">
          Optional
        </Badge>
      </HStack>
      <Text fontSize="xs" color={mutedTextColor} mb={2}>
        Simulated tools for testing — select to enable
      </Text>
    </>
  );
}