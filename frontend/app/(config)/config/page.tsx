'use client'

import { Box, Container, VStack } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { ConfigSection, LLMConfigManager, RepoConfigManager } from '@/components/config'
import { ConfigHeader } from '../../../components/config/ConfigHeader'
import { useConfigActions, useConfig } from '@/stores/configStore'
import { useLoadingStore } from '@/stores/loadingStore'

export default function ConfigPage() {
  const router = useRouter()
  const { showLoading, hideLoading, isLoading } = useLoadingStore()
  const { updateConfig } = useConfigActions()
  const config = useConfig()

  const handleSave = async () => {
    showLoading()
    
    try {
      // Pass the current config data to updateConfig
      await updateConfig({
        llm_configs: config.llm_configs || [],
        repo_configs: config.repo_configs || [],
      })
      router.push('/')
    } catch (error) {
      console.error('Failed to save config:', error)
    } finally {
      hideLoading()
    }
  }

  return (
    <Box width="100%">
      <VStack gap={8} align="stretch">
        <ConfigHeader onSave={handleSave} isLoading={isLoading} />
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