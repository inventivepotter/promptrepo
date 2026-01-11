'use client';

import {
  Box,
  HStack,
  Text,
  Link,
} from '@chakra-ui/react';
import { LuExternalLink } from 'react-icons/lu';

export function SharedChatFooter() {
  return (
    <Box px={4} py={3} borderTopWidth="1px" bg="bg.subtle">
      <HStack justify="center" gap={2} fontSize="xs" color="fg.muted">
        <Text>This is a read-only shared conversation.</Text>
        <Text>|</Text>
        <Link href="/" display="flex" alignItems="center" gap={1}>
          <Text>Create your own</Text>
          <LuExternalLink size={10} />
        </Link>
      </HStack>
    </Box>
  );
}
