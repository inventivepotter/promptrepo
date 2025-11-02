/**
 * URL-safe base64 encoding/decoding utilities
 * These functions handle encoding and decoding of parameters that may contain special characters
 * like slashes, making them safe for use in URL path segments.
 */

/**
 * Encode a string to URL-safe base64
 * @param str - The string to encode
 * @returns URL-safe base64 encoded string
 */
export function encodeBase64Url(str: string): string {
  if (typeof window === 'undefined') {
    // Server-side encoding (Node.js)
    return Buffer.from(str, 'utf-8')
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  } else {
    // Client-side encoding (browser)
    return btoa(str)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }
}

/**
 * Decode a URL-safe base64 string
 * @param str - The base64 string to decode
 * @returns Decoded string
 */
export function decodeBase64Url(str: string): string {
  // Add back padding if needed
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  while (base64.length % 4) {
    base64 += '=';
  }

  if (typeof window === 'undefined') {
    // Server-side decoding (Node.js)
    return Buffer.from(base64, 'base64').toString('utf-8');
  } else {
    // Client-side decoding (browser)
    return atob(base64);
  }
}

/**
 * Build an editor URL with base64-encoded parameters
 * @param repoName - Repository name (may contain slashes)
 * @param filePath - File path (may contain slashes)
 * @param mode - Optional mode (e.g., 'new' for creating new artifacts)
 * @returns Formatted URL path
 */
export function buildEditorUrl(repoName: string, filePath?: string, mode?: string): string {
  const encodedRepo = encodeBase64Url(repoName);
  
  if (mode === 'new' || !filePath) {
    // For new artifacts, only include repo
    return `/prompts/editor/${encodedRepo}/new`;
  }
  
  const encodedFile = encodeBase64Url(filePath);
  return `/prompts/editor/${encodedRepo}/${encodedFile}`;
}

  /**
   * Build an eval editor URL with base64-encoded parameters
   * @param repoName - Repository name (may contain slashes)
   * @param evalId - Eval ID or 'new' for creating new evals
   * @returns Formatted URL path
   */
export function buildEvalEditorUrl(repoName: string, evalId?: string): string {
    const encodedRepo = encodeBase64Url(repoName);
    const id = evalId || 'new';
    
    if (id === 'new') {
      return `/evals/editor/${encodedRepo}/new`;
    }
    
    const encodedId = encodeBase64Url(id);
    return `/evals/editor/${encodedRepo}/${encodedId}`;
}

/**
 * Build a tool editor URL with base64-encoded parameters
 * @param repoName - Repository name (may contain slashes)
 * @param toolName - Tool name or 'new' for creating new tools
 * @returns Formatted URL path
 */
export function buildToolEditorUrl(repoName: string, toolName?: string): string {
  const encodedRepo = encodeBase64Url(repoName);
  const tool = toolName || 'new';
  
  if (tool === 'new') {
    return `/tools/editor/${encodedRepo}/new`;
  }
  
  const encodedTool = encodeBase64Url(tool);
  return `/tools/editor/${encodedRepo}/${encodedTool}`;
}