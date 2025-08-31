"use client"

import { VStack, HStack, Text, Button, Box } from '@chakra-ui/react'

interface HostingStepProps {
  hostingType: string
  setHostingType: (type: 'individual' | 'organization') => void
  disabled?: boolean
}

export default function HostingStep({ hostingType, setHostingType, disabled = false }: HostingStepProps) {
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="xl" fontWeight="bold">Hosting Configuration</Text>
        <Text fontSize="sm" opacity={0.7}>How do you want to host this application?</Text>
        <HStack gap={4} align="stretch">
          <Button
            variant={hostingType === 'individual' ? 'solid' : 'outline'}
            size="lg"
            width="50%"
            p={8}
            onClick={() => setHostingType('individual')}
            disabled={disabled}
          >
            <VStack gap={2}>
              <Text fontWeight="bold">Individual</Text>
              <Text fontSize="sm" opacity={0.8}>
                Just for personal use
              </Text>
            </VStack>
          </Button>
          <Button
            variant={hostingType === 'organization' ? 'solid' : 'outline'}
            size="lg"
            width="50%"
            p={8}
            onClick={() => setHostingType('organization')}
            disabled={disabled}
          >
            <VStack gap={2}>
              <Text fontWeight="bold">Organization</Text>
              <Text fontSize="sm" opacity={0.8}>
                For teams or organization use with GitHub OAuth
              </Text>
            </VStack>
          </Button>
        </HStack>
      </VStack>
    </Box>
  )
}