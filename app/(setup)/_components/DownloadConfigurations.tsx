"use client"

import { VStack, Box, Text, Button } from '@chakra-ui/react'

interface EnvReadyStepProps {
  downloadEnvFile: () => void
}

export default function DownloadConfigurations({ downloadEnvFile }: EnvReadyStepProps) {
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={4} align="stretch">
        <Text fontWeight="bold" fontSize="lg" textAlign="left">
          Configurations
        </Text>
        <Text fontSize="sm" opacity={0.8} textAlign="left">
          Download your .env file and keep it safe for future deployments.
          This file contains your API keys and configuration.
        </Text>
        <Button variant="outline" onClick={downloadEnvFile} alignSelf="flex-start">
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Download .env File
          </span>
        </Button>
      </VStack>
    </Box>
  )
}