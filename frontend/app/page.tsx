'use client';

import { Button, HStack, VStack, Text, Box, Spinner, Image, Container, Flex } from "@chakra-ui/react";
import { useAuth } from "./(auth)/_components/AuthProvider";
import { useEffect, useMemo, useState } from "react";
import { PromptQuotes } from "@/components/PromptQuotes";
import { Branding } from "@/components/Branding";

const AuthButton = () => {
  const { isAuthenticated, isLoading, user, login, logout } = useAuth();

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
            src={user.avatar_url}
            alt={user.name}
            borderRadius="full"
            boxSize="32px"
          />
        </Box>
        <VStack gap={0} alignItems="flex-start">
          <Text fontSize="sm" fontWeight="medium">{user.name}</Text>
          <Text fontSize="xs" color="gray.500">@{user.login}</Text>
        </VStack>
        <Button size="sm" colorScheme="red" variant="outline" onClick={() => logout()}>
          Logout
        </Button>
      </HStack>
    );
  }

  return (
    <Button colorScheme="blue" onClick={() => login()}>
      Login with GitHub
    </Button>
  );
};

const Demo = () => {
  const { checkAuth } = useAuth();

  useEffect(() => {
    // Check authentication status on component mount
    checkAuth();
  }, [checkAuth]);

  // Track window dimensions for background
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    // Set initial dimensions
    updateDimensions();
    
    // Update on resize
    window.addEventListener('resize', updateDimensions);

    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  // Generate random positions for curly braces across entire screen
  const bracePositions = useMemo(() => {
    const positions = [];
    const braceCount = 800;
    
    for (let i = 0; i < braceCount; i++) {
      positions.push({
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height,
        scale: 0.3 + Math.random() * 2.0,
        isOpening: Math.random() > 0.5,
        rotation: Math.random() * 360,
      });
    }
    return positions;
  }, [dimensions.width, dimensions.height]);

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
        {/* SVG Background with scattered curly braces */}
        <Box
          position="fixed"
          top={0}
          left={0}
          right={0}
          bottom={0}
          zIndex={0}
          overflow="hidden"
          pointerEvents="none"
        >
          <svg
            width="100%"
            height="100%"
            viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
            preserveAspectRatio="xMidYMid slice"
            style={{
              opacity: 0.4,
            }}
          >
            {/* Define curly brace paths - simpler, regular font style */}
            <defs>
              <g id="opening-brace">
                <text
                  fontSize="64"
                  fill="#374151"
                  fontFamily="monospace"
                  textAnchor="middle"
                  dominantBaseline="central"
                >
                  {"{"}
                </text>
              </g>
              <g id="closing-brace">
                <text
                  fontSize="64"
                  fill="#374151"
                  fontFamily="monospace"
                  textAnchor="middle"
                  dominantBaseline="central"
                >
                  {"}"}
                </text>
              </g>
            </defs>

            {/* Dynamically positioned braces */}
            {bracePositions.map((brace, index) => (
              <use
                key={index}
                href={brace.isOpening ? "#opening-brace" : "#closing-brace"}
                x={brace.x}
                y={brace.y}
                transform={`scale(${brace.scale}) rotate(${brace.rotation} ${brace.x} ${brace.y})`}
              />
            ))}
          </svg>
        </Box>

        {/* Main content - positioned above background */}
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
                  Master Prompt Engineering
                </Text>
                <Text
                  fontSize={{ base: "lg", md: "xl" }}
                  color="gray.600"
                  _dark={{ color: "gray.400" }}
                  maxW="2xl"
                  lineHeight="1.6"
                >
                  Discover, create, and share powerful prompts that unlock
                  the full potential of AI agents and guide them to your goals.
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
    <Demo />
  );
}
