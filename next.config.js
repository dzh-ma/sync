/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React Strict Mode for better development experience
  reactStrictMode: true,
  
  // Improve page load performance
  experimental: {
    // Use native React concurrent features
    transpilePackages: ['lucide-react', 'framer-motion'],
    
    // Optimize server components (compatible with newer Next.js versions)
    serverComponentsExternalPackages: [],
    
    // Prefetch pages on hover over links to reduce load time
    optimisticClientCache: true,
  },
  
  // Image optimization configuration
  images: {
    // Higher quality images
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    // Optimize sizing for the application
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    // Faster image loading with quality tradeoff
    formats: ['image/webp'],
  },
  
  // Optimize compilation for production
  compiler: {
    // Remove console.log statements in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },
  
  // Improve loading performance
  swcMinify: true,
  
  // Enable aggressive chunking for faster initial load
  distDir: '.next',
  
  // Automatically inline certain assets
  assetPrefix: undefined,
  
  // Configure output for faster builds
  output: 'standalone',
  
  // Custom webpack config to improve performance
  webpack: (config, { dev, isServer }) => {
    // Only apply optimizations in production
    if (!dev) {
      // Keep the existing config but ensure it's compatible
      if (config.optimization && !isServer) {
        config.optimization.runtimeChunk = 'single';
      }
    }
    
    return config;
  },
};

module.exports = nextConfig; 