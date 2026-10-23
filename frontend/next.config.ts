import type { NextConfig } from "next";
// @ts-expect-error
import withPWAInit from "next-pwa";


const withPWA = withPWAInit({
  dest: "public",
  disable: process.env.NODE_ENV === "development", // Don't cache aggressively in dev mode
  register: true,
  skipWaiting: true,
  publicExcludes: ["!unity-build/**/*"],
  runtimeCaching: [
    { urlPattern: /^https?:\/\/.*\/api\/v1\//, handler: "NetworkOnly", method: "GET" },
  ],
});

const nextConfig: NextConfig = {
  /* Default Next.js output directory and build settings. */
  reactStrictMode: false,
  allowedDevOrigins: ['172.20.10.4'],
};

export default withPWA(nextConfig);


