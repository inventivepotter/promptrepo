import type { components } from '@/types/generated/api';

export type User = components['schemas']['User'];
export type LoginResponse = components['schemas']['LoginResponseData'];

export interface SessionData {
  isAuthenticated: boolean;
  user?: User;
}