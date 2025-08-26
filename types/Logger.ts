import { Logger as PinoLogger } from 'pino';

export type Logger = PinoLogger;

export interface LogContext {
  [key: string]: unknown;
  component?: string;
  action?: string;
  requestId?: string;
  userId?: string;
  duration?: number;
  error?: Error;
}
