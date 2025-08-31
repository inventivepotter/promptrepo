"use client"

import { VStack, Box, Text, Input } from '@chakra-ui/react'

interface AdminConfigStepProps {
  adminEmails: string[]
  setAdminEmails: (emails: string[]) => void
  disabled?: boolean
  showEnvNote?: boolean
}

export default function AdminConfigStep({
  adminEmails,
  setAdminEmails,
  disabled = false,
  showEnvNote = false
}: AdminConfigStepProps) {
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">Admin Configuration</Text>
        <Text fontSize="sm" opacity={0.7}>
          Configure administrator email addresses for system management and notifications.
        </Text>
        {showEnvNote && (
          <Box p={3} bg="blue.50" _dark={{ bg: "blue.900", borderColor: "blue.700" }} borderRadius="md" border="1px solid" borderColor="blue.200">
            <Text fontSize="sm" color="blue.600" _dark={{ color: "blue.300" }}>
              💡 <strong>Note:</strong> Admin email settings are editable here but will be displayed as environment variables for you to copy to your deployment configuration. Only repository settings are saved to the system.
            </Text>
          </Box>
        )}
        <VStack gap={4} align="stretch">
          <Box>
            <Text mb={2} fontWeight="medium">Admin Email Addresses</Text>
            <Input
              placeholder="admin1@example.com, admin2@example.com"
              value={adminEmails.join(', ')}
              onChange={(e) => {
                const emailsArray = e.target.value
                  .split(',')
                  .map(email => email.trim())
                  .filter(email => email.length > 0)
                setAdminEmails(emailsArray)
              }}
              disabled={disabled}
            />
            <Text fontSize="sm" opacity={0.7} mt={1}>
              Enter comma-separated email addresses for administrators who will have access to system management features.
            </Text>
          </Box>
        </VStack>
      </VStack>
    </Box>
  )
}