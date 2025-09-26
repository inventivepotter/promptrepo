'use client';

import { Box, HStack, VStack, Text } from '@chakra-ui/react';
import { LuUser } from 'react-icons/lu';
import { useUser } from '@/stores/authStore';

interface UserProfileProps {
  isCollapsed?: boolean;
  textColor?: string;
  mutedTextColor?: string;
  userProfileBg?: string;
  borderColor?: string;
}

export const UserProfile = ({ 
  isCollapsed = false,
  textColor,
  mutedTextColor,
  userProfileBg,
  borderColor
}: UserProfileProps) => {
  const user = useUser();
  
  if (!user) return null;

  if (isCollapsed) {
    return (
      <Box
        p={2}
        bg={userProfileBg}
        borderRadius="8px"
        border="1px solid"
        borderColor={borderColor}
        mb={2}
      >
        <HStack justify="center">
          <Box
            width="32px"
            height="32px"
            borderRadius="full"
            bg={mutedTextColor}
            display="flex"
            alignItems="center"
            justifyContent="center"
            backgroundImage={user.oauth_avatar_url ? `url(${user.oauth_avatar_url})` : undefined}
            backgroundSize="cover"
            backgroundPosition="center"
          >
            {!user.oauth_avatar_url && (
              <LuUser size={16} color="white" />
            )}
          </Box>
        </HStack>
      </Box>
    );
  }

  return (
    <Box
      p={3}
      bg={userProfileBg}
      borderRadius="8px"
      border="1px solid"
      borderColor={borderColor}
      mb={2}
    >
      <VStack gap={2} align="stretch">
        <HStack gap={3} align="center">
          <Box
            width="32px"
            height="32px"
            borderRadius="full"
            bg={mutedTextColor}
            display="flex"
            alignItems="center"
            justifyContent="center"
            backgroundImage={user.oauth_avatar_url ? `url(${user.oauth_avatar_url})` : undefined}
            backgroundSize="cover"
            backgroundPosition="center"
          >
            {!user.oauth_avatar_url && (
              <LuUser size={16} color="white" />
            )}
          </Box>
          <VStack gap={0} align="flex-start" flex={1} minW={0}>
            <Text
              fontSize="13px"
              fontWeight="600"
              color={textColor}
              width="100%"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              {user.oauth_name || user.oauth_username}
            </Text>
            <Text
              fontSize="12px"
              color={mutedTextColor}
              width="100%"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              @{user.oauth_username}
            </Text>
          </VStack>
        </HStack>
      </VStack>
    </Box>
  );
};