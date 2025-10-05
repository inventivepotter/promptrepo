'use client';
import { usePathname } from 'next/navigation';
import { Button } from '@chakra-ui/react';
import { SiGitlab, SiBitbucket, SiGithub } from 'react-icons/si';
import { useAuthActions } from '@/stores/authStore';
import type { components } from '@/types/generated/api';

type OAuthProvider = components['schemas']['OAuthProvider'];

interface LoginPageButtonProps {
  provider: OAuthProvider;
}

const providerConfig = {
  github: {
    icon: SiGithub,
    label: 'GitHub',
    bgColor: '#24292e',
    hoverBgColor: '#1a1e22',
    textColor: 'white',
  },
  gitlab: {
    icon: SiGitlab,
    label: 'GitLab',
    bgColor: '#FC6D26',
    hoverBgColor: '#E24329',
    textColor: 'white',
  },
  bitbucket: {
    icon: SiBitbucket,
    label: 'BitBucket',
    bgColor: '#0052CC',
    hoverBgColor: '#0747A6',
    textColor: 'white',
  },
} as const;

export const LoginPageButton = ({ provider }: LoginPageButtonProps) => {
  const { login } = useAuthActions();
  const pathname = usePathname();

  const config = providerConfig[provider];
  const Icon = config.icon;

  return (
    <Button
      justifyContent="center"
      size="sm"
      p={2}
      transition="all 0.4s ease"
      onClick={() => login(pathname)}
      bg={config.bgColor}
      color={config.textColor}
      _hover={{
        bg: config.hoverBgColor,
      }}
      border="none"
    >
      <Icon size={18} />
      <span style={{ marginLeft: 10, fontSize: 15, fontWeight: 500 }}>
        Login with {config.label}
      </span>
    </Button>
  );
};