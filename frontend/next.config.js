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
    // For mobile access: use NEXT_PUBLIC_API_URL if set (contains local IP)
    // For Docker internal: use BACKEND_URL or fallback to service name
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://backend:8000';
    
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
