import { NotificationOptions } from '@/types/ApiResponse';
import { toaster } from '@/components/ui/toaster';

// This utility works with Chakra UI's toaster system
// It creates and immediately displays notifications

export const createNotification = (options: NotificationOptions): void => {
  const notificationConfig = {
    title: options.title,
    description: options.description,
    type: options.status,
    duration: options.duration || 5000,
    isClosable: options.isClosable !== false,
  };
  
  toaster.create(notificationConfig);
};

export const successNotification = (title: string, description?: string): void => {
  createNotification({
    title,
    description,
    status: 'success',
  });
};

export const errorNotification = (title: string, description?: string): void => {
  createNotification({
    title,
    description,
    status: 'error',
    duration: 8000, // Error messages stay longer
  });
};

export const warningNotification = (title: string, description?: string): void => {
  createNotification({
    title,
    description,
    status: 'warning',
  });
};

export const infoNotification = (title: string, description?: string): void => {
  createNotification({
    title,
    description,
    status: 'info',
  });
};

// Helper to convert API errors to notification
export const apiErrorToNotification = (error: string, message?: string): void => {
  errorNotification(
    'Operation Failed',
    message || error || 'An unexpected error occurred'
  );
};

// Helper to create success notification from API response
export const apiSuccessToNotification = (message: string, description?: string): void => {
  successNotification(
    message || 'Operation Successful',
    description
  );
};