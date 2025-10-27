import { NextRequest, NextResponse } from 'next/server';

// Mark this route as dynamic - it fetches from backend
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    const url = `${backendUrl}/api/v2/ingredients/stats/summary`;
    
    console.log('Proxying stats request to:', url);
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      console.error('Backend error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Backend request failed' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch from backend' },
      { status: 500 }
    );
  }
}
