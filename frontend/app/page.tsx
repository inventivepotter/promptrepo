'use client';

import { Button, HStack, VStack, Text, Box, Spinner, Image, Container, Flex } from "@chakra-ui/react";
import {
  useUser,
  useIsAuthenticated,
  useAuthLoading,
  useAuthActions,
} from '@/stores/authStore';
import { PromptQuotes } from "@/components/home/PromptQuotes";
import { Branding } from "@/components/Branding";
import { ConfigService } from "@/services/config/configService";
import { useConfigStore, useConfig } from '@/stores/configStore';

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

const AuthButton = () => {
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();
  const user = useUser();
  const { login, logout } = useAuthActions();
  const config = useConfig();
  const hostingType = config?.hosting_config?.type;

  if (isLoading) {
    return (
      <HStack gap={2}>
        <Spinner size="sm" />
        <Text fontSize="sm">Checking...</Text>
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
        <Button size="sm" colorScheme="red" variant="outline" onClick={() => logout()}>
          Logout
        </Button>
      </HStack>
    );
  }

  // Don't show GitHub login for individual hosting
  if (ConfigService.shouldSkipAuth(hostingType || undefined)) {
    return null;
  }

  return (
    <Button colorScheme="blue" onClick={() => login()}>
      Login with GitHub
    </Button>
  );
};

const HomePage = () => {
  return (
    <>
      {/* Top Navigation Bar - Sticky */}
      <Flex
        as="header"
        justify="space-between"
        align="center"
        p={4}
        position="sticky"
        top={0}
        zIndex={10}
        maxW="6xl"
        mx="auto"
        py={8}
      >
        <Branding fontSize="3xl" />
        <AuthButton />
      </Flex>

      <Box position="relative">
        {/* Main content */}
        <Box position="relative" zIndex={1}>
        <Container maxW="4xl" py={16}>
          <VStack gap={16} alignItems="center" textAlign="center">
            {/* Hero Section */}
            <Box position="relative" maxW="3xl">
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
                  fontWeight="bold"
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
            </Box>

            {/* Quote Section */}
            <Box w="full" maxW="4xl">
              <PromptQuotes />
            </Box>

            {/* Action Buttons */}
            <HStack gap={4} flexWrap="wrap" justify="center" mt={8}>
              <Button
                size="lg"
                variant="solid"
                px={8}
                py={6}
                fontSize="md"
                fontWeight="semibold"
              >
                Explore Prompts
              </Button>
              <Button
                size="lg"
                variant="outline"
                px={8}
                py={6}
                fontSize="md"
                fontWeight="semibold"
              >
                Learn More
              </Button>
            </HStack>
          </VStack>
        </Container>
        </Box>
      </Box>
    </>
  );
}

export default function Home() {
  return (
    <HomePage />
  );
}
