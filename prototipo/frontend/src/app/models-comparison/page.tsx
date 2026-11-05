import type { Metadata } from "next";
import { Suspense } from "react";

import { ComparisonPage } from "@/features/model-comparison/components/comparison-page";

export const metadata: Metadata = {
  title: "TEMPORÁRIO: comparação de modelos 3D",
};

export default function ModelsComparison() {
  return (
    <Suspense>
      <ComparisonPage />
    </Suspense>
  );
}
