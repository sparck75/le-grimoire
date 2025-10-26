/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  images: {
    domains: ['localhost', '192.168.1.133'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
  async rewrites() {
    // Server-side rewrites MUST use Docker service name 'backend'
    // NEXT_PUBLIC_* variables are for browser/client-side only
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    
    console.log('🔗 API Rewrite configured to:', backendUrl);
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
