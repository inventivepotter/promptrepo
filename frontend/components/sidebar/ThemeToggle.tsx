'use client';

import { Button, ClientOnly, Skeleton } from '@chakra-ui/react';
import { LuMoon, LuSun } from 'react-icons/lu';
import { useColorMode } from '../ui/color-mode';

interface ThemeToggleProps {
  isCollapsed?: boolean;
  hoverBg?: string;
  activeBg?: string;
}

export const ThemeToggle = ({ 
  isCollapsed = false,
  hoverBg,
  activeBg 
}: ThemeToggleProps) => {
  const { colorMode, toggleColorMode } = useColorMode();

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
      onClick={toggleColorMode}
    >
      <ClientOnly fallback={<Skeleton boxSize="4" />}>
        {colorMode === 'dark' ? (
          <LuSun size={16} />
        ) : (
          <LuMoon size={16} />
        )}
      </ClientOnly>
      {!isCollapsed && (
        <ClientOnly fallback={<Skeleton height="20px" width="80px" />}>
          <span style={{ marginLeft: 12, fontSize: 14, fontWeight: 500 }}>
            {colorMode === 'dark' ? 'Light mode' : 'Dark mode'}
          </span>
        </ClientOnly>
      )}
    </Button>
  );
};