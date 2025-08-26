import { NotificationOptions } from '@/types/ApiResponse';

// This utility will work with any toast notification system (Chakra UI, react-hot-toast, etc.)
// For now, it's designed to work with Chakra UI's useToast hook

export const createNotification = (options: NotificationOptions): NotificationOptions => {
  return {
    duration: 5000,
    isClosable: true,
    ...options,
  };
};

export const successNotification = (title: string, description?: string): NotificationOptions => {
  return createNotification({
    title,
    description,
    status: 'success',
  });
};

export const errorNotification = (title: string, description?: string): NotificationOptions => {
  return createNotification({
    title,
    description,
    status: 'error',
    duration: 8000, // Error messages stay longer
  });
};

export const warningNotification = (title: string, description?: string): NotificationOptions => {
  return createNotification({
    title,
    description,
    status: 'warning',
  });
};

export const infoNotification = (title: string, description?: string): NotificationOptions => {
  return createNotification({
    title,
    description,
    status: 'info',
  });
};

// Helper to convert API errors to notification options
export const apiErrorToNotification = (error: string, message?: string): NotificationOptions => {
  return errorNotification(
    'Operation Failed',
    message || error || 'An unexpected error occurred'
  );
};

// Helper to create success notification from API response
export const apiSuccessToNotification = (message: string, description?: string): NotificationOptions => {
  return successNotification(
    message || 'Operation Successful',
    description
  );
};