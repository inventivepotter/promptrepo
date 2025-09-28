'use client';

import { Button } from '@chakra-ui/react';
import { LuChevronLeft, LuChevronRight } from 'react-icons/lu';
import { useSidebarCollapsed, useSidebarActions } from '@/stores/sidebarStore';

interface SidebarToggleProps {
  hoverBg?: string;
  activeBg?: string;
}

export const SidebarToggle = ({
  hoverBg,
  activeBg 
}: SidebarToggleProps) => {
  const isCollapsed = useSidebarCollapsed();
  const { toggleCollapsed } = useSidebarActions();

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
      onClick={toggleCollapsed}
    >
      {isCollapsed ? (
        <LuChevronRight size={16} />
      ) : (
        <LuChevronLeft size={16} />
      )}
      {!isCollapsed && (
        <span style={{ marginLeft: 12, fontSize: 14, fontWeight: 500 }}>
          Collapse sidebar
        </span>
      )}
    </Button>
  );
};