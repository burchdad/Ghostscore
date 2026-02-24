/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    // Get the backend URL from environment or use default
    // In devcontainer: http://localhost:8000 (port forwarded from docker container)
    // In docker: http://backend:8000 (docker service name)
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    
    return {
      beforeFiles: [
        // Plaid routes are handled by Next.js API routes directly
        {
          source: '/api/plaid/:path*',
          destination: '/api/plaid/:path*',
        },
      ],
      afterFiles: [
        // All other /api/* routes go to the backend (without /api prefix)
        {
          source: '/api/:path*',
          destination: `${backendUrl}/:path*`,
        },
      ],
    }
  },
}

module.exports = nextConfig
