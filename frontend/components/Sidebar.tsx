"use client"

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  Box,
  HStack,
  Text,
  Button,
  Separator,
  Stack,
  VStack,
} from '@chakra-ui/react'
import {
  LuSettings,
  LuFileText,
  LuGithub,
  LuChevronLeft,
  LuChevronRight,
  LuMoon,
  LuSun,
  LuLogOut,
  LuUser,
} from 'react-icons/lu'
import { useColorMode, useColorModeValue } from './ui/color-mode'
import { useAuth } from '@/app/(auth)/_components/AuthProvider'
import { Branding } from './Branding'

interface SidebarProps {
  className?: string
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)

  // Load saved sidebar state from localStorage on component mount
  useEffect(() => {
    const savedState = localStorage.getItem('sidebarCollapsed')
    if (savedState !== null) {
      setIsCollapsed(JSON.parse(savedState))
    }
  }, [])

  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(isCollapsed))
  }, [isCollapsed])
  const { colorMode, toggleColorMode } = useColorMode()
  const { isAuthenticated, user, login, logout } = useAuth()

  // Theme-aware semantic colors
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const textColor = useColorModeValue('gray.900', 'gray.50')
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400')
  const hoverBg = useColorModeValue('gray.50', 'gray.800')
  const activeBg = useColorModeValue('blue.50', 'blue.900')
  const userProfileBg = useColorModeValue('gray.50', 'gray.800')

  const toggleCollapsed = () => {
    setIsCollapsed(!isCollapsed)
  }

  const sidebarWidth = isCollapsed ? '60px' : '240px'

  const handleAuth = async () => {
    try {
      if (isAuthenticated) {
        await logout()
      } else {
        await login()
      }
    } catch (error) {
      console.error('Auth action failed:', error)
    }
  }

  return (
    <Box
      className={className}
      width={sidebarWidth}
      minHeight="100vh"
      bg={bgColor}
      borderRight="1px solid"
      borderColor={borderColor}
      transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
      position="relative"
      zIndex={10}
      boxShadow={useColorModeValue('sm', 'dark-lg')}
    >
      {/* Header with branding */}
      <Box p={isCollapsed ? 2 : 4} borderBottom="1px solid" borderColor={borderColor}>
        <HStack justify="space-between" align="center" minH="40px">
          <Branding collapsed={isCollapsed} color={textColor} />
        </HStack>
      </Box>

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
              _active={{ bg: activeBg }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="6px"
              fontWeight="500"
              transition="all 0.15s ease"
              width="100%"
            >
              <LuSettings size={16} color={mutedTextColor} />
              {!isCollapsed && (
                <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                  Configuration
                </Text>
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
              _active={{ bg: activeBg }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="6px"
              fontWeight="500"
              transition="all 0.15s ease"
              width="100%"
            >
              <LuFileText size={16} color={mutedTextColor} />
              {!isCollapsed && (
                <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                  Prompts
                </Text>
              )}
            </Button>
          </Link>
        </Box>
      </Stack>

      {/* Bottom section */}
      <Box position="absolute" bottom={0} left={0} right={0} p={2}>
        <Stack gap={1}>
          {/* User Profile Section - Only show when authenticated */}
          {isAuthenticated && user && (
            <Box
              p={isCollapsed ? 2 : 3}
              bg={userProfileBg}
              borderRadius="8px"
              border="1px solid"
              borderColor={borderColor}
              mb={2}
            >
              {isCollapsed ? (
                <HStack justify="center">
                  <Box
                    width="32px"
                    height="32px"
                    borderRadius="full"
                    bg={mutedTextColor}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    backgroundImage={user.avatar_url ? `url(${user.avatar_url})` : undefined}
                    backgroundSize="cover"
                    backgroundPosition="center"
                  >
                    {!user.avatar_url && (
                      <LuUser size={16} color="white" />
                    )}
                  </Box>
                </HStack>
              ) : (
                <VStack gap={2} align="stretch">
                  <HStack gap={3} align="center">
                    <Box
                      width="32px"
                      height="32px"
                      borderRadius="full"
                      bg={mutedTextColor}
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      backgroundImage={user.avatar_url ? `url(${user.avatar_url})` : undefined}
                      backgroundSize="cover"
                      backgroundPosition="center"
                    >
                      {!user.avatar_url && (
                        <LuUser size={16} color="white" />
                      )}
                    </Box>
                    <VStack gap={0} align="flex-start" flex={1} minW={0}>
                      <Text
                        fontSize="13px"
                        fontWeight="600"
                        color={textColor}
                        width="100%"
                        overflow="hidden"
                        textOverflow="ellipsis"
                        whiteSpace="nowrap"
                      >
                        {user.name || user.username}
                      </Text>
                      <Text
                        fontSize="12px"
                        color={mutedTextColor}
                        width="100%"
                        overflow="hidden"
                        textOverflow="ellipsis"
                        whiteSpace="nowrap"
                      >
                        @{user.username}
                      </Text>
                    </VStack>
                  </HStack>
                </VStack>
              )}
            </Box>
          )}

          <Separator borderColor={borderColor} />

          {/* GitHub Login or Logout Button */}
          {isAuthenticated ? (
            <Button
              variant="ghost"
              justifyContent={isCollapsed ? "center" : "flex-start"}
              size="sm"
              width="100%"
              _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
              _active={{ bg: activeBg }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="6px"
              fontWeight="500"
              transition="all 0.15s ease"
              onClick={handleAuth}
            >
              <LuLogOut size={16} color={mutedTextColor} />
              {!isCollapsed && (
                <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                  Logout
                </Text>
              )}
            </Button>
          ) : (
            <Button
              variant="ghost"
              justifyContent={isCollapsed ? "center" : "flex-start"}
              size="sm"
              width="100%"
              _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
              _active={{ bg: activeBg }}
              px={isCollapsed ? 2 : 3}
              py={2}
              height="36px"
              borderRadius="6px"
              fontWeight="500"
              transition="all 0.15s ease"
              onClick={handleAuth}
            >
              <LuGithub size={16} color={mutedTextColor} />
              {!isCollapsed && (
                <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                  Login with GitHub
                </Text>
              )}
            </Button>
          )}

          {/* Theme Toggle */}
          <Button
            variant="ghost"
            justifyContent={isCollapsed ? "center" : "flex-start"}
            size="sm"
            width="100%"
            _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
            _active={{ bg: activeBg }}
            px={isCollapsed ? 2 : 3}
            py={2}
            height="36px"
            borderRadius="6px"
            fontWeight="500"
            transition="all 0.15s ease"
            onClick={toggleColorMode}
          >
            {colorMode === 'dark' ? (
              <LuSun size={16} color={mutedTextColor} />
            ) : (
              <LuMoon size={16} color={mutedTextColor} />
            )}
            {!isCollapsed && (
              <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                {colorMode === 'dark' ? 'Light mode' : 'Dark mode'}
              </Text>
            )}
          </Button>

          {/* Sidebar Toggle Button */}
          <Button
            variant="ghost"
            justifyContent={isCollapsed ? "center" : "flex-start"}
            size="sm"
            width="100%"
            _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
            _active={{ bg: activeBg }}
            px={isCollapsed ? 2 : 3}
            py={2}
            height="36px"
            borderRadius="6px"
            fontWeight="500"
            transition="all 0.15s ease"
            onClick={toggleCollapsed}
          >
            {isCollapsed ? (
              <LuChevronRight size={16} color={mutedTextColor} />
            ) : (
              <LuChevronLeft size={16} color={mutedTextColor} />
            )}
            {!isCollapsed && (
              <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                Collapse sidebar
              </Text>
            )}
          </Button>
        </Stack>
      </Box>
    </Box>
  )
}

export default Sidebar