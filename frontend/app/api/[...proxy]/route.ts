import { NextRequest, NextResponse } from 'next/server';

// Get backend URL from environment or default
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';

async function proxyRequest(
  request: NextRequest,
  params: Promise<{ proxy: string[] }>
): Promise<NextResponse> {
  try {
    const { proxy } = await params;
    const path = proxy.join('/');
    
    // Construct the target URL - preserve the /api prefix for backend
    const targetUrl = `${BACKEND_URL}/api/${path}`;
    
    // Get search parameters from the original request
    const searchParams = request.nextUrl.searchParams.toString();
    const fullTargetUrl = searchParams ? `${targetUrl}?${searchParams}` : targetUrl;

    // Prepare headers for the backend request
    const headers = new Headers();
    
    // Copy relevant headers from the original request
    const relevantHeaders = [
      'authorization',
      'content-type',
      'accept',
      'user-agent'
    ];
    
    relevantHeaders.forEach(headerName => {
      const headerValue = request.headers.get(headerName);
      if (headerValue) {
        headers.set(headerName, headerValue);
      }
    });

    // Prepare the request configuration
    const requestConfig: RequestInit = {
      method: request.method,
      headers,
    };

    // Add body for non-GET requests
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        const body = await request.text();
        if (body) {
          requestConfig.body = body;
        }
      } catch (error) {
        console.error('Error reading request body:', error);
      }
    }

    // Make the request to the backend
    const response = await fetch(fullTargetUrl, requestConfig);
    
    // Get the response body
    const responseBody = await response.text();
    
    // Create response headers
    const responseHeaders = new Headers();
    
    // Copy relevant response headers
    const relevantResponseHeaders = [
      'content-type',
      'cache-control',
      'etag',
      'expires',
      'last-modified'
    ];
    
    relevantResponseHeaders.forEach(headerName => {
      const headerValue = response.headers.get(headerName);
      if (headerValue) {
        responseHeaders.set(headerName, headerValue);
      }
    });

    // Add CORS headers for frontend
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });

  } catch (error) {
    console.error('Proxy request failed:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Proxy request failed',
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      },
      { status: 500 }
    );
  }
}

// Handle all HTTP methods
export async function GET(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function POST(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function PUT(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function OPTIONS(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  // Handle preflight CORS requests
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}