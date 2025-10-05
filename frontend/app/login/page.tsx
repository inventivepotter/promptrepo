'use client';

import { Box, Grid, GridItem, VStack, Text, Card, Heading, Skeleton, EmptyState } from '@chakra-ui/react';
import { List } from '@chakra-ui/react';
import { HiColorSwatch } from 'react-icons/hi';
import { Branding } from '@/components/Branding';
import { PromptQuotes } from '@/components/home/PromptQuotes';
import { LoginPageButton } from '@/components/login/LoginPageButton';
import { useConfigStore } from '@/stores/configStore';
import { ConfigService } from '@/services/config/configService';
import type { components } from '@/types/generated/api';
import { useEffect, useState } from 'react';

type OAuthProvider = components['schemas']['OAuthProvider'];

export default function LoginPage() {
  const config = useConfigStore((state) => state.config);
  const hostingType = config?.hosting_config?.type;
  const { initializeConfig } = useConfigStore.getState();
  const [loading, setLoading] = useState(true);

  // Initialize config on mount
  useEffect(() => {
    const loadConfig = async () => {
      setLoading(true);
      await initializeConfig(true, false);
      setLoading(false);
    };
    loadConfig();
  }, []);

  // Get all configured OAuth providers
  const configuredProviders = config?.oauth_configs?.map(
    (provider) => provider?.provider as OAuthProvider
  ).filter(Boolean) || [];
  // Determine whether to show auth buttons
  const shouldShowAuth = !ConfigService.shouldSkipAuth(hostingType || undefined) && configuredProviders.length > 0;

  return (
    <Grid
      templateColumns={{ base: '1fr', lg: '1fr 1fr' }}
      minHeight="100vh"
      width="100%"
    >
      {/* Left Section - Login */}
      <GridItem
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        bg={{ _light: 'gray.50', _dark: 'gray.900' }}
      >
        <VStack gap={8} maxW="400px" width="100%" alignItems="center">
          {/* Branding */}
          <Box>
            <Branding fontSize="4xl" />
          </Box>

          {/* Login Card */}
          <Card.Root
            width="100%"
            borderWidth="1px"
            shadow="lg"
            position="relative"
            overflow="hidden"
          >
            {/* Background bubble effects */}
            <Box
              position="absolute"
              top="-40px"
              right="-40px"
              boxSize="160px"
              bg="primary.500"
              borderRadius="full"
              opacity={0.05}
            />
            <Box
              position="absolute"
              bottom="-40px"
              left="-40px"
              boxSize="160px"
              bg="primary.500"
              borderRadius="full"
              opacity={0.05}
            />
            <Card.Body p={8} position="relative" zIndex={1}>
              <VStack gap={6} align="stretch">
                <Box textAlign="center">
                  <Heading size="xl" mb={2}>
                    Welcome Back
                  </Heading>
                  <Text color="fg.subtle" fontSize="sm">
                    Sign in to continue to Prompt Repo
                  </Text>
                </Box>

                {loading ? (
                  <VStack gap={3} align="stretch">
                    <Skeleton height="10">
                      <Text>Loading providers...</Text>
                    </Skeleton>
                  </VStack>
                ) : shouldShowAuth ? (
                  <VStack gap={3} align="stretch">
                    {configuredProviders.map((provider) => (
                      <LoginPageButton
                        key={provider}
                        provider={provider}
                      />
                    ))}
                  </VStack>
                ) : (
                  <EmptyState.Root>
                    <EmptyState.Content>
                      <EmptyState.Indicator>
                        <HiColorSwatch />
                      </EmptyState.Indicator>
                      <VStack textAlign="center">
                        <EmptyState.Title>No providers found</EmptyState.Title>
                        <EmptyState.Description>
                          No authentication providers are configured
                        </EmptyState.Description>
                      </VStack>
                      <List.Root variant="marker">
                        <List.Item>Check your server configuration</List.Item>
                        <List.Item>Contact your administrator</List.Item>
                      </List.Root>
                    </EmptyState.Content>
                  </EmptyState.Root>
                )}

                <Box textAlign="center" pt={4}>
                  <Text fontSize="xs" color="fg.muted">
                    By signing in, you agree to our Terms of Service and Privacy Policy
                  </Text>
                </Box>
              </VStack>
            </Card.Body>
          </Card.Root>
        </VStack>
      </GridItem>

      {/* Right Section - Quotes Slider */}
      <GridItem
        display={{ base: 'none', lg: 'flex' }}
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        bg={{ _light: 'white', _dark: 'gray.800' }}
        borderLeft="1px solid"
        borderColor={{ _light: 'gray.200', _dark: 'gray.700' }}
        px={8}
        position="relative"
      >
        <Box
          position="absolute"
          top="50%"
          left="30px"
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
          right="30px"
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
          <Box>
            <PromptQuotes />
          </Box>
        </VStack>
      </GridItem>
    </Grid>
  );
}