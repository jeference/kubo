/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Proxy Django through Next so the browser stays same-origin (no CORS). Same-origin
  // media also matters for <canvas> (color editing) and the GLTF loader.
  //
  // Django routes are slash-terminated: skip Next's trailing-slash normalization and
  // re-append the slash on the destination.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const django = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [
      { source: "/api/:path*", destination: `${django}/api/:path*/` },
      { source: "/media/:path*", destination: `${django}/media/:path*` },
    ];
  },
};

export default nextConfig;
