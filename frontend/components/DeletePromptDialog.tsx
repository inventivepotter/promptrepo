'use client';

import { Dialog, Button, Portal } from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';

interface DeletePromptDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  promptName: string;
  onConfirm: () => void;
  isDeleting?: boolean;
}

export function DeletePromptDialog({
  open,
  onOpenChange,
  promptName,
  onConfirm,
  isDeleting = false,
}: DeletePromptDialogProps) {
  const handleDelete = () => {
    onConfirm();
  };

  return (
    <Dialog.Root open={open} onOpenChange={(e) => onOpenChange(e.open)} role="alertdialog">
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>Delete Prompt?</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <p>
                Are you sure you want to delete &quot;{promptName}&quot;? This action cannot be undone. 
                This will permanently remove the prompt file from the repository.
              </p>
            </Dialog.Body>
            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <Button variant="outline" disabled={isDeleting}>
                  Cancel
                </Button>
              </Dialog.ActionTrigger>
              <Button 
                colorPalette="red" 
                onClick={handleDelete}
                loading={isDeleting}
                disabled={isDeleting}
              >
                Delete
              </Button>
            </Dialog.Footer>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" disabled={isDeleting} />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
}