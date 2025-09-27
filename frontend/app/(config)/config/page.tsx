'use client'

import { Box, Container, VStack } from '@chakra-ui/react'
import { ConfigSection, LLMConfigManager, RepoConfigManager } from '@/components/config'
import { ConfigHeader } from '../../../components/config/ConfigHeader'

export default function ConfigPage() {
  return (
    <Box width="100%">
      <VStack gap={8} align="stretch">
        <ConfigHeader />
        <Container maxW="7xl" py={6}>
          <ConfigSection>
            <LLMConfigManager />
            <RepoConfigManager />
          </ConfigSection>
        </Container>
      </VStack>
    </Box>
  )
}