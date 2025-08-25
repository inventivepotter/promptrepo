"use client"

import React, { useState } from 'react'
import {
  Box,
  HStack,
  Text,
  Button,
  Separator,
  Stack,
} from '@chakra-ui/react'
import {
  LuSettings,
  LuFileText,
  LuGithub,
  LuChevronLeft,
  LuChevronRight,
  LuMoon,
  LuSun,
} from 'react-icons/lu'
import { useColorMode, useColorModeValue } from './ui/color-mode'

interface SidebarProps {
  className?: string
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { colorMode, toggleColorMode } = useColorMode()

  // Theme-aware semantic colors
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const textColor = useColorModeValue('gray.900', 'gray.50')
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400')
  const hoverBg = useColorModeValue('gray.50', 'gray.800')
  const activeBg = useColorModeValue('blue.50', 'blue.900')

  const toggleCollapsed = () => {
    setIsCollapsed(!isCollapsed)
  }

  const sidebarWidth = isCollapsed ? '60px' : '240px'

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
      boxShadow={useColorModeValue('sm', 'dark-lg')}
    >
      {/* Header with branding */}
      <Box p={isCollapsed ? 2 : 4} borderBottom="1px solid" borderColor={borderColor}>
        <HStack justify="space-between" align="center" minH="40px">
          {isCollapsed ? (
            <Text
              fontSize="lg"
              color={textColor}
              fontWeight="300"
              letterSpacing="tight"
            >
              {'{'}P<Text as="span" fontWeight="700">R</Text>{'}'}
            </Text>
          ) : (
            <Text
              fontSize="xl"
              color={textColor}
              fontWeight="300"
              letterSpacing="tight"
            >
              {'{'}Prompt{'}'}<Text as="span" fontWeight="700"> Repo</Text>
            </Text>
          )}
        </HStack>
      </Box>

      {/* Navigation Menu */}
      <Stack gap={1} p={2} pt={3}>
        {/* Setup */}
        <Box as="span" width="100%">
          <a href="/setup" style={{ textDecoration: 'none' }}>
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
                  Setup
                </Text>
              )}
            </Button>
          </a>
        </Box>

        {/* Prompts */}
        <Box as="span" width="100%">
          <a href="/prompts" style={{ textDecoration: 'none' }}>
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
          </a>
        </Box>
      </Stack>

      {/* Bottom section */}
      <Box position="absolute" bottom={0} left={0} right={0} p={2}>
        <Stack gap={1}>
          <Separator borderColor={borderColor} />
          
          {/* GitHub Login */}
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
          >
            <LuGithub size={16} color={mutedTextColor} />
            {!isCollapsed && (
              <Text ml={3} fontSize="14px" color={textColor} fontWeight="500">
                Login with GitHub
              </Text>
            )}
          </Button>

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