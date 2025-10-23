'use client';
import { usePathname } from 'next/navigation';
import { Button } from '@chakra-ui/react';
import { LuGithub } from 'react-icons/lu';
import { SiGitlab, SiBitbucket } from 'react-icons/si';
import { useAuthActions } from '@/stores/authStore';
import type { components } from '@/types/generated/api';
import { useSidebarStore } from '@/stores/sidebarStore';

type OAuthProvider = components['schemas']['OAuthProvider'];

interface LoginButtonProps {
  provider: OAuthProvider;
}

const providerConfig = {
  github: {
    icon: LuGithub,
    label: 'GitHub',
  },
  gitlab: {
    icon: SiGitlab,
    label: 'GitLab',
  },
  bitbucket: {
    icon: SiBitbucket,
    label: 'BitBucket',
  },
} as const;

export const LoginButton = ({ provider }: LoginButtonProps) => {
  const { login } = useAuthActions();
  const pathname = usePathname();
  const isCollapsed = useSidebarStore((state) => state.isCollapsed);
  const hoverBg = "bg.muted";
  const activeBg = "bg.emphasized";

  const config = providerConfig[provider];
  const Icon = config.icon;

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
      <Icon size={16} />
      {!isCollapsed && (
        <span style={{ marginLeft: 12, fontSize: 14, fontWeight: 500 }}>
          {config.label} Login
        </span>
      )}
    </Button>
  );
};