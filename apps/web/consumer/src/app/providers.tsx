"use client";

import { Toaster } from "@kubo/ui/sonner";
import { CoreProviders } from "@kubo/web-core/providers";
import type { ReactNode } from "react";

export function Providers({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <CoreProviders>
      {children}
      <Toaster />
    </CoreProviders>
  );
}
