'use client';

import React from 'react';

import {
  Button,
  HStack,
  VStack,
  Text,
  Box,
  Spinner,
  Image,
  Container,
  Flex,
  Heading,
  SimpleGrid,
  Card,
  Icon,
  Link as ChakraLink,
  ScrollArea
} from "@chakra-ui/react";
import {
  useUser,
  useIsAuthenticated,
  useAuthLoading,
  useAuthActions,
} from '@/stores/authStore';
import { Branding } from "@/components/Branding";
import { ConfigService } from "@/services/config/configService";
import { useConfigStore, useConfig } from '@/stores/configStore';
import { useColorModeValue } from '@/components/ui/color-mode';
import { motion, useScroll, useTransform } from 'framer-motion';
import {
  FaGitAlt,
  FaShieldAlt,
  FaFlask,
  FaBolt,
  FaMagic,
  FaUsers,
  FaChartLine,
  FaCogs,
  FaDatabase,
  FaExchangeAlt,
  FaSlidersH,
  FaGithub,
  FaTwitter,
  FaLinkedin,
  FaEnvelope,
  FaHeart,
  FaCodeBranch,
  FaShareAlt,
  FaVial
} from 'react-icons/fa';
import Link from 'next/link';

// Initialize stores on module load
// This ensures data is loaded from localStorage or API once
const initApp = () => {
  const { initializeConfig } = useConfigStore.getState();
  
  // Only fetch config if it's not already loaded
  // The store will be hydrated from localStorage automatically by zustand persist
  initializeConfig(true, false);
};

// Run initialization once when the module loads
if (typeof window !== 'undefined') {
  initApp();
}

const MotionBox = motion(Box);


const AuthButton = () => {
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();
  const user = useUser();
  const { logout } = useAuthActions();
  const config = useConfig();
  const hostingType = config?.hosting_config?.type;

  if (isLoading) {
    return (
      <HStack gap={2}>
        <Spinner size="sm" />
        <Text fontSize="sm">Loading...</Text>
      </HStack>
    );
  }

  if (isAuthenticated && user) {
    return (
      <HStack gap={3}>
        <Box>
          {user.oauth_avatar_url ? (
            <Image
              src={user.oauth_avatar_url}
              alt={user.oauth_name || ''}
              borderRadius="full"
              boxSize="32px"
            />
          ) : (
            <Box
              bg="gray.200"
              borderRadius="full"
              boxSize="32px"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text fontSize="sm" fontWeight="bold" color="gray.600">
                {user.oauth_name?.[0]?.toUpperCase() || 'U'}
              </Text>
            </Box>
          )}
        </Box>
        <VStack gap={0} alignItems="flex-start">
          <Text fontSize="sm" fontWeight="medium">{user.oauth_name}</Text>
          <Text fontSize="xs" color="gray.500">@{user.oauth_username}</Text>
        </VStack>
        <Button size="sm" variant="outline" onClick={() => logout()}>
          Logout
        </Button>
      </HStack>
    );
  }

  // Don't show login button for individual hosting
  if (ConfigService.shouldSkipAuth(hostingType || undefined)) {
    return null;
  }

  return (
    <Link href="/login" passHref>
      <Button>
        Login
      </Button>
    </Link>
  );
};

// Helper function to render text with highlighted {words}
const renderHighlightedText = (text: string) => {
  const parts = text.split(/(\{[^}]+\})/);
  
  return parts.map((part, index) => {
    if (part.startsWith('{') && part.endsWith('}')) {
      const content = part.slice(1, -1).toLowerCase();
      return (
        <Text
          key={index}
          as="span"
          fontWeight="600"
          color="primary.500"
          _dark={{
            color: "primary.400"
          }}
        >
          {`{${content}}`}
        </Text>
      );
    }
    return <Text as="span" key={index}>{part}</Text>;
  });
};

const HomePage = () => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const featureIconColor = useColorModeValue('primary.600', 'primary.300');
  const footerBg = useColorModeValue('gray.50', 'gray.900');

  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 300], [0, -50]);

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Top Navigation Bar - Outside ScrollArea */}
      <Flex
        as="header"
        justify="space-between"
        align="center"
        px={4}
        py={4}
        position="sticky"
        top={0}
        zIndex={30}
        maxW="6xl"
        width="100%"
        mx="auto"
      >
        <Branding fontSize="3xl" />
        <HStack gap={4}>
          <ChakraLink
            href="https://github.com/inventivepotter/promptrepo"
            target="_blank"
            rel="noopener noreferrer"
            _hover={{ color: "primary.500" }}
            display="flex"
            alignItems="center"
          >
            <Icon as={FaGithub} boxSize={6} />
          </ChakraLink>
          <AuthButton />
        </HStack>
      </Flex>

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
              {/* Main content */}
              <Box position="relative" zIndex={1}>
                <Container maxW="6xl" py={16}>
                  <VStack gap={24} alignItems="center">
              
              {/* Hero Section - This stays immediately visible */}
              <MotionBox
                position="relative"
                maxW="3xl"
                textAlign="center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <Box
                  position="absolute"
                  top="50%"
                  left="-60px"
                  transform="translateY(-50%)"
                  fontSize="200px"
                  color="fg.muted"
                  zIndex={0}
                  opacity={0.3}
                  pointerEvents="none"
                  fontWeight={100}
                  lineHeight="1"
                  fontFamily="'Palatino Linotype', 'Book Antiqua', Palatino, serif"
                >
                  {"{"}
                </Box>
                <Box
                  position="absolute"
                  top="50%"
                  right="-60px"
                  transform="translateY(-50%)"
                  fontSize="200px"
                  color="fg.muted"
                  zIndex={0}
                  opacity={0.3}
                  pointerEvents="none"
                  fontWeight={100}
                  lineHeight="1"
                  fontFamily="'Palatino Linotype', 'Book Antiqua', Palatino, serif"
                >
                  {"}"}
                </Box>
                <VStack gap={6} position="relative" zIndex={1}>
                  <Text
                    fontSize={{ base: "4xl", md: "5xl", lg: "6xl" }}
                    fontWeight="extrabold"
                    color={{ _light: "primary.600", _dark: "primary.300" }}
                    lineHeight="1.1"
                  >
                    Craft Better Prompts
                  </Text>
                  <Text
                    fontSize={{ base: "lg", md: "xl" }}
                    color="fg.subtle"
                    opacity={0.8}
                    maxW="2xl"
                    lineHeight="1.6"
                  >
                    Evaluate, test, and optimize your prompts to make informed
                    decisions and build AI agents that work better for you.
                  </Text>
                </VStack>
              </MotionBox>
              
              {/* Welcome Section */}
              <MotionBox
                position="relative"
                w="full"
                style={{ y: heroY }}
              >
                <VStack textAlign="center">
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
                  >
                    <HStack gapX={6} flexWrap="wrap" justify="center">
                      <Link href="/prompts" passHref>
                        <Button
                          size="lg"
                          colorScheme="primary"
                          px={8}
                          py={6}
                          fontSize="md"
                          fontWeight="semibold"
                        >
                          Get Started
                        </Button>
                      </Link>
                      <Button
                        size="lg"
                        variant="outline"
                        px={8}
                        py={6}
                        fontSize="md"
                        fontWeight="semibold"
                      >
                        View Demo
                      </Button>
                    </HStack>
                  </MotionBox>
                </VStack>
              </MotionBox>

              {/* Feature Highlights Section */}
              <Box w="full">
                <VStack gap={0}>
                  {/* Fading Divider - Top */}
                  <Box
                    w="full"
                    maxW="4xl"
                    mx="auto"
                    h="1px"
                    style={{
                      background: `linear-gradient(to right, transparent, ${useColorModeValue('#CBD5E0', '#4A5568')}, transparent)`
                    }}
                  />

                  {/* Prompt Optimizer - Text Left, Image Right */}
                  <MotionBox
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.2 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    w="full"
                    py={{ base: 10, md: 14 }}
                  >
                    <Flex
                      direction={{ base: "column", md: "row" }}
                      align="center"
                      gap={{ base: 6, md: 10 }}
                      maxW="5xl"
                      mx="auto"
                      px={{ base: 4, md: 8 }}
                    >
                      <VStack align={{ base: "center", md: "start" }} gap={4} flex={1} textAlign={{ base: "center", md: "left" }}>
                        <HStack gap={2}>
                          <Icon as={FaMagic} boxSize={4} color="primary.500" />
                          <Text fontSize="xs" fontWeight="semibold" textTransform="uppercase" letterSpacing="wider" color="primary.500">
                            AI-Powered
                          </Text>
                        </HStack>
                        <Heading size={{ base: "lg", md: "xl" }} lineHeight="1.2">
                          Optimize Your Prompts with AI
                        </Heading>
                        <Text color="fg.subtle" fontSize="md" lineHeight="1.7">
                          Use AI to analyze and enhance your prompts. Get intelligent suggestions for clarity, effectiveness, and edge case handling. Our optimizer identifies ambiguities, suggests improvements, and helps you craft production-ready prompts that deliver consistent results.
                        </Text>
                        <Link href="/prompts" passHref>
                          <Button size="md" colorScheme="primary">
                            Try Prompt Optimizer
                          </Button>
                        </Link>
                      </VStack>
                      <Box
                        flex={1}
                        w="full"
                        maxW={{ base: "full", md: "200px" }}
                        borderRadius="xl"
                        position="relative"
                        overflow="hidden"
                      >
                        <Image
                          src="/promptoptimizer.png"
                          alt="Prompt Optimizer"
                          objectFit="contain"
                          w="full"
                          borderRadius="xl"
                        />
                        <Box
                          position="absolute"
                          top={3}
                          right={3}
                          bg="primary.500"
                          color="white"
                          px={2}
                          py={0.5}
                          borderRadius="full"
                          fontSize="2xs"
                          fontWeight="bold"
                        >
                          NEW
                        </Box>
                      </Box>
                    </Flex>
                  </MotionBox>

                  {/* Fading Divider */}
                  <Box
                    w="full"
                    maxW="4xl"
                    mx="auto"
                    h="1px"
                    style={{
                      background: `linear-gradient(to right, transparent, ${useColorModeValue('#CBD5E0', '#4A5568')}, transparent)`
                    }}
                  />

                  {/* Share Conversations - Image Left, Text Right */}
                  <MotionBox
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.2 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    w="full"
                    py={{ base: 10, md: 14 }}
                  >
                    <Flex
                      direction={{ base: "column-reverse", md: "row" }}
                      align="center"
                      gap={{ base: 6, md: 10 }}
                      maxW="5xl"
                      mx="auto"
                      px={{ base: 4, md: 8 }}
                    >
                      <Box
                        flex={1}
                        w="full"
                        maxW={{ base: "full", md: "200px" }}
                        borderRadius="xl"
                        position="relative"
                        overflow="hidden"
                      >
                        <Image
                          src="/sharechat.png"
                          alt="Share Conversations"
                          objectFit="contain"
                          w="full"
                          borderRadius="xl"
                        />
                      </Box>
                      <VStack align={{ base: "center", md: "start" }} gap={4} flex={1} textAlign={{ base: "center", md: "left" }}>
                        <HStack gap={2}>
                          <Icon as={FaShareAlt} boxSize={4} color="primary.500" />
                          <Text fontSize="xs" fontWeight="semibold" textTransform="uppercase" letterSpacing="wider" color="primary.500">
                            Collaboration
                          </Text>
                        </HStack>
                        <Heading size={{ base: "lg", md: "xl" }} lineHeight="1.2">
                          Share Conversations with Your Team
                        </Heading>
                        <Text color="fg.subtle" fontSize="md" lineHeight="1.7">
                          Share chat sessions with your team via a simple link. Collaborate on prompt testing, gather feedback from stakeholders, and build shared knowledge around what works. Perfect for team reviews, client demos, and documenting successful prompt strategies.
                        </Text>
                        <Link href="/prompts" passHref>
                          <Button size="md" colorScheme="primary">
                            Start Sharing
                          </Button>
                        </Link>
                      </VStack>
                    </Flex>
                  </MotionBox>

                  {/* Fading Divider */}
                  <Box
                    w="full"
                    maxW="4xl"
                    mx="auto"
                    h="1px"
                    style={{
                      background: `linear-gradient(to right, transparent, ${useColorModeValue('#CBD5E0', '#4A5568')}, transparent)`
                    }}
                  />

                  {/* Test System Prompts - Text Left, Image Right */}
                  <MotionBox
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.2 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    w="full"
                    py={{ base: 10, md: 14 }}
                  >
                    <Flex
                      direction={{ base: "column", md: "row" }}
                      align="center"
                      gap={{ base: 6, md: 10 }}
                      maxW="5xl"
                      mx="auto"
                      px={{ base: 4, md: 8 }}
                    >
                      <VStack align={{ base: "center", md: "start" }} gap={4} flex={1} textAlign={{ base: "center", md: "left" }}>
                        <HStack gap={2}>
                          <Icon as={FaVial} boxSize={4} color="primary.500" />
                          <Text fontSize="xs" fontWeight="semibold" textTransform="uppercase" letterSpacing="wider" color="primary.500">
                            Quality Assurance
                          </Text>
                        </HStack>
                        <Heading size={{ base: "lg", md: "xl" }} lineHeight="1.2">
                          Test Prompts Like You Test Code
                        </Heading>
                        <Text color="fg.subtle" fontSize="md" lineHeight="1.7">
                          Write test cases for your system prompts just like unit tests for code. Define expected behaviors, catch regressions before they hit production, and ensure consistent AI responses across updates. Build confidence in your prompts with automated validation.
                        </Text>
                        <Link href="/evals" passHref>
                          <Button size="md" colorScheme="primary">
                            Explore Evaluations
                          </Button>
                        </Link>
                      </VStack>
                      <Box
                        flex={1}
                        w="full"
                        maxW={{ base: "full", md: "200px" }}
                        borderRadius="xl"
                        position="relative"
                        overflow="hidden"
                      >
                        <Image
                          src="/tests.png"
                          alt="Test System Prompts"
                          objectFit="contain"
                          w="full"
                          borderRadius="xl"
                        />
                      </Box>
                    </Flex>
                  </MotionBox>

                  {/* Fading Divider - Bottom */}
                  <Box
                    w="full"
                    maxW="4xl"
                    mx="auto"
                    h="1px"
                    style={{
                      background: `linear-gradient(to right, transparent, ${useColorModeValue('#CBD5E0', '#4A5568')}, transparent)`
                    }}
                  />
                </VStack>
              </Box>

              {/* Yet Another Prompt Registry Section */}
              <Box w="full" px={{ base: 4, md: 0 }}>
                <VStack gap={16}>
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.3 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    textAlign="center"
                  >
                    <Text
                      fontSize="sm"
                      fontWeight="semibold"
                      textTransform="uppercase"
                      letterSpacing="wider"
                      color="primary.500"
                      mb={2}
                    >
                      The Difference
                    </Text>
                    <Heading
                      as="h2"
                      fontSize={{ base: "3xl", md: "4xl", lg: "5xl" }}
                      fontWeight="600"
                      mb={4}
                      lineHeight="1.2"
                    >
                      Not Just Another{" "}
                      <Text as="span" color="primary.500">
                        Registry
                      </Text>
                    </Heading>
                    <Text
                      fontSize={{ base: "lg", md: "xl" }}
                      color="fg.subtle"
                      maxW="3xl"
                      mx="auto"
                    >
                      Built on principles that matter for real-world prompt engineering
                    </Text>
                  </MotionBox>

                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={8} w="full" maxW="6xl" mx="auto">
                    {/* Source Control First Card */}
                    <MotionBox
                      initial={{ opacity: 0, x: -30 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true, amount: 0.2 }}
                      transition={{ duration: 0.7, delay: 0.1, ease: "easeOut" }}
                      h="full"
                    >
                      <Card.Root
                        h="full"
                        bg={useColorModeValue('white', 'gray.800')}
                        borderWidth="1px"
                        borderColor={borderColor}
                        overflow="hidden"
                        position="relative"
                        transition="all 0.3s"
                        _hover={{
                          transform: 'translateY(-4px)',
                          shadow: 'xl',
                          borderColor: 'primary.400'
                        }}
                      >
                        <Box
                          position="absolute"
                          top="-20px"
                          right="-20px"
                          boxSize="120px"
                          bg="primary.500"
                          borderRadius="full"
                          opacity={0.05}
                        />
                        <Card.Body p={{ base: 6, md: 8 }}>
                          <VStack align="start" gap={5}>
                            <Box>
                              <Box
                                bg={useColorModeValue('primary.50', 'primary.900')}
                                p={3}
                                borderRadius="xl"
                                display="inline-flex"
                                mb={4}
                              >
                                <Icon
                                  as={FaGitAlt}
                                  boxSize={7}
                                  color={useColorModeValue('primary.600', 'primary.300')}
                                />
                              </Box>
                              <Heading size="lg" mb={2}>
                                Own Your Code
                              </Heading>
                              <Text
                                fontSize="sm"
                                color="primary.500"
                                fontWeight="semibold"
                                textTransform="uppercase"
                                letterSpacing="wider"
                              >
                                Git-Native Architecture
                              </Text>
                            </Box>
                            
                            <VStack align="start" gap={3}>
                              <Text color="fg.subtle" lineHeight="tall" fontSize="md">
                                Your prompts live where they belong - in <Text as="span" fontWeight="semibold">your repository</Text>.
                                No external databases, no vendor lock-in.
                              </Text>
                              <HStack gap={2} flexWrap="wrap">
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('green.50', 'green.900')}
                                  color={useColorModeValue('green.700', 'green.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Full version control
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('blue.50', 'blue.900')}
                                  color={useColorModeValue('blue.700', 'blue.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Branch & merge
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('purple.50', 'purple.900')}
                                  color={useColorModeValue('purple.700', 'purple.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Code reviews
                                </Text>
                              </HStack>
                            </VStack>
                          </VStack>
                        </Card.Body>
                      </Card.Root>
                    </MotionBox>

                    {/* Prompts + Models Together Card */}
                    <MotionBox
                      initial={{ opacity: 0, x: 30 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true, amount: 0.2 }}
                      transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
                      h="full"
                    >
                      <Card.Root
                        h="full"
                        bg={useColorModeValue('white', 'gray.800')}
                        borderWidth="1px"
                        borderColor={borderColor}
                        overflow="hidden"
                        position="relative"
                        transition="all 0.3s"
                        _hover={{
                          transform: 'translateY(-4px)',
                          shadow: 'xl',
                          borderColor: 'primary.400'
                        }}
                      >
                        <Box
                          position="absolute"
                          bottom="-30px"
                          left="-30px"
                          boxSize="140px"
                          bg="primary.500"
                          borderRadius="full"
                          opacity={0.05}
                        />
                        <Card.Body p={{ base: 6, md: 8 }}>
                          <VStack align="start" gap={5}>
                            <Box>
                              <Box
                                bg={useColorModeValue('primary.50', 'primary.900')}
                                p={3}
                                borderRadius="xl"
                                display="inline-flex"
                                mb={4}
                              >
                                <Icon
                                  as={FaDatabase}
                                  boxSize={7}
                                  color={useColorModeValue('primary.600', 'primary.300')}
                                />
                              </Box>
                              <Heading size="lg" mb={2}>
                                Complete Context
                              </Heading>
                              <Text
                                fontSize="sm"
                                color="primary.500"
                                fontWeight="semibold"
                                textTransform="uppercase"
                                letterSpacing="wider"
                              >
                                Unified Configuration
                              </Text>
                            </Box>
                            
                            <VStack align="start" gap={3}>
                              <Text color="fg.subtle" lineHeight="tall" fontSize="md">
                                Prompts paired with their <Text as="span" fontWeight="semibold">exact models & parameters</Text>.
                                Reproduce results perfectly, every time.
                              </Text>
                              <HStack gap={2} flexWrap="wrap">
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('orange.50', 'orange.900')}
                                  color={useColorModeValue('orange.700', 'orange.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Model settings
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('teal.50', 'teal.900')}
                                  color={useColorModeValue('teal.700', 'teal.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Temperature
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('pink.50', 'pink.900')}
                                  color={useColorModeValue('pink.700', 'pink.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ All parameters
                                </Text>
                              </HStack>
                            </VStack>
                          </VStack>
                        </Card.Body>
                      </Card.Root>
                    </MotionBox>

                    {/* Open Source Card */}
                    <MotionBox
                      initial={{ opacity: 0, x: 30 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true, amount: 0.2 }}
                      transition={{ duration: 0.7, delay: 0.3, ease: "easeOut" }}
                      h="full"
                    >
                      <Card.Root
                        h="full"
                        bg={useColorModeValue('white', 'gray.800')}
                        borderWidth="1px"
                        borderColor={borderColor}
                        overflow="hidden"
                        position="relative"
                        transition="all 0.3s"
                        _hover={{
                          transform: 'translateY(-4px)',
                          shadow: 'xl',
                          borderColor: 'primary.400'
                        }}
                      >
                        <Box
                          position="absolute"
                          top="-20px"
                          right="-20px"
                          boxSize="120px"
                          bg="primary.500"
                          borderRadius="full"
                          opacity={0.05}
                        />
                        <Card.Body p={{ base: 6, md: 8 }}>
                          <VStack align="start" gap={5}>
                            <Box>
                              <Box
                                bg={useColorModeValue('primary.50', 'primary.900')}
                                p={3}
                                borderRadius="xl"
                                display="inline-flex"
                                mb={4}
                              >
                                <Icon
                                  as={FaCodeBranch}
                                  boxSize={7}
                                  color={useColorModeValue('primary.600', 'primary.300')}
                                />
                              </Box>
                              <Heading size="lg" mb={2}>
                                100% Open Source
                              </Heading>
                              <Text
                                fontSize="sm"
                                color="primary.500"
                                fontWeight="semibold"
                                textTransform="uppercase"
                                letterSpacing="wider"
                              >
                                Community-Driven
                              </Text>
                            </Box>

                            <VStack align="start" gap={3}>
                              <Text color="fg.subtle" lineHeight="tall" fontSize="md">
                                Built in the open, for the community. <Text as="span" fontWeight="semibold">MIT licensed</Text>,
                                fork it, improve it, make it yours.
                              </Text>
                              <HStack gap={2} flexWrap="wrap">
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('cyan.50', 'cyan.900')}
                                  color={useColorModeValue('cyan.700', 'cyan.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ MIT License
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('green.50', 'green.900')}
                                  color={useColorModeValue('green.700', 'green.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ Self-hostable
                                </Text>
                                <Text
                                  as="span"
                                  px={2}
                                  py={1}
                                  bg={useColorModeValue('purple.50', 'purple.900')}
                                  color={useColorModeValue('purple.700', 'purple.200')}
                                  borderRadius="md"
                                  fontSize="xs"
                                  fontWeight="semibold"
                                >
                                  ✓ No telemetry
                                </Text>
                              </HStack>
                            </VStack>
                          </VStack>
                        </Card.Body>
                      </Card.Root>
                    </MotionBox>
                  </SimpleGrid>

                  {/* Bottom highlight message */}
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.5 }}
                    transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
                    w="full"
                    maxW="4xl"
                    mx="auto"
                  >
                    <Box
                      p={6}
                      bg={useColorModeValue('primary.50', 'gray.900/30')}
                      borderRadius="xl"
                      borderWidth="1px"
                      borderColor={useColorModeValue('primary.100', 'gray.800/50')}
                      textAlign="center"
                      position="relative"
                      overflow="hidden"
                      backdropFilter="blur(10px)"
                      _dark={{
                        bg: 'blackAlpha.200',
                        borderColor: 'whiteAlpha.100'
                      }}
                    >
                      <Box
                        position="absolute"
                        top="50%"
                        left="50%"
                        transform="translate(-50%, -50%)"
                        boxSize="200px"
                        bg={useColorModeValue('primary.500', 'primary.400')}
                        borderRadius="full"
                        opacity={useColorModeValue(0.1, 0.08)}
                        filter="blur(60px)"
                      />
                      <VStack gap={2} position="relative">
                        <Icon
                          as={FaBolt}
                          boxSize={5}
                          color="primary.500"
                        />
                        <Text
                          fontSize={{ base: "md", md: "lg" }}
                          fontWeight="semibold"
                          color={useColorModeValue('primary.700', 'primary.300')}
                        >
                          Simple premise. Powerful results.
                        </Text>
                        <Text
                          fontSize="sm"
                          color={useColorModeValue('gray.600', 'gray.400')}
                        >
                          Your prompts, your control, your workflow - supercharged.
                        </Text>
                      </VStack>
                    </Box>
                  </MotionBox>
                </VStack>
              </Box>

              {/* Features Section */}
              <Box
                w="full"
                py={16}
                px={{ base: 4, md: 0 }}
              >
                <VStack gap={12}>
                  <MotionBox
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.3 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    textAlign="center"
                    maxW="3xl"
                    mx="auto"
                  >
                    <Text
                      fontSize="sm"
                      fontWeight="semibold"
                      textTransform="uppercase"
                      letterSpacing="wider"
                      color="primary.500"
                      mb={3}
                    >
                      Complete Platform
                    </Text>
                    <Heading
                      as="h2"
                      fontSize={{ base: "3xl", md: "4xl", lg: "5xl" }}
                      fontWeight="600"
                      mb={4}
                      lineHeight="1.2"
                    >
                      Features That{" "}
                      <Text as="span" color="primary.500">
                        Actually Matter
                      </Text>
                    </Heading>
                    <Text
                      fontSize={{ base: "lg", md: "xl" }}
                      color="fg.subtle"
                      lineHeight="1.6"
                    >
                      Everything you need for production-ready prompt management,
                      nothing you don&apos;t
                    </Text>
                  </MotionBox>

                  <Box position="relative" w="full">
                    {/* Vertical dividers - solid color */}
                    <Box
                      position="absolute"
                      left="33.33%"
                      top="0"
                      bottom="0"
                      width="1px"
                      bg="gray.300"
                      _dark={{
                        bg: "gray.600"
                      }}
                      display={{ base: "none", lg: "block" }}
                      zIndex={1}
                      pointerEvents="none"
                    />
                    <Box
                      position="absolute"
                      left="66.66%"
                      top="0"
                      bottom="0"
                      width="1px"
                      bg="gray.300"
                      _dark={{
                        bg: "gray.600"
                      }}
                      display={{ base: "none", lg: "block" }}
                      zIndex={1}
                      pointerEvents="none"
                    />
                    
                    {/* Horizontal dividers - solid color */}
                    <Box
                      position="absolute"
                      left="0"
                      right="0"
                      top="33.33%"
                      height="1px"
                      bg="gray.300"
                      _dark={{
                        bg: "gray.600"
                      }}
                      display={{ base: "none", lg: "block" }}
                      zIndex={1}
                      pointerEvents="none"
                    />
                    <Box
                      position="absolute"
                      left="0"
                      right="0"
                      top="66.66%"
                      height="1px"
                      bg="gray.300"
                      _dark={{
                        bg: "gray.600"
                      }}
                      display={{ base: "none", lg: "block" }}
                      zIndex={1}
                      pointerEvents="none"
                    />

                    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={0} position="relative">
                      {[
                        {
                          icon: FaShieldAlt,
                          title: "Take Control of Your Prompts",
                          description: "Keep your prompts in {your own} source control. {No vendor lock-in}, no data silos. Your prompts, {your rules}."
                        },
                        {
                          icon: FaFlask,
                          title: "Test & Evaluate Prompts",
                          description: "Test prompts for different scenarios and ensure you won't introduce {regressions} when updating prompts."
                        },
                        {
                          icon: FaBolt,
                          title: 'No more "Works in my machine!"',
                          description: "Marry prompts with specific models and parameters for {consistent}, {predictable} results in production environments."
                        },
                        {
                          icon: FaMagic,
                          title: "AI-Enhanced Prompts",
                          description: "Leverage AI to {enhance} and {optimize} your prompts, making them more {effective} and {efficient}."
                        },
                        {
                          icon: FaUsers,
                          title: "Collaborative Chat Experience",
                          description: "Integrated chat for manual evaluations with {shareable} conversations for {team collaboration}."
                        },
                        {
                          icon: FaChartLine,
                          title: "Cost & Performance Insights",
                          description: "Track input/output {tokens} and approximate pricing to make {informed decisions} about quality vs. cost - {best bang} for the buck."
                        },
                        {
                          icon: FaExchangeAlt,
                          title: "Easy Migration",
                          description: "{Effortlessly} migrate your existing codebase using prompts scattered throughout to an {organized} prompt management repository."
                        },
                        {
                          icon: FaSlidersH,
                          title: "Parameters in Prompts",
                          description: "Full support for {dynamic parameters} in prompts for both Chat interactions and {Evaluation workflows}."
                        },
                        {
                          icon: FaCogs,
                          title: "CI/CD Ready",
                          description: "{Version-controlled} prompts integrate with CI/CD. Share across repos as {modules}. {Zero} additional infrastructure required."
                        }
                      ].map((feature, index) => (
                        <Box
                          key={index}
                          p={8}
                          position="relative"
                          overflow="hidden"
                          transition="transform 0.3s ease, z-index 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease"
                          _hover={{
                            transform: "scale(1.08)",
                            zIndex: 10,
                            boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
                            bg: "white",
                            _dark: {
                              bg: "gray.800",
                              boxShadow: "0 10px 40px rgba(0,0,0,0.5)"
                            }
                          }}
                          _after={{
                            content: '""',
                            position: "absolute",
                            bottom: 0,
                            left: "20px",
                            right: "20px",
                            height: "1px",
                            bg: "gray.300",
                            _dark: {
                              bg: "gray.600"
                            },
                            display: { base: index < 8 ? "block" : "none", lg: "none" }
                          }}
                        >
                          {/* Icon as background - left side, vertically centered */}
                          <Box
                            position="absolute"
                            left="-30px"
                            top="50%"
                            transform="translateY(-50%)"
                            opacity={0.05}
                            _dark={{
                              opacity: 0.08
                            }}
                            pointerEvents="none"
                          >
                            <Icon
                              as={feature.icon}
                              boxSize="140px"
                              color={featureIconColor}
                            />
                          </Box>
                          
                          <VStack align="start" gap={4} position="relative" zIndex={1}>
                            <Heading size="md">{feature.title}</Heading>
                            <Text color="fg.subtle" lineHeight="tall">
                              {renderHighlightedText(feature.description)}
                            </Text>
                          </VStack>
                        </Box>
                      ))}
                    </SimpleGrid>
                  </Box>
                </VStack>
              </Box>

              {/* Call to Action Section */}
              <Box w="full" py={16} textAlign="center">
                <MotionBox
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                >
                  <VStack gap={6}>
                    <Heading
                      as="h3"
                      fontSize={{ base: "2xl", md: "3xl", lg: "4xl" }}
                    >
                      Ready to Take Control of Your Prompts?
                    </Heading>
                    <Text fontSize="lg" color="fg.subtle" maxW="2xl" mx="auto">
                      Start managing your prompts the right way - in your source control,
                      with powerful testing and optimization.
                    </Text>
                    <Link href="/prompts" passHref>
                      <Button
                        size="lg"
                        colorScheme="primary"
                        px={8}
                        py={6}
                        fontSize="md"
                        fontWeight="semibold"
                      >
                        Start Now
                      </Button>
                    </Link>
                  </VStack>
                </MotionBox>
              </Box>
            </VStack>
          </Container>

          {/* Footer */}
          <Box
            as="footer"
            w="full"
            bg={footerBg}
            borderTopWidth="1px"
            borderTopColor={borderColor}
            mt={20}
          >
            <Container maxW="6xl" py={12}>
              <VStack gap={8}>
                {/* Top Footer Content */}
                <SimpleGrid
                  columns={{ base: 1, md: 3 }}
                  gap={8}
                  w="full"
                  textAlign={{ base: "center", md: "left" }}
                >
                  {/* Brand Column */}
                  <VStack align={{ base: "center", md: "start" }} gap={4}>
                    <Branding fontSize="2xl" />
                    <Text fontSize="sm" color="fg.subtle" maxW="250px">
                      Open-source prompt management that puts you in control.
                    </Text>
                    <HStack gap={3}>
                      <ChakraLink
                        href="https://github.com/promptrepo"
                        target="_blank"
                        rel="noopener noreferrer"
                        _hover={{ color: "primary.500" }}
                      >
                        <Icon as={FaGithub} boxSize={5} />
                      </ChakraLink>
                      <ChakraLink
                        href="https://twitter.com/promptrepo"
                        target="_blank"
                        rel="noopener noreferrer"
                        _hover={{ color: "primary.500" }}
                      >
                        <Icon as={FaTwitter} boxSize={5} />
                      </ChakraLink>
                      <ChakraLink
                        href="https://linkedin.com/company/promptrepo"
                        target="_blank"
                        rel="noopener noreferrer"
                        _hover={{ color: "primary.500" }}
                      >
                        <Icon as={FaLinkedin} boxSize={5} />
                      </ChakraLink>
                    </HStack>
                  </VStack>

                  {/* Quick Links */}
                  <VStack align={{ base: "center", md: "start" }} gap={3}>
                    <Text fontWeight="semibold" fontSize="sm" textTransform="uppercase" letterSpacing="wider">
                      Resources
                    </Text>
                    <VStack align={{ base: "center", md: "start" }} gap={2}>
                      <ChakraLink
                        href="/docs"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        Documentation
                      </ChakraLink>
                      <ChakraLink
                        href="/prompts"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        Browse Prompts
                      </ChakraLink>
                      <ChakraLink
                        href="https://github.com/promptrepo/promptrepo"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        GitHub Repository
                      </ChakraLink>
                      <ChakraLink
                        href="/api"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        API Reference
                      </ChakraLink>
                    </VStack>
                  </VStack>

                  {/* Contact */}
                  <VStack align={{ base: "center", md: "start" }} gap={3}>
                    <Text fontWeight="semibold" fontSize="sm" textTransform="uppercase" letterSpacing="wider">
                      Connect
                    </Text>
                    <VStack align={{ base: "center", md: "start" }} gap={2}>
                      <HStack gap={2}>
                        <Icon as={FaEnvelope} boxSize={4} color="fg.subtle" />
                        <ChakraLink
                          href="mailto:hello@promptrepo.dev"
                          fontSize="sm"
                          color="fg.subtle"
                          _hover={{ color: "primary.500" }}
                        >
                          hello@promptrepo.dev
                        </ChakraLink>
                      </HStack>
                      <ChakraLink
                        href="/support"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        Support Center
                      </ChakraLink>
                      <ChakraLink
                        href="/community"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        Community Forum
                      </ChakraLink>
                      <ChakraLink
                        href="/changelog"
                        fontSize="sm"
                        color="fg.subtle"
                        _hover={{ color: "primary.500" }}
                      >
                        Changelog
                      </ChakraLink>
                    </VStack>
                  </VStack>
                </SimpleGrid>

                <Box
                  w="full"
                  h="1px"
                  bg={borderColor}
                  my={4}
                />

                {/* Bottom Footer */}
                <Box w="full" textAlign="center">
                  <VStack gap={2}>
                    <HStack gap={1} fontSize="sm" color="fg.subtle">
                      <Text>Made with</Text>
                      <Icon as={FaHeart} boxSize={3} color="red.500" />
                      <Text>in open source</Text>
                    </HStack>
                    <HStack gap={4} fontSize="xs" color="fg.muted" flexWrap="wrap" justify="center">
                      <Text>© {new Date().getFullYear()} Prompt Repo</Text>
                      <Text>•</Text>
                      <ChakraLink href="/privacy" _hover={{ color: "primary.500" }}>
                        Privacy Policy
                      </ChakraLink>
                      <Text>•</Text>
                      <ChakraLink href="/terms" _hover={{ color: "primary.500" }}>
                        Terms of Service
                      </ChakraLink>
                      <Text>•</Text>
                      <ChakraLink
                        href="https://github.com/promptrepo/promptrepo/blob/main/LICENSE"
                        target="_blank"
                        rel="noopener noreferrer"
                        _hover={{ color: "primary.500" }}
                      >
                        MIT License
                      </ChakraLink>
                    </HStack>
                  </VStack>
                </Box>
              </VStack>
                  </Container>
                </Box>
              </Box>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>
    </Box>
  );
}

export default function Home() {
  return (
    <HomePage />
  );
}
