import { NextRequest, NextResponse } from 'next/server';
import { authService } from '@/services/auth/authService';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const promptrepoRedirectUrl = searchParams.get('promptrepo_redirect_url') || undefined;

    // Get the authorization URL from the auth service
    const authUrl = await authService.getAuthUrl(promptrepoRedirectUrl);

    if (!authUrl) {
      return NextResponse.json(
        { error: 'Failed to get authorization URL' },
        { status: 500 }
      );
    }

    // Redirect the user to the GitHub authorization URL
    return NextResponse.redirect(authUrl);
  } catch (error) {
    console.error('Error in GitHub login route:', error);
    return NextResponse.json(
      { error: 'An unexpected error occurred during login initiation' },
      { status: 500 }
    );
  }
}