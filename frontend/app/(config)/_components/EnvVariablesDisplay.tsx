"use client"

import React from 'react'
import {
  VStack,
  Box,
  Text,
  Button,
  HStack,
  Textarea,
  Clipboard
} from '@chakra-ui/react'
import { LuCopy, LuCheck } from 'react-icons/lu'

interface EnvVariablesDisplayProps {
  hostingType: string
  githubClientId: string
  githubClientSecret: string
  llmConfigs: Array<{
    provider: string
    model: string
    apiKey: string
    apiBaseUrl?: string
  }>
}

export function EnvVariablesDisplay({
  hostingType,
  githubClientId,
  githubClientSecret,
  llmConfigs
}: EnvVariablesDisplayProps) {
  
  // Generate environment variables string
  const generateEnvVars = () => {
    const envVars: string[] = []
    
    // Add comments for organization
    envVars.push('# Application Configuration')
    envVars.push('')
    
    // Hosting type
    envVars.push('## Hosting Type')
    envVars.push('# Options: individual, organization, multi-tenant')
    envVars.push('# - individual: Single user, no auth required, LLM configs only')
    envVars.push('# - organization: Multi-user with GitHub OAuth, requires LLM configs')
    envVars.push('# - multi-tenant: Multiple organizations, no global LLM configs')
    envVars.push(`HOSTING_TYPE="${hostingType}"`)
    envVars.push('')
    
    // GitHub OAuth (only for organization hosting)
    if (hostingType === 'organization' && githubClientId && githubClientSecret) {
      envVars.push('## GitHub OAuth')
      envVars.push(`GITHUB_CLIENT_ID="${githubClientId}"`)
      envVars.push(`GITHUB_CLIENT_SECRET="${githubClientSecret}"`)
      envVars.push('')
    }
    
    // LLM configurations (only for non multi-tenant)
    if (hostingType !== 'multi-tenant' && llmConfigs.length > 0) {
      envVars.push('## LLM Configs')
      const configArray = llmConfigs.map(config => ({
        provider: config.provider,
        model: config.model,
        apiKey: config.apiKey,
        apiBaseUrl: config.apiBaseUrl || ""
      }))
      envVars.push(`LLM_CONFIGS=${JSON.stringify(configArray)}`)
      envVars.push('')
    }
    
    
    return envVars.join('\n')
  }
  
  const envVarsString = generateEnvVars()
  
  if (!envVarsString.trim()) {
    return null
  }
  
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized" bg="bg.subtle" minHeight="600px">
      <VStack gap={4} align="stretch" height="100%">
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Text fontSize="lg" fontWeight="bold">
              Environment Variables
            </Text>
            <Text fontSize="sm" opacity={0.7}>
              Copy these variables to your environment configuration
            </Text>
          </VStack>
          <Clipboard.Root value={envVarsString}>
            <Clipboard.Trigger asChild>
              <Button size="sm" variant="outline">
                <HStack gap={2}>
                  <LuCopy size={16} />
                  <Text>Copy All</Text>
                </HStack>
              </Button>
            </Clipboard.Trigger>
            <Clipboard.Indicator copied={<LuCheck size={16} />}>
              <LuCopy size={16} />
            </Clipboard.Indicator>
          </Clipboard.Root>
        </HStack>
        
        <Box position="relative" flex="1">
          <Textarea
            value={envVarsString}
            readOnly
            fontFamily="mono"
            fontSize="sm"
            height="100%"
            minHeight="400px"
            bg="blackAlpha.50"
            _dark={{ bg: "whiteAlpha.50" }}
            borderColor="border.muted"
            resize="vertical"
            spellCheck={false}
          />
        </Box>
        
        <Text fontSize="xs" opacity={0.6}>
          <strong>Note:</strong> Repository configurations are saved to the system. 
          All other settings above are for reference only - copy them to your .env or deployment configuration.
        </Text>
      </VStack>
    </Box>
  )
}