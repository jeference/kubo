import "@kubo/design-tokens/styles/tokens.css";
import "./globals.css";

import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import type { ReactNode } from "react";

import { Providers } from "@/app/providers";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const display = Space_Grotesk({ subsets: ["latin"], variable: "--font-display" });

export const metadata: Metadata = {
  title: { default: "Kubo: crie e receba sua peça impressa em 3D", template: "%s · Kubo" },
  description:
    "Descreva o que você imagina ou envie uma foto. A gente cria o modelo com IA, e você recebe a peça impressa em 3D em casa.",
  manifest: "/manifest.webmanifest",
  icons: { icon: "/icon.svg" },
};

export const viewport: Viewport = { themeColor: "#7C3AED", viewportFit: "cover" };

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="pt-BR" className={`${sans.variable} ${display.variable}`}>
      <body className="flex min-h-dvh flex-col">
        <Providers>
          <SiteHeader />
          <main className="mx-auto w-full max-w-[1800px] flex-1 px-4 pb-16 pt-6 sm:px-6">
            {children}
          </main>
          <SiteFooter />
        </Providers>
      </body>
    </html>
  );
}
