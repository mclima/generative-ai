/** @type {import('next').NextConfig} */
const nextConfig = {
  // Suppress Node.js deprecation warnings in production logs
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals = [...(config.externals || []), 'punycode']
    }
    return config
  },
}

module.exports = nextConfig
