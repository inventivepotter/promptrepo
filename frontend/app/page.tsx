'use client';

import { Button, HStack, VStack, Text, Box, Spinner, Image, Container, Flex } from "@chakra-ui/react";
import {
  useUser,
  useIsAuthenticated,
  useAuthLoading,
  useAuthActions
} from '@/stores/authStore';
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PromptQuotes } from "@/components/PromptQuotes";
import { Branding } from "@/components/Branding";
import { ConfigService } from "@/services/config/configService";

const AuthButton = () => {
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();
  const user = useUser();
  const { login, logout, initializeAuth } = useAuthActions();
  const [hostingType, setHostingType] = useState<string>('');

  useEffect(() => {
    // Initialize authentication on component mount
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    const loadHostingType = async () => {
      try {
        const type = await ConfigService.getHostingType();
        setHostingType(type);
      } catch (error) {
        console.warn('Failed to load hosting type:', error);
        setHostingType('individual');
      }
    };
    
    loadHostingType();
  }, []);

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
          <Image
            src={user.oauth_avatar_url || ''}
            alt={user.oauth_name || ''}
            borderRadius="full"
            boxSize="32px"
          />
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
  if (ConfigService.shouldSkipAuth(hostingType)) {
    return null;
  }

  return (
    <Button colorScheme="blue" onClick={() => login()}>
      Login with GitHub
    </Button>
  );
};

const HomePage = () => {
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();
  const router = useRouter();


  // useEffect(() => {
  //   // Redirect authenticated users to prompts page
  //   if (isAuthenticated && !isLoading) {
  //     router.push('/prompts');
  //   }
  // }, [isAuthenticated, isLoading, router]);


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
        <Branding color="gray.900" _dark={{ color: "gray.100" }} fontSize="3xl" />
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
                color="gray.200"
                _dark={{ color: "gray.800" }}
                zIndex={0}
                opacity={0.9}
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
                color="gray.200"
                _dark={{ color: "gray.800" }}
                zIndex={0}
                opacity={0.7}
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
                  color="gray.900"
                  _dark={{ color: "gray.100" }}
                  lineHeight="1.1"
                >
                  Craft Better Prompts
                </Text>
                <Text
                  fontSize={{ base: "lg", md: "xl" }}
                  color="gray.600"
                  _dark={{ color: "gray.400" }}
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
                bg="gray.900"
                color="white"
                _hover={{ bg: "gray.800" }}
                _dark={{
                  bg: "gray.100",
                  color: "gray.900",
                  _hover: { bg: "gray.200" }
                }}
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
                borderColor="gray.300"
                color="gray.700"
                _hover={{
                  borderColor: "gray.400",
                  bg: "gray.50"
                }}
                _dark={{
                  borderColor: "gray.600",
                  color: "gray.300",
                  _hover: {
                    borderColor: "gray.500",
                    bg: "gray.800"
                  }
                }}
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
