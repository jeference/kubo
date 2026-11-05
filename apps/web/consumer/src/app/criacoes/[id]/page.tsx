import type { Metadata } from "next";

import { Studio } from "@/features/creations/components/studio";

export const metadata: Metadata = { title: "Sua criação", robots: { index: false } };

export default async function CreationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Studio id={id} />;
}
