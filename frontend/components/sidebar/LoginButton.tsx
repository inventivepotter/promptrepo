'use client';
import { usePathname } from 'next/navigation';
import { Button } from '@chakra-ui/react';
import { LuGithub } from 'react-icons/lu';
import { useAuthActions } from '@/stores/authStore';

interface LoginButtonProps {
  isCollapsed?: boolean;
  textColor?: string;
  mutedTextColor?: string;
  hoverBg?: string;
  activeBg?: string;
}

export const LoginButton = ({ 
  isCollapsed = false,
  textColor,
  mutedTextColor,
  hoverBg,
  activeBg 
}: LoginButtonProps) => {
  const { login } = useAuthActions();
  const pathname = usePathname();
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
      onClick={() => login(pathname)}
    >
      <LuGithub size={16} color={mutedTextColor} />
      {!isCollapsed && (
        <span style={{ marginLeft: 12, fontSize: 14, color: textColor, fontWeight: 500 }}>
          Login with GitHub
        </span>
      )}
    </Button>
  );
};