'use client';

import React from 'react';
import { useLoadingStore } from '@/stores/loadingStore';
import { LoadingOverlay } from './LoadingOverlay';

export function GlobalLoadingOverlay() {
  const { isLoading, title, message } = useLoadingStore();

  return (
    <LoadingOverlay
      isVisible={isLoading}
      title={title}
      subtitle={message}
    />
  );
}