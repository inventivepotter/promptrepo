"use client"

import { VStack, Box, Text, Input } from '@chakra-ui/react'

interface AuthStepProps {
  hostingType: string
  githubClientId: string
  githubClientSecret: string
  setGithubClientId: (id: string) => void
  setGithubClientSecret: (secret: string) => void
  disabled?: boolean
}

export default function AuthStep({
  hostingType,
  githubClientId,
  githubClientSecret,
  setGithubClientId,
  setGithubClientSecret,
  disabled = false
}: AuthStepProps) {
  if (hostingType === 'self') {
    return (
      <VStack gap={4}>
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
          <Text fontWeight="normal" fontSize="sm" color="blue.fg">
            For self-use hosting, no additional authentication setup is required.
          </Text>
        </Box>
        <Text>You can proceed to the next step.</Text>
      </VStack>
    )
  }
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">GitHub OAuth Configuration</Text>
        <Text opacity={0.7} fontSize="sm">
          To enable multi-user access, you will need to create a GitHub OAuth App and provide the credentials.
        </Text>
        <VStack gap={4} align="stretch">
          <Box>
            <Text mb={2} fontWeight="medium">GitHub Client ID</Text>
            <Input
              placeholder="Enter your GitHub Client ID"
              value={githubClientId}
              onChange={(e) => setGithubClientId(e.target.value)}
              disabled={disabled}
            />
          </Box>
          <Box>
            <Text mb={2} fontWeight="medium">GitHub Client Secret</Text>
            <Input
              type="password"
              placeholder="Enter your GitHub Client Secret"
              value={githubClientSecret}
              onChange={(e) => setGithubClientSecret(e.target.value)}
              disabled={disabled}
            />
            <Text fontSize="sm" opacity={0.7} mt={1}>
              Keep this secret safe. It will be stored in your .env file.
            </Text>
          </Box>
        </VStack>
      </VStack>
    </Box>
  )
}