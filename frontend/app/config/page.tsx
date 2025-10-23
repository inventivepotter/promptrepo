'use client'

import { useEffect } from 'react'
import { Box, Container, ScrollArea } from '@chakra-ui/react'
import { ConfigSection, ConfigHeader, LLMConfigManager, RepoConfigManager } from '@/components/config'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export default function ConfigPage() {
  useEffect(() => {
    // Check for hash in URL and scroll to that section
    if (window.location.hash) {
      const hash = window.location.hash.substring(1); // Remove the '#'
      const element = document.getElementById(hash);
      if (element) {
        // Use setTimeout to ensure the element is fully rendered
        setTimeout(() => {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }
    }
  }, []);

  return (
    <ProtectedRoute>
      <Box height="100vh" width="100%" display="flex" flexDirection="column">
        {/* Config Header - Outside ScrollArea */}
        <ConfigHeader />

        <ScrollArea.Root flex="1" width="100%">
          <ScrollArea.Viewport
            css={{
              "--scroll-shadow-size": "5rem",
              maskImage:
                "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              "&[data-at-top]": {
                maskImage:
                  "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              },
              "&[data-at-bottom]": {
                maskImage:
                  "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
              },
            }}
          >
            <ScrollArea.Content>
              <Box position="relative">
                <Container maxW="7xl" py={6}>
                  <ConfigSection>
                    <LLMConfigManager />
                    <RepoConfigManager />
                  </ConfigSection>
                </Container>
              </Box>
            </ScrollArea.Content>
          </ScrollArea.Viewport>
          <ScrollArea.Scrollbar orientation="vertical">
            <ScrollArea.Thumb />
          </ScrollArea.Scrollbar>
        </ScrollArea.Root>
      </Box>
    </ProtectedRoute>
  )
}