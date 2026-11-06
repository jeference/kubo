const isProduction = process.env.NODE_ENV === "production";

const contentSecurityPolicy = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  // As imagens vêm do storage por URL assinada.
  "img-src 'self' data: blob: https:",
  "font-src 'self'",
  "connect-src 'self'",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Só na imagem Docker: no Windows, o modo standalone exige permissão para criar symlinks.
  output: process.env.NEXT_STANDALONE ? "standalone" : undefined,
  transpilePackages: [
    "@kubo/api-types",
    "@kubo/api-client",
    "@kubo/design-tokens",
    "@kubo/ui",
    "@kubo/web-core",
    "@kubo/analytics",
  ],
  // O navegador fica na mesma origem, sem CORS. As rotas do Django terminam em barra: evitamos
  // o redirecionamento do Next e devolvemos a barra no destino.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    const django = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${django}/api/:path*/` }];
  },
  async headers() {
    const security = [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    ];
    if (isProduction) {
      security.push({ key: "Content-Security-Policy", value: contentSecurityPolicy });
    }
    return [
      { source: "/:path*", headers: security },
      // O token do acompanhamento está na URL: não pode vazar em cabeçalhos.
      {
        source: "/acompanhar/:token*",
        headers: [{ key: "Referrer-Policy", value: "no-referrer" }],
      },
    ];
  },
};

export default nextConfig;
