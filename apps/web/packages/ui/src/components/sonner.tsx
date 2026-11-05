"use client";

import { Toaster as Sonner, type ToasterProps } from "sonner";

export function Toaster(props: ToasterProps) {
  // No topo: embaixo, cobriria os botões fixos do celular.
  return <Sonner position="top-center" richColors closeButton {...props} />;
}
