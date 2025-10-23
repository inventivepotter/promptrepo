'use client'

import Link from 'next/link'
import {
  Box,
  HStack,
  Button,
  Separator,
  Stack,
} from '@chakra-ui/react'
import {
  LuSettings,
  LuFileText,
} from 'react-icons/lu'
import { useSidebarCollapsed, useSidebarHasHydrated } from '@/stores/sidebarStore'
import { Branding } from '../Branding'
import { AuthSection } from './AuthSection'
import { ThemeToggle } from './ThemeToggle'
import { SidebarToggle } from './SidebarToggle'

interface SidebarProps {
  className?: string
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const hasHydrated = useSidebarHasHydrated();
  const isCollapsed = useSidebarCollapsed();

  // Show placeholder with correct width while hydrating
  if (!hasHydrated) {
    return
  }

  // Theme-aware semantic colors
  const hoverBg = "bg.muted"
  const activeBg = "bg.emphasized"
  const userProfileBg = "bg.muted"

  const sidebarWidth = isCollapsed ? '60px' : '180px'

  return (
    <Box
      className={className}
      width={sidebarWidth}
      minHeight="100vh"
      bg="bg.subtle"
      borderRight="1px solid"
      borderColor="bg.muted"
      transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
      position="relative"
      zIndex={10}
    >
      {/* Header with branding */}
      <Box px={isCollapsed ? 2 : 4} py={6}>
        <HStack justify="space-between" align="center" minH="46px">
          <Branding collapsed={isCollapsed} />
        </HStack>
      </Box>
      <Separator borderColor="bg.muted" mx={2} />
      {/* Navigation Menu */}
      <Stack gap={1} p={2} pt={3}>
        {/* Setup */}
        <Box as="span" width="100%">
          <Link href="/config" style={{ textDecoration: 'none' }}>
            <Button
              variant="ghost"
              justifyContent={isCollapsed ? "center" : "flex-start"}
              size="sm"
              _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="2px"
              fontWeight="500"
              transition="all 0.15s ease"
              width="100%"
            >
              <LuSettings size={16} />
              {!isCollapsed && (
                <span style={{ marginLeft: 12, fontSize: '14px', fontWeight: 500 }}>
                  Configuration
                </span>
              )}
            </Button>
          </Link>
        </Box>

        {/* Prompts */}
        <Box as="span" width="100%">
          <Link href="/prompts" style={{ textDecoration: 'none' }}>
            <Button
              variant="ghost"
              justifyContent={isCollapsed ? "center" : "flex-start"}
              size="sm"
              _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="2px"
              fontWeight="500"
              transition="all 0.15s ease"
              width="100%"
            >
              <LuFileText size={16} />
              {!isCollapsed && (
                <span style={{ marginLeft: 12, fontSize: '14px', fontWeight: 500 }}>
                  Prompts
                </span>
              )}
            </Button>
          </Link>
        </Box>
      </Stack>

      {/* Bottom section */}
      <Box position="absolute" bottom={0} left={0} right={0} p={2}>
        <Stack gap={1}>
          {/* Auth Section (User Profile + Login/Logout) */}
          <AuthSection
            isCollapsed={isCollapsed}
            hoverBg={hoverBg}
            activeBg={activeBg}
            userProfileBg={userProfileBg}
            borderColor="bg.muted"
          />
          
          <Separator borderColor="bg.muted" />

          {/* Theme Toggle */}
          <ThemeToggle
            isCollapsed={isCollapsed}
            hoverBg={hoverBg}
            activeBg={activeBg}
          />

          {/* Sidebar Toggle Button */}
          <SidebarToggle
            hoverBg={hoverBg}
            activeBg={activeBg}
          />
        </Stack>
      </Box>
    </Box>
  )
}

export default Sidebar