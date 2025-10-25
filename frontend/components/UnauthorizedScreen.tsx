'use client';

import React from 'react';
import Link from 'next/link';
import {
  Box,
  Text,
  VStack,
  HStack,
  Link as ChakraLink,
} from '@chakra-ui/react';

export function UnauthorizedScreen() {

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
          
          <Box
            width="1px"
            height="50px"
            bg="gray.300"
            _dark={{ bg: "gray.600" }}
          />
          
          <VStack
            align={"start"}
          >
            <Text fontSize="sm" fontWeight={500}>
              Unauthorized access.
            </Text>

            <Text fontSize="xs">
              Please <ChakraLink as={Link} href="/login" textDecoration="underline" color="blue.500">log in</ChakraLink> to access this page.
            </Text>
          </VStack>
        </HStack>
      </Box>
  );
}