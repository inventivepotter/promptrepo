import pino from 'pino';

// Create a safe logger that works in both client and server environments
const createLogger = () => {
  try {
    // Simple pino configuration that works in both environments
    return pino({
      name: 'promptrepo',
      level: process.env.NEXT_PUBLIC_LOG_LEVEL || 'info'
    });
  } catch (error) {
    // Fallback to a simple console-based logger if pino fails
    return {
      info: (obj?: Record<string, unknown> | string, msg?: string) => {
        if (typeof obj === 'string') {
          console.info(obj);
        } else {
          console.info(msg || 'Info', obj);
        }
      },
      warn: (obj?: Record<string, unknown> | string, msg?: string) => {
        if (typeof obj === 'string') {
          console.warn(obj);
        } else {
          console.warn(msg || 'Warning', obj);
        }
      },
      error: (obj?: Record<string, unknown> | string, msg?: string) => {
        if (typeof obj === 'string') {
          console.error(obj);
        } else {
          console.error(msg || 'Error', obj);
        }
      },
      debug: (obj?: Record<string, unknown> | string, msg?: string) => {
        if (typeof obj === 'string') {
          console.debug(obj);
        } else {
          console.debug(msg || 'Debug', obj);
        }
      },
    };
  }
};

const logger = createLogger();

export default logger;

// Simple utility functions
export const createRequestId = (): string => {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const logWithTiming = async <T>(
  operation: string,
  fn: () => Promise<T>
): Promise<T> => {
  const start = Date.now();
  logger.debug({ operation }, 'Starting operation');
  
  try {
    const result = await fn();
    const duration = Date.now() - start;
    logger.info({ operation, duration }, 'Operation completed');
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    logger.error({ operation, duration, error }, 'Operation failed');
    throw error;
  }
};