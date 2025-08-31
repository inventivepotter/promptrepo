"use client"

import { VStack, Text, Button, Box } from '@chakra-ui/react'

interface HostingStepProps {
  hostingType: string
  setHostingType: (type: 'self' | 'multi-user') => void
  disabled?: boolean
}

export default function HostingStep({ hostingType, setHostingType, disabled = false }: HostingStepProps) {
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="xl" fontWeight="bold">Hosting Configuration</Text>
        <Text fontSize="sm" opacity={0.7}>How do you want to host this application?</Text>
        <VStack gap={4}>
          <Button
            variant={hostingType === 'self' ? 'solid' : 'outline'}
            size="lg"
            width="100%"
            p={8}
            onClick={() => setHostingType('self')}
            disabled={disabled}
          >
            <VStack gap={2}>
              <Text fontWeight="bold">Self Use Only</Text>
              <Text fontSize="sm" opacity={0.8}>
                Just for personal use
              </Text>
            </VStack>
          </Button>
          <Button
            variant={hostingType === 'multi-user' ? 'solid' : 'outline'}
            size="lg"
            width="100%"
            p={8}
            onClick={() => setHostingType('multi-user')}
            disabled={disabled}
          >
            <VStack gap={2}>
              <Text fontWeight="bold">Multi-User Deployment</Text>
              <Text fontSize="sm" opacity={0.8}>
                Allow multiple users with GitHub OAuth
              </Text>
            </VStack>
          </Button>
        </VStack>
      </VStack>
    </Box>
  )
}