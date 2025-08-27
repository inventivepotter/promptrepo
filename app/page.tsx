'use client';

import { Button, HStack, VStack, Text, Box, Spinner, Image } from "@chakra-ui/react";
import { useAuth } from "./(auth)/_components/AuthProvider";
import { useEffect } from "react";

const AuthButton = () => {
  const { isAuthenticated, isLoading, user, login, logout } = useAuth();

  if (isLoading) {
    return (
      <HStack gap={2}>
        <Spinner size="sm" />
        <Text>Checking authentication...</Text>
      </HStack>
    );
  }

  if (isAuthenticated && user) {
    return (
      <VStack gap={2} alignItems="flex-start">
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
            <Box>
              <a
                href={user.html_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontSize: "12px",
                  color: "gray",
                  textDecoration: "none"
                }}
                onMouseEnter={(e: React.MouseEvent<HTMLAnchorElement>) =>
                  (e.target as HTMLAnchorElement).style.textDecoration = "underline"
                }
                onMouseLeave={(e: React.MouseEvent<HTMLAnchorElement>) =>
                  (e.target as HTMLAnchorElement).style.textDecoration = "none"
                }
              >
                @{user.login}
              </a>
            </Box>
          </VStack>
        </HStack>
        <Button size="sm" colorScheme="red" onClick={() => logout()}>
          Logout
        </Button>
      </VStack>
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

  return (
    <VStack gap={4} p={6} alignItems="flex-start">
      <Box>
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Welcome to PromptRepo
        </Text>
        <Text color="gray.600">
          Please log in with GitHub to access your repositories and prompts.
        </Text>
      </Box>
      
      <AuthButton />
      
      <HStack gap={2} mt={4}>
        <Button variant="outline">View Public Prompts</Button>
        <Button variant="outline">Documentation</Button>
      </HStack>
    </VStack>
  );
}

export default function Home() {
  return (
    <Demo />
  );
}
