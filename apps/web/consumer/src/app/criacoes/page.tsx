import type { Metadata } from "next";

import { CreationList } from "@/features/creations/components/creation-list";

export const metadata: Metadata = { title: "Minhas criações" };

export default function CreationsPage() {
  return <CreationList />;
}
