'use client';

import type { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { Box, Stack } from '@chakra-ui/react';
import { Sidebar } from '@/components/sidebar/Sidebar';

export function LayoutContent({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  
  // Don't show sidebar on login page
  const showSidebar = !pathname?.startsWith('/login');

  if (!showSidebar) {
    return <>{children}</>;
  }

  return (
    <Stack direction="row" gap={0} align="stretch" minHeight="100vh">
      <Sidebar />
      <Box flex={1} overflow="auto" height="100vh">
        {children}
      </Box>
    </Stack>
  );
}