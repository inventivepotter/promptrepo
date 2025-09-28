'use client';

import { Button } from '@chakra-ui/react';
import { LuLogOut } from 'react-icons/lu';
import { useAuthActions } from '@/stores/authStore';

interface LogoutButtonProps {
  isCollapsed?: boolean;
  hoverBg?: string;
  activeBg?: string;
}

export const LogoutButton = ({ 
  isCollapsed = false,
  hoverBg,
  activeBg 
}: LogoutButtonProps) => {
  const { logout } = useAuthActions();

  return (
    <Button
      variant="ghost"
      justifyContent={isCollapsed ? "center" : "flex-start"}
      size="sm"
      width="100%"
      _hover={{ bg: hoverBg, transform: "translateX(2px)" }}
      _active={{ bg: activeBg }}
      px={isCollapsed ? 2 : 3}
      py={2}
      height="36px"
      borderRadius="6px"
      fontWeight="500"
      transition="all 0.15s ease"
      onClick={() => logout()}
    >
      <LuLogOut size={16} />
      {!isCollapsed && (
        <span style={{ marginLeft: 12, fontSize: 14, fontWeight: 500 }}>
          Logout
        </span>
      )}
    </Button>
  );
};