export type CatalogModel = {
  key: string;
  label: string;
  estimated_cost: number;
  settings: Record<string, unknown>;
};

export type RunModel = CatalogModel & {
  status: "processing" | "success" | "error";
  glb_url: string;
  /** Real cost reported by Runware. Null while generating or when it wasn't reported. */
  cost: number | null;
  error: string;
  seconds: number | null;
  triangles: number | null;
  file_bytes: number | null;
};

export type Run = {
  id: string;
  image_url: string;
  models: RunModel[];
};
