export type StoredImage = {
  id: string;
  url: string;
  cost: number | null;
};

export type ModelStatus = {
  id: string;
  status: "processing" | "success" | "error";
  glb_url: string;
  cost: number | null;
  error: string;
};

export type Step = "create" | "pick" | "model";

export type ImageRound = {
  prompt: string;
  images: StoredImage[];
};

export type CostEntry = {
  label: string;
  value: number;
};
