'use client';

import React from 'react';
import {
  Box,
  Text,
  HStack,
} from '@chakra-ui/react';

interface UnauthorizedScreenProps {
  title?: string;
  message?: string;
  showLoginButton?: boolean;
}

export function UnauthorizedScreen({
}: UnauthorizedScreenProps) {

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <HStack gap={6} textAlign="center" maxW="400px" px={4}>
        {/* Large error code */}
        <Text
          fontSize="2xl"
          fontWeight={600}
          lineHeight="1"
        >
          401
        </Text>
        
        {/* Divider line */}
        <Box
          width="1px"
          height="50px"
          bg="gray.300"
          _dark={{ bg: "gray.600" }}
          display={{ base: "none", md: "block" }}
        />
        
          <Text fontSize="sm">
            Unauthorized access.
          </Text>
      </HStack>
    </Box>
  );
}