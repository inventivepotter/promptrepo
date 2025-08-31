import { configApi } from '@/app/(config)/_lib/api/configApi';

interface HostingTypeCache {
  type: string | null;
  timestamp: number;
  promise: Promise<string> | null;
}

const cache: HostingTypeCache = {
  type: null,
  timestamp: 0,
  promise: null
};

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export async function getHostingType(): Promise<string> {
  const now = Date.now();
  
  // Return cached value if it's fresh
  if (cache.type && (now - cache.timestamp) < CACHE_DURATION) {
    return cache.type;
  }
  
  // Return existing promise if one is already in flight
  if (cache.promise) {
    return cache.promise;
  }
  
  // Create new promise
  cache.promise = fetchHostingType();
  
  try {
    const type = await cache.promise;
    cache.type = type;
    cache.timestamp = now;
    cache.promise = null;
    return type;
  } catch (error) {
    cache.promise = null;
    // Return cached value if available, otherwise default to individual
    return cache.type || 'individual';
  }
}

async function fetchHostingType(): Promise<string> {
  try {
    const result = await configApi.getHostingType();
    if (result.success && result.data) {
      return result.data.hosting_type;
    }
    return 'individual';
  } catch (error) {
    console.warn('Failed to fetch hosting type, defaulting to individual:', error);
    return 'individual';
  }
}

export function isIndividualHosting(hostingType?: string): boolean {
  return !hostingType || hostingType === 'individual';
}

export function shouldSkipAuth(hostingType?: string): boolean {
  return isIndividualHosting(hostingType);
}

// Clear cache (useful for testing or manual refresh)
export function clearHostingTypeCache(): void {
  cache.type = null;
  cache.timestamp = 0;
  cache.promise = null;
}