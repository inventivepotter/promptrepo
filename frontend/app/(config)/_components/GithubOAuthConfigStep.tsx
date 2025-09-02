"use client"

import { VStack, Box, Text, Input } from '@chakra-ui/react'

interface AuthStepProps {
  hostingType: string
  githubClientId: string
  githubClientSecret: string
  setGithubClientId: (id: string) => void
  setGithubClientSecret: (secret: string) => void
  disabled?: boolean
  showEnvNote?: boolean
}

export default function AuthStep({
  hostingType,
  githubClientId,
  githubClientSecret,
  setGithubClientId,
  setGithubClientSecret,
  disabled = false,
  showEnvNote = false
}: AuthStepProps) {
  if (hostingType === 'individual') {
    return (
      <></>
    )
  }

  if (hostingType === 'multi-tenant') {
    return (
      <VStack gap={4}>
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
          <Text fontWeight="normal" fontSize="sm" color="blue.fg">
            For multi-tenant hosting, GitHub OAuth is handled per tenant. No global configuration is needed here.
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
          To enable organization access, you will need to create a GitHub OAuth App and provide the credentials.
        </Text>
        {showEnvNote && (
          <Box p={3} bg="blue.50" _dark={{ bg: "blue.900", borderColor: "blue.700" }} borderRadius="md" border="1px solid" borderColor="blue.200">
            <Text fontSize="sm" color="blue.600" _dark={{ color: "blue.300" }}>
              💡 <strong>Note:</strong> GitHub OAuth settings are editable here but will be displayed as environment variables for you to copy to your deployment configuration. Only repository settings are saved to the system.
            </Text>
          </Box>
        )}
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