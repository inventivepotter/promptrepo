'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Text, Code, Box, Heading } from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const codeBg = useColorModeValue('gray.100', 'gray.700');
  const codeColor = useColorModeValue('gray.800', 'gray.100');
  const blockquoteBorder = useColorModeValue('gray.300', 'gray.600');
  const blockquoteBg = useColorModeValue('gray.50', 'gray.800');

  return (
    <ReactMarkdown
      components={{
        // Paragraphs
        p: ({ children }) => (
          <Text fontSize="sm" mb={2} whiteSpace="pre-wrap">
            {children}
          </Text>
        ),
        
        // Headings
        h1: ({ children }) => (
          <Heading size="lg" mb={2} mt={4}>
            {children}
          </Heading>
        ),
        h2: ({ children }) => (
          <Heading size="md" mb={2} mt={3}>
            {children}
          </Heading>
        ),
        h3: ({ children }) => (
          <Heading size="sm" mb={2} mt={3}>
            {children}
          </Heading>
        ),
        
        // Inline code
        code: ({ children, className }) => {
          const isBlock = className?.includes('language-');
          
          if (isBlock) {
            // Block code
            return (
              <Box
                as="pre"
                bg={codeBg}
                color={codeColor}
                p={3}
                borderRadius="md"
                overflow="auto"
                fontSize="sm"
                fontFamily="mono"
                mb={2}
              >
                <code>{children}</code>
              </Box>
            );
          }
          
          // Inline code
          return (
            <Code
              bg={codeBg}
              color={codeColor}
              px={1}
              py={0.5}
              borderRadius="sm"
              fontSize="sm"
            >
              {children}
            </Code>
          );
        },
        
        // Blockquotes
        blockquote: ({ children }) => (
          <Box
            borderLeft="4px solid"
            borderColor={blockquoteBorder}
            bg={blockquoteBg}
            pl={4}
            py={2}
            my={2}
            borderRadius="md"
          >
            {children}
          </Box>
        ),
        
        // Lists
        ul: ({ children }) => (
          <Box as="ul" ml={4} mb={2}>
            {children}
          </Box>
        ),
        ol: ({ children }) => (
          <Box as="ol" ml={4} mb={2}>
            {children}
          </Box>
        ),
        li: ({ children }) => (
          <Text as="li" fontSize="sm" mb={1}>
            {children}
          </Text>
        ),
        
        // Strong and emphasis
        strong: ({ children }) => (
          <Text as="strong" fontWeight="bold">
            {children}
          </Text>
        ),
        em: ({ children }) => (
          <Text as="em" fontStyle="italic">
            {children}
          </Text>
        ),
        
        // Links
        a: ({ children, href }) => (
          <a
            href={href}
            style={{
              color: 'var(--chakra-colors-blue-500)',
              textDecoration: 'underline'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--chakra-colors-blue-600)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--chakra-colors-blue-500)';
            }}
          >
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}