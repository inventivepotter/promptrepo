'use client';

import { useState } from 'react';
import {
  Button,
  Dialog,
  Portal,
  VStack,
  HStack,
  Text,
  Input,
  Box,
  Field,
  Checkbox,
} from '@chakra-ui/react';
import { LuShare2, LuCopy, LuCheck, LuExternalLink } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { useChatStore } from '@/stores/chatStore';

interface ShareChatButtonProps {
  disabled?: boolean;
}

export function ShareChatButton({ disabled = false }: ShareChatButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [title, setTitle] = useState('');
  const [includeSystemPrompt, setIncludeSystemPrompt] = useState(true);
  const [step, setStep] = useState<'title' | 'sharing' | 'done' | 'error'>('title');

  // Use individual selectors to avoid infinite loop from object creation
  const shareCurrentSession = useChatStore((state) => state.shareCurrentSession);
  const isSharing = useChatStore((state) => state.isSharing);
  const messages = useChatStore((state) => state.messages);

  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const inputBgColor = useColorModeValue('gray.50', 'gray.800');

  const hasMessages = messages.length > 0;

  const handleOpenModal = () => {
    setIsOpen(true);
    setStep('title');
    setTitle('');
    setIncludeSystemPrompt(true);
    setShareUrl(null);
    setCopied(false);
  };

  const handleShare = async () => {
    if (!title.trim()) return;

    setStep('sharing');

    const result = await shareCurrentSession(title.trim(), includeSystemPrompt);
    if (result) {
      // Use current origin to build full URL if share_url is relative
      const fullUrl = result.shareUrl.startsWith('http')
        ? result.shareUrl
        : `${window.location.origin}${result.shareUrl.startsWith('/') ? '' : '/'}${result.shareUrl}`;
      setShareUrl(fullUrl);
      setStep('done');
    } else {
      setStep('error');
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setShareUrl(null);
    setCopied(false);
    setTitle('');
    setIncludeSystemPrompt(true);
    setStep('title');
  };

  const handleCopy = async () => {
    if (shareUrl) {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleOpenLink = () => {
    if (shareUrl) {
      window.open(shareUrl, '_blank');
    }
  };

  return (
    <>
      <Button
        variant="ghost"
        _hover={{ bg: 'bg.subtle' }}
        size="sm"
        colorPalette="blue"
        onClick={handleOpenModal}
        disabled={disabled || !hasMessages || isSharing}
        loading={isSharing}
      >
        <HStack gap={1}>
          <LuShare2 size={14} />
          <Text fontSize="xs" fontWeight="medium">
            Share
          </Text>
        </HStack>
      </Button>

      <Portal>
        <Dialog.Root open={isOpen} onOpenChange={(e) => e.open ? null : handleClose()}>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>Share Chat</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <VStack gap={4} align="stretch">
                {step === 'title' && (
                  <>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Give your shared chat a title so others know what it's about.
                    </Text>
                    <Field.Root required>
                      <Field.Label>Chat Title</Field.Label>
                      <Input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="e.g., Debugging API Error"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && title.trim()) {
                            handleShare();
                          }
                        }}
                        autoFocus
                      />
                    </Field.Root>
                    <Checkbox.Root
                      checked={includeSystemPrompt}
                      onCheckedChange={(e) => setIncludeSystemPrompt(!!e.checked)}
                      size="sm"
                    >
                      <Checkbox.HiddenInput />
                      <Checkbox.Control />
                      <Checkbox.Label fontSize="sm">Include system prompt in shared chat</Checkbox.Label>
                    </Checkbox.Root>
                  </>
                )}

                {step === 'sharing' && (
                  <Box textAlign="center" py={4}>
                    <Text color={mutedTextColor}>Generating share link...</Text>
                  </Box>
                )}

                {step === 'done' && shareUrl && (
                  <>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Anyone with this link can view this chat conversation. The shared view is read-only.
                    </Text>
                    <HStack gap={2}>
                      <Input
                        value={shareUrl}
                        readOnly
                        bg={inputBgColor}
                        fontSize="sm"
                        onClick={(e) => (e.target as HTMLInputElement).select()}
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopy}
                        minW="80px"
                      >
                        <HStack gap={1}>
                          {copied ? <LuCheck size={14} /> : <LuCopy size={14} />}
                          <Text>{copied ? 'Copied!' : 'Copy'}</Text>
                        </HStack>
                      </Button>
                    </HStack>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleOpenLink}
                      alignSelf="flex-start"
                    >
                      <HStack gap={1}>
                        <LuExternalLink size={14} />
                        <Text>Open in new tab</Text>
                      </HStack>
                    </Button>
                  </>
                )}

                {step === 'error' && (
                  <Box textAlign="center" py={4}>
                    <Text color="red.500">Failed to generate share link. Please try again.</Text>
                  </Box>
                )}
              </VStack>
            </Dialog.Body>
            <Dialog.Footer>
              {step === 'title' ? (
                <>
                  <Button variant="outline" onClick={handleClose}>
                    Cancel
                  </Button>
                  <Button
                    colorPalette="blue"
                    onClick={handleShare}
                    disabled={!title.trim()}
                  >
                    Share
                  </Button>
                </>
              ) : (
                <Button variant="outline" onClick={handleClose}>
                  Close
                </Button>
              )}
            </Dialog.Footer>
            <Dialog.CloseTrigger />
          </Dialog.Content>
          </Dialog.Positioner>
        </Dialog.Root>
      </Portal>
    </>
  );
}
